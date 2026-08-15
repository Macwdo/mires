# React

React patterns for state ownership, forms, hooks, server state, and anti-pattern checks.

## When To Use

Use for React component structure, state ownership, forms, hooks, server state, client state, and React-focused review.

## Core Rules

- Inspect the existing component and state ownership patterns first.
- Keep fetched data, form state, and local UI state separated.
- Load only the React references relevant to the touched component.

## Preferred Patterns

- Focused components with explicit props and boundaries.
- Clear state ownership.
- Validation and form composition that match nearby code.

## Anti-Patterns

- Duplicating server data in unrelated client state.
- Ad hoc multi-field state for non-trivial forms when the repo has a better pattern.
- Loading every React reference for a small change.

## Checklist

- Identify the state ownership problem first.
- Check existing form and server-state patterns.
- Validate the specific interaction that changed.

## References Index

- `references/react/explorer.md`
- `references/react/state-decision-matrix.md`
- `references/react/server-state.md`
- `references/react/client-state.md`
- `references/react/forms.md`
- `references/react/anti-patterns.md`
