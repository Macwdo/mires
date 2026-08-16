from __future__ import annotations

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from mires.compatibility.codex import (
    install_codex_assets,
    patch_agents_config,
    patch_mcp_servers_config,
    render_agent_toml,
)
from mires.compatibility.models import AgentAsset
from mires.compatibility.parsing import filter_inventory, load_inventory
from mires.state import load_state

ROOT = Path(__file__).resolve().parents[3]
CLI = ["-m", "mires.cli"]


def make_agent(name: str = "explorer") -> AgentAsset:
    return AgentAsset(
        name=name,
        description=f"{name} canonical description",
        parent="",
        children=(),
        path=ROOT / "subagents" / name / "AGENT.md",
        metadata_path=ROOT / "subagents" / name / "agents" / "openai.yaml",
        metadata={
            "interface": {
                "display_name": name.title(),
                "short_description": f"{name} short description",
                "default_prompt": f'Use ${name}. Keep "quotes" valid.',
            },
            "metadata": {"name": name, "parent": "", "children": []},
        },
    )


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *CLI, *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def install(home: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run_cli("install", "--target", "codex", "--root", str(ROOT), "--codex-home", str(home), *extra)


def full_inventory():
    return load_inventory(ROOT, load_state(ROOT))


class CodexAgentRenderingTests(unittest.TestCase):
    def test_render_agent_toml_is_valid_codex_config_layer(self) -> None:
        rendered = render_agent_toml(make_agent(), ())
        parsed = tomllib.loads(rendered)

        self.assertEqual(set(parsed), {"developer_instructions"})
        self.assertIn('Keep "quotes" valid.', parsed["developer_instructions"])
        self.assertNotIn("Use $explorer.", parsed["developer_instructions"])
        self.assertIn("/.codex/mires/agents/explorer/AGENT.md", parsed["developer_instructions"])
        self.assertNotIn("subagents/", rendered)
        self.assertNotIn("display_name", parsed)
        self.assertNotIn("default_prompt", parsed)

    def test_render_agent_toml_wraps_prompt_lines(self) -> None:
        rendered = render_agent_toml(make_agent(), ())
        parsed = tomllib.loads(rendered)

        for line in parsed["developer_instructions"].splitlines():
            self.assertLessEqual(len(line), 131)


class CodexConfigPatchTests(unittest.TestCase):
    def test_patch_config_creates_agents_section_when_missing(self) -> None:
        patched = patch_agents_config('model = "gpt-5"\n', (make_agent(),))
        parsed = tomllib.loads(patched)

        self.assertEqual(parsed["model"], "gpt-5")
        self.assertEqual(parsed["agents"]["explorer"]["config_file"], "agents/explorer.toml")

    def test_patch_config_preserves_existing_agents_settings_and_unrelated_agent(self) -> None:
        existing = """
[agents]
max_threads = 6

[agents.personal_patterns]
description = "Keep me"
config_file = "agents/personal_patterns.toml"
""".lstrip()
        patched = patch_agents_config(existing, (make_agent(),))
        parsed = tomllib.loads(patched)

        self.assertEqual(parsed["agents"]["max_threads"], 6)
        self.assertEqual(
            parsed["agents"]["personal_patterns"]["config_file"],
            "agents/personal_patterns.toml",
        )
        self.assertEqual(parsed["agents"]["explorer"]["description"], "explorer short description")

    def test_patch_config_updates_managed_entry_without_duplicates(self) -> None:
        existing = """
[agents]
max_depth = 2

[agents.explorer]
description = "Old"
config_file = "agents/old.toml"
""".lstrip()
        patched_once = patch_agents_config(existing, (make_agent(),))
        patched_twice = patch_agents_config(patched_once, (make_agent(),))

        self.assertEqual(patched_once, patched_twice)
        self.assertEqual(patched_once.count("[agents.explorer]"), 1)
        parsed = tomllib.loads(patched_once)
        self.assertEqual(parsed["agents"]["explorer"]["config_file"], "agents/explorer.toml")

    def test_patch_config_removes_previously_owned_agents_and_mcp_servers(self) -> None:
        existing = """
[agents]
max_threads = 2

[agents.planner]
description = "Stale"
config_file = "agents/planner.toml"

[mcp_servers.context7]
command = "old"

[mcp_servers.mine]
command = "keep-me"
""".lstrip()
        patched = patch_mcp_servers_config(
            patch_agents_config(existing, (make_agent(),), previous_names=["planner", "explorer"]),
            (),
            previous_names=["context7"],
        )
        parsed = tomllib.loads(patched)

        self.assertEqual(parsed["agents"]["max_threads"], 2)
        self.assertIn("explorer", parsed["agents"])
        self.assertNotIn("planner", parsed["agents"])
        self.assertNotIn("context7", parsed.get("mcp_servers", {}))
        self.assertEqual(parsed["mcp_servers"]["mine"]["command"], "keep-me")


class CodexInstallCommandTests(unittest.TestCase):
    def test_install_command_writes_agents_and_config_to_alternate_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            legacy_bundle = codex_home / "agents" / "mires" / "planner"
            legacy_bundle.mkdir(parents=True)
            (legacy_bundle / "MANIFEST.toml").write_text('generated_by = "mires"\n')
            result = install(codex_home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Installed 2 subagents", result.stdout)
            self.assertTrue((codex_home / "agents" / "explorer.toml").exists())
            self.assertTrue((codex_home / "mires" / "agents" / "explorer" / "AGENT.md").exists())
            self.assertTrue((codex_home / "mires" / "agents" / "explorer" / "agents" / "openai.yaml").exists())
            self.assertTrue((codex_home / "mires" / "agents" / "explorer" / "skills" / "mires").exists())
            self.assertTrue((codex_home / "skills" / "mires" / "SKILL.md").exists())
            self.assertTrue((codex_home / "AGENTS.md").exists())
            self.assertIn("<!-- BEGIN MIRES -->", (codex_home / "AGENTS.md").read_text())
            bundled_text = "\n".join(
                path.read_text()
                for path in (codex_home / "mires" / "agents").rglob("*")
                if path.is_file() and path.suffix in {".md", ".yaml", ".yml", ".toml"}
            )
            self.assertNotIn("subagents/", bundled_text)
            self.assertEqual(sorted((codex_home / "agents").glob("*/*.toml")), [])
            self.assertFalse((codex_home / "agents" / "mires").exists())
            parsed_config = tomllib.loads((codex_home / "config.toml").read_text())
            self.assertEqual(parsed_config["agents"]["explorer"]["config_file"], "agents/explorer.toml")
            self.assertIn("context7", parsed_config["mcp_servers"])
            parsed_agent = tomllib.loads((codex_home / "agents" / "explorer.toml").read_text())
            skill_paths = [entry["path"] for entry in parsed_agent["skills"]["config"]]
            self.assertTrue(all(Path(path).is_absolute() for path in skill_paths))

    def test_reinstalling_a_narrower_inventory_removes_config_keys_and_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / ".codex"
            inventory = full_inventory()
            install_codex_assets(inventory, home)

            config = tomllib.loads((home / "config.toml").read_text())
            self.assertIn("planner", config["agents"])
            self.assertIn("context7", config["mcp_servers"])
            self.assertIn("<!-- BEGIN MIRES -->", (home / "AGENTS.md").read_text())

            narrowed = filter_inventory(
                inventory,
                agent_names={"explorer"},
                skill_names={"mires", "mires-python", "mires-django"},
                rule_names=set(),
                mcp_names=set(),
                hook_names=set(),
            )
            install_codex_assets(narrowed, home)

            config = tomllib.loads((home / "config.toml").read_text())
            self.assertIn("explorer", config["agents"])
            self.assertNotIn("planner", config["agents"])
            self.assertNotIn("mcp_servers", config)
            self.assertFalse((home / "agents" / "planner.toml").exists())
            self.assertFalse((home / "mires" / "agents" / "planner").exists())
            self.assertFalse((home / "AGENTS.md").exists())

    def test_dry_run_does_not_write_to_alternate_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            result = install(codex_home, "--dry-run")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Dry run: would install the Mires catalog", result.stdout)
            self.assertFalse(codex_home.exists())

    def test_profile_narrows_the_installed_skill_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            result = install(codex_home, "--profile", "tenant-evaluation")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((codex_home / "skills" / "mires-django").exists())
            self.assertFalse((codex_home / "skills" / "mires-react").exists())
            self.assertIn("No Secrets", (codex_home / "AGENTS.md").read_text())
            self.assertNotIn("Commit Style", (codex_home / "AGENTS.md").read_text())

    def test_unknown_profile_fails_clearly(self) -> None:
        result = run_cli("install", "--target", "codex", "--root", str(ROOT), "--profile", "missing")

        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown profile: missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
