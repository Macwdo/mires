# View Patterns

## Purpose and when to use it

Django itself is never optional — there is no `django-views`,
`django-viewsets`, or `django-modelviewsets` module in
[reconstruction](reconstruction.md)'s module graph. This standard instead
documents the three view-layer shapes already used across this handbook, so
the choice between them is explicit and discoverable rather than implicit
per app.

## When not to use it

Do not reach for a heavier shape than the endpoint needs — see the decision
guide below before adding a `ModelViewSet` for a single custom action, or an
`APIView` for conventional CRUD that a `ModelViewSet` already gives you for
free.

## Responsibilities and invariants

Three shapes cover every endpoint in this handbook:

- **`ModelViewSet`** (full CRUD): [`AccountScopedViewSet`](../src/apps/api/views.md),
  the tenant-scoping base every full-CRUD resource inherits, subclasses
  `rest_framework.viewsets.ModelViewSet` directly. Use it when a resource
  needs list, retrieve, create, update, and destroy with no behavior beyond
  serializer and model operations plus account scoping — see
  [`CustomerViewSet`](../src/apps/customer/views.md), which only overrides
  `perform_create` to attach the trusted account.
- **`GenericViewSet` + mixins** (partial CRUD): use when a resource exposes
  only some of the standard actions. [`JobViewSet`](../recipes/celery/celery-postgres-results.md)
  combines `RetrieveModelMixin` with `GenericViewSet` because jobs are
  created by a service call from another endpoint, not by a client `POST`
  directly to the jobs resource — list/create/update/destroy would be
  meaningless there.
- **Plain `APIView`**: use for an endpoint that is not resource CRUD at all
  — a workflow step, a custom action shape, or a streaming response.
  [`StartUploadView`/`CompleteUploadView`/`DeleteFileView`](../recipes/storage/storage-django.md)
  each model one step of a presigned-upload workflow, not a `StoredFile`
  CRUD resource. [`EventStreamView`](../recipes/sse.md) and
  [`ChatStartAPIView`](../recipes/chat.md) use `APIView` because a
  `StreamingHttpResponse` and an async streaming body have no ViewSet
  action to map onto.

Every shape scopes its queryset (or, for plain `APIView`, its service call)
to the requesting account before any lookup — see
[architecture](architecture.md)'s account-isolation invariant. No shape
hides the ORM: a service is justified by a transaction, multiple writes, or
an external effect, not by the choice of view class (see
[conventions](conventions.md)).

## Alternatives and trade-offs

A hand-written `APIView` offers full control but repeats list, detail,
validation, and status-code behavior that ViewSets already make consistent
— reserve it for endpoints that genuinely are not resource CRUD.
`GenericViewSet` with explicit mixins costs one extra line per action
compared to `ModelViewSet`'s implicit "all five," in exchange for a
resource that cannot accidentally expose an action it never intended to
support.

## Required tests

For a `ModelViewSet` or `GenericViewSet` resource, exercise every action it
exposes and confirm objects from another account are unreachable (404) for
retrieve, update, and destroy. For a plain `APIView`, test its specific
contract directly — there is no shared action matrix to inherit coverage
from.

## Related standards

See [architecture](architecture.md), [conventions](conventions.md),
[API design](api-design.md), [the account-scoped view base](../src/apps/api/views.md),
and [testing](testing.md).
