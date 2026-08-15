# API contracts

TypeScript types disappear at runtime. Treat response bodies, request bodies,
headers, cookies, URL parameters, `postMessage` payloads, and realtime events as
unknown until a runtime schema validates them.

At an HTTP boundary:

1. apply a timeout or cancellation signal where the caller owns cancellation;
2. check the status before parsing a success schema;
3. parse JSON into `unknown`;
4. validate with a Zod schema;
5. map infrastructure errors to a stable feature error;
6. log only safe metadata.

Do not export an upstream vendor response throughout the application. Convert
it at the boundary into the smallest internal contract the feature needs.

The canonical [API client](../recipes/data.md) distinguishes transport failure
from contract failure.
