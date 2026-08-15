# React and Next.js Standards Handbook

This repository is a Markdown-only, executable reference for production React
and Next.js applications. Markdown is the canonical source. Complete artifacts
inside fenced blocks can be reconstructed into disposable projects for
verification or study.

This is a standards handbook, not a product template or a project generator.
Read the guidance, select the patterns that fit the problem, and keep
application-specific decisions in the application.

## Profiles

| Profile    | Adds to the shared foundation                                                                |
| ---------- | -------------------------------------------------------------------------------------------- |
| `base`     | App Router, strict TypeScript, environment boundaries, accessible UI                         |
| `forms`    | React Hook Form, Zod validation, pending/success/server-error states                         |
| `data`     | Typed API client, TanStack Query, filters, pagination, mutations                             |
| `auth`     | Server-managed sessions, protected routes, safe redirects, CSRF checks                       |
| `realtime` | Deterministic SSE and WebSocket lifecycle patterns                                           |
| `full`     | A compatible combination of all executable recipes                                           |

## Start here

1. Read [the architecture rules](docs/architecture.md).
2. Use [the source map](source-map.md) to locate an artifact.
3. Read [the reconstruction protocol](docs/reconstruction.md).
4. Review [the exact dependency snapshot](docs/version-snapshot.md).

Bootstrap the Node.js reconstructor from `docs/reconstruction.md`, then run:

```text
reconstruct --profile base --output /tmp/react-next-base
reconstruct --profile full --output /tmp/react-next-full
```

The output directory must already exist, be empty, be absolute, be outside this
repository, and contain no symbolic-link path components.

## Canonical-source contract

- Every tracked file ends in `.md`.
- An artifact marker is immediately followed by one complete named fence.
- Canonical code contains no omitted sections, placeholder ellipses, or
  pseudocode.
- Reconstructed output is disposable and must never be committed here.
- The validator rejects malformed markers, unsafe paths, conflicts, broken
  relative links, missing source-map ownership, and non-Markdown tracked files.

See [maintainer-instructions.md](maintainer-instructions.md) before changing the handbook.
