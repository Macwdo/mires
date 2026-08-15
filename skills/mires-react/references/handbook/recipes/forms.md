# Forms recipe

Use React Hook Form when a form is interaction-heavy enough to benefit from
field registration and targeted updates. Zod remains the shared runtime
contract. Server validation is authoritative; client validation improves
feedback speed. Errors are associated with fields, pending disables duplicate
submissions, and success is announced.

<!-- artifact: src/features/forms/model.ts; profiles: forms,full -->
```ts
import { z } from "zod";

export const contactSchema = z.object({
  name: z.string().trim().min(2, "Enter at least two characters."),
  email: z.email("Enter a valid email address."),
});

export type ContactInput = z.infer<typeof contactSchema>;

export type ContactResponse =
  | { ok: true; message: string }
  | { ok: false; message: string; fieldErrors?: Partial<Record<keyof ContactInput, string>> };
```

<!-- artifact: src/features/forms/contact-form.tsx; profiles: forms,full -->
```tsx
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";

import { contactSchema, type ContactInput, type ContactResponse } from "@/features/forms/model";

async function submitContact(input: ContactInput): Promise<ContactResponse> {
  const response = await fetch("/api/contact", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const body = (await response.json()) as ContactResponse;
  return body;
}

export function ContactForm() {
  const {
    formState: { errors, isSubmitting },
    handleSubmit,
    register,
    reset,
    setError,
  } = useForm<ContactInput>({ defaultValues: { name: "", email: "" } });
  const [status, setStatus] = useState<string | null>(null);

  const onSubmit = handleSubmit(async (values) => {
    setStatus(null);
    const parsed = contactSchema.safeParse(values);
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        const field = issue.path[0];
        if (field === "name" || field === "email") {
          setError(field, { message: issue.message });
        }
      }
      return;
    }

    try {
      const result = await submitContact(parsed.data);
      if (!result.ok) {
        for (const [field, message] of Object.entries(result.fieldErrors ?? {})) {
          if ((field === "name" || field === "email") && message) {
            setError(field, { message });
          }
        }
        setStatus(result.message);
        return;
      }
      reset();
      setStatus(result.message);
    } catch {
      setStatus("The form could not be submitted. Try again.");
    }
  });

  return (
    <form className="stack" noValidate onSubmit={onSubmit}>
      <div className="field">
        <label htmlFor="contact-name">Name</label>
        <input
          id="contact-name"
          autoComplete="name"
          aria-describedby={errors.name ? "contact-name-error" : undefined}
          aria-invalid={Boolean(errors.name)}
          {...register("name")}
        />
        {errors.name ? (
          <span id="contact-name-error" className="error">
            {errors.name.message}
          </span>
        ) : null}
      </div>

      <div className="field">
        <label htmlFor="contact-email">Email</label>
        <input
          id="contact-email"
          type="email"
          inputMode="email"
          autoComplete="email"
          aria-describedby={errors.email ? "contact-email-error" : undefined}
          aria-invalid={Boolean(errors.email)}
          {...register("email")}
        />
        {errors.email ? (
          <span id="contact-email-error" className="error">
            {errors.email.message}
          </span>
        ) : null}
      </div>

      <button className="button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Sending…" : "Send"}
      </button>
      {status ? (
        <p className="notice" role="status">
          {status}
        </p>
      ) : null}
    </form>
  );
}
```

<!-- artifact: src/app/api/contact/route.ts; profiles: forms,full -->
```ts
import { NextResponse } from "next/server";

import { contactSchema, type ContactResponse } from "@/features/forms/model";

export async function POST(request: Request) {
  const body: unknown = await request.json().catch(() => null);
  const parsed = contactSchema.safeParse(body);

  if (!parsed.success) {
    const fieldErrors = parsed.error.flatten().fieldErrors;
    return NextResponse.json<ContactResponse>(
      {
        ok: false,
        message: "Review the highlighted fields.",
        fieldErrors: {
          name: fieldErrors.name?.[0],
          email: fieldErrors.email?.[0],
        },
      },
      { status: 400 },
    );
  }

  if (parsed.data.email === "server-error@example.test") {
    return NextResponse.json<ContactResponse>(
      { ok: false, message: "The service rejected this deterministic example." },
      { status: 422 },
    );
  }

  return NextResponse.json<ContactResponse>(
    { ok: true, message: "Your message was received." },
    { status: 201 },
  );
}
```

<!-- artifact: src/app/forms/page.tsx; profiles: forms,full -->
```tsx
import type { Metadata } from "next";

import { ContactForm } from "@/features/forms/contact-form";

export const metadata: Metadata = { title: "Accessible form" };

export default function FormsPage() {
  return (
    <main id="main" className="shell">
      <h1>Accessible form</h1>
      <ContactForm />
    </main>
  );
}
```
