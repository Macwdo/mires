# Deployment

Deploy the same artifact that passed the frozen-lockfile build. Run as a
non-root user, inject configuration at runtime, terminate TLS at a reviewed
edge, and keep secrets outside image layers and build arguments.

<!-- artifact: Dockerfile; profiles: full -->
```dockerfile
FROM node:22.22.0-alpine AS dependencies
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:22.22.0-alpine AS build
WORKDIR /app
RUN corepack enable
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM node:22.22.0-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=build --chown=nextjs:nodejs /app ./
USER nextjs
EXPOSE 3000
CMD ["pnpm", "start"]
```

<!-- artifact: .dockerignore; profiles: full -->
```gitignore
.git
.next
node_modules
.env*
```
