# Authoring guide — manifest and ProviderSpec schema reference

This document is the authoritative field-by-field reference for `plugin.json`. Every field listed here matches the `PluginManifest` and `ProviderSpec` Swift structs exactly.

Related docs: [declarative-plugins.md](./declarative-plugins.md) · [javascript-plugins.md](./javascript-plugins.md) · [publishing.md](./publishing.md) · [examples.md](./examples.md)

---

## Package manifest (`plugin.json`)

The top-level object in `plugin.json` describes the **package** — the install and consent unit.

| Field | Type | Required | Constraint |
|---|---|---|---|
| `id` | string | yes | Non-empty. Reverse-DNS recommended, e.g. `"com.yourname.myplugin"`. Must be globally unique in the marketplace. |
| `name` | string | yes | Non-empty. Shown as the package display name. |
| `version` | string | yes | Non-empty. Semantic version recommended, e.g. `"1.0.0"`. |
| `description` | string | yes | Non-empty. **Maximum 120 characters.** Shown as the package tooltip. |
| `longHelp` | string | no | Extended description. Shown in the package detail view. No length limit. |
| `author` | object | no | `{ "name": "...", "url": "..." }` — `url` is optional. |
| `minAppVersion` | string | no | Minimum Maccay version required. If absent, any version is accepted. |
| `capabilities` | array of strings | yes (use `[]` if none) | Declare every resource the package accesses. See [Capabilities](#capabilities) below. |
| `providers` | array of ProviderSpec | yes | Must be non-empty. Each element describes one provider. |

**Validation rules enforced by `PluginManifest.validate()`:**

- `id`, `name`, `version`, `description` must not be blank after whitespace trimming.
- `description` must not exceed 120 characters.
- `providers` must not be empty.
- Each provider is validated individually (see below).

### Example package skeleton

```json
{
  "id": "com.yourname.myplugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": { "name": "Your Name", "url": "https://github.com/yourname" },
  "description": "One sentence description, 120 chars max.",
  "longHelp": "A longer explanation for the detail view.",
  "minAppVersion": "2.7.0",
  "capabilities": [],
  "providers": []
}
```

---

## ProviderSpec

Each element of the `providers` array describes one provider.

| Field | Type | Required | Constraint |
|---|---|---|---|
| `id` | string | yes | Non-empty. Unique within the package. Reverse-DNS recommended. |
| `name` | string | yes | Non-empty. Shown as the provider display name. |
| `description` | string | yes | Non-empty. **Maximum 120 characters.** |
| `longHelp` | string | no | Extended description. No length limit. |
| `kind` | string | yes | `"action"` or `"condition"`. |
| `engine` | string | yes | `"declarative"` or `"javascript"`. Never `"native"` — that value is reserved for built-in Maccay providers and is rejected by `validate()`. |
| `declarative` | object | if engine is `"declarative"` | Transform op list (actions) or predicate tree (conditions). See [declarative-plugins.md](./declarative-plugins.md). |
| `entry` | string | if engine is `"javascript"` | Filename of the JS script relative to the plugin folder, e.g. `"main.js"`. Must be non-empty. |
| `function` | string | no | Named JS function to call. Defaults to `"transform"` for actions, `"matches"` for conditions. Multiple providers in the same package can share one `entry` file by specifying different `function` values. |
| `params` | array of ParamSpec | no | User-configurable parameters. See [ParamSpec](#paramspec) below. |

**Validation rules:**

- `id`, `name`, `description` must not be blank after whitespace trimming.
- `description` must not exceed 120 characters.
- If `engine` is `"declarative"`, `declarative` must be present (not null).
- If `engine` is `"javascript"`, `entry` must be present and non-empty.

---

## Capabilities

Capabilities are declared at the **package** level. The user is shown the consent dialog once when installing the package.

| Value | Meaning |
|---|---|
| `"network"` | Plugin sends or receives data over the network. |
| `"fileRead"` | Plugin reads files from the filesystem. |
| `"fileWrite"` | Plugin writes or modifies files on the filesystem. |
| `"storage"` | Plugin persists data between invocations. |

Declare every capability the plugin uses. Use `[]` for a plugin that only manipulates the clipboard text in memory.

**Important (v1):** Capabilities are declared, displayed to the user at install time, and badged in the UI. In v1, the JS runtime is bridge-less and capabilities are not enforced at runtime — the bridge is planned for a future version. Plugins that declare capabilities dishonestly will be removed.

---

## ParamSpec

Optional user-configurable parameters. Each element in a provider's `params` array:

| Field | Type | Required | Notes |
|---|---|---|---|
| `key` | string | yes | Identifier used to read the value in JS (`params[key]`). |
| `label` | string | yes | Label shown next to the input field in the UI. |
| `kind` | string | yes | `"text"`, `"valueKind"`, or `"bundleID"`. |
| `placeholder` | string | no | Placeholder text for the input field. |

---

## Full example — multi-provider package

```json
{
  "id": "com.yourname.text-utils",
  "name": "Text Utilities",
  "version": "1.0.0",
  "author": { "name": "Your Name" },
  "description": "A collection of useful text transforms.",
  "capabilities": [],
  "providers": [
    {
      "id": "com.yourname.text-utils.trim",
      "name": "Trim whitespace",
      "description": "Removes leading and trailing whitespace.",
      "kind": "action",
      "engine": "declarative",
      "declarative": {
        "transform": [{ "op": "trim" }]
      }
    },
    {
      "id": "com.yourname.text-utils.upper",
      "name": "UPPERCASE",
      "description": "Converts the text to uppercase.",
      "kind": "action",
      "engine": "declarative",
      "declarative": {
        "transform": [{ "op": "case", "value": "upper" }]
      }
    }
  ]
}
```
