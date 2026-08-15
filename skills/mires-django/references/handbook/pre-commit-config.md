# pre-commit Configuration

## Purpose and when to use it

Use pre-commit as a fast local gate; CI remains authoritative.

## Complete canonical artifact

<!-- artifact: .pre-commit-config.yaml; profiles: base -->
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.0
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

## Alternatives and trade-offs

Auto-fixes are useful locally; CI runs read-only checks.

## Required tests

Run `pre-commit run --all-files` in a reconstructed project.
