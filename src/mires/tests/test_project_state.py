from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mires.project.loader import (
    ProjectNotFoundError,
    find_project_root,
    load_project,
    project_state_path,
    validate_project,
)
from mires.project.models import ProjectState, normalize_include
from mires.state.loader import StateFileError

SKILL_SECTION = '\nskills:\n  - name: Billing\n    slug: billing\n    description: "Billing"\n'


def project_document(
    slug: str = "demo",
    *,
    include: tuple[str, ...] = (),
    repo: str | None = None,
    sections: str = "",
) -> str:
    lines = ["version: 1", "", "project:", f"  name: {slug}", f"  slug: {slug}"]
    if repo is not None:
        lines.extend(["  remote:", f"    repo: {repo}"])
    if include:
        lines.append("  include:")
        lines.extend(f"    - {item}" for item in include)
    document = "\n".join(lines) + "\n"
    return f"{document}{sections}" if sections else document


def write_project(root: Path, slug: str = "demo", **options: object) -> Path:
    path = project_state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(project_document(slug, **options))  # type: ignore[arg-type]
    return path


def write_project_skill(root: Path, slug: str, body: str = "Whatever this project needs.\n") -> Path:
    directory = root / ".mires" / "skills" / slug
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: {slug} guidance\n---\n\n{body}")
    return directory


class IncludeTests(unittest.TestCase):
    def test_relative_paths_are_normalized(self) -> None:
        self.assertEqual(normalize_include(".cursor/skills/internal/"), ".cursor/skills/internal")
        self.assertEqual(normalize_include("  AGENTS.md  "), "AGENTS.md")

    def test_paths_that_escape_the_project_are_rejected(self) -> None:
        for candidate in ("/etc/passwd", "../elsewhere", "~/secrets", "a/../../b"):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                normalize_include(candidate)

    def test_the_project_root_and_reserved_directories_are_rejected(self) -> None:
        for candidate in (".", ".git", ".git/config", ".mires", ".mires/state.yml"):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                normalize_include(candidate)

    def test_duplicate_includes_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProjectState.model_validate(
                {
                    "version": 1,
                    "project": {"name": "Demo", "slug": "demo", "include": ["AGENTS.md", "AGENTS.md/"]},
                }
            )


class ProjectLoadingTests(unittest.TestCase):
    def test_a_project_is_found_from_a_nested_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            write_project(root)
            nested = root / "src" / "deep"
            nested.mkdir(parents=True)

            self.assertEqual(find_project_root(nested), root)

    def test_a_directory_without_a_project_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ProjectNotFoundError):
                find_project_root(Path(temp_dir))

    def test_the_project_section_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = project_state_path(root)
            path.parent.mkdir(parents=True)
            path.write_text("version: 1\n")

            with self.assertRaises(StateFileError) as caught:
                load_project(root)

            self.assertTrue(any("project" in message.message for message in caught.exception.messages))


class ProjectValidationTests(unittest.TestCase):
    def test_a_project_declaring_its_own_skill_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_project(root, sections=SKILL_SECTION)
            write_project_skill(root, "billing")

            self.assertEqual(validate_project(root, load_project(root)), ())

    def test_a_declared_entry_without_files_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_project(root, sections=SKILL_SECTION)

            messages = [message.message for message in validate_project(root, load_project(root))]

            self.assertIn("declared skills entry directory does not exist", messages)

    def test_an_include_symlinked_out_of_the_project_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outside = Path(temp_dir) / "outside"
            outside.mkdir()
            root = Path(temp_dir) / "project"
            root.mkdir()
            write_project(root, include=("linked",))
            (root / "linked").symlink_to(outside, target_is_directory=True)

            messages = [message.message for message in validate_project(root, load_project(root))]

            self.assertIn("include resolves outside the project root", messages)


if __name__ == "__main__":
    unittest.main()
