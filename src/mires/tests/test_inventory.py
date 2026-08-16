from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mires.compatibility.parsing import CANONICAL_HOOK_EVENTS, load_inventory
from mires.state import load_state

ROOT = Path(__file__).resolve().parents[3]

STATE = """
version: 1
mcps:
  - name: Example
    slug: example
    description: "An example server."
skills: []
subagents: []
rules:
  - name: Example Rule
    slug: example-rule
    description: "An example rule."
hooks:
  - name: Example Hook
    slug: example-hook
    description: "An example hook."
"""


def build_catalog(root: Path, mcp: dict, hooks: dict) -> None:
    (root / "state.yml").write_text(STATE.lstrip())
    (root / "skills").mkdir()
    (root / "subagents").mkdir()
    (root / "rules").mkdir()
    (root / "rules" / "example-rule.md").write_text("# Example Rule\n\nDo the thing.\n")
    (root / "mcps" / "example").mkdir(parents=True)
    (root / "mcps" / "example" / "mcp.json").write_text(json.dumps(mcp))
    (root / "hooks" / "example-hook").mkdir(parents=True)
    (root / "hooks" / "example-hook" / "hooks.json").write_text(json.dumps(hooks))
    (root / "hooks" / "example-hook" / "run.sh").write_text("#!/bin/sh\nexit 0\n")


def load(root: Path, mcp: dict, hooks: dict):
    build_catalog(root, mcp, hooks)
    return load_inventory(root, load_state(root))


VALID_MCP = {"name": "example", "command": "run-server", "args": ["--flag"]}
VALID_HOOKS = {"version": 1, "hooks": {"afterFileEdit": [{"command": "hooks/example-hook/run.sh"}]}}


class InventoryTests(unittest.TestCase):
    def test_loads_rules_mcps_and_hooks_declared_in_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = load(Path(temp_dir), VALID_MCP, VALID_HOOKS)

            self.assertEqual([rule.name for rule in inventory.rules], ["example-rule"])
            self.assertEqual([mcp.name for mcp in inventory.mcps], ["example"])
            self.assertEqual([hook.name for hook in inventory.hooks], ["example-hook"])
            self.assertEqual(inventory.mcps[0].server, {"command": "run-server", "args": ["--flag"]})
            self.assertEqual(tuple(inventory.hooks[0].events), ("afterFileEdit",))
            self.assertIn("Do the thing.", inventory.rules[0].body)
            self.assertEqual(inventory.specs, (), "a catalog without openspec/specs is still valid")

    def test_a_server_must_declare_a_command_or_a_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = load(Path(temp_dir), {"name": "example"}, VALID_HOOKS)

            self.assertEqual(inventory.mcps, ())
            self.assertTrue(any("command" in error.message for error in inventory.errors))

    def test_a_server_name_must_match_its_slug(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = load(Path(temp_dir), {"name": "other", "command": "run"}, VALID_HOOKS)

            self.assertTrue(any("must match the declared slug" in error.message for error in inventory.errors))

    def test_hooks_may_only_bind_canonical_events(self) -> None:
        invalid = {"version": 1, "hooks": {"onWhatever": [{"command": "hooks/example-hook/run.sh"}]}}
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = load(Path(temp_dir), VALID_MCP, invalid)

            self.assertEqual(inventory.hooks, ())
            self.assertTrue(any("unknown hook event: onWhatever" in error.message for error in inventory.errors))

    def test_a_hook_command_must_exist_on_disk(self) -> None:
        missing = {"version": 1, "hooks": {"stop": [{"command": "hooks/example-hook/absent.sh"}]}}
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = load(Path(temp_dir), VALID_MCP, missing)

            self.assertTrue(any("script does not exist" in error.message for error in inventory.errors))

    def test_the_repository_catalog_loads_without_errors(self) -> None:
        inventory = load_inventory(ROOT, load_state(ROOT))

        self.assertEqual(inventory.errors, ())
        self.assertTrue(inventory.rules and inventory.mcps and inventory.hooks)
        for hook in inventory.hooks:
            for event in hook.events:
                with self.subTest(hook=hook.name, event=event):
                    self.assertIn(event, CANONICAL_HOOK_EVENTS)


if __name__ == "__main__":
    unittest.main()
