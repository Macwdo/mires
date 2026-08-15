# Design-system integration

A design system is a contract among tokens, primitives, accessibility behavior,
documentation, and release policy. Integrate it at `src/components/ui`; domain
features may compose those primitives but shared primitives never import a
feature.

Prefer:

- semantic variants such as `primary`, `danger`, and `quiet`;
- CSS custom properties for stable semantic tokens;
- compound APIs for coordinated components;
- platform behavior before custom scripting;
- local wrappers only when they add a real product contract.

Do not wrap every third-party component preemptively. Preserve ref forwarding,
accessible names, keyboard behavior, focus restoration, and disabled semantics
when a wrapper is justified. The canonical
[compound Tabs primitive](../src/components/ui/tabs.md) is the executable
reference.
