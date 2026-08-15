# Operations

A production release needs observable, reversible behavior.

- Build from the frozen lockfile.
- Run format, lint, typecheck, and a production build before promotion.
- Inject environment values at deployment; do not bake secrets into images or
  browser bundles.
- Expose health and readiness at the platform boundary without leaking config.
- Use structured logs with request identifiers and redaction.
- Record errors and latency, not sensitive payloads.
- Roll out risky behavior behind server-evaluated flags with an owner and
  removal date.
- Keep a rollback artifact and document database or API compatibility.
- Audit dependencies and generated software bills of materials.

See [deployment](../recipes/deployment.md) and
[observability](../recipes/analytics-observability.md).
