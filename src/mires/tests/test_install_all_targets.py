from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mires.catalog import BUNDLED_ROOT, CatalogNotFoundError, resolve_root
from mires.compatibility.targets import TARGETS, resolve_targets

ROOT = Path(__file__).resolve().parents[3]
CLI = ["-m", "mires.cli"]


def run_cli(*arguments: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *CLI, *arguments],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def homes(temp_dir: str) -> tuple[dict[str, Path], list[str]]:
    base = Path(temp_dir)
    mapping = {slug: base / slug for slug in TARGETS}
    arguments: list[str] = []
    for slug, home in mapping.items():
        arguments.extend([TARGETS[slug].destination, str(home)])
    return mapping, arguments


class SingleCommandInstallTests(unittest.TestCase):
    def test_one_command_installs_every_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mapping, arguments = homes(temp_dir)
            result = run_cli("install", "--target", "all", "--root", str(ROOT), *arguments)

            self.assertEqual(result.returncode, 0, result.stderr)
            for slug, home in mapping.items():
                with self.subTest(target=slug):
                    self.assertIn(TARGETS[slug].display_name, result.stdout)
                    self.assertTrue((home / "skills" / "mires" / "SKILL.md").exists())
                    self.assertTrue((home / "mires" / "install-manifest.json").exists())

    def test_installing_twice_changes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, arguments = homes(temp_dir)
            run_cli("install", "--target", "all", "--root", str(ROOT), *arguments)
            first = sorted(path.relative_to(temp_dir) for path in Path(temp_dir).rglob("*") if path.is_file())
            snapshot = {path: (Path(temp_dir) / path).read_bytes() for path in first}

            run_cli("install", "--target", "all", "--root", str(ROOT), *arguments)
            second = sorted(path.relative_to(temp_dir) for path in Path(temp_dir).rglob("*") if path.is_file())

            self.assertEqual(first, second)
            for path, content in snapshot.items():
                with self.subTest(path=str(path)):
                    self.assertEqual((Path(temp_dir) / path).read_bytes(), content)

    def test_unsupported_target_lists_the_supported_ones(self) -> None:
        result = run_cli("install", "--target", "emacs", "--root", str(ROOT))

        self.assertEqual(result.returncode, 2)
        for slug in TARGETS:
            self.assertIn(slug, result.stderr)


class TargetRegistryTests(unittest.TestCase):
    def test_all_expands_to_every_registered_target(self) -> None:
        self.assertEqual({target.slug for target in resolve_targets("all")}, set(TARGETS))

    def test_registry_covers_the_runtimes_mires_supports(self) -> None:
        self.assertEqual(set(TARGETS), {"codex", "cursor", "claude", "opencode"})

    def test_unknown_target_raises(self) -> None:
        with self.assertRaises(LookupError):
            resolve_targets("nano")


class CatalogRootTests(unittest.TestCase):
    def test_repository_root_wins_when_running_inside_a_clone(self) -> None:
        self.assertEqual(resolve_root(start=ROOT / "src" / "mires"), ROOT)

    def test_falls_back_to_the_catalog_shipped_in_the_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            if not (BUNDLED_ROOT / "state.yml").is_file():
                self.skipTest("catalog is only bundled in a built wheel")
            self.assertEqual(resolve_root(start=Path(temp_dir)), BUNDLED_ROOT.resolve())

    def test_reports_where_it_looked_when_no_catalog_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            if (BUNDLED_ROOT / "state.yml").is_file():
                self.skipTest("a bundled catalog is present, so resolution cannot fail")
            with self.assertRaises(CatalogNotFoundError) as caught:
                resolve_root(start=Path(temp_dir))
            self.assertIn("state.yml", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
