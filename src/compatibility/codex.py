from __future__ import annotations

from pathlib import Path
from typing import Any

from compatibility.models import AssetInventory, ValidationMessage


SUPPORTED_TARGET = "codex"


def validate_codex(inventory: AssetInventory) -> tuple[ValidationMessage, ...]:
    errors: list[ValidationMessage] = list(inventory.errors)
    for agent in inventory.agents:
        metadata_path = agent.metadata_path or agent.path.parent / "agents" / "openai.yaml"
        metadata = agent.metadata
        interface = _mapping(metadata.get("interface"))
        runtime_metadata = _mapping(metadata.get("metadata"))

        _require_string(interface, "display_name", metadata_path, errors)
        _require_string(interface, "short_description", metadata_path, errors)
        _require_string(interface, "default_prompt", metadata_path, errors)
        codex_name = _require_string(runtime_metadata, "name", metadata_path, errors)
        if codex_name and codex_name != agent.name:
            errors.append(
                ValidationMessage(
                    metadata_path,
                    f"metadata.name must match agent front matter name: {agent.name}",
                )
            )

        children = runtime_metadata.get("children")
        if children is not None and not (
            isinstance(children, list) and all(isinstance(child, str) for child in children)
        ):
            errors.append(ValidationMessage(metadata_path, "metadata.children must be a list of strings"))

    return tuple(errors)


def check_target_supported(target: str, path: Path) -> tuple[ValidationMessage, ...]:
    if target == SUPPORTED_TARGET:
        return ()
    return (ValidationMessage(path, f"unsupported compatibility target: {target}"),)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _require_string(
    data: dict[str, Any],
    key: str,
    path: Path,
    errors: list[ValidationMessage],
) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    errors.append(ValidationMessage(path, f"missing required Codex metadata field: {key}"))
    return ""

