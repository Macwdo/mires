---
name: testing
description: Testing rules for classifying coverage, reusing fixtures, adding regression tests, and validating changed behavior.
---

# Testing

## When To Use

Use for unit, integration, and end-to-end testing strategy, fixture usage, regression planning, and execution guidance.

## Core Rules

- Classify the required coverage level before writing or running tests.
- Reuse existing fixtures and helpers.
- Prefer regression tests that cover the changed behavior directly.
- Match local naming, directory, and command conventions.

## Preferred Patterns

- Small targeted tests close to the affected behavior.
- Existing fixture and helper composition.
- Clear test setup and assertion flow.
- Explicit regression coverage for bugs.

## Anti-Patterns

- Adding test infrastructure that duplicates the repo's current pattern.
- Broad integration coverage when a focused unit test would catch the regression.
- Changing production code just to make a test strategy fit.

## Checklist

- Decide whether the change needs unit, integration, or end-to-end coverage.
- Reuse existing fixtures and helpers when possible.
- Add or run regression coverage for the changed behavior.
- Report residual risk when full validation was not possible.

## References Index
