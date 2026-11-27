# VS Code Launch Configuration

## Purpose and when to use it

Use this optional configuration to debug Django locally through the reconstructed virtual environment.

## Complete canonical artifact

<!-- artifact: .vscode/launch.json; profiles: base -->
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django API",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/src/manage.py",
      "args": ["runserver", "0.0.0.0:8000"],
      "django": true,
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

## Required tests

Debug configuration must not contain credentials or override production flags.
