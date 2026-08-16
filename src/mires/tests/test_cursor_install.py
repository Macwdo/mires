from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mires.compatibility.cursor import PLUGIN_DIR
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
    return run_cli("install", "--target", "cursor", "--root", str(ROOT), "--cursor-home", str(home), *extra)


class CursorInstallTests(unittest.TestCase):
    def test_install_writes_every_asset_kind(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".cursor"
            result = install(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / "agents" / "explorer.md").exists())
            self.assertTrue((home / "skills" / "mires-python" / "SKILL.md").exists())
            self.assertTrue((home / PLUGIN_DIR / "rules" / "no-secrets.mdc").exists())
            self.assertTrue((home / PLUGIN_DIR / ".cursor-plugin" / "plugin.json").exists())
            self.assertTrue((home / "mcp.json").exists())
            self.assertTrue((home / "hooks.json").exists())

    def test_rules_ship_as_a_local_plugin_because_cursor_has_no_global_rules_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".cursor"
            install(home)
            manifest = json.loads((home / PLUGIN_DIR / ".cursor-plugin" / "plugin.json").read_text())
            frontmatter = parse_frontmatter((home / PLUGIN_DIR / "rules" / "commit-style.mdc").read_text())

            self.assertEqual(manifest["name"], "mires")
            self.assertTrue(frontmatter["alwaysApply"])
            self.assertTrue(frontmatter["description"].strip())
            self.assertFalse((home / "rules").exists(), "Cursor never loads a global ~/.cursor/rules directory")

    def test_hook_commands_point_at_the_installed_copy_not_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".cursor"
            install(home)
            document = json.loads((home / "hooks.json").read_text())
            command = Path(document["hooks"]["afterFileEdit"][0]["command"])

            self.assertEqual(document["version"], 1)
            self.assertTrue(command.is_relative_to(home))
            self.assertTrue(command.exists())
            self.assertTrue(command.stat().st_mode & 0o111, "installed hook script must be executable")

    def test_install_preserves_configuration_the_user_owns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".cursor"
            home.mkdir(parents=True)
            (home / "mcp.json").write_text(json.dumps({"mcpServers": {"mine": {"command": "own-server"}}}))
            (home / "hooks.json").write_text(
                json.dumps({"version": 1, "hooks": {"stop": [{"command": "./mine.sh"}]}})
            )
            install(home)

            servers = json.loads((home / "mcp.json").read_text())["mcpServers"]
            hooks = json.loads((home / "hooks.json").read_text())["hooks"]

            self.assertEqual(servers["mine"], {"command": "own-server"})
            self.assertIn("context7", servers)
            self.assertEqual(hooks["stop"], [{"command": "./mine.sh"}])

    def test_reinstalling_a_narrower_profile_removes_what_it_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".cursor"
            install(home)
            self.assertTrue((home / "skills" / "mires-react").exists())
            self.assertTrue((home / PLUGIN_DIR / "rules" / "commit-style.mdc").exists())

            install(home, "--profile", "tenant-evaluation")

            self.assertFalse((home / "skills" / "mires-react").exists())
            self.assertFalse((home / PLUGIN_DIR / "rules" / "commit-style.mdc").exists())
            self.assertTrue((home / PLUGIN_DIR / "rules" / "no-secrets.mdc").exists())
            self.assertTrue((home / "skills" / "mires-python").exists())
            self.assertNotIn("hooks", json.loads((home / "hooks.json").read_text()))


if __name__ == "__main__":
    unittest.main()
