# Version Snapshot

The canonical pins were checked against current stable package indexes on 2026-07-26.

| Component | Version | Scope |
| --- | ---: | --- |
| Python | 3.14.6 | all profiles |
| Django | 6.0.7 | all profiles |
| Django REST framework | 3.17.1 | all profiles |
| Simple JWT | 5.5.1 | all profiles |
| django-filter | 26.1 | all profiles |
| psycopg | 3.3.4 | PostgreSQL |
| Ruff | 0.16.0 | development |
| ty | 0.0.63 | development |
| pytest | 9.1.1 | development |
| pre-commit | 4.6.1 | development |
| HTTPX | 0.28.1 | tasks and optional AI tests |
| Celery | 5.6.3 | tasks |
| Channels | 4.3.2 | realtime |
| Daphne | 4.2.3 | realtime |
| pgvector | 0.5.0 | vector |
| OpenAI Python | 2.48.0 | optional AI |
| Deep Agents | 0.6.12 | optional multi-step AI |
| LangChain OpenAI | 1.4.1 | Deep Agents OpenAI model adapter |
| websockets | 15.0.1 | realtime test compatibility |

Prereleases are excluded. A version bump must update `pyproject.md`, `uv-lock.md`, compatibility notes, and reconstructed verification together.

The handbook target is Python 3.14.6. At verification time, the available managed interpreter and official container patch were 3.14.4, so executable checks and the container artifact use 3.14.4 within the declared `>=3.14,<3.15` compatibility range. Advance the container pin to 3.14.6 after that official image is published and repeat every gate.
