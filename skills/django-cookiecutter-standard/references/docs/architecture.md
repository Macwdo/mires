# Architecture

## Purpose and when to use it

Use this standard for JSON Django backends that benefit from Django's ORM, admin, migrations, authentication, and DRF.

## When not to use it

Do not adopt Django for a tiny stateless function, a primarily server-rendered application covered by another standard, or a workload whose dominant constraint requires a different runtime.

## Responsibilities and invariants

The base project has `core` for process configuration and `apps` for application behavior. `authentication` owns the email user, `account` owns tenancy, `customer` demonstrates CRUD, `api` owns HTTP-wide policy, and `common` holds genuinely shared Django primitives.

Simple CRUD stays in models, serializers, and ViewSets. A service is justified by a transaction, multiple writes, or an external effect. A selector is justified by a reusable complex read. Neither hides the ORM. Repository and use-case layers are deliberately excluded.

Account isolation is structural: every tenant-owned model inherits `AccountOwnedModel`, and every endpoint scopes its queryset before object lookup. Base tenancy is one Account per User. Advanced membership and account selection are optional recipes.

## Alternatives and trade-offs

A single settings package, split by concern rather than by environment, avoids drift among environment-specific settings files, at the cost of explicit environment parsing and fail-fast production validation. Cursor pagination provides stable traversal but does not expose arbitrary page numbers.

## Required tests

Test models, direct CRUD, services, selectors, permissions, tenant isolation, migrations, and configuration checks independently.

## Related standards

See [conventions](conventions.md), [API design](api-design.md), [view patterns](view-patterns.md), and the [base reference tree](../src/README.md).
