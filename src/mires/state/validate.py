from __future__ import annotations

from pathlib import Path

from mires.frontmatter import FrontMatterError, read_frontmatter
from mires.messages import ValidationMessage
from mires.state.models import (
    PRIVATE_SKILL_SECTIONS,
    SECTIONS,
    CatalogEntry,
    MiresState,
    SectionSpec,
    SkillEntry,
)

FRONTMATTER_SECTIONS = {"skills": "SKILL.md", "subagents": "AGENT.md"}


def validate_state(root: Path, state: MiresState) -> tuple[ValidationMessage, ...]:
    """Check the state definition against the catalogs it declares and the files on disk."""
    root = root.resolve()
    errors: list[ValidationMessage] = []
    errors.extend(_check_profile_references(root, state))
    for section in SECTIONS:
        errors.extend(_check_entries_exist(root, state, section))
        errors.extend(_check_orphans(root, state, section))
    errors.extend(_check_skill_visibility(root, state))
    return tuple(errors)


def _check_profile_references(root: Path, state: MiresState) -> list[ValidationMessage]:
    path = root / "state.yml"
    errors: list[ValidationMessage] = []
    for profile in state.config.profiles:
        for section in SECTIONS:
            known = state.slugs(section.field)
            for slug in profile.using.slugs(section.field):
                if slug not in known:
                    errors.append(
                        ValidationMessage(
                            path,
                            f"profile '{profile.slug}' references unknown {section.field} entry: {slug}",
                        )
                    )
    return errors


def _check_entries_exist(root: Path, state: MiresState, section: SectionSpec) -> list[ValidationMessage]:
    errors: list[ValidationMessage] = []
    for entry in state.entries(section.field):
        target = root / state.entry_path(section.field, entry)
        if section.kind == "file":
            if not target.is_file():
                errors.append(ValidationMessage(target, f"declared {section.field} entry file does not exist"))
            continue
        if not target.is_dir():
            errors.append(ValidationMessage(target, f"declared {section.field} entry directory does not exist"))
            continue
        artifact = target / section.artifact
        if not artifact.is_file():
            errors.append(ValidationMessage(artifact, f"missing required {section.field} artifact"))
            continue
        errors.extend(_check_frontmatter_name(section, entry, artifact))
    return errors


def _check_frontmatter_name(section: SectionSpec, entry: CatalogEntry, artifact: Path) -> list[ValidationMessage]:
    if section.field not in FRONTMATTER_SECTIONS:
        return []
    try:
        frontmatter = read_frontmatter(artifact)
    except FrontMatterError as exc:
        return [ValidationMessage(artifact, str(exc))]
    if frontmatter.get("name") != entry.slug:
        return [ValidationMessage(artifact, f"front matter name must match the declared slug: {entry.slug}")]
    return []


def _check_orphans(root: Path, state: MiresState, section: SectionSpec) -> list[ValidationMessage]:
    directory = root / section.directory
    if not directory.is_dir():
        return []
    declared = {root / state.entry_path(section.field, entry) for entry in state.entries(section.field)}
    errors: list[ValidationMessage] = []
    for candidate in sorted(directory.iterdir()):
        if candidate.name.startswith("."):
            continue
        if section.kind == "file":
            if candidate.is_file() and candidate.suffix == section.artifact and candidate not in declared:
                errors.append(ValidationMessage(candidate, f"undeclared {section.field} entry"))
            continue
        if candidate.is_dir() and candidate not in declared:
            errors.append(ValidationMessage(candidate, f"undeclared {section.field} entry"))
    return errors


def _check_skill_visibility(root: Path, state: MiresState) -> list[ValidationMessage]:
    errors: list[ValidationMessage] = []
    for entry in state.skills:
        skill_dir = root / state.entry_path("skills", entry)
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue
        if entry.visibility == "private":
            errors.extend(_check_private_skill(skill_file))
        else:
            errors.extend(_check_public_skill(skill_dir, entry))
    return errors


def _check_private_skill(skill_file: Path) -> list[ValidationMessage]:
    text = skill_file.read_text()
    return [
        ValidationMessage(skill_file, f"private skill is missing required section: {heading}")
        for heading in PRIVATE_SKILL_SECTIONS
        if heading not in text
    ]


def _check_public_skill(skill_dir: Path, entry: SkillEntry) -> list[ValidationMessage]:
    metadata_path = skill_dir / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        return [ValidationMessage(metadata_path, "public skill is missing runtime metadata")]
    if f"${entry.slug}" not in metadata_path.read_text():
        return [ValidationMessage(metadata_path, f"public skill metadata must invoke ${entry.slug}")]
    return []
