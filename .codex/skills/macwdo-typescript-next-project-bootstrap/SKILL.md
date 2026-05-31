---
name: macwdo-typescript-next-project-bootstrap
description: "Macwdo Next.js project bootstrap guidance. Use to create a new Next app with pnpm, shadcn init, axios, React Hook Form, Zod, resolvers, React Query, and Zustand without manual package edits."
---

# Next Project Bootstrap

Use this skill when the user wants a fresh Next.js codebase with the preferred frontend stack.

## Rules

- Package manager: `pnpm`.
- Bootstrap through `pnpm dlx shadcn@latest init` instead of manually assembling `package.json`.
- Install runtime packages with `pnpm add`; do not edit dependencies by hand.
- Default stack: shadcn/ui, axios, React Hook Form, Zod, `@hookform/resolvers`, TanStack React Query, and Zustand.
- Do not add auth, persistence, state machines, or testing tools unless the user asks.

## Workflow

1. Derive the app name from the request.
2. Run `pnpm dlx shadcn@latest init --name <app-name> --template next --defaults`.
3. Enter the new project directory.
4. Run `pnpm add axios react-hook-form zod @hookform/resolvers @tanstack/react-query zustand`.
5. Add only the minimum starter wiring requested by the task.
