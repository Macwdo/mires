---
name: macwdo-python-django-services-flow-services
description: "Macwdo Django flow-service guidance. Use when a multi-step service needs a small class namespace or shared dependencies, while ordinary mutations remain plain service functions."
---

# Django Services Flow Services

Use this skill when service behavior spans a multi-step workflow or shared dependencies.

## Rules

- Use plain functions for most mutations.
- Use a class only when the service represents a multi-step flow or needs a small namespace around shared dependencies.
- If the existing app already uses a `services/` package or class-based flow services, follow that local shape.
- Keep each method explicit, typed, and transaction-aware.
- Do not turn ordinary create/update/delete behavior into a class just for organization.

## Example

```python
class ExampleExportService:
    def __init__(self, *, account) -> None:
        self.account = account

    @transaction.atomic
    def start(self, *, name: str) -> ExampleExport:
        export = ExampleExport(account=self.account, name=name, status="pending")
        export.full_clean()
        export.save()
        return export
```
