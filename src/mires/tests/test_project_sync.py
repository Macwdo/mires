from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mires.project.loader import load_project
from mires.project.sync import (
    PULL,
    PUSH,
    SecretsRefusedError,
    SyncManifest,
    compare,
    digests,
    drifted,
    payload_paths,
    transfer,
)
from mires.tests.test_project_state import write_project, write_project_skill

SKILL_SECTION = '\nskills:\n  - name: Billing\n    slug: billing\n    description: "Billing"\n'


class PayloadTests(unittest.TestCase):
    def test_the_payload_is_the_state_its_entries_and_its_includes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_project(root, include=("AGENTS.md", ".cursor/skills/internal"), sections=SKILL_SECTION)
            write_project_skill(root, "billing")

            self.assertEqual(
                payload_paths(load_project(root)),
                (".mires/state.yml", ".mires/skills/billing", "AGENTS.md", ".cursor/skills/internal"),
            )

    def test_the_manifest_is_not_part_of_the_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_project(root)
            SyncManifest(root=root, recorded={}).save("demo", {".mires/state.yml": "abc"})

            self.assertNotIn(".mires/sync-manifest.json", payload_paths(load_project(root)))


class TransferTests(unittest.TestCase):
    def test_only_declared_paths_travel(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md",))
            (sides.source / "AGENTS.md").write_text("agents\n")
            (sides.source / "secret-source-code.py").write_text("print('mine')\n")

            transfer(load_project(sides.source), sides.source, sides.destination, direction=PUSH)

            self.assertTrue((sides.destination / "AGENTS.md").is_file())
            self.assertFalse((sides.destination / "secret-source-code.py").exists())

    def test_a_second_run_reports_everything_as_unchanged(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md",))
            (sides.source / "AGENTS.md").write_text("agents\n")
            state = load_project(sides.source)
            transfer(state, sides.source, sides.destination, direction=PUSH)

            report = transfer(state, sides.source, sides.destination, direction=PUSH)

            self.assertEqual(report.created, ())
            self.assertEqual(report.updated, ())
            self.assertEqual(len(report.unchanged), 2)
            self.assertFalse(report.changed)

    def test_a_directory_is_replaced_rather_than_merged(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=(".cursor/skills/internal",))
            skill = sides.source / ".cursor" / "skills" / "internal"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("kept\n")
            state = load_project(sides.source)
            transfer(state, sides.source, sides.destination, direction=PUSH)
            stale = sides.destination / ".cursor" / "skills" / "internal" / "stale.md"
            stale.write_text("gone\n")

            transfer(state, sides.source, sides.destination, direction=PUSH)

            self.assertFalse(stale.exists())

    def test_a_path_dropped_from_the_state_is_removed_on_the_other_side(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md", "NOTES.md"))
            (sides.source / "AGENTS.md").write_text("agents\n")
            (sides.source / "NOTES.md").write_text("notes\n")
            previous = payload_paths(load_project(sides.source))
            transfer(load_project(sides.source), sides.source, sides.destination, direction=PUSH)

            write_project(sides.source, include=("AGENTS.md",))
            report = transfer(
                load_project(sides.source),
                sides.source,
                sides.destination,
                direction=PUSH,
                previous=previous,
            )

            self.assertEqual(report.removed, ("NOTES.md",))
            self.assertFalse((sides.destination / "NOTES.md").exists())

    def test_a_declared_path_that_does_not_exist_is_reported_not_written(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md",))

            report = transfer(load_project(sides.source), sides.source, sides.destination, direction=PUSH)

            self.assertEqual(report.missing, ("AGENTS.md",))
            self.assertFalse((sides.destination / "AGENTS.md").exists())

    def test_a_dry_run_writes_nothing(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md",))
            (sides.source / "AGENTS.md").write_text("agents\n")

            report = transfer(
                load_project(sides.source),
                sides.source,
                sides.destination,
                direction=PUSH,
                dry_run=True,
            )

            self.assertEqual(len(report.created), 2)
            self.assertFalse((sides.destination / "AGENTS.md").exists())

    def test_repository_noise_inside_an_included_directory_is_skipped(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("tools",))
            tools = sides.source / "tools"
            (tools / "node_modules" / "left-pad").mkdir(parents=True)
            (tools / "node_modules" / "left-pad" / "index.js").write_text("noise\n")
            (tools / "helper.sh").write_text("echo hi\n")

            transfer(load_project(sides.source), sides.source, sides.destination, direction=PUSH)

            self.assertTrue((sides.destination / "tools" / "helper.sh").is_file())
            self.assertFalse((sides.destination / "tools" / "node_modules").exists())


class SecretTests(unittest.TestCase):
    def test_a_push_refuses_files_that_look_like_credentials(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=(".env",))
            (sides.source / ".env").write_text("TOKEN=live\n")

            with self.assertRaises(SecretsRefusedError) as caught:
                transfer(load_project(sides.source), sides.source, sides.destination, direction=PUSH)

            self.assertEqual(caught.exception.paths, (".env",))

    def test_a_push_carries_them_once_allowed(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=(".env",))
            (sides.source / ".env").write_text("TOKEN=live\n")

            transfer(
                load_project(sides.source),
                sides.source,
                sides.destination,
                direction=PUSH,
                allow_secrets=True,
            )

            self.assertTrue((sides.destination / ".env").is_file())

    def test_a_pull_is_not_blocked_by_them(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=(".env",))
            (sides.source / ".env").write_text("TOKEN=live\n")

            transfer(load_project(sides.source), sides.source, sides.destination, direction=PULL)

            self.assertTrue((sides.destination / ".env").is_file())


class DriftTests(unittest.TestCase):
    def test_only_the_side_that_changed_is_reported_as_drifted(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md",))
            (sides.source / "AGENTS.md").write_text("v1\n")
            state = load_project(sides.source)
            transfer(state, sides.source, sides.destination, direction=PUSH)
            recorded = digests(payload_paths(state), sides.source)

            (sides.source / "AGENTS.md").write_text("v2\n")

            self.assertEqual(drifted(payload_paths(state), sides.source, recorded), ("AGENTS.md",))
            self.assertEqual(drifted(payload_paths(state), sides.destination, recorded), ())

    def test_a_directory_digest_follows_its_contents(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("tools",))
            (sides.source / "tools").mkdir()
            (sides.source / "tools" / "helper.sh").write_text("v1\n")
            state = load_project(sides.source)
            recorded = digests(payload_paths(state), sides.source)

            (sides.source / "tools" / "helper.sh").write_text("v2\n")

            self.assertEqual(drifted(payload_paths(state), sides.source, recorded), ("tools",))

    def test_compare_splits_the_two_sides(self) -> None:
        with Sides() as sides:
            write_project(sides.source, include=("AGENTS.md", "NOTES.md"))
            (sides.source / "AGENTS.md").write_text("v1\n")
            (sides.source / "NOTES.md").write_text("notes\n")
            state = load_project(sides.source)
            transfer(state, sides.source, sides.destination, direction=PUSH)
            (sides.source / "AGENTS.md").write_text("v2\n")
            (sides.destination / "NOTES.md").unlink()

            only_local, only_remote, differing = compare(payload_paths(state), sides.source, sides.destination)

            self.assertEqual(only_local, ("NOTES.md",))
            self.assertEqual(only_remote, ())
            self.assertEqual(differing, ("AGENTS.md",))


class ManifestTests(unittest.TestCase):
    def test_the_manifest_survives_a_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_project(root)
            recorded = digests(payload_paths(load_project(root)), root)
            SyncManifest(root=root, recorded={}).save("demo", recorded)

            self.assertEqual(SyncManifest.load(root).recorded, recorded)

    def test_an_unreadable_manifest_is_treated_as_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_project(root)
            (root / ".mires" / "sync-manifest.json").write_text("{not json")

            self.assertEqual(SyncManifest.load(root).recorded, {})


class Sides:
    """A source project and the directory it syncs with, both throwaway."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="mires-sync-")
        root = Path(self._temporary.name)
        self.source = root / "project"
        self.destination = root / "repo" / "projects" / "demo"
        self.source.mkdir(parents=True)
        self.destination.mkdir(parents=True)

    def __enter__(self) -> Sides:
        return self

    def __exit__(self, *exception: object) -> None:
        self._temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
