from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from mires.messages import ValidationMessage
from mires.state.models import MiresState

STATE_FILE = "state.yml"


class StateFileError(Exception):
    """Raised when state.yml cannot be read or does not satisfy the schema."""

    def __init__(self, path: Path, messages: tuple[ValidationMessage, ...]) -> None:
        super().__init__(f"invalid {path}")
        self.path = path
        self.messages = messages


def state_path(root: Path) -> Path:
    return root / STATE_FILE


def load_state(root: Path) -> MiresState:
    path = state_path(root)
    if not path.exists():
        raise StateFileError(path, (ValidationMessage(path, "missing state definition"),))

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise StateFileError(path, (ValidationMessage(path, f"invalid YAML: {exc}"),)) from exc

    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise StateFileError(path, (ValidationMessage(path, "state definition must be a mapping"),))

    try:
        return MiresState.model_validate(raw)
    except ValidationError as exc:
        raise StateFileError(path, _schema_messages(path, exc)) from exc


def _schema_messages(path: Path, error: ValidationError) -> tuple[ValidationMessage, ...]:
    messages = []
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"]) or "<root>"
        messages.append(ValidationMessage(path, f"{location}: {detail['msg']}"))
    return tuple(messages)
