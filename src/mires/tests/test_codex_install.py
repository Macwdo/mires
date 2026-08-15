from __future__ import annotations

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from mires.compatibility.codex import patch_agents_config, render_agent_toml
from mires.compatibility.models import AgentAsset

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


class CodexInstallCommandTests(unittest.TestCase):
    def test_install_command_writes_agents_and_config_to_alternate_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            legacy_bundle = codex_home / "agents" / "mires" / "planner"
            legacy_bundle.mkdir(parents=True)
            (legacy_bundle / "MANIFEST.toml").write_text('generated_by = "mires"\n')
            result = run_cli("install", "--target", "codex", "--root", str(ROOT), "--codex-home", str(codex_home))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Installed 2 Codex agents", result.stdout)
            self.assertTrue((codex_home / "agents" / "explorer.toml").exists())
            self.assertTrue((codex_home / "mires" / "agents" / "explorer" / "AGENT.md").exists())
            self.assertTrue((codex_home / "mires" / "agents" / "explorer" / "agents" / "openai.yaml").exists())
            self.assertTrue(
                (codex_home / "mires" / "agents" / "explorer" / "skills" / "project-conventions").exists()
            )
            self.assertFalse((codex_home / "skills" / "project-conventions").exists())
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
            parsed_agent = tomllib.loads((codex_home / "agents" / "explorer.toml").read_text())
            skill_paths = [entry["path"] for entry in parsed_agent["skills"]["config"]]
            self.assertTrue(all(Path(path).is_absolute() for path in skill_paths))

    def test_dry_run_does_not_write_to_alternate_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            result = run_cli(
                "install", "--target", "codex", "--root", str(ROOT), "--codex-home", str(codex_home), "--dry-run"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Dry run: would install 2 Codex agents", result.stdout)
            self.assertFalse(codex_home.exists())

    def test_profile_narrows_the_installed_skill_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            result = run_cli(
                "install",
                "--target",
                "codex",
                "--root",
                str(ROOT),
                "--codex-home",
                str(codex_home),
                "--profile",
                "tenant-evaluation",
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Would install 2 Codex agents", result.stdout)

    def test_unknown_profile_fails_clearly(self) -> None:
        result = run_cli("install", "--target", "codex", "--root", str(ROOT), "--profile", "missing")

        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown profile: missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
