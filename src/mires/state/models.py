from __future__ import annotations

from typing import Annotated, Any, Literal, NamedTuple

from pydantic import BaseModel, ConfigDict, Field, model_validator

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"

Slug = Annotated[str, Field(pattern=SLUG_PATTERN, max_length=64)]
Text = Annotated[str, Field(min_length=1)]


class SectionSpec(NamedTuple):
    """Where a catalog section lives on disk and which artifact proves an entry exists."""

    field: str
    directory: str
    kind: Literal["dir", "file"]
    artifact: str


SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec("mcps", "mcps", "dir", "mcp.json"),
    SectionSpec("skills", "skills", "dir", "SKILL.md"),
    SectionSpec("subagents", "subagents", "dir", "AGENT.md"),
    SectionSpec("rules", "rules", "file", ".md"),
    SectionSpec("hooks", "hooks", "dir", "hooks.json"),
)

SECTIONS_BY_FIELD = {section.field: section for section in SECTIONS}

PRIVATE_SKILL_SECTIONS = (
    "## When To Use",
    "## Core Rules",
    "## Preferred Patterns",
    "## Anti-Patterns",
    "## Checklist",
    "## References Index",
)


class StateModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CatalogEntry(StateModel):
    name: Text
    slug: Slug
    description: Text
    path: str | None = None
    config: dict[str, Any] | None = None


class McpEntry(CatalogEntry):
    pass


class SkillEntry(CatalogEntry):
    visibility: Literal["public", "private"] = "private"


class SubagentEntry(CatalogEntry):
    pass


class RuleEntry(CatalogEntry):
    pass


class HookEntry(CatalogEntry):
    pass


class ProfileUsing(StateModel):
    mcps: list[Slug] = []
    skills: list[Slug] = []
    subagents: list[Slug] = []
    rules: list[Slug] = []
    hooks: list[Slug] = []

    @model_validator(mode="before")
    @classmethod
    def _accept_sequence_form(cls, value: Any) -> Any:
        """Allow `using:` to be written as a list of mappings as well as a single mapping."""
        if not isinstance(value, list):
            return value
        merged: dict[str, list[Any]] = {}
        for item in value:
            if not isinstance(item, dict):
                raise ValueError("every `using` list item must be a mapping of section to slugs")
            for key, slugs in item.items():
                merged.setdefault(key, []).extend(slugs or [])
        return merged

    def slugs(self, field: str) -> list[str]:
        return getattr(self, field)


class Profile(StateModel):
    name: Text
    slug: Slug
    description: Text
    using: ProfileUsing = ProfileUsing()


class Config(StateModel):
    profiles: list[Profile] = []


class MiresState(StateModel):
    version: int = 1
    config: Config = Config()
    mcps: list[McpEntry] = []
    skills: list[SkillEntry] = []
    subagents: list[SubagentEntry] = []
    rules: list[RuleEntry] = []
    hooks: list[HookEntry] = []

    @model_validator(mode="after")
    def _reject_duplicate_slugs(self) -> MiresState:
        for section in SECTIONS:
            _reject_duplicates(self.entries(section.field), f"{section.field} slug")
        _reject_duplicates(self.config.profiles, "profile slug")
        return self

    def entries(self, field: str) -> list[CatalogEntry]:
        return getattr(self, field)

    def slugs(self, field: str) -> set[str]:
        return {entry.slug for entry in self.entries(field)}

    def profile(self, slug: str) -> Profile | None:
        return next((profile for profile in self.config.profiles if profile.slug == slug), None)

    def profile_slugs(self) -> list[str]:
        return [profile.slug for profile in self.config.profiles]

    def entry_path(self, field: str, entry: CatalogEntry) -> str:
        """Relative path of an entry, defaulting to the section layout when `path` is omitted."""
        if entry.path:
            return entry.path
        section = SECTIONS_BY_FIELD[field]
        if section.kind == "file":
            return f"{section.directory}/{entry.slug}{section.artifact}"
        return f"{section.directory}/{entry.slug}"


def _reject_duplicates(items: list[Any], label: str) -> None:
    seen: set[str] = set()
    for item in items:
        if item.slug in seen:
            raise ValueError(f"duplicate {label}: {item.slug}")
        seen.add(item.slug)
