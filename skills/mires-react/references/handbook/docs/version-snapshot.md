# Version snapshot

Verified on 2026-07-26 against the npm registry and official React and Next.js
documentation.

| Package                      |    Version |
| ---------------------------- | ---------: |
| Node.js                      | `>=20.9.0` |
| pnpm                         |  `11.17.0` |
| Next.js / eslint-config-next |  `16.2.12` |
| React / React DOM            |   `19.2.8` |
| TypeScript                   |    `6.0.3` |
| ESLint                       |   `9.39.5` |
| Prettier                     |    `3.9.6` |
| Zod                          |    `4.4.3` |
| React Hook Form              |   `7.83.0` |
| TanStack Query               |  `5.101.4` |

The registry also published TypeScript `7.0.2` and ESLint `10.8.0` on the
verification date. They are not used because the stable lint plugins in
`eslint-config-next@16.2.12` declare TypeScript `<6.1.0` and ESLint `^9` peer
ranges. This snapshot selects the newest stable compatible releases and records
that decision instead of bypassing peer contracts.

Re-verify the complete graph, peer ranges, release notes, and lockfile before
updating any version. Never substitute a prerelease silently.
