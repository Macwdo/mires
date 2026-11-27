# Reproducible Dependency Locks

## Purpose and when to use it

`uv.lock` is generated **after** reconstruction, not carried as a canonical
artifact in this handbook. With modules freely composable (see
[reconstruction](docs/reconstruction.md)), the number of possible module
combinations is combinatorially large; pre-baking a lock for each one, the
way this file once pre-baked six — one per legacy flat profile — does not
scale to fine-grained modules. This follows the same precedent already
established for migrations: [migration
generation](docs/reconstruction.md#migration-generation) regenerates
derivable migrations post-reconstruction instead of carrying them as
artifacts, and [dependency lock
generation](docs/reconstruction.md#dependency-lock-generation) does the same
for `uv.lock`.

## When not to use it

Do not hand-edit a lock or reuse one after changing the resolved module set
— run `uv lock` again.

## Responsibilities and invariants

After materializing a project (and running `makemigrations` for any plain
recipe app included), run:

```bash
uv lock
```

once, from the materialized project root. Commit the resulting `uv.lock`
in the derived project alongside the generated migrations. The lock
includes hashes and transitive metadata for exactly the dependencies the
resolved module set's `pyproject.toml` declares (see [project
configuration](pyproject.md)). The 2026-07-26 dependency snapshot targets
Python 3.14.6; lock resolution was also checked on the available Python
3.14 line.

## Alternatives and trade-offs

Pre-baked, per-profile locks (this file's approach before modules became
composable) let every combination ship a reviewable, hash-pinned lock
without running `uv lock` at all — but only because there were exactly six
combinations to pre-bake. A composable module graph trades that
zero-step convenience for scalability: one `uv lock` invocation handles any
of the arbitrarily many resolvable module sets.

## Required tests

Materialize at least `base` and one non-alias module combination, run
`uv lock` in each, and confirm `uv sync --frozen` succeeds against the
result.

## Related standards

See [project configuration](pyproject.md), [reconstruction](docs/reconstruction.md),
and [version snapshot](docs/version-snapshot.md).
