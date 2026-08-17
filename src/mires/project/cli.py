"""The `mires project` command group.

A project is synced, not installed. `pull` materializes what the sync repository
holds, `push` sends the local payload back, and `sync` picks the direction when
only one side has the project. When both sides exist and their state definitions
disagree, the command stops and asks for a direction rather than guessing which
definition is the real one.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import TextIO

from mires.messages import ValidationMessage
from mires.project.loader import (
    ProjectNotFoundError,
    find_project_root,
    load_project,
    project_state_path,
    validate_project,
)
from mires.project.models import DEFAULT_BRANCH, DEFAULT_PREFIX, PROJECT_DIR, ProjectState
from mires.project.remote import (
    GitError,
    RemoteNotConfiguredError,
    SyncRepo,
    open_sync_repo,
    resolve_remote,
)
from mires.project.sync import (
    PULL,
    PUSH,
    SecretsRefusedError,
    SyncManifest,
    SyncReport,
    compare,
    digests,
    drifted,
    payload_paths,
    transfer,
)
from mires.state.loader import STATE_FILE, StateFileError

__all__ = ["main"]

EXIT_OK = 0
EXIT_INVALID = 1

STATE_TEMPLATE = """\
version: 1

project:
  name: {name}
  slug: {slug}
  remote:
    {repo}
    branch: {branch}
    prefix: {prefix}
  # Paths this project keeps outside its own repository, mirrored exactly as they are.
  include: []
"""

REPO_PLACEHOLDER = "# repo: git@github.com:you/your-repo.git   # or set MIRES_SYNC_REPO"


def main(argv: list[str]) -> int:
    """Entry point for `mires project ...`, called with the leading command word removed."""
    args = build_parser().parse_args(argv)
    try:
        return ACTIONS[args.action](args)
    except StateFileError as exc:
        return fail(f"Failed to load {exc.path}.", exc.messages)
    except (
        ProjectNotFoundError,
        RemoteNotConfiguredError,
        GitError,
        SecretsRefusedError,
        FileNotFoundError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_INVALID


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mires project",
        description="Sync a project's agent configuration with a git repository.",
    )
    actions = parser.add_subparsers(dest="action", required=True)

    init = actions.add_parser("init", help=f"create {PROJECT_DIR}/{STATE_FILE} for this project")
    add_common_options(init)
    init.add_argument("--name", help="Human readable project name. Defaults to the directory name.")
    init.add_argument("--branch", default=DEFAULT_BRANCH, help=f"Branch to sync with. Defaults to {DEFAULT_BRANCH}.")
    init.add_argument(
        "--prefix",
        default=DEFAULT_PREFIX,
        help=f"Directory holding projects in the sync repository. Defaults to {DEFAULT_PREFIX}.",
    )

    listing = actions.add_parser("list", help="list the projects the sync repository holds")
    add_common_options(listing)

    status = actions.add_parser("status", help="compare this project with the sync repository")
    add_common_options(status)

    for name, help_text in (
        ("sync", "pull, push, or both, depending on which side has the project"),
        ("pull", "overwrite the local project with what the sync repository holds"),
        ("push", "overwrite the sync repository with the local project"),
    ):
        action = actions.add_parser(name, help=help_text)
        add_common_options(action)
        add_transfer_options(action)
        if name == "sync":
            direction = action.add_mutually_exclusive_group()
            direction.add_argument("--pull", action="store_true", help="Force the repository to win.")
            direction.add_argument("--push", action="store_true", help="Force the local project to win.")
    return parser


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", type=Path, help="Project root. Defaults to the nearest .mires/state.yml.")
    parser.add_argument("--slug", help="Project slug. Required when the project does not exist locally yet.")
    parser.add_argument("--repo", help="Sync repository. Overrides the project state, MIRES_SYNC_REPO, and the config.")


def add_transfer_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true", help="Preview the transfer without writing anything.")
    parser.add_argument("-m", "--message", help="Commit message for the push. Defaults to `sync project <slug>`.")
    parser.add_argument(
        "--allow-secrets",
        action="store_true",
        help="Push files that look like credentials, which are refused by default.",
    )


def run_init(args: argparse.Namespace) -> int:
    root = args.project.expanduser().resolve() if args.project is not None else Path.cwd().resolve()
    path = project_state_path(root)
    if path.exists():
        print(f"{path} already exists.", file=sys.stderr)
        return EXIT_INVALID

    slug = args.slug or slugify(root.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        STATE_TEMPLATE.format(
            name=args.name or root.name,
            slug=slug,
            repo=f"repo: {args.repo}" if args.repo else REPO_PLACEHOLDER,
            branch=args.branch,
            prefix=args.prefix,
        )
    )

    state = load_project(root)
    errors = validate_project(root, state)
    if errors:
        return fail(f"Created {path}, but it does not validate.", errors)
    print(f"Created {path} for project '{slug}'.")
    print("Declare what to sync under `project.include`, then run `mires project sync`.")
    return EXIT_OK


def run_list(args: argparse.Namespace) -> int:
    _, state = locate(args)
    repo = open_repo(state, args)
    slugs = repo.project_slugs()
    if not slugs:
        print(f"No projects in {repo.remote.repo} under {repo.remote.prefix}/.")
        return EXIT_OK
    print(f"Projects in {repo.remote.repo} ({repo.remote.branch}):")
    for slug in slugs:
        print(f"- {slug}")
    return EXIT_OK


def run_status(args: argparse.Namespace) -> int:
    root, state = locate(args)
    slug = resolve_slug(args, state)
    repo = open_repo(state, args)

    print(f"Project '{slug}'")
    print(f"Local: {root if state else 'not present'}")
    print(f"Repo:  {repo.remote.repo} ({repo.remote.branch}) at {repo.remote.prefix}/{slug}")

    if not repo.has_project(slug):
        print("The sync repository does not hold this project yet. Run `mires project push`.")
        return EXIT_OK
    if state is None:
        remote_state = load_project(repo.project_path(slug))
        print(f"Not present locally. `mires project pull --slug {slug}` would write:")
        for path in payload_paths(remote_state):
            print(f"- {path}")
        return EXIT_OK

    remote_root = repo.project_path(slug)
    declared = tuple(dict.fromkeys(payload_paths(state) + payload_paths(load_project(remote_root))))
    only_local, only_remote, differing = compare(declared, root, remote_root)
    print_paths("Only local", only_local)
    print_paths("Only in the repo", only_remote)
    print_paths("Different on both sides", differing)
    print_paths("Uncommitted in the sync clone", tuple(repo.pending_changes(slug)))
    if not (only_local or only_remote or differing):
        print("In sync.")
    return EXIT_OK


def run_sync(args: argparse.Namespace) -> int:
    root, state = locate(args)
    slug = resolve_slug(args, state)
    repo = open_repo(state, args)

    forced = PULL if args.pull else PUSH if args.push else None
    if forced == PULL or (forced is None and state is None):
        return pull(root, repo, slug, args)
    if forced == PUSH or (forced is None and not repo.has_project(slug)):
        return push(root, repo, slug, args)

    return converge(root, state, repo, slug, args)


def converge(root: Path, state: ProjectState, repo: SyncRepo, slug: str, args: argparse.Namespace) -> int:
    """Sync the side that moved since the last sync, and refuse to choose when both did."""
    remote_root = repo.project_path(slug)
    remote_state = load_project(remote_root)
    declared = tuple(dict.fromkeys(payload_paths(state) + payload_paths(remote_state)))
    only_local, only_remote, differing = compare(declared, root, remote_root)
    if not (only_local or only_remote or differing):
        print(f"'{slug}' is already in sync with {repo.remote.repo} ({repo.remote.branch}).")
        return EXIT_OK

    recorded = SyncManifest.load(root).recorded
    local_moved = drifted(payload_paths(state), root, recorded)
    remote_moved = drifted(payload_paths(remote_state), remote_root, recorded)

    if local_moved and remote_moved:
        return fail_direction(slug, only_local, only_remote, differing)
    if remote_moved:
        return pull(root, repo, slug, args)
    return push(root, repo, slug, args)


def run_pull(args: argparse.Namespace) -> int:
    root, state = locate(args)
    slug = resolve_slug(args, state)
    return pull(root, open_repo(state, args), slug, args)


def run_push(args: argparse.Namespace) -> int:
    root, state = locate(args)
    slug = resolve_slug(args, state)
    return push(root, open_repo(state, args), slug, args)


def pull(root: Path, repo: SyncRepo, slug: str, args: argparse.Namespace) -> int:
    source = repo.project_path(slug)
    if not source.is_dir():
        print(f"The sync repository holds no project '{slug}'. Push it first.", file=sys.stderr)
        return EXIT_INVALID

    state = load_project(source)
    errors = validate_project(source, state)
    if errors:
        return fail(f"The project '{slug}' in the sync repository does not validate.", errors)

    manifest = SyncManifest.load(root)
    report = transfer(
        state,
        source,
        root,
        direction=PULL,
        previous=manifest.paths,
        dry_run=args.dry_run,
    )
    if not args.dry_run:
        manifest.save(slug, digests(payload_paths(state), root))
    print_report(report)
    return EXIT_OK


def push(root: Path, repo: SyncRepo, slug: str, args: argparse.Namespace) -> int:
    state = load_project(root)
    errors = validate_project(root, state)
    if errors:
        return fail(f"The local project '{slug}' does not validate.", errors)

    manifest = SyncManifest.load(root)
    report = transfer(
        state,
        root,
        repo.project_path(slug),
        direction=PUSH,
        previous=manifest.paths,
        dry_run=args.dry_run,
        allow_secrets=args.allow_secrets,
    )
    print_report(report)
    if args.dry_run:
        print(f"- would commit and push to {repo.remote.repo} ({repo.remote.branch})")
        return EXIT_OK

    manifest.save(slug, digests(payload_paths(state), root))
    message = args.message or f"sync project {slug}"
    if repo.commit_and_push(slug, message):
        print(f"Pushed '{slug}' to {repo.remote.repo} ({repo.remote.branch}).")
    else:
        print(f"{repo.remote.repo} ({repo.remote.branch}) already matches '{slug}'. Nothing to push.")
    return EXIT_OK


def locate(args: argparse.Namespace) -> tuple[Path, ProjectState | None]:
    """The project directory and its state, tolerating a project that does not exist locally yet.

    A first pull runs in a directory with no `.mires/state.yml`, so a missing state is a
    normal outcome here rather than an error. Commands that need one say so themselves.
    """
    root = project_root(args)
    return root, load_project(root) if project_state_path(root).is_file() else None


def project_root(args: argparse.Namespace) -> Path:
    if args.project is not None:
        return args.project.expanduser().resolve()
    try:
        return find_project_root()
    except ProjectNotFoundError:
        return Path.cwd().resolve()


def resolve_slug(args: argparse.Namespace, state: ProjectState | None) -> str:
    if args.slug:
        return args.slug
    if state is not None:
        return state.project.slug
    raise ProjectNotFoundError(Path.cwd().resolve())


def open_repo(state: ProjectState | None, args: argparse.Namespace) -> SyncRepo:
    remote = resolve_remote(state.project.remote if state else None, args.repo)
    return open_sync_repo(remote)


def fail_direction(
    slug: str,
    only_local: tuple[str, ...],
    only_remote: tuple[str, ...],
    differing: tuple[str, ...],
) -> int:
    print(
        f"Both sides of '{slug}' changed since the last sync, so sync will not choose for you. "
        "Run `mires project sync --pull` to let the repository win, or `--push` to let this project win.",
        file=sys.stderr,
    )
    print_paths("Only local", only_local, stream=sys.stderr)
    print_paths("Only in the repo", only_remote, stream=sys.stderr)
    print_paths("Different on both sides", differing, stream=sys.stderr)
    return EXIT_INVALID


def print_report(report: SyncReport) -> None:
    action = "Would sync" if report.dry_run else "Synced"
    arrow = "from" if report.direction == PULL else "to"
    print(f"{action} {report.summary()} for '{report.slug}' {arrow} {report.other_side}.")
    for path in report.created:
        print(f"- new {path}")
    for path in report.updated:
        print(f"- overwrote {path}")
    for path in report.removed:
        print(f"- removed {path}, no longer declared")
    for path in report.missing:
        print(f"- skipped {path}, declared but absent")


def print_paths(headline: str, paths: tuple[str, ...], stream: TextIO | None = None) -> None:
    if not paths:
        return
    target = stream or sys.stdout
    print(f"{headline}:", file=target)
    for path in paths:
        print(f"- {path}", file=target)


def fail(headline: str, messages: tuple[ValidationMessage, ...]) -> int:
    print(headline, file=sys.stderr)
    for message in messages:
        print(f"- {message.message}", file=sys.stderr)
    return EXIT_INVALID


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


ACTIONS = {
    "init": run_init,
    "list": run_list,
    "status": run_status,
    "sync": run_sync,
    "pull": run_pull,
    "push": run_push,
}
