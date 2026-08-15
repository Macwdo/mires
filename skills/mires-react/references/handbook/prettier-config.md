# Prettier configuration

Formatting is deterministic and checked in CI.

<!-- artifact: .prettierrc.json; profiles: base,forms,data,auth,realtime,full -->
```json
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "printWidth": 100
}
```

<!-- artifact: .prettierignore; profiles: base,forms,data,auth,realtime,full -->
```text
.next
node_modules
```
