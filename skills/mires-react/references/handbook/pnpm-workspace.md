# pnpm workspace settings

The workspace file is present even for one package because pnpm 11 stores
approved dependency build-script policy here.

<!-- artifact: pnpm-workspace.yaml; profiles: base,forms,data,auth,realtime,full -->
```yaml
packages:
  - "."

autoInstallPeers: false

allowBuilds:
  sharp: true
  unrs-resolver: true
```
