---
name: review
description: Review rules for correctness, risk, performance, security, maintainability, and missing tests.
---

# Review

## When To Use

Use for review-only work, PR review, architecture review, or implementation risk assessment.

## Core Rules

- Lead with findings ordered by severity.
- Prioritize correctness, behavioral regressions, security, performance, maintainability, dead code, and missing tests.
- Load only the framework or stack references that apply to the reviewed code.

## Preferred Patterns

- File-referenced findings.
- Concrete risk statements.
- Focused test gap callouts.

## Anti-Patterns

- Style-only comments that ignore real risk.
- Broad speculative criticism without evidence.
- Silent assumptions about external behavior that should be verified.

## Checklist

- Identify the changed boundary.
- Load only the matching review references.
- Report findings first.
- Note missing tests or validation gaps.

## References Index

- `references/backend-review-checklist.md`
