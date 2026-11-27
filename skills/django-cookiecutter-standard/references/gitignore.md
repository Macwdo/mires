# Generated Project Ignore Rules

## Purpose and when to use it

This artifact keeps reconstructed local state out of version control.

## Complete canonical artifact

<!-- artifact: .gitignore; profiles: base -->
```gitignore
.env
.env.*
!.env.example
.venv/
__pycache__/
*.py[cod]
*.sqlite3
.coverage
coverage.xml
htmlcov/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.ty/
.data/
media/
staticfiles/
dist/
build/
*.egg-info/
.DS_Store
.idea/
.vscode/
```

## Responsibilities and invariants

The example environment file remains trackable. Migrations and `uv.lock` must never be ignored.

## Required tests

Inspect `git status` after local setup and test execution.
