from __future__ import annotations

import re
import unittest
from pathlib import Path

from mires.frontmatter import read_frontmatter
from mires.state import load_state

ROOT = Path(__file__).resolve().parents[3]
PUBLIC_SKILLS = {"mires", "mires-python", "mires-django", "mires-react", "mires-typescript"}
HANDBOOK_COUNTS = {"mires-django": 121, "mires-react": 41}


class PublicSkillCatalogTests(unittest.TestCase):
    def test_public_skills_are_self_contained_packages(self) -> None:
        for name in sorted(PUBLIC_SKILLS):
            with self.subTest(name=name):
                package = ROOT / "skills" / name
                skill_path = package / "SKILL.md"
                metadata_path = package / "agents" / "openai.yaml"
                text = skill_path.read_text()

                self.assertEqual(read_frontmatter(skill_path)["name"], name)
                self.assertTrue(metadata_path.exists())
                self.assertIn(f"${name}", metadata_path.read_text())
                for relative in re.findall(r"`(references/[^`]+\.md)`", text):
                    self.assertTrue((package / relative).exists(), relative)

    def test_state_marks_exactly_the_intended_skills_public(self) -> None:
        state = load_state(ROOT)
        declared_public = {skill.slug for skill in state.skills if skill.visibility == "public"}

        self.assertEqual(declared_public, PUBLIC_SKILLS)

    def test_every_topic_is_a_rule_document_routed_by_its_domain_skill(self) -> None:
        for name in sorted(PUBLIC_SKILLS):
            references = ROOT / "skills" / name / "references"
            routed = (ROOT / "skills" / name / "SKILL.md").read_text()
            topics = [d for d in sorted(references.iterdir()) if d.is_dir() and d.name != "handbook"]

            self.assertTrue(topics, f"{name} aggregates no topic")
            for topic in topics:
                with self.subTest(skill=name, topic=topic.name):
                    self.assertTrue((topic / "rules.md").exists())
                    self.assertIn(f"references/{topic.name}/rules.md", routed)

    def test_merged_handbooks_exclude_generated_content(self) -> None:
        for name, expected_count in HANDBOOK_COUNTS.items():
            with self.subTest(name=name):
                handbook = ROOT / "skills" / name / "references" / "handbook"
                markdown = list(handbook.rglob("*.md"))

                self.assertEqual(len(markdown), expected_count)
                self.assertFalse(any("graphify-out" in path.parts for path in handbook.rglob("*")))
                self.assertFalse((handbook / "AGENTS.md").exists())
                self.assertTrue((handbook / "maintainer-instructions.md").exists())


if __name__ == "__main__":
    unittest.main()
