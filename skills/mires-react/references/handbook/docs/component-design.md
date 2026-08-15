# Component design

Start with semantic HTML and composition. A component API should express
meaningful variants, not accumulate boolean switches such as `compact`,
`withIcon`, `isCard`, and `isModal`.

Use:

- children composition for layout and content;
- explicit variant names for mutually exclusive presentation;
- compound components when descendants coordinate a shared interaction model;
- a narrow context value containing state and actions, not implementation
  details;
- render props only when a caller must control rendering around reusable
  behavior.

The canonical [Tabs primitive](../src/components/ui/tabs.md) demonstrates a
compound component with keyboard behavior and a narrow provider contract.

Client boundaries belong at the interaction owner. A Server Component can
compose a Client Component; it should not become client-rendered merely because
one descendant is interactive.

Every interactive component documents:

- semantic role and accessible name;
- keyboard behavior;
- focus entry, restoration, and failure behavior;
- disabled and pending behavior;
- responsive constraints;
- reduced-motion behavior.
