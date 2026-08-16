from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mires.frontmatter import parse_frontmatter

ROOT = Path(__file__).resolve().parents[3]
CLI = ["-m", "mires.cli"]


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *CLI, *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def install(home: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run_cli("install", "--target", "claude", "--root", str(ROOT), "--claude-home", str(home), *extra)


class ClaudeInstallTests(unittest.TestCase):
    def test_install_writes_every_asset_kind(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".claude"
            result = install(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / "agents" / "planner.md").exists())
            self.assertTrue((home / "skills" / "mires-django" / "SKILL.md").exists())
            self.assertTrue((home / "CLAUDE.md").exists())
            self.assertTrue((home / "settings.json").exists())
            self.assertTrue((home.parent / ".claude.json").exists())

    def test_subagents_carry_the_frontmatter_claude_requires(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".claude"
            install(home)
            frontmatter = parse_frontmatter((home / "agents" / "explorer.md").read_text())

            self.assertEqual(frontmatter["name"], "explorer")
            self.assertTrue(frontmatter["description"].strip())

    def test_canonical_hook_events_map_onto_claude_matchers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".claude"
            install(home)
            entry = json.loads((home / "settings.json").read_text())["hooks"]["PostToolUse"][0]

            self.assertIn("Edit", entry["matcher"])
            self.assertEqual(entry["hooks"][0]["type"], "command")
            self.assertTrue(Path(entry["hooks"][0]["command"]).is_relative_to(home))

    def test_rules_land_in_a_replaceable_block_inside_existing_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".claude"
            home.mkdir(parents=True)
            (home / "CLAUDE.md").write_text("# My own notes\n\nKeep this line.\n")
            install(home)
            install(home)
            memory = (home / "CLAUDE.md").read_text()

            self.assertIn("Keep this line.", memory)
            self.assertEqual(memory.count("<!-- BEGIN MIRES -->"), 1)
            self.assertIn("No Secrets", memory)

    def test_install_preserves_mcp_servers_the_user_owns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".claude"
            home.mkdir(parents=True)
            (home.parent / ".claude.json").write_text(
                json.dumps({"mcpServers": {"mine": {"command": "own"}}, "otherState": 42})
            )
            install(home)
            document = json.loads((home.parent / ".claude.json").read_text())

            self.assertEqual(document["otherState"], 42)
            self.assertEqual(document["mcpServers"]["mine"], {"command": "own"})
            self.assertIn("context7", document["mcpServers"])


if __name__ == "__main__":
    unittest.main()
