---
name: celery
description: Celery task, worker, queue, and worker-testing guidance for repositories that already use Celery-style job processing.
---

# Celery

## When To Use

Use when the change touches background tasks, workers, retries, queue routing, or Celery-backed testing.

## Core Rules

- Keep business logic out of task wrappers.
- Reuse the existing worker app and broker setup.
- Pass small serializable task payloads.

## Preferred Patterns

- Thin task wrappers around service functions.
- Explicit queue and retry behavior.
- Focused worker tests when background execution matters.

## Anti-Patterns

- Hiding core logic in task functions.
- Creating a second Celery app without local precedent.
- Passing request-scoped or framework objects into tasks.

## Checklist

- Confirm the current worker app and broker pattern.
- Confirm where task registration lives.
- Validate enqueue and worker execution paths that changed.

## References Index

- `references/celery-app-setup.md`
- `references/celery-testing.md`
- `references/celery-live-worker-testing.md`
