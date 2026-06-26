# Publishing to the marketplace

This document covers `marketplace.json` — its schema, how to compute the `sha256`, how the app verifies and installs plugins, and how to develop locally before publishing.

Related docs: [authoring.md](./authoring.md) · [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## marketplace.json schema

`marketplace.json` is the top-level index file. It is a single JSON object:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Identifier for this marketplace, e.g. `"maccay-official"`. |
| `name` | string | yes | Display name, e.g. `"MaccyPlus Official Plugins"`. |
| `version` | string | yes | Marketplace index version. Bump when you add or update plugins. |
| `description` | string | no | Short description of the marketplace. |
| `maintainer` | string | no | GitHub username or display name of the maintainer. |
| `plugins` | array | yes | Array of `MarketplaceEntry` objects. |

### MarketplaceEntry

Each element of `plugins`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Must match the `id` in the package's `plugin.json`. |
| `name` | string | yes | Display name shown in the browse list. |
| `description` | string | yes | Short description. 120 chars max (validated by CI). |
| `version` | string | yes | Must match the `version` in `plugin.json`. |
| `minAppVersion` | string | no | Minimum MaccyPlus version required. |
| `kind` | string | yes | `"action"` or `"condition"`. Primary kind of the package. |
| `tags` | array of strings | no | Freeform tags for filtering, e.g. `["transform", "text"]`. |
| `capabilities` | array of strings | no | Same values as in `plugin.json`: `"network"`, `"fileRead"`, `"fileWrite"`, `"storage"`. |
| `source` | object | yes | Where the plugin files live. See [Source object](#source-object) below. |
| `sha256` | string | yes | Lowercase hex SHA-256 of the plugin's `plugin.json`. |

### Source object

Two source types are supported. Use `"type"` as the discriminator:

**GitHub source (recommended for plugins in this repo):**

```json
{
  "type": "github",
  "repo": "roypadina/maccay-plugins",
  "ref": "main",
  "path": "plugins/com.yourname.myplugin"
}
```

| Field | Required | Notes |
|---|---|---|
| `type` | yes | `"github"` |
| `repo` | yes | `"owner/repo"` |
| `ref` | yes | Branch, tag, or commit SHA |
| `path` | no | Path within the repo to the plugin folder. Omit if the plugin is at the repo root. |

The app resolves file URLs as: `https://raw.githubusercontent.com/<repo>/<ref>/<path>/<file>`

**URL source:**

```json
{
  "type": "url",
  "url": "https://example.com/plugins/myplugin"
}
```

The app resolves file URLs as: `<url>/<file>` (strips a trailing `/` if present).

---

## Computing and verifying sha256

The `sha256` in each `MarketplaceEntry` must equal the **lowercase hex SHA-256 of the plugin's `plugin.json` file** as it is committed in the repository.

Compute it:

```sh
shasum -a 256 plugins/com.yourname.myplugin/plugin.json
```

The first field of the output is the hex digest. Copy it into `marketplace.json`.

The CI script (`scripts/validate.py`) recomputes this hash for every entry and fails if it does not match. The app also verifies the hash at install time before writing anything to disk — a mismatch raises a `checksumMismatch` error and the install is aborted.

**Note:** The hash covers only `plugin.json`. JavaScript files (`main.js`, etc.) are fetched separately after the manifest is verified and are not individually hashed in v1.

---

## Install and verify flow (how the app works)

1. The app fetches `marketplace.json` and decodes the index.
2. When the user installs a plugin, the app calls `MarketplaceResolver.download(_:)`:
   - Fetches `plugin.json` from the source URL.
   - Computes SHA-256 of the downloaded bytes.
   - Compares against the `sha256` in `marketplace.json`. Aborts on mismatch.
3. The app writes the verified `plugin.json` to `~/.maccay/plugins/<entry.id>/plugin.json`.
4. For each distinct `entry` filename declared by JavaScript providers, the app fetches and writes the corresponding JS file alongside `plugin.json`.
5. No zip extraction — the install is always a flat directory of small files.

---

## Local-folder development loop

You do not need to publish to iterate. Point MaccyPlus at your local folder:

1. Create your plugin folder anywhere on disk (e.g. `~/dev/my-plugin/`).
2. In MaccyPlus → Settings → Plugins, click **Add Local Folder** and select the folder.
3. Edit `plugin.json` (and `main.js`) in your editor.
4. Click **Reload** in MaccyPlus to pick up changes.

Local plugins are not verified with a sha256 — verification only applies to marketplace installs.

---

## Full marketplace.json example

```json
{
  "id": "maccay-official",
  "name": "MaccyPlus Official Plugins",
  "version": "1",
  "description": "First-party MaccyPlus clipboard plugins.",
  "maintainer": "roypadina",
  "plugins": [
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
      "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    }
  ]
}
```
