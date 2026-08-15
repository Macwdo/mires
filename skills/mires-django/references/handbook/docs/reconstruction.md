# Reconstruction

## Purpose and when to use it

Use `reconstruct` to materialize one disposable, executable reference project
from the canonical artifacts in this handbook. Run it from the repository
root and send the output to a fresh directory outside the repository.

Content is organized as small, independently selectable **modules** with
explicit dependency edges (`requires`). Request any combination of modules
and `reconstruct` resolves the transitive closure automatically. The six
names used before this handbook adopted modules — `base`, `tasks`,
`storage`, `realtime`, `vector-ai`, `full` — still work, as **aliases** that
expand to a fixed module set:

| Module family | Members | Notes |
| --- | --- | --- |
| Sentry | `sentry-python`, `sentry-django` | `sentry-django` requires `sentry-python` |
| Celery | `celery-core`, `celery-redis-broker`, `celery-postgres-results`, `celery-django`, `celery-beat` | see requirement chain below |
| Storage | `storage-s3-core`, `storage-django` | `storage-django` requires `storage-s3-core` |
| Realtime | `realtime-sse`, `realtime-channels` | independent of each other |
| Vector/AI | `vector-pgvector`, `vector-ai-openai`, `chat-streaming` | `vector-ai-openai` requires `vector-pgvector`; `chat-streaming` requires `celery-core`, `celery-redis-broker`, `realtime-sse` (it has its own task and Redis client, independent of the `apps.jobs` Job model) |
| Tenancy | `tenancy-advanced` | independent |

Celery requirement chain: `celery-redis-broker` and `celery-postgres-results`
both require only `celery-core`; `celery-django` (the durable `Job` model's
task glue) requires `celery-core` **and** `celery-postgres-results`, because
its tasks and services operate on the `Job` model that
`celery-postgres-results` owns; `celery-beat` requires `celery-django`.

| Alias | Resolves to |
| --- | --- |
| `base` | no modules — the generic Django REST API, account tenancy, authentication, and Customer CRUD that every request always includes |
| `tasks` | `celery-core`, `celery-django`, `celery-redis-broker`, `celery-postgres-results`, `celery-beat` |
| `storage` | `storage-s3-core`, `storage-django` |
| `realtime` | `realtime-sse`, `realtime-channels` |
| `vector-ai` | `vector-pgvector`, `vector-ai-openai`, `chat-streaming` |
| `full` | every module listed above, plus `sentry-django` and `tenancy-advanced` |

`base` content is inherited by every request, module or alias, exactly as
before.

## When not to use it

Do not use reconstruction as an application generator or write its result
back into this handbook. A reconstructed tree is a derived test fixture, not
another canonical source. Fork the resulting design deliberately in a real
project rather than repeatedly regenerating an application that has begun to
evolve.

## Responsibilities and invariants

A canonical artifact consists of one marker immediately followed by one
fenced block:

````markdown
&lt;!-- artifact: src/apps/customer/models.py; profiles: base,full --&gt;
```python
complete_file_contents = True
```
````

The target is a repository-relative POSIX path. The `profiles:` list is an
order-independent set of module names and/or alias names (see the tables
above); `dependency-fragment` markers use a `modules:` list restricted to
plain module names (aliases are not meaningful there — a fragment activates
per resolved module, and an alias only ever appears expanded). A
target/profile pair may occur only once across the entire handbook, exactly
as before. The fence language must agree with the target type.

`base` is inherited by every request. Artifacts explicitly assigned to a
requested module or alias replace a base artifact at the same exact target.
Recipe artifacts that belong in the combined project therefore declare both
their module tag and `full`. A combined aggregator, such as `settings.py`,
can declare a dedicated `full` variant. Whether an artifact applies to a
request is decided by intersecting the artifact's own tags against the union
of two sets: the modules the request transitively resolves to (plain module
names only — aliases never appear here), and the request's own literal
tags as typed (which may still be an alias). This is why a request only
closes over module `requires` edges, never over an artifact's alias tags: an
artifact tagged `celery-beat,tasks,full` applies to `--modules celery-beat`
(direct tag match) and to `--profile tasks` (`celery-beat` is one of the
modules `tasks` resolves to) and to `--profile full` (`full` is a literal
tag on the artifact and the literal request), but *not* to
`--modules celery-django` alone, since neither `celery-beat` nor `tasks` nor
`full` is in that request's resolved or literal set.

### Dependency fragments

`pyproject.toml`'s dependency list cannot be owned by one profile-specific
whole-file artifact the way most files are — with modules composable, there
is no fixed number of dependency combinations to pre-bake. Instead
`pyproject.toml` has exactly one `base` **artifact** (project metadata, tool
configuration, and a `dependencies = [...]` array containing a placeholder
line `    # {{FRAGMENT:dependencies}}`), plus any number of small
**dependency-fragment** markers that each contribute the array entries one
module introduces:

````markdown
&lt;!-- dependency-fragment: pyproject.toml#dependencies; modules: sentry-python --&gt;
```toml
    "sentry-sdk[django]==2.66.1",
```
````

At materialization time, every fragment whose `modules:` tag is in the
resolved module set is concatenated (sorted by module name, then by
document/line for determinism) and substituted for the placeholder line, so
the emitted `pyproject.toml` has exactly the dependencies its resolved
module set introduces — no unused entries. A fragment for a module absent
from the request contributes nothing. Two selected fragments with
byte-identical content (e.g. two modules that both need the same
`tool.pytest.ini_options` line) collapse to one copy in the output, so a
config line shared by more than one module can be declared once per owning
module without producing a duplicate.

The utility performs all repository, marker, fence, profile, fragment, path,
language, and selected-tree conflict validation before its first write. The
output must be an existing, empty, absolute directory outside the
repository, with no symbolic-link component. The utility never deletes or
overwrites a path.

## Migration generation

An ordinary schema migration only replays what `makemigrations` would
already derive from its app's `models.py`. Carrying it as a canonical
artifact would duplicate the models it comes from, so `account`,
`authentication`, `common`, `customer`, and the plain recipe apps (`files`,
`jobs`, `membership`, `realtime`) ship no migration artifacts. After
materializing a project, run:

```bash
uv run python src/manage.py makemigrations account authentication common customer
```

adding any plain recipe app included in the resolved module set. Commit the
generated migrations in the derived project; they become that project's own
forward-only history per [conventions](conventions.md).

A migration stays a canonical artifact only when it carries logic
`makemigrations` cannot derive from models alone: enabling a database
extension, a data migration, or a hand-written index.
`src/apps/documents/migrations/0001_initial.py` in
[pgvector](../recipes/vector.md) is the sample — it mixes ordinary
`CreateModel` operations with `VectorExtension()` and a `RunPython`/`RunSQL`
HNSW index pair, so it must be authored once and reconstructed exactly, not
regenerated.

## Dependency lock generation

Because modules are freely composable, pre-baking a `uv.lock` for every
possible combination is not attempted — the same reasoning as migrations
above. After materializing a project and (if needed) running
`makemigrations`, run:

```bash
uv lock
```

once, from the materialized project root, to produce the lock file for the
exact module set just generated. Commit it in the derived project alongside
the generated migrations.

## Complete reconstruction utility

The utility uses only the Python standard library. Its marker is
intentionally `utility`, not `artifact`: the executable belongs beside a
temporary reconstruction, not inside every reconstructed Django project.

<!-- utility: reconstruct; language: python -->
```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import stat
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MODULES: dict[str, frozenset[str]] = {
    "sentry-python": frozenset(),
    "sentry-django": frozenset({"sentry-python"}),
    "celery-core": frozenset(),
    "celery-redis-broker": frozenset({"celery-core"}),
    "celery-postgres-results": frozenset({"celery-core"}),
    "celery-django": frozenset({"celery-core", "celery-postgres-results"}),
    "celery-beat": frozenset({"celery-django"}),
    "storage-s3-core": frozenset(),
    "storage-django": frozenset({"storage-s3-core"}),
    "realtime-sse": frozenset(),
    "realtime-channels": frozenset(),
    "vector-pgvector": frozenset(),
    "vector-ai-openai": frozenset({"vector-pgvector"}),
    "chat-streaming": frozenset({"celery-core", "celery-redis-broker", "realtime-sse"}),
    "tenancy-advanced": frozenset(),
}

ALIAS_MEMBERS: dict[str, frozenset[str]] = {
    "base": frozenset(),
    "tasks": frozenset(
        {
            "celery-core",
            "celery-django",
            "celery-redis-broker",
            "celery-postgres-results",
            "celery-beat",
        }
    ),
    "storage": frozenset({"storage-s3-core", "storage-django"}),
    "realtime": frozenset({"realtime-sse", "realtime-channels"}),
    "vector-ai": frozenset({"vector-pgvector", "vector-ai-openai", "chat-streaming"}),
    "full": frozenset(MODULES) | frozenset({"sentry-django", "tenancy-advanced"}),
}

TAG_SET = frozenset(MODULES) | frozenset(ALIAS_MEMBERS)

MARKER_RE = re.compile(
    r"^<!-- artifact: (?P<target>[^;]+); profiles: (?P<profiles>[^>]+) -->\r?\n?$"
)
FRAGMENT_RE = re.compile(
    r"^<!-- dependency-fragment: (?P<target>[^#]+)#(?P<section>[^;]+); "
    r"modules: (?P<modules>[^>]+) -->\r?\n?$"
)
FENCE_RE = re.compile(r"^```(?P<language>[A-Za-z0-9_+.-]+)\r?\n?$")
ORDINARY_FENCE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)\r?\n?$")
PLACEHOLDER_RE = re.compile(r"^(?P<indent>[ \t]*)# \{\{FRAGMENT:(?P<section>[A-Za-z0-9_-]+)\}\}\r?\n?$")

EXACT_LANGUAGES = {
    ".gitignore": frozenset({"gitignore", "text"}),
    ".python-version": frozenset({"text"}),
    "Dockerfile": frozenset({"dockerfile"}),
    "Makefile": frozenset({"makefile"}),
}
SUFFIX_LANGUAGES = {
    ".conf": frozenset({"text"}),
    ".ini": frozenset({"ini"}),
    ".json": frozenset({"json"}),
    ".lock": frozenset({"toml"}),
    ".md": frozenset({"markdown"}),
    ".py": frozenset({"python"}),
    ".pyi": frozenset({"python"}),
    ".sh": frozenset({"bash", "sh"}),
    ".toml": frozenset({"toml"}),
    ".txt": frozenset({"text"}),
    ".yaml": frozenset({"yaml"}),
    ".yml": frozenset({"yaml"}),
}


class ReconstructionError(Exception):
    """A user-correctable repository or destination error."""


@dataclass(frozen=True)
class Artifact:
    target: PurePosixPath
    profiles: Sequence[str]
    language: str
    content: str
    document: str
    line: int


@dataclass(frozen=True)
class Fragment:
    target: PurePosixPath
    section: str
    modules: Sequence[str]
    content: str
    document: str
    line: int


def _close_modules(requested: frozenset[str]) -> frozenset[str]:
    unknown = sorted(requested - TAG_SET)
    if unknown:
        raise ReconstructionError(f"unknown modules: {', '.join(unknown)}")
    expanded: set[str] = set()
    for item in requested:
        expanded |= ALIAS_MEMBERS.get(item, frozenset({item}))
    frontier = set(expanded)
    while frontier:
        additions: set[str] = set()
        for module in frontier:
            additions |= MODULES.get(module, frozenset()) - expanded
        expanded |= additions
        frontier = additions
    return frozenset(expanded)


def resolve_modules(requested: frozenset[str]) -> frozenset[str]:
    if not requested:
        raise ReconstructionError("at least one module or alias is required")
    return _close_modules(requested)


def run_git(repo: Path, *arguments: str) -> bytes:
    process = subprocess.run(
        ("git", *arguments),
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise ReconstructionError(f"git {' '.join(arguments)} failed: {detail}")
    return process.stdout


def repository_root() -> Path:
    try:
        raw_root = subprocess.run(
            ("git", "rev-parse", "--show-toplevel"),
            cwd=Path.cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as error:
        raise ReconstructionError("git is required to locate tracked Markdown") from error
    if raw_root.returncode != 0:
        raise ReconstructionError("run reconstruct from a Git repository root")
    root = Path(raw_root.stdout.decode("utf-8").strip()).resolve()
    if Path.cwd().resolve() != root:
        raise ReconstructionError(f"run reconstruct from the repository root: {root}")
    return root


def tracked_markdown(repo: Path) -> list[Path]:
    entries = run_git(repo, "ls-files", "-z").split(b"\0")
    names = [entry.decode("utf-8") for entry in entries if entry]
    non_markdown = [name for name in names if not name.endswith(".md")]
    if non_markdown:
        sample = ", ".join(non_markdown[:5])
        raise ReconstructionError(f"tracked paths must all end in .md: {sample}")
    paths: list[Path] = []
    for name in names:
        candidate = repo / name
        if not candidate.is_file():
            raise ReconstructionError(f"tracked Markdown is missing from the worktree: {name}")
        paths.append(candidate)
    return sorted(paths)


def safe_target(raw_target: str, document: str, line: int) -> PurePosixPath:
    if raw_target != raw_target.strip() or not raw_target:
        raise ReconstructionError(f"{document}:{line}: target has surrounding whitespace")
    if "\\" in raw_target or "\0" in raw_target or raw_target.startswith("/"):
        raise ReconstructionError(f"{document}:{line}: target is not a safe POSIX path")
    raw_parts = raw_target.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ReconstructionError(f"{document}:{line}: target contains an unsafe component")
    if any(":" in part or any(ord(character) < 32 for character in part) for part in raw_parts):
        raise ReconstructionError(f"{document}:{line}: target contains unsafe characters")
    target = PurePosixPath(raw_target)
    if target.is_absolute():
        raise ReconstructionError(f"{document}:{line}: target must be relative")
    return target


def allowed_languages(target: PurePosixPath) -> frozenset[str]:
    if target.name in EXACT_LANGUAGES:
        return EXACT_LANGUAGES[target.name]
    if target.name.startswith(".env"):
        return frozenset({"dotenv"})
    allowed = SUFFIX_LANGUAGES.get(target.suffix.lower())
    if allowed is None:
        raise ReconstructionError(f"unsupported artifact target type: {target}")
    return allowed


def closing_fence(line: str, opening: str) -> bool:
    stripped = line.rstrip("\r\n")
    if not stripped or stripped[0] != opening[0]:
        return False
    return not stripped.strip(opening[0]).strip() and len(stripped) >= len(opening)


def _parse_tag_list(raw: str, document: str, line: int, kind: str) -> tuple[str, ...]:
    items = tuple(item.strip() for item in raw.split(","))
    if not items or any(not item for item in items) or len(set(items)) != len(items):
        raise ReconstructionError(f"{document}:{line}: {kind} must be a unique non-empty list")
    unknown = sorted(set(items) - TAG_SET)
    if unknown:
        raise ReconstructionError(f"{document}:{line}: unknown {kind}: {', '.join(unknown)}")
    return items


def _read_fence(
    lines: list[str], index: int, target: PurePosixPath, document: str, marker_line: int
) -> tuple[str, str, int]:
    if index + 1 >= len(lines):
        raise ReconstructionError(f"{document}:{marker_line}: marker has no fenced artifact")
    opening = FENCE_RE.fullmatch(lines[index + 1])
    if opening is None:
        raise ReconstructionError(
            f"{document}:{marker_line}: marker must be immediately followed "
            "by a named triple-backtick fence"
        )
    language = opening.group("language").lower()
    allowed = allowed_languages(target)
    if language not in allowed:
        expected = ", ".join(sorted(allowed))
        raise ReconstructionError(
            f"{document}:{marker_line}: {target} requires fence language {expected}, "
            f"not {language}"
        )
    close_index = index + 2
    while close_index < len(lines):
        if lines[close_index].rstrip("\r\n") == "```":
            break
        close_index += 1
    if close_index == len(lines):
        raise ReconstructionError(f"{document}:{marker_line}: canonical fence is not closed")
    content = "".join(lines[index + 2 : close_index])
    return content, language, close_index


def parse_document(
    repo: Path, document_path: Path
) -> tuple[list[Artifact], list[Fragment]]:
    relative = document_path.relative_to(repo).as_posix()
    text = document_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    artifacts: list[Artifact] = []
    fragments: list[Fragment] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        marker = MARKER_RE.fullmatch(line)
        fragment_marker = FRAGMENT_RE.fullmatch(line)
        if marker is not None:
            marker_line = index + 1
            target = safe_target(marker.group("target"), relative, marker_line)
            profile_items = _parse_tag_list(
                marker.group("profiles"), relative, marker_line, "profiles"
            )
            content, language, close_index = _read_fence(lines, index, target, relative, marker_line)
            artifacts.append(
                Artifact(
                    target=target,
                    profiles=profile_items,
                    language=language,
                    content=content,
                    document=relative,
                    line=marker_line,
                )
            )
            index = close_index + 1
            continue
        if fragment_marker is not None:
            marker_line = index + 1
            target = safe_target(fragment_marker.group("target"), relative, marker_line)
            section = fragment_marker.group("section").strip()
            module_items = _parse_tag_list(
                fragment_marker.group("modules"), relative, marker_line, "modules"
            )
            unaliased = [item for item in module_items if item not in ALIAS_MEMBERS]
            if len(unaliased) != len(module_items):
                raise ReconstructionError(
                    f"{relative}:{marker_line}: dependency-fragment modules must be "
                    "plain module names, not aliases"
                )
            content, _language, close_index = _read_fence(lines, index, target, relative, marker_line)
            fragments.append(
                Fragment(
                    target=target,
                    section=section,
                    modules=module_items,
                    content=content,
                    document=relative,
                    line=marker_line,
                )
            )
            index = close_index + 1
            continue
        if "<!-- artifact:" in line or "<!-- dependency-fragment:" in line:
            raise ReconstructionError(f"{relative}:{index + 1}: malformed marker")
        ordinary = ORDINARY_FENCE_RE.match(line)
        if ordinary is not None:
            opening_fence = ordinary.group("fence")
            index += 1
            while index < len(lines) and not closing_fence(lines[index], opening_fence):
                index += 1
            if index < len(lines):
                index += 1
            continue
        index += 1
    return artifacts, fragments


def collect_artifacts(repo: Path) -> tuple[list[Artifact], list[Fragment]]:
    artifacts: list[Artifact] = []
    fragments: list[Fragment] = []
    seen: dict[tuple[PurePosixPath, str], Artifact] = {}
    for document_path in tracked_markdown(repo):
        document_artifacts, document_fragments = parse_document(repo, document_path)
        for artifact in document_artifacts:
            for profile in artifact.profiles:
                key = (artifact.target, profile)
                previous = seen.get(key)
                if previous is not None:
                    raise ReconstructionError(
                        f"duplicate {artifact.target} for {profile}: "
                        f"{previous.document}:{previous.line} and "
                        f"{artifact.document}:{artifact.line}"
                    )
                seen[key] = artifact
            artifacts.append(artifact)
        fragments.extend(document_fragments)
    return artifacts, fragments


def selected_artifacts(
    artifacts: list[Artifact], requested: frozenset[str], resolved: frozenset[str]
) -> dict[PurePosixPath, Artifact]:
    # An artifact applies if one of its own tags is either a module the
    # request transitively resolved to (`resolved`, always plain module
    # names) or a tag the caller typed literally (`requested`, which may
    # still be an alias like "tasks" or "full"). Matching against `resolved`
    # alone would miss alias-tagged artifacts (aliases never appear in
    # `resolved`); closing the artifact's own alias tags instead of the
    # request's would wrongly expand "full" into every module regardless of
    # what was actually requested.
    applicable = requested | resolved
    selected: dict[PurePosixPath, Artifact] = {}
    for artifact in artifacts:
        if "base" in artifact.profiles:
            selected[artifact.target] = artifact
    for artifact in artifacts:
        if set(artifact.profiles) & applicable:
            selected[artifact.target] = artifact
    if not selected:
        raise ReconstructionError("resolved module set has no artifacts")
    return selected


def merge_fragments(
    selected: dict[PurePosixPath, Artifact],
    fragments: list[Fragment],
    resolved: frozenset[str],
) -> dict[PurePosixPath, Artifact]:
    by_target_section: dict[tuple[PurePosixPath, str], list[Fragment]] = {}
    for fragment in fragments:
        if any(module in resolved for module in fragment.modules):
            by_target_section.setdefault((fragment.target, fragment.section), []).append(
                fragment
            )
    if not by_target_section:
        return selected
    merged = dict(selected)
    for (target, section), matches in by_target_section.items():
        artifact = merged.get(target)
        if artifact is None:
            raise ReconstructionError(f"dependency-fragment target not selected: {target}")
        lines = artifact.content.splitlines(keepends=True)
        placeholder_index = None
        for line_index, line in enumerate(lines):
            found = PLACEHOLDER_RE.fullmatch(line)
            if found is not None and found.group("section") == section:
                placeholder_index = line_index
                break
        if placeholder_index is None:
            raise ReconstructionError(
                f"{artifact.document}:{artifact.line}: no placeholder for section {section}"
            )
        ordered = sorted(matches, key=lambda item: (item.modules, item.document, item.line))
        seen_content: set[str] = set()
        deduplicated = []
        for fragment in ordered:
            if fragment.content in seen_content:
                continue
            seen_content.add(fragment.content)
            deduplicated.append(fragment)
        replacement = "".join(fragment.content for fragment in deduplicated)
        lines[placeholder_index : placeholder_index + 1] = [replacement]
        merged[target] = Artifact(
            target=artifact.target,
            profiles=artifact.profiles,
            language=artifact.language,
            content="".join(lines),
            document=artifact.document,
            line=artifact.line,
        )
    return merged


def validate_tree(selected: dict[PurePosixPath, Artifact]) -> None:
    targets = sorted(selected, key=lambda item: item.as_posix())
    folded: dict[str, PurePosixPath] = {}
    target_set = set(targets)
    for target in targets:
        folded_name = target.as_posix().casefold()
        prior = folded.get(folded_name)
        if prior is not None and prior != target:
            raise ReconstructionError(f"case-insensitive target conflict: {prior} and {target}")
        folded[folded_name] = target
        for parent in target.parents:
            if parent == PurePosixPath("."):
                break
            if parent in target_set:
                raise ReconstructionError(f"file/directory target conflict: {parent} and {target}")


def reject_symlink_components(destination: Path) -> None:
    current = Path(destination.anchor)
    for component in destination.parts[1:]:
        current = current / component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            raise ReconstructionError(f"output directory does not exist: {destination}")
        if stat.S_ISLNK(mode):
            raise ReconstructionError(f"output path contains a symbolic link: {current}")


def output_directory(raw_output: str, repo: Path) -> Path:
    destination = Path(raw_output)
    if not destination.is_absolute():
        raise ReconstructionError("--output must be an absolute path")
    reject_symlink_components(destination)
    if not destination.is_dir():
        raise ReconstructionError(f"output is not a directory: {destination}")
    destination = destination.resolve(strict=True)
    try:
        destination.relative_to(repo)
    except ValueError:
        pass
    else:
        raise ReconstructionError("output must be outside the Markdown repository")
    if any(destination.iterdir()):
        raise ReconstructionError(f"output directory must be empty: {destination}")
    return destination


def executable(target: PurePosixPath) -> bool:
    return (
        target.suffix == ".sh"
        or target.name == "manage.py"
        or (bool(target.parts) and target.parts[0] == "bin")
    )


def materialize(destination: Path, selected: dict[PurePosixPath, Artifact]) -> None:
    for relative_target in sorted(selected, key=lambda item: item.as_posix()):
        artifact = selected[relative_target]
        target = destination.joinpath(*relative_target.parts)
        target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        mode = 0o755 if executable(relative_target) else 0o644
        descriptor = os.open(target, flags, mode)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(artifact.content.encode("utf-8"))
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        prog="reconstruct",
        description="Materialize a canonical Django handbook module selection.",
    )
    selector = argument_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument(
        "--modules", metavar="MODULE[,MODULE...]", help="comma-separated modules and/or aliases"
    )
    selector.add_argument(
        "--profile", choices=sorted(ALIAS_MEMBERS), help="legacy alias, equivalent to --modules NAME"
    )
    argument_parser.add_argument("--output", required=True, metavar="ABSOLUTE_PATH")
    return argument_parser


def main() -> int:
    arguments = parser().parse_args()
    requested_raw = arguments.profile if arguments.profile else arguments.modules
    try:
        requested = frozenset(item.strip() for item in requested_raw.split(","))
        repo = repository_root()
        resolved = resolve_modules(requested)
        artifacts, fragments = collect_artifacts(repo)
        selected = selected_artifacts(artifacts, requested, resolved)
        selected = merge_fragments(selected, fragments, resolved)
        validate_tree(selected)
        destination = output_directory(arguments.output, repo)
        materialize(destination, selected)
    except (OSError, UnicodeError, ReconstructionError) as error:
        print(f"reconstruct: error: {error}", file=sys.stderr)
        return 2
    print(f"materialized {len(selected)} artifacts for {sorted(requested)} at {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Bootstrap extraction

Create a temporary executable without copying the utility by hand. This
extractor also uses only the standard library and refuses to overwrite its
destination:

```bash
reconstruct_dir="$(mktemp -d)"
python3 - "$PWD/docs/reconstruction.md" "$reconstruct_dir/reconstruct" <<'PY'
import os
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(keepends=True)
destination = Path(sys.argv[2])
marker = "<!-- utility: reconstruct; language: python -->\n"
matches = [index for index, line in enumerate(source) if line == marker]
if len(matches) != 1:
    raise SystemExit("expected exactly one reconstruct utility marker")
start = matches[0] + 1
if start >= len(source) or source[start] != "```python\n":
    raise SystemExit("utility marker is not followed by a Python fence")
end = start + 1
while end < len(source) and source[end].rstrip("\r\n") != "```":
    end += 1
if end == len(source):
    raise SystemExit("reconstruct utility fence is not closed")
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
descriptor = os.open(destination, flags, 0o755)
with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
    stream.writelines(source[start + 1 : end])
PY
```

Then create an empty destination and invoke the exact interface — either a
legacy alias:

```bash
output_dir="$(mktemp -d /tmp/django-standard-base.XXXXXX)"
"$reconstruct_dir/reconstruct" --profile base --output "$output_dir"
```

or an explicit module combination, mixing atomic modules and aliases freely:

```bash
output_dir="$(mktemp -d /tmp/django-standard-custom.XXXXXX)"
"$reconstruct_dir/reconstruct" --modules celery-django,sentry-django --output "$output_dir"
```

Use a new output directory for every request. Running the command again
against the same directory correctly fails because it is no longer empty.
After materializing, run `makemigrations` (see
[Migration generation](#migration-generation)) and `uv lock` (see
[Dependency lock generation](#dependency-lock-generation)).

## Alternatives and trade-offs

Keeping the utility embedded preserves the Markdown-only repository contract
and makes the parser reviewable with the protocol it enforces. It does
require one bootstrap extraction step. A packaged generator would be more
convenient to install, but would introduce a second canonical source and
revive lifecycle work that this handbook intentionally retired.

A composable module graph costs more validation surface than the flat
profile enum it replaced (transitive resolution, dependency-fragment
merging, alias/module tag overlap), but it is what makes "Celery without
Beat" or "Sentry on its own" expressible at all. The flat six-profile design
this replaces treated every recipe as an indivisible unit; that was simpler
to implement but forced an all-or-nothing choice per recipe, which is the
problem this revision exists to fix. Dependency-fragment merging is
deliberately restricted to one placeholder substitution per section rather
than arbitrary text patching, so a fragment can only append array entries in
a documented, reviewable location.

## Required tests

- Extract the utility and confirm it is executable.
- Materialize every legacy alias (`base`, `tasks`, `storage`, `realtime`,
  `vector-ai`, `full`) into separate fresh directories under `/tmp` and
  confirm each alias's file set matches its documented module expansion.
- Materialize at least two module combinations that were not expressible
  before this revision, e.g. `celery-django` alone (no beat, no
  postgres-results, but `celery-core` pulled in transitively) and
  `sentry-django,celery-redis-broker` (crossing two otherwise-unrelated
  families).
- Reject a relative output, a repository-internal output, a non-empty
  output, a missing output, and an output with a symbolic-link component.
- Reject malformed markers, unknown modules or aliases, repeated tags,
  duplicate target/profile pairs, unsafe paths, unsupported target
  extensions, mismatched fence languages, unclosed fences, and
  file/directory conflicts.
- Reject a `dependency-fragment` marker whose `modules:` list contains an
  alias, and one whose target has no matching placeholder.
- Confirm a request inherits base artifacts and replaces only an exact
  target explicitly assigned to one of its resolved modules.
- Confirm `pyproject.toml` for a resolved module set contains exactly the
  dependency-fragment entries for that set, in deterministic order, with no
  duplicates and no entries from unselected modules.
- Confirm scripts and `src/manage.py` are executable and ordinary files are
  not.
- Run the reconstructed project checks in [testing](testing.md), including
  `uv lock` succeeding against the generated `pyproject.toml`.

## Related standards

See [architecture](architecture.md), [testing](testing.md), the
[source map](../source-map.md), and the [recipe index](../recipes/README.md).
