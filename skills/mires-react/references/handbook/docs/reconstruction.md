# Reconstruction

The handbook is the canonical source. Reconstruction materializes a disposable
project for one profile; it never modifies the handbook, deletes content, or
overwrites a destination file.

## Bootstrap

Run this from the handbook root. It extracts the single utility fence to a
temporary executable:

```sh
node --input-type=module -e 'import{readFileSync,writeFileSync,chmodSync}from"node:fs";const s=readFileSync("docs/reconstruction.md","utf8");const lines=s.split(/\r?\n/);const marker="<!-- utility: reconstruct; language: javascript -->";const start=lines.findIndex(line=>line===marker)+1;const ticks=String.fromCharCode(96).repeat(3);const end=lines.indexOf(ticks,start+1);if(start===0||lines[start]!==ticks+"javascript"||end<0)throw new Error("reconstruction utility not found");writeFileSync("/tmp/reconstruct.mjs",lines.slice(start+1,end).join("\n")+"\n",{flag:"wx",mode:0o700});chmodSync("/tmp/reconstruct.mjs",0o700);'
ln -s /tmp/reconstruct.mjs /tmp/reconstruct
```

Choose fresh paths if either temporary path already exists. The utility refuses
to overwrite them by design.

Validate the handbook without writing:

```text
/tmp/reconstruct --validate
```

Materialize profiles into existing empty absolute directories outside the
handbook:

```text
/tmp/reconstruct --profile base --output /tmp/react-next-base
/tmp/reconstruct --profile full --output /tmp/react-next-full
```

## Protocol

The utility discovers canonical inputs with `git ls-files`, so untracked
experiments cannot silently become source material. It validates the entire
handbook before checking or writing a selected output.

Validation covers:

- all tracked paths end in `.md`;
- all relative Markdown links resolve;
- artifact markers, named fences, profiles, paths, and languages are valid;
- target/profile pairs are unique;
- each profile has no case-insensitive or file/directory target conflicts;
- canonical blocks contain no incomplete-code sentinels;
- `source-map.md` records each target and its owning document;
- obvious credential forms and handbook-specific product terms are absent.

Destination checks require an existing, empty, absolute directory outside the
repository. Every existing path component is checked with `lstat`; symbolic
links are rejected. Files are created exclusively and selected script paths are
made executable.

<!-- utility: reconstruct; language: javascript -->
```javascript
#!/usr/bin/env node

import {
  chmodSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  realpathSync,
  statSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const PROFILES = new Set(["base", "forms", "data", "auth", "realtime", "full"]);
const MARKER = /^<!-- artifact: ([^;\r\n]+); profiles: ([a-z]+(?:,[a-z]+)*) -->$/;
const UTILITY_MARKER = "<!-- utility: reconstruct; language: javascript -->";
const FENCE_TEXT = String.fromCharCode(96).repeat(3);
const FENCE = new RegExp(`^${FENCE_TEXT}([a-z0-9-]+)$`);
const SOURCE_ROW = /^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|$/;

function fail(message) {
  throw new Error(message);
}

function git(root, args) {
  return execFileSync("git", ["-C", root, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function repositoryRoot() {
  const start = path.dirname(fileURLToPath(import.meta.url));
  try {
    return git(start, ["rev-parse", "--show-toplevel"]).trim();
  } catch {
    return git(process.cwd(), ["rev-parse", "--show-toplevel"]).trim();
  }
}

function trackedMarkdown(root) {
  const entries = git(root, ["ls-files", "-z"]).split("\0").filter(Boolean);
  if (entries.length === 0) {
    fail("The handbook has no tracked files. Stage the Markdown sources before validation.");
  }
  const invalid = entries.filter((entry) => !entry.endsWith(".md"));
  if (invalid.length) {
    fail(`Every tracked file must end in .md: ${invalid.join(", ")}`);
  }
  return entries.sort();
}

function validateAllFences(document, owner) {
  const lines = document.split(/\r?\n/);
  let open = null;
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (!open) {
      if (line.startsWith(FENCE_TEXT)) {
        const match = FENCE.exec(line);
        if (!match) {
          fail(`${owner}:${index + 1}: every fence must have a valid language`);
        }
        open = { line: index + 1, language: match[1] };
      }
    } else if (line === FENCE_TEXT) {
      open = null;
    }
  }
  if (open) {
    fail(`${owner}:${open.line}: unclosed ${open.language} fence`);
  }
}

function safeTarget(target, owner, line) {
  if (
    !target ||
    target.includes("\0") ||
    target.includes("\\") ||
    path.posix.isAbsolute(target) ||
    path.posix.normalize(target) !== target ||
    target === "." ||
    target.split("/").some((part) => part === "" || part === "." || part === "..")
  ) {
    fail(`${owner}:${line}: unsafe artifact target ${JSON.stringify(target)}`);
  }
}

function expectedLanguage(target) {
  const basename = path.posix.basename(target);
  if (basename === "Dockerfile") return "dockerfile";
  if (basename === ".gitignore" || basename === ".dockerignore") return "gitignore";
  if (basename === ".prettierignore") return "text";
  if (basename.startsWith(".env")) return "dotenv";
  const extension = path.posix.extname(target);
  const languages = {
    ".css": "css",
    ".json": "json",
    ".js": "js",
    ".mjs": "js",
    ".ts": "ts",
    ".tsx": "tsx",
    ".yaml": "yaml",
    ".yml": "yaml",
  };
  return languages[extension] ?? null;
}

function validateCompleteCode(content, owner, line) {
  const sentinels = [
    /^\s*(?:\/\/|#|\/\*)\s*(?:TODO|FIXME|TBD)\b/im,
    /^\s*(?:\/\/|#)\s*\.\.\.\s*$/m,
    /<[^>]+>\s*\.\.\.\s*<\/[^>]+>/,
    /\b(?:INSERT|ADD) (?:CODE|IMPLEMENTATION) HERE\b/i,
  ];
  if (sentinels.some((pattern) => pattern.test(content))) {
    fail(`${owner}:${line}: canonical artifact contains incomplete code`);
  }
}

function parseArtifacts(document, owner) {
  validateAllFences(document, owner);
  const lines = document.split(/\r?\n/);
  const artifacts = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (!line.startsWith("<!-- artifact:")) continue;
    const marker = MARKER.exec(line);
    if (!marker) {
      fail(`${owner}:${index + 1}: malformed artifact marker`);
    }

    const target = marker[1].trim();
    const profiles = marker[2].split(",");
    safeTarget(target, owner, index + 1);
    for (const profile of profiles) {
      if (!PROFILES.has(profile)) {
        fail(`${owner}:${index + 1}: unknown profile ${profile}`);
      }
    }
    if (new Set(profiles).size !== profiles.length) {
      fail(`${owner}:${index + 1}: duplicate profile in marker`);
    }

    const fence = FENCE.exec(lines[index + 1] ?? "");
    if (!fence) {
      fail(`${owner}:${index + 1}: marker must be immediately followed by one named fence`);
    }
    const language = fence[1];
    const expected = expectedLanguage(target);
    if (!expected || language !== expected) {
      fail(
        `${owner}:${index + 2}: ${target} requires a ${expected ?? "supported"} fence, received ${language}`,
      );
    }

    const contentStart = index + 2;
    let close = contentStart;
    while (close < lines.length && lines[close] !== FENCE_TEXT) close += 1;
    if (close >= lines.length) {
      fail(`${owner}:${index + 2}: unclosed artifact fence`);
    }
    const content = `${lines.slice(contentStart, close).join("\n")}\n`;
    if (!content.trim()) {
      fail(`${owner}:${index + 2}: empty canonical artifact`);
    }
    validateCompleteCode(content, owner, index + 2);
    artifacts.push({ content, language, line: index + 1, owner, profiles, target });
    index = close;
  }
  return artifacts;
}

function validateUtility(documents) {
  const owners = [];
  for (const [owner, document] of documents) {
    const count = document.split(/\r?\n/).filter((line) => line === UTILITY_MARKER).length;
    if (count) owners.push({ count, document, owner });
  }
  if (owners.length !== 1 || owners[0].count !== 1) {
    fail("Exactly one reconstruction utility marker is required.");
  }
  const { document, owner } = owners[0];
  const lines = document.split(/\r?\n/);
  const markerLine = lines.findIndex((line) => line === UTILITY_MARKER);
  const suffix = lines.slice(markerLine + 1).join("\n");
  if (
    !suffix.startsWith(`${FENCE_TEXT}javascript\n`) ||
    !suffix.includes(`\n${FENCE_TEXT}`)
  ) {
    fail(`${owner}: reconstruction utility marker must precede one javascript fence`);
  }
}

function validateDuplicates(artifacts) {
  const pairs = new Map();
  for (const artifact of artifacts) {
    for (const profile of artifact.profiles) {
      const key = `${profile}\0${artifact.target}`;
      const previous = pairs.get(key);
      if (previous) {
        fail(
          `Duplicate target/profile pair ${artifact.target}/${profile}: ${previous.owner}:${previous.line} and ${artifact.owner}:${artifact.line}`,
        );
      }
      pairs.set(key, artifact);
    }
  }
}

function selectedArtifacts(artifacts, profile) {
  return artifacts.filter((artifact) => artifact.profiles.includes(profile));
}

function validateTree(artifacts, profile) {
  const folded = new Map();
  const targets = new Set(artifacts.map((artifact) => artifact.target));
  for (const target of targets) {
    const key = target.toLocaleLowerCase("en-US");
    const previous = folded.get(key);
    if (previous && previous !== target) {
      fail(`Case-insensitive target conflict in ${profile}: ${previous} and ${target}`);
    }
    folded.set(key, target);

    const parts = target.split("/");
    for (let index = 1; index < parts.length; index += 1) {
      const parent = parts.slice(0, index).join("/");
      if (targets.has(parent)) {
        fail(`File/directory target conflict in ${profile}: ${parent} and ${target}`);
      }
    }
  }
}

function validateRelativeLinks(root, documents) {
  const known = new Set(documents.keys());
  const linkPattern = /(?<!!)\[[^\]]*\]\(([^)]+)\)/g;
  for (const [owner, document] of documents) {
    for (const match of document.matchAll(linkPattern)) {
      let destination = match[1].trim();
      if (destination.startsWith("<") && destination.endsWith(">")) {
        destination = destination.slice(1, -1);
      }
      destination = destination.split("#", 1)[0];
      if (
        !destination ||
        destination.startsWith("#") ||
        /^[a-z][a-z0-9+.-]*:/i.test(destination) ||
        destination.startsWith("//")
      ) {
        continue;
      }
      const resolved = path.posix.normalize(
        path.posix.join(path.posix.dirname(owner), destination),
      );
      if (resolved.startsWith("../") || !known.has(resolved)) {
        fail(`${owner}: unresolved relative Markdown link ${destination}`);
      }
    }
  }
}

function validateSourceMap(documents, artifacts) {
  const sourceMap = documents.get("source-map.md");
  if (!sourceMap) fail("source-map.md is required");
  const recorded = new Map();
  for (const line of sourceMap.split(/\r?\n/)) {
    const match = SOURCE_ROW.exec(line);
    if (!match || match[1] === "Target") continue;
    const [target, owner, profileText] = match.slice(1);
    if (recorded.has(target)) fail(`source-map.md records ${target} more than once`);
    recorded.set(target, {
      owner,
      profiles: new Set(profileText.split(",").map((profile) => profile.trim())),
    });
  }

  const actual = new Map();
  for (const artifact of artifacts) {
    const entry = actual.get(artifact.target) ?? {
      owner: artifact.owner,
      profiles: new Set(),
    };
    if (entry.owner !== artifact.owner) {
      fail(`Artifact target ${artifact.target} has multiple owning documents`);
    }
    for (const profile of artifact.profiles) entry.profiles.add(profile);
    actual.set(artifact.target, entry);
  }

  for (const [target, entry] of actual) {
    const sourceEntry = recorded.get(target);
    if (!sourceEntry) fail(`source-map.md does not record ${target}`);
    const actualProfiles = [...entry.profiles].sort().join(",");
    const recordedProfiles = [...sourceEntry.profiles].sort().join(",");
    if (sourceEntry.owner !== entry.owner || recordedProfiles !== actualProfiles) {
      fail(`source-map.md ownership or profiles are stale for ${target}`);
    }
  }
  for (const target of recorded.keys()) {
    if (!actual.has(target)) fail(`source-map.md records nonexistent target ${target}`);
  }
}

function validateSensitiveContent(documents) {
  const patterns = [
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
    /\b(?:sk|ghp|github_pat)_[A-Za-z0-9_-]{20,}\b/,
    new RegExp(`\\b(?:${["mi", "res"].join("")}|${["pingou", "-o-que"].join("")})\\b`, "i"),
  ];
  for (const [owner, document] of documents) {
    if (patterns.some((pattern) => pattern.test(document))) {
      fail(`${owner}: possible secret or product-specific content`);
    }
  }
}

function loadHandbook(root) {
  const tracked = trackedMarkdown(root);
  const documents = new Map(
    tracked.map((owner) => [owner, readFileSync(path.join(root, owner), "utf8")]),
  );
  validateUtility(documents);
  validateRelativeLinks(root, documents);
  validateSensitiveContent(documents);
  const artifacts = [...documents].flatMap(([owner, document]) => parseArtifacts(document, owner));
  validateDuplicates(artifacts);
  for (const profile of PROFILES) {
    validateTree(selectedArtifacts(artifacts, profile), profile);
  }
  validateSourceMap(documents, artifacts);
  return artifacts;
}

function assertNoSymlinkComponents(destination) {
  const parsed = path.parse(destination);
  let current = parsed.root;
  for (const part of destination.slice(parsed.root.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    if (existsSync(current) && lstatSync(current).isSymbolicLink()) {
      fail(`Symbolic-link path component is forbidden: ${current}`);
    }
  }
}

function validateDestination(root, destination) {
  if (!path.isAbsolute(destination)) fail("Output must be an absolute path.");
  assertNoSymlinkComponents(destination);
  if (!existsSync(destination) || !statSync(destination).isDirectory()) {
    fail("Output must be an existing directory.");
  }
  if (readdirSync(destination).length !== 0) {
    fail("Output directory must be empty.");
  }
  const realRoot = realpathSync(root);
  const realDestination = realpathSync(destination);
  if (realDestination === realRoot || realDestination.startsWith(`${realRoot}${path.sep}`)) {
    fail("Output must be outside the handbook repository.");
  }
}

function isExecutableTarget(target) {
  return (
    target.startsWith("bin/") ||
    target.startsWith("scripts/") ||
    [".sh", ".bash", ".command"].includes(path.posix.extname(target))
  );
}

function materialize(root, destination, artifacts, profile) {
  const selected = selectedArtifacts(artifacts, profile).sort((left, right) =>
    left.target.localeCompare(right.target),
  );
  if (!selected.length) fail(`Profile ${profile} has no artifacts.`);
  validateDestination(root, destination);

  const directories = new Set(
    selected
      .map((artifact) => path.posix.dirname(artifact.target))
      .filter((directory) => directory !== "."),
  );
  for (const directory of [...directories].sort(
    (left, right) => left.split("/").length - right.split("/").length,
  )) {
    mkdirSync(path.join(destination, ...directory.split("/")), { recursive: true });
  }
  for (const artifact of selected) {
    const output = path.join(destination, ...artifact.target.split("/"));
    writeFileSync(output, artifact.content, { encoding: "utf8", flag: "wx", mode: 0o644 });
    if (isExecutableTarget(artifact.target)) chmodSync(output, 0o755);
  }
  return selected.length;
}

function parseArguments(argv) {
  const options = { validate: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--validate") {
      options.validate = true;
    } else if (argument === "--profile" || argument === "--output") {
      const value = argv[index + 1];
      if (!value) fail(`${argument} requires a value`);
      options[argument.slice(2)] = value;
      index += 1;
    } else {
      fail(`Unknown argument: ${argument}`);
    }
  }
  if (options.validate && (options.profile || options.output)) {
    fail("--validate cannot be combined with --profile or --output");
  }
  if (!options.validate && (!options.profile || !options.output)) {
    fail("Use --validate or provide both --profile and --output");
  }
  if (options.profile && !PROFILES.has(options.profile)) {
    fail(`Unknown profile: ${options.profile}`);
  }
  return options;
}

try {
  const options = parseArguments(process.argv.slice(2));
  const root = repositoryRoot();
  const artifacts = loadHandbook(root);
  if (options.validate) {
    console.log(
      `Validated ${trackedMarkdown(root).length} Markdown files and ${artifacts.length} artifact variants.`,
    );
  } else {
    const count = materialize(root, options.output, artifacts, options.profile);
    console.log(`Materialized ${count} artifacts for ${options.profile} in ${options.output}.`);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
```

## Negative checks

When changing the utility, verify that temporary copies reject an unknown
profile, a relative output path, a non-empty destination, an in-repository
destination, a symlink component, a duplicate target/profile pair, an unsafe
target, and an unclosed fence. A failure must happen before the first output
file is written.
