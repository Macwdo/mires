# Package manifests

The manifests pin a verified, reproducible compatibility snapshot. Optional
runtime dependencies are absent from profiles that do not use them.

<!-- artifact: package.json; profiles: base,auth,realtime -->
```json
{
  "name": "react-next-standards-base",
  "version": "1.0.0",
  "private": true,
  "packageManager": "pnpm@11.17.0",
  "engines": {
    "node": ">=20.9.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "next": "16.2.12",
    "react": "19.2.8",
    "react-dom": "19.2.8",
    "server-only": "0.0.1",
    "zod": "4.4.3"
  },
  "devDependencies": {
    "@types/node": "26.1.1",
    "@types/react": "19.2.17",
    "@types/react-dom": "19.2.3",
    "eslint": "9.39.5",
    "eslint-config-next": "16.2.12",
    "prettier": "3.9.6",
    "typescript": "6.0.3"
  }
}
```

<!-- artifact: package.json; profiles: forms -->
```json
{
  "name": "react-next-standards-forms",
  "version": "1.0.0",
  "private": true,
  "packageManager": "pnpm@11.17.0",
  "engines": {
    "node": ">=20.9.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "next": "16.2.12",
    "react": "19.2.8",
    "react-dom": "19.2.8",
    "react-hook-form": "7.83.0",
    "server-only": "0.0.1",
    "zod": "4.4.3"
  },
  "devDependencies": {
    "@types/node": "26.1.1",
    "@types/react": "19.2.17",
    "@types/react-dom": "19.2.3",
    "eslint": "9.39.5",
    "eslint-config-next": "16.2.12",
    "prettier": "3.9.6",
    "typescript": "6.0.3"
  }
}
```

<!-- artifact: package.json; profiles: data -->
```json
{
  "name": "react-next-standards-data",
  "version": "1.0.0",
  "private": true,
  "packageManager": "pnpm@11.17.0",
  "engines": {
    "node": ">=20.9.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@tanstack/react-query": "5.101.4",
    "next": "16.2.12",
    "react": "19.2.8",
    "react-dom": "19.2.8",
    "server-only": "0.0.1",
    "zod": "4.4.3"
  },
  "devDependencies": {
    "@types/node": "26.1.1",
    "@types/react": "19.2.17",
    "@types/react-dom": "19.2.3",
    "eslint": "9.39.5",
    "eslint-config-next": "16.2.12",
    "prettier": "3.9.6",
    "typescript": "6.0.3"
  }
}
```

<!-- artifact: package.json; profiles: full -->
```json
{
  "name": "react-next-standards-full",
  "version": "1.0.0",
  "private": true,
  "packageManager": "pnpm@11.17.0",
  "engines": {
    "node": ">=20.9.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@tanstack/react-query": "5.101.4",
    "next": "16.2.12",
    "react": "19.2.8",
    "react-dom": "19.2.8",
    "react-hook-form": "7.83.0",
    "server-only": "0.0.1",
    "zod": "4.4.3"
  },
  "devDependencies": {
    "@types/node": "26.1.1",
    "@types/react": "19.2.17",
    "@types/react-dom": "19.2.3",
    "eslint": "9.39.5",
    "eslint-config-next": "16.2.12",
    "prettier": "3.9.6",
    "typescript": "6.0.3"
  }
}
```
