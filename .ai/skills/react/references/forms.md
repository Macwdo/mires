---
name: forms
description: "Mires React form guidance. Use for zod-first contracts, zodResolver, react-hook-form, inferred form values, default values, shadcn form composition, and avoiding ad hoc multi-field useState forms."
---

# React Forms

Use this skill when a React feature has non-trivial form validation.

## Rules

- Define the `zod` schema first when the feature needs validation, parsing, or a reusable client-side contract.
- Infer TypeScript types from schemas instead of duplicating types by hand.
- Use `react-hook-form` with `zodResolver` for multi-field validated forms.
- Keep simple one-field or throwaway inputs in local component state when form tooling would be unnecessary overhead.
- Use shadcn form primitives when the project uses shadcn UI.

## Example

```tsx
const profileSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
})

type ProfileFormValues = z.infer<typeof profileSchema>

const form = useForm<ProfileFormValues>({
  resolver: zodResolver(profileSchema),
  defaultValues: { name: "", email: "" },
})
```
