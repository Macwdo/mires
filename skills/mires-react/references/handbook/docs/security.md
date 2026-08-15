# Security

## Boundary rules

- Keep credentials and provider tokens in server-only modules.
- Never expose a secret through `NEXT_PUBLIC_*`.
- Validate external data and redirect destinations.
- Re-authorize protected reads and every mutation on the server.
- Use `HttpOnly`, `Secure`, scoped, same-site cookies for sessions.
- Protect cookie-authenticated mutations against CSRF.
- Escape user content through React; avoid arbitrary HTML.
- Restrict upload size, type, count, extension, and storage destination.
- Keep logs free of credentials, tokens, cookies, message bodies, and sensitive
  user content.

## Browser policy

Deploy a validated Content Security Policy. Start in report-only mode when adding
it to an established product, remove unsafe inline execution, and scope
`connect-src`, `img-src`, and `frame-ancestors` to actual needs. Also set
`nosniff`, a restrictive referrer policy, permissions policy, HSTS at the TLS
edge, and clickjacking protection through CSP.

## Operations

Run dependency auditing and license review in CI, apply security updates
promptly, rotate credentials through the deployment platform, and retain only
the minimum telemetry needed for operations.

See [authentication](../recipes/authentication.md),
[uploads](../recipes/file-uploads.md), and [operations](operations.md).
