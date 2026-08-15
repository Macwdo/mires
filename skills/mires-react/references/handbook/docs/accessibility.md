# Accessibility

Accessibility is a release criterion, not a later audit.

- Prefer native elements and landmarks before ARIA.
- Preserve a logical heading hierarchy and one clear page heading.
- Make all actions keyboard reachable with visible focus.
- Implement documented keyboard models for composite widgets.
- Move or restore focus after dialogs, route failures, and destructive
  confirmations.
- Associate validation errors with their controls.
- Announce async outcomes with restrained live regions.
- Keep touch targets at least 44 CSS pixels where practical.
- Do not encode meaning with color alone.
- Verify at narrow and wide viewports, zoomed text, high contrast, and reduced
  motion.

Animations must communicate continuity or feedback. Prefer transform and
opacity, name transitioned properties, and remove nonessential movement under
`prefers-reduced-motion`.

The [Tabs primitive](../src/components/ui/tabs.md) is an executable example.
