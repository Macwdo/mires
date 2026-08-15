# ESLint configuration

Next.js core-web-vitals and TypeScript rules are the baseline. Generated output
is ignored explicitly.

<!-- artifact: eslint.config.mjs; profiles: base,forms,data,auth,realtime,full -->
```js
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTypeScript from "eslint-config-next/typescript";

export default defineConfig([...nextVitals, ...nextTypeScript, globalIgnores([".next/**"])]);
```
