# Conventions

- Use English for public identifiers, documentation, and error contracts in
  this handbook.
- Name components and types with `PascalCase`; functions, variables, and files
  with descriptive lowercase names.
- Prefer named exports in shared modules and default exports only where Next.js
  file conventions require them.
- Keep route files thin: parse input, authorize, invoke feature behavior, and
  shape the response.
- Represent finite UI states explicitly. Do not infer an error from missing
  data or show an empty state while a request is still pending.
- Validate unknown values before narrowing their type.
- Treat comments as rationale, not a narration of syntax.
- Do not suppress TypeScript or lint rules to bypass an unclear contract.
- Use `button` for actions and links for navigation.
- Use `AbortSignal` for cancellable work and return cleanup from effects.
- Name transitions explicitly; never use `transition: all`.
