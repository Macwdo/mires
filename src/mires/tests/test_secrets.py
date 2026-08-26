from __future__ import annotations

import unittest
from pathlib import Path

from mires.cli import select_inventory
from mires.compatibility.parsing import filter_inventory
from mires.compatibility.secrets import bind_secret_references
from mires.state import load_state

ROOT = Path(__file__).resolve().parents[3]


class ScopedSecretTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = load_state(ROOT)
        self.inventory = select_inventory(ROOT, self.state, "personal")

    def test_profile_includes_secret_only_through_its_selected_mcp(self) -> None:
        self.assertEqual([secret.name for secret in self.inventory.secrets], ["context7-api-key"])
        self.assertEqual(self.inventory.mcps[0].secrets[0].secret, "context7-api-key")

        without_mcps = filter_inventory(
            self.inventory,
            agent_names={agent.name for agent in self.inventory.agents},
            skill_names={skill.name for skill in self.inventory.skills},
            rule_names={rule.name for rule in self.inventory.rules},
            mcp_names=set(),
            hook_names={hook.name for hook in self.inventory.hooks},
        )

        self.assertEqual(without_mcps.secrets, ())

    def test_codex_whitelists_the_source_environment_variable_by_name(self) -> None:
        bound = bind_secret_references(self.inventory, "codex")

        self.assertEqual(bound.mcps[0].server["env_vars"], ["CONTEXT7_API_KEY"])
        self.assertNotIn("env", bound.mcps[0].server)

    def test_claude_uses_runtime_environment_expansion(self) -> None:
        bound = bind_secret_references(self.inventory, "claude")

        self.assertEqual(bound.mcps[0].server["env"], {"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"})

    def test_opencode_uses_runtime_environment_expansion(self) -> None:
        bound = bind_secret_references(self.inventory, "opencode")

        self.assertEqual(bound.mcps[0].server["env"], {"CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}"})

    def test_unscoped_cursor_config_never_receives_a_literal_or_placeholder(self) -> None:
        bound = bind_secret_references(self.inventory, "cursor")

        self.assertNotIn("env", bound.mcps[0].server)


if __name__ == "__main__":
    unittest.main()
