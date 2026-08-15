# Forms

Prefer native form semantics and Server Actions for small server-owned
mutations. Use React Hook Form for forms with substantial client interaction,
conditional fields, or targeted validation behavior.

Requirements:

- a visible label for every control;
- `aria-invalid` and an associated error description;
- client validation for fast feedback and server validation for authority;
- a disabled pending submission control;
- explicit success, field-error, form-error, and network-error states;
- preservation of user input after a recoverable failure;
- focus movement only when it helps recovery.

Never trust hidden fields for authorization, ownership, price, role, or
entitlement. See the executable [forms recipe](../recipes/forms.md).
