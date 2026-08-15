---
name: endpoints-service-first-crud
description: "Mires service-first DRF CRUD guidance. Use when CRUD create/update/destroy logic needs services, selectors, explicit input/output serializers, and overridden ViewSet actions."
---

# Django Endpoints Service First CRUD

Use this skill when CRUD behavior has branches, side effects, or cross-model rules.

## Rules

- Override the action method or prefer an APIView instead of pushing business writes into serializer hooks.
- Use selectors in `get_queryset()` for read scope and optimization.
- Use an input serializer for validation and an output serializer for the response when they differ.
- Call the service from the action method and return an explicit status code.
- Use `ModelViewSet` only while create, update, and destroy remain straightforward.
