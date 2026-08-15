---
name: services-dependencies
description: "Mires Django service dependency guidance. Use for passing external clients, repositories, selectors, tasks, S3/OpenAI clients, and settings-backed collaborators into services explicitly."
---

# Django Services Dependencies

Use this skill when a Django service needs other services, selectors, tasks, repositories, or external clients.

## Rules

- Pass external clients and configurable collaborators as arguments instead of instantiating them deep in the service.
- Call selectors for read-heavy checks or visibility queries instead of duplicating fetch logic.
- Allow services to call model methods, external clients, and async tasks when those are explicit dependencies.
- Keep request and response objects out of services.
- Obtain SDK clients through the project dependency layer at the edge, then pass them into the service.
