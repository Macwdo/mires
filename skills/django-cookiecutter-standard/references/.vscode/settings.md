# VS Code Settings

## Purpose and when to use it

These optional editor settings align save-time behavior with repository tools.

## Complete canonical artifact

<!-- artifact: .vscode/settings.json; profiles: base -->
```json
{
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["."],
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

## Required tests

Workspace settings must remain optional; command-line checks define correctness.
