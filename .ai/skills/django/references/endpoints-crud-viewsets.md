---
name: endpoints-crud-viewsets
description: "Mires DRF CRUD ViewSet guidance. Use for ReadOnlyModelViewSet, GenericViewSet with mixins, create/list/retrieve/update/destroy combinations, and deciding when ModelViewSet is mechanical enough."
---

# Django Endpoints CRUD ViewSets

Use this skill when an endpoint maps to standard resource CRUD or partial CRUD.

## Rules

- Use `ReadOnlyModelViewSet` for router-backed list/retrieve behavior.
- Use `GenericViewSet` plus mixins for create-only, list-only, list-create, or other partial CRUD shapes.
- Use `ModelViewSet` only when CRUD is genuinely mechanical or the app already uses it for that resource.
- Create shared mixin combinations only when partial CRUD repeats across the repo.
- Drop to an APIView when the workflow does not map cleanly to resource CRUD.

## Curated ViewSet Shapes

- `ModelViewSet`
- `ReadOnlyModelViewSet`
- `CreateViewSet`
- `ListViewSet`
- `RetrieveViewSet`
- `UpdateViewSet`
- `DestroyViewSet`
- `ListCreateViewSet`
- `CreateListRetrieveViewSet`
- `RetrieveUpdateDestroyViewSet`
