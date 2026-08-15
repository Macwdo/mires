# Companion Skills

Mires companion skills are optional and independently installable. They provide detailed stack standards while the `mires` skill owns personal preferences and the operating model.

## Django

- Skill: `$mires-django`
- Source package: `Macwdo/mires@mires-django`
- Use for Django, Django REST framework, models, services, selectors, serializers, APIs, migrations, security, testing, deployment, and optional recipes.
- Install globally for Codex:

```bash
bunx skills add Macwdo/mires --skill mires-django -g -a codex -y
```

## React and Next.js

- Skill: `$mires-react`
- Source package: `Macwdo/mires@mires-react`
- Use for React, Next.js App Router, components, state ownership, forms, API contracts, data fetching, accessibility, security, performance, and operations.
- Install globally for Codex:

```bash
bunx skills add Macwdo/mires --skill mires-react -g -a codex -y
```

## Fallback

If a companion skill is not installed:

1. Continue from the target repository's instructions and nearby implementation patterns.
2. Use the runtime's ordinary framework knowledge conservatively.
3. Do not pretend that a Mires companion standard was loaded.

Installing a skill does not register native subagents. Use the Mires repository compatibility installer for the `subagents` layer.
