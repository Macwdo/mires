---
name: state-decision-matrix
description: "Mires React state ownership guidance. Use to classify local UI state, validated form state, remote server state, shared client workflow state, and the right tool for each."
---

# React State Decision Matrix

Use this skill before writing React or Next.js feature state.

## Rules

- Use `zod` to validate or parse input and infer types where practical.
- Use `react-hook-form` with `zodResolver` for multi-field validated forms.
- Use `@tanstack/react-query` for remote reads, mutations, cache lifecycle, loading states, and invalidation.
- Use `zustand` for shared client-only UI or workflow state that spans multiple components.
- Use component state for simple local toggles and throwaway inputs.
