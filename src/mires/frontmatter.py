from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

FENCE = "---"


class FrontMatterError(ValueError):
    pass


def read_frontmatter(path: Path) -> dict[str, Any]:
    return parse_frontmatter(path.read_text())


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith(f"{FENCE}\n"):
        raise FrontMatterError("missing YAML front matter")
    end = text.find(f"\n{FENCE}", len(FENCE) + 1)
    if end == -1:
        raise FrontMatterError("unterminated YAML front matter")
    return parse_yaml_mapping(text[len(FENCE) + 1 : end])


def read_yaml_mapping(path: Path) -> dict[str, Any]:
    return parse_yaml_mapping(path.read_text())


def parse_yaml_mapping(text: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise FrontMatterError(f"invalid YAML: {exc}") from exc
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FrontMatterError("expected a YAML mapping")
    return value
