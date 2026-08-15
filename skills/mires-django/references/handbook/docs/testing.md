# Testing and Acceptance

## Repository validation

The Markdown validator must establish:

- every tracked path ends in `.md`;
- all 91 original paths appear exactly once in `source-map.md`;
- artifact paths are safe and markers have complete fenced blocks;
- artifact/profile pairs are unique;
- relative Markdown links resolve;
- forbidden secrets, generator commands, product-specific terms, unresolved placeholders, and incomplete canonical code are absent.

## Reconstruction matrix

Materialize `base`, `tasks`, `storage`, `realtime`, `vector-ai`, and `full` into fresh directories under `/tmp`.

For `base` and `full`, run:

```text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run python src/manage.py makemigrations
uv run coverage run -m pytest
uv run coverage report --fail-under=90
uv run python src/manage.py check
uv run python src/manage.py check --deploy
uv run python src/manage.py makemigrations --check --dry-run
docker compose config
```

The plain apps ship no migration artifacts; see
[migration generation](reconstruction.md#migration-generation). Run
`makemigrations` once before the drift check so it verifies the generated
migrations match the models, not that migrations are missing entirely.

Integration tests use PostgreSQL/pgvector, Redis, and MinIO. They cover JWT rotation/revocation, account isolation, direct CRUD, service and selector paths, task retries/idempotency, upload validation, vector isolation, ordered SSE with heartbeats and cancellation, WebSocket auth/origin/groups/reconnect, and a Daphne smoke test.

Test throttling only when an application's abuse model gives it a concrete
acceptance contract. Do not include generic tests that merely restate DRF's
throttling behavior or the settings dictionary.

OpenAI tests are deterministic mocks covering streaming text, refusal, rate
limiting, and provider failure. Test tool authorization, delegation,
persistence isolation, interrupts, and recovery through application behavior
when those capabilities are enabled. A real API key is neither required nor
used.

## Test structure

Every test follows Arrange, Act, Assert in that order and labels the three
sections when the phases are not self-evident. Keep assertions after all actions
under test. Treat `pytest.raises` as an assertion: establish fixtures and inputs
first, then place the raising call inside the final Assert section. Split a test
when independent scenarios would require interleaving actions and assertions.

## Final gate

Run `git diff --check`, inspect `git status --short`, and repeat the tracked Markdown-only invariant.
