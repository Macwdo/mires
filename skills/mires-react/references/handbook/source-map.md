# Canonical source map

Each reconstructed target has one owning handbook document. Profiles are listed
as a comma-separated set and are checked by the reconstruction validator.

| Target                                      | Owning document                      | Profiles                             |
| ------------------------------------------- | ------------------------------------ | ------------------------------------ |
| `.dockerignore`                             | `recipes/deployment.md`              | `full`                               |
| `.env.example`                              | `environment.md`                     | `auth,base,data,forms,full,realtime` |
| `.gitignore`                                | `gitignore.md`                       | `auth,base,data,forms,full,realtime` |
| `.prettierignore`                           | `prettier-config.md`                 | `auth,base,data,forms,full,realtime` |
| `.prettierrc.json`                          | `prettier-config.md`                 | `auth,base,data,forms,full,realtime` |
| `Dockerfile`                                | `recipes/deployment.md`              | `full`                               |
| `eslint.config.mjs`                         | `eslint-config.md`                   | `auth,base,data,forms,full,realtime` |
| `next-env.d.ts`                             | `next-config.md`                     | `auth,base,data,forms,full,realtime` |
| `next.config.ts`                            | `next-config.md`                     | `auth,base,data,forms,full,realtime` |
| `package.json`                              | `package-json.md`                    | `auth,base,data,forms,full,realtime` |
| `pnpm-lock.yaml`                            | `pnpm-lock.md`                       | `auth,base,data,forms,full,realtime` |
| `pnpm-workspace.yaml`                       | `pnpm-workspace.md`                  | `auth,base,data,forms,full,realtime` |
| `src/app/api/chat/route.ts`                 | `recipes/ai-chat.md`                 | `full`                               |
| `src/app/api/contact/route.ts`              | `recipes/forms.md`                   | `forms,full`                         |
| `src/app/api/events/route.ts`               | `recipes/realtime.md`                | `full,realtime`                      |
| `src/app/api/products/route.ts`             | `recipes/data.md`                    | `data,full`                          |
| `src/app/api/telemetry/route.ts`            | `recipes/analytics-observability.md` | `full`                               |
| `src/app/api/uploads/route.ts`              | `recipes/file-uploads.md`            | `full`                               |
| `src/app/data/page.tsx`                     | `recipes/data.md`                    | `data,full`                          |
| `src/app/error-demo/page.tsx`               | `src/app/boundaries.md`              | `auth,base,data,forms,full,realtime` |
| `src/app/error.tsx`                         | `src/app/boundaries.md`              | `auth,base,data,forms,full,realtime` |
| `src/app/forms/page.tsx`                    | `recipes/forms.md`                   | `forms,full`                         |
| `src/app/globals.css`                       | `src/app/globals.md`                 | `auth,base,data,forms,full,realtime` |
| `src/app/layout.tsx`                        | `src/app/layout.md`                  | `auth,base,data,forms,full,realtime` |
| `src/app/loading.tsx`                       | `src/app/boundaries.md`              | `auth,base,data,forms,full,realtime` |
| `src/app/login/page.tsx`                    | `recipes/authentication.md`          | `auth,full`                          |
| `src/app/not-found.tsx`                     | `src/app/boundaries.md`              | `auth,base,data,forms,full,realtime` |
| `src/app/page.tsx`                          | `src/app/page.md`                    | `auth,base,data,forms,full,realtime` |
| `src/app/protected/page.tsx`                | `recipes/authentication.md`          | `auth,full`                          |
| `src/app/realtime/page.tsx`                 | `recipes/realtime.md`                | `full,realtime`                      |
| `src/components/ui/tabs.tsx`                | `src/components/ui/tabs.md`          | `auth,base,data,forms,full,realtime` |
| `src/features/auth/model.ts`                | `recipes/authentication.md`          | `auth,full`                          |
| `src/features/auth/session.ts`              | `recipes/authentication.md`          | `auth,full`                          |
| `src/features/chat/chat-panel.tsx`          | `recipes/ai-chat.md`                 | `full`                               |
| `src/features/chat/model.ts`                | `recipes/ai-chat.md`                 | `full`                               |
| `src/features/chat/provider.ts`             | `recipes/ai-chat.md`                 | `full`                               |
| `src/features/flags/server-flags.ts`        | `recipes/feature-flags.md`           | `full`                               |
| `src/features/forms/contact-form.tsx`       | `recipes/forms.md`                   | `forms,full`                         |
| `src/features/forms/model.ts`               | `recipes/forms.md`                   | `forms,full`                         |
| `src/features/home/reference-tabs.tsx`      | `src/app/page.md`                    | `auth,base,data,forms,full,realtime` |
| `src/features/products/model.ts`            | `recipes/data.md`                    | `data,full`                          |
| `src/features/products/products-panel.tsx`  | `recipes/data.md`                    | `data,full`                          |
| `src/features/products/query-provider.tsx`  | `recipes/data.md`                    | `data,full`                          |
| `src/features/realtime/realtime-status.tsx` | `recipes/realtime.md`                | `full,realtime`                      |
| `src/lib/api-client.ts`                     | `recipes/data.md`                    | `data,full`                          |
| `src/lib/env/client.ts`                     | `environment.md`                     | `auth,base,data,forms,full,realtime` |
| `src/lib/env/server.ts`                     | `environment.md`                     | `auth,base,data,forms,full,realtime` |
| `src/lib/i18n.ts`                           | `recipes/internationalization.md`    | `full`                               |
| `src/lib/realtime.ts`                       | `recipes/realtime.md`                | `full,realtime`                      |
| `tsconfig.json`                             | `tsconfig.md`                        | `auth,base,data,forms,full,realtime` |
