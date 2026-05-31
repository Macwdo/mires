# Mires Skill Installer

This repository packages Mires Codex skills from `.codex/skills/` plus OpenCode skills and commands from `.opencode/`, and exposes a Node CLI named `mires`.

For a maintainer-oriented explanation of how the skill hierarchy is structured, see [`docs/mires-skill-architecture.md`](docs/mires-skill-architecture.md).

## Global package install

Install the CLI globally with your package manager of choice:

```sh
npm install -g @macwdo/mires
pnpm add -g @macwdo/mires
bun add -g @macwdo/mires
```

Then install the bundled assets for both runtimes:

```sh
mires install --scope user
```

By default, `mires install` uses `--target both`.

User scope targets:

- Codex: `$CODEX_HOME/skills` when `CODEX_HOME` is set, otherwise `~/.codex/skills`
- OpenCode: `${XDG_CONFIG_HOME:-~/.config}/opencode/skills` and `${XDG_CONFIG_HOME:-~/.config}/opencode/commands`

Current OpenCode command entrypoints bundled by this package include `/opsx-apply`, `/opsx-archive`, `/opsx-explore`, `/opsx-propose`, `/mires-tester`, and `/mires-reviewer`.

## Project install

Install assets only for one project:

```sh
mires install --scope project --project-root /path/to/project
```

Project scope targets:

- Codex: `<project-root>/.codex/skills`
- OpenCode: `<project-root>/.opencode/skills` and `<project-root>/.opencode/commands`

If `--project-root` is omitted, the current directory is used.

After an OpenCode install, `mires-tester` and `mires-reviewer` are available as both skills and slash commands in the selected scope.

## Runtime targeting

Install target options:

- `--target both`: install Codex and OpenCode assets. Default.
- `--target codex`: install only Codex skills.
- `--target opencode`: install only OpenCode skills and commands.

Examples:

```sh
mires install --scope user --target both
mires install --scope user --target opencode
mires install --scope project --target codex
```

For OpenCode specifically:

```sh
mires install --scope user --target opencode
mires install --scope project --target opencode
```

That installs the `/mires-tester` and `/mires-reviewer` commands plus their matching OpenCode skills.

## Local package usage

You can also install the package in a project and run the CLI locally:

```sh
npm install --save-dev @macwdo/mires
npm exec -- mires install --scope project

pnpm add -D @macwdo/mires
pnpm exec mires install --scope project --target both

bun add -d @macwdo/mires
bunx mires install --scope project --target both
```

Or add an npm script:

```json
{
  "scripts": {
    "install:mires-skills": "mires install --scope project --yes"
  }
}
```

`npm install -g @macwdo/mires`, `pnpm add -g @macwdo/mires`, and `bun add -g @macwdo/mires` control where the CLI package is installed. `mires install --scope user|project --target codex|opencode|both` controls which runtime assets are copied and where they go.

## CLI commands

```sh
mires --help
mires --version
mires list
mires install --scope user
mires install --scope project --project-root /path/to/project
mires install --scope user --target opencode
```

Install flags:

- `--yes`: accept non-destructive confirmations and skip conflicts unless `--force` is set
- `--target`: choose `codex`, `opencode`, or `both`
- `--force`: replace existing destination files or directories
- `--dry-run`: print planned actions without writing files

The installer copies every bundled Codex skill directory, every bundled OpenCode skill directory, and every bundled OpenCode command file. Codex skill directories keep `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/`, and other package-local files intact.

`bunx` and `pnpm dlx` can also run the published package without a prior global install:

```sh
pnpm dlx @macwdo/mires install --scope project --target both
bunx --package @macwdo/mires mires install --scope project --target both
```

## Source installer fallback

When working from a clone or downloaded source tree, the shell installer is still available:

```sh
sh ./install.sh --target both
```

The shell installer supports the same `--target codex|opencode|both` flag, prompts for user-level or project-level installation, and asks before overwriting existing files or directories. `--yes` skips non-destructive confirmations and skips conflicts unless `--force` is also set.

## Maintainer validation

Run the syntax and packaging checks before publishing:

```sh
npm run check
npm run pack:dry-run
npm run verify:package
```

`npm run verify:package` creates an npm tarball, installs it into temporary projects, verifies help/version/list behavior, checks Codex and OpenCode user/project install scopes, confirms dry-run and conflict behavior across both runtimes, and ensures all bundled Codex skills, OpenCode skills, and OpenCode commands are copied.
