from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from mires.state import load_state, validate_state
from mires.state.loader import StateFileError
from mires.state.models import MiresState

REPO_ROOT = Path(__file__).resolve().parents[3]

MINIMAL_STATE = """
version: 1
config:
  profiles:
    - name: Personal
      slug: personal
      description: "Personal profile"
      using:
        skills:
          - python
        subagents:
          - explorer
skills:
  - name: Python
    slug: python
    description: "Python guidance"
subagents:
  - name: Explorer
    slug: explorer
    description: "Explore the repository"
"""

PRIVATE_SKILL_BODY = """
## When To Use

Always.

## Core Rules

Be explicit.

## Preferred Patterns

Small functions.

## Anti-Patterns

Hidden mutation.

## Checklist

- Ran the tests.

## References Index

None.
"""


def write_skill(root: Path, slug: str, *, body: str = PRIVATE_SKILL_BODY, name: str | None = None) -> Path:
    directory = root / "skills" / slug
    directory.mkdir(parents=True, exist_ok=True)
    frontmatter = f"---\nname: {name or slug}\ndescription: {slug} guidance\n---\n"
    (directory / "SKILL.md").write_text(frontmatter + body)
    return directory


def write_subagent(root: Path, slug: str) -> Path:
    directory = root / "subagents" / slug
    (directory / "agents").mkdir(parents=True, exist_ok=True)
    frontmatter = f'---\nname: {slug}\ndescription: {slug} agent\nparent: ""\nchildren: []\n---\n'
    (directory / "AGENT.md").write_text(frontmatter)
    (directory / "agents" / "openai.yaml").write_text(f'metadata:\n  name: "{slug}"\n')
    return directory


class StateFixture:
    """A throwaway repository root containing a state.yml and the assets it declares."""

    def __init__(self, state_text: str = MINIMAL_STATE) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="mires-state-")
        self.root = Path(self._temporary.name)
        (self.root / "state.yml").write_text(textwrap.dedent(state_text).lstrip())
        write_skill(self.root, "python")
        write_subagent(self.root, "explorer")

    def __enter__(self) -> StateFixture:
        return self

    def __exit__(self, *exception: object) -> None:
        self._temporary.cleanup()

    def write_state(self, state_text: str) -> None:
        (self.root / "state.yml").write_text(textwrap.dedent(state_text).lstrip())

    def add_skill_entry(self, slug: str, name: str) -> None:
        entry = f'  - name: {name}\n    slug: {slug}\n    description: "{name}"\n'
        self.write_state(MINIMAL_STATE.replace("\nsubagents:\n", f"\n{entry}subagents:\n", 1))

    def errors(self) -> list[str]:
        state = load_state(self.root)
        return [message.message for message in validate_state(self.root, state)]


class StateSchemaTests(unittest.TestCase):
    def test_valid_state_produces_no_errors(self) -> None:
        with StateFixture() as fixture:
            self.assertEqual(fixture.errors(), [])

    def test_missing_state_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(StateFileError) as caught:
                load_state(Path(temp_dir))

            self.assertIn("missing state definition", caught.exception.messages[0].message)

    def test_invalid_slug_is_rejected(self) -> None:
        with StateFixture() as fixture:
            fixture.write_state(MINIMAL_STATE.replace("slug: python", "slug: Python_Rules"))

            with self.assertRaises(StateFileError) as caught:
                load_state(fixture.root)

            self.assertTrue(any("skills.0.slug" in message.message for message in caught.exception.messages))

    def test_duplicate_slug_is_rejected(self) -> None:
        with StateFixture() as fixture:
            fixture.add_skill_entry("python", "Python Again")

            with self.assertRaises(StateFileError) as caught:
                load_state(fixture.root)

            self.assertTrue(any("duplicate skills slug: python" in m.message for m in caught.exception.messages))

    def test_unknown_field_is_rejected(self) -> None:
        with StateFixture() as fixture:
            fixture.write_state(MINIMAL_STATE.replace('description: "Python guidance"', "unexpected: true"))

            with self.assertRaises(StateFileError):
                load_state(fixture.root)

    def test_using_accepts_the_sequence_form(self) -> None:
        sequence_form = MINIMAL_STATE.replace(
            """      using:
        skills:
          - python
        subagents:
          - explorer""",
            """      using:
        - skills:
            - python
          subagents:
            - explorer""",
        )
        state = MiresState.model_validate_json(json.dumps(_as_mapping(sequence_form)))

        self.assertEqual(state.config.profiles[0].using.skills, ["python"])
        self.assertEqual(state.config.profiles[0].using.subagents, ["explorer"])

    def test_secret_declaration_accepts_only_an_environment_source(self) -> None:
        raw = _as_mapping(MINIMAL_STATE)
        raw["secrets"] = [_secret_entry()]

        state = MiresState.model_validate(raw)

        self.assertEqual(state.secrets[0].source.env, "EXAMPLE_API_KEY")
        self.assertEqual(state.secrets[0].slug, "example-api-key")

    def test_secret_declaration_rejects_a_literal_value(self) -> None:
        raw = _as_mapping(MINIMAL_STATE)
        secret = _secret_entry()
        source = secret["source"]
        self.assertIsInstance(source, dict)
        assert isinstance(source, dict)
        source["value"] = "must-not-be-accepted"
        raw["secrets"] = [secret]

        with self.assertRaises(ValueError):
            MiresState.model_validate(raw)

    def test_secret_declaration_rejects_consumer_scopes(self) -> None:
        raw = _as_mapping(MINIMAL_STATE)
        secret = _secret_entry()
        secret["scopes"] = {"mcps": ["example"]}
        raw["secrets"] = [secret]

        with self.assertRaises(ValueError):
            MiresState.model_validate(raw)

    def test_mcp_rejects_overlapping_secret_bindings(self) -> None:
        raw = _as_mapping(MINIMAL_STATE)
        first = _secret_entry()
        second = _secret_entry()
        second["name"] = "Other API Key"
        second["slug"] = "other-api-key"
        raw["secrets"] = [first, second]
        mcp = _mcp_entry()
        secret_refs = mcp["secrets"]
        assert isinstance(secret_refs, list)
        secret_refs.append(
            {
                "secret": "other-api-key",
                "env": "EXAMPLE_API_KEY",
                "targets": ["codex", "claude"],
            }
        )
        raw["mcps"] = [mcp]

        with self.assertRaisesRegex(ValueError, "duplicate secret binding"):
            MiresState.model_validate(raw)


class StateIntegrityTests(unittest.TestCase):
    def test_profile_referencing_an_unknown_slug_is_reported(self) -> None:
        with StateFixture() as fixture:
            fixture.write_state(
                MINIMAL_STATE.replace("          - python\n", "          - python\n          - ghost\n")
            )

            self.assertIn(
                "profile 'personal' references unknown skills entry: ghost",
                fixture.errors(),
            )

    def test_mcp_referencing_an_unknown_secret_is_reported(self) -> None:
        with StateFixture() as fixture:
            state = MiresState.model_validate({**_as_mapping(MINIMAL_STATE), "mcps": [_mcp_entry("ghost")]})

            errors = [message.message for message in validate_state(fixture.root, state)]

            self.assertIn("MCP 'example' references unknown secret: ghost", errors)

    def test_mcp_secret_binding_referencing_an_unknown_target_is_reported(self) -> None:
        with StateFixture() as fixture:
            mcp = _mcp_entry()
            secret_refs = mcp["secrets"]
            assert isinstance(secret_refs, list)
            secret_ref = secret_refs[0]
            assert isinstance(secret_ref, dict)
            secret_ref["targets"] = ["unknown-runtime"]
            state = MiresState.model_validate(
                {**_as_mapping(MINIMAL_STATE), "secrets": [_secret_entry()], "mcps": [mcp]}
            )

            errors = [message.message for message in validate_state(fixture.root, state)]

            self.assertIn(
                "MCP 'example' secret 'example-api-key' references unknown target: unknown-runtime",
                errors,
            )

    def test_declared_entry_without_a_directory_is_reported(self) -> None:
        with StateFixture() as fixture:
            fixture.add_skill_entry("missing", "Missing")

            self.assertIn("declared skills entry directory does not exist", fixture.errors())

    def test_undeclared_directory_is_reported_as_orphan(self) -> None:
        with StateFixture() as fixture:
            write_skill(fixture.root, "orphan")

            self.assertIn("undeclared skills entry", fixture.errors())

    def test_front_matter_name_must_match_the_slug(self) -> None:
        with StateFixture() as fixture:
            write_skill(fixture.root, "python", name="not-python")

            self.assertIn("front matter name must match the declared slug: python", fixture.errors())

    def test_private_skill_missing_a_required_section_is_reported(self) -> None:
        with StateFixture() as fixture:
            write_skill(fixture.root, "python", body="\n## When To Use\n\nAlways.\n")

            self.assertIn("private skill is missing required section: ## Core Rules", fixture.errors())

    def test_public_skill_requires_runtime_metadata(self) -> None:
        with StateFixture() as fixture:
            fixture.write_state(
                MINIMAL_STATE.replace("    slug: python\n", "    slug: python\n    visibility: public\n")
            )

            self.assertIn("public skill is missing runtime metadata", fixture.errors())


class RepositoryStateTests(unittest.TestCase):
    def test_repository_catalog_is_valid(self) -> None:
        state = load_state(REPO_ROOT)

        self.assertEqual(validate_state(REPO_ROOT, state), ())

    def test_every_profile_selects_at_least_one_subagent(self) -> None:
        state = load_state(REPO_ROOT)

        for profile in state.config.profiles:
            with self.subTest(profile=profile.slug):
                self.assertTrue(profile.using.subagents)


def _as_mapping(state_text: str) -> dict[str, object]:
    import yaml

    return yaml.safe_load(textwrap.dedent(state_text).lstrip())


def _secret_entry() -> dict[str, object]:
    return {
        "name": "Example API Key",
        "slug": "example-api-key",
        "description": "Example environment-backed credential.",
        "source": {"env": "EXAMPLE_API_KEY"},
    }


def _mcp_entry(secret: str = "example-api-key") -> dict[str, object]:
    return {
        "name": "Example",
        "slug": "example",
        "description": "Example MCP.",
        "secrets": [
            {
                "secret": secret,
                "env": "EXAMPLE_API_KEY",
                "targets": ["codex", "claude"],
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
