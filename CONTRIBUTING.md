# Contributing to maccay-plugins

This repository is the official Maccay plugin marketplace. All plugins listed in `marketplace.json` are reviewed by the maintainer and satisfy the requirements below before merge.

---

## How to add a plugin

### 1. Create your plugin folder

Add a folder under `plugins/` using your package id as the folder name:

```
plugins/com.yourname.myplugin/
  plugin.json
  main.js          (only needed for engine: "javascript")
```

Use a reverse-DNS id, e.g. `com.yourname.myplugin`. The folder name must match the `id` field inside `plugin.json`.

### 2. Write plugin.json

Every package manifest must include these top-level fields:

| Field | Required | Constraint |
|---|---|---|
| `id` | yes | Reverse-DNS string. Globally unique in this repo. |
| `name` | yes | Non-empty display name. |
| `version` | yes | Semantic version string, e.g. `"1.0.0"`. |
| `description` | yes | Non-empty. **120 characters maximum.** |
| `capabilities` | yes | Array. Use `[]` if the plugin needs no special access. |
| `providers` | yes | Non-empty array of provider objects (see below). |
| `author` | no | Object with `name` and optional `url`. |
| `longHelp` | no | Extended description shown in the plugin detail view. |
| `minAppVersion` | no | Minimum Maccay version required, e.g. `"2.7.0"`. |

Each entry in `providers` must include:

| Field | Required | Constraint |
|---|---|---|
| `id` | yes | Reverse-DNS string. Must be unique within the package. |
| `name` | yes | Non-empty display name. |
| `description` | yes | Non-empty. **120 characters maximum.** |
| `kind` | yes | `"action"` or `"condition"`. |
| `engine` | yes | `"declarative"` or `"javascript"`. Never `"native"`. |
| `declarative` | if engine is `declarative` | Transform op list (actions) or predicate tree (conditions). |
| `entry` | if engine is `javascript` | Filename of the JS script, e.g. `"main.js"`. |
| `function` | no | Named JS function to call. Defaults to `transform` (actions) or `matches` (conditions). |
| `longHelp` | no | Extended description for the provider detail view. |

Full schema: [docs/authoring.md](./docs/authoring.md).

### 3. Add an entry to marketplace.json

Add one object to the `plugins` array in `marketplace.json`:

```json
{
  "id": "com.yourname.myplugin",
  "name": "My Plugin",
  "description": "One sentence, 120 chars max.",
  "version": "1.0.0",
  "minAppVersion": "2.7.0",
  "kind": "action",
  "tags": ["transform"],
  "capabilities": [],
  "source": {
    "type": "github",
    "repo": "roypadina/maccay-plugins",
    "ref": "main",
    "path": "plugins/com.yourname.myplugin"
  },
  "sha256": "<hex from shasum command below>"
}
```

The `kind` field in the marketplace entry should reflect the primary kind of the package (use `"action"` for packages that include any action provider; use `"condition"` for condition-only packages). `minAppVersion` and `tags` are optional.

### 4. Compute the sha256

The `sha256` field must be the lowercase hex SHA-256 of your `plugin.json` file exactly as it will appear in the repo:

```sh
shasum -a 256 plugins/com.yourname.myplugin/plugin.json
```

Copy the first field of the output. The CI script recomputes this hash and fails if it does not match. The hash covers only `plugin.json` — not `main.js` or any other file. This is how the app verifies integrity at install time.

### 5. Open a pull request

- Fork this repo and create a branch (e.g. `add/com.yourname.myplugin`).
- Commit your `plugins/<id>/` folder and the updated `marketplace.json`.
- Open a PR to `main`.

`main` is a **protected branch** — direct pushes are not allowed. Every PR goes through the review flow below.

---

## PR workflow

1. CI runs `scripts/validate.py` on every push and PR. It must exit 0.
2. CODEOWNERS assigns `@roypadina` as a required reviewer for all changes to `marketplace.json` and `plugins/`.
3. The maintainer reviews the plugin for correctness, safety, and policy compliance, then squash-merges.

---

## Requirements

- Every provider must have non-empty `id`, `name`, `description`, `kind`, and `engine`.
- `description` at every level (package and each provider) must be 120 characters or fewer.
- `capabilities` must declare every resource the plugin actually accesses. Permitted values: `"network"`, `"fileRead"`, `"fileWrite"`, `"storage"`.
- Declarative providers must include a valid `declarative` object.
- JavaScript providers must include a non-empty `entry` filename, and the referenced file must exist in the plugin folder.
- The `sha256` in `marketplace.json` must match the SHA-256 of the committed `plugin.json`.
- No obfuscated JavaScript.
- No `engine: "native"` (reserved for built-in Maccay providers).
- No undeclared network or filesystem access.

> **Note on capabilities in v1:** Capabilities are declared, displayed to the user during install, and badged in the UI — but the bridge-less JS sandbox does not yet enforce them at runtime. Plugins that declare capabilities dishonestly will be removed and the author blocked. The enforcement bridge is planned for a future version.

---

## What is NOT allowed

- `engine: "native"` — only the Maccay app itself may register native providers.
- Undeclared network or filesystem access.
- Plugins that exfiltrate clipboard content to external servers.
- Obfuscated JavaScript.
- Binary files other than recognized image assets.

---

## Questions

Open a GitHub Discussion or issue before submitting a PR, especially for new capability types or plugin ideas that might be out of scope.
