---
name: macwdo-typescript-next-form-setup
description: "Macwdo Next.js form setup guidance. Use for a client form example with react-hook-form, zodResolver, schema-first typing, default values, and shadcn form primitives."
---

# Next Form Setup

Use this skill when starter output or a feature needs a validated client form in Next.js.

## Rules

- Create the form in a client component.
- Define the schema with Zod first, then infer the form type from that schema.
- Use `react-hook-form` and `zodResolver` for multi-field validation.
- Use shadcn form primitives and inputs when the project uses shadcn UI.
- Do not add a demo form if the user only asked for project bootstrap and no starter wiring.
