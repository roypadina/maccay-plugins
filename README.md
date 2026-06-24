# maccay-plugins

The official plugin marketplace for [Maccay](https://github.com/roypadina/Maccay), a macOS clipboard manager.

Browse the [`plugins/`](./plugins/) directory to see what's available, or jump straight to [Building your first plugin](#quickstart-build-your-first-plugin).

---

## What is a plugin?

A **plugin** is a folder containing one `plugin.json` (and optionally one or more `.js` files). The manifest declares a list of **providers** — any mix of:

- **Conditions** — predicates that inspect the clipboard entry and return `true`/`false`. Used to filter when actions fire.
- **Actions** — transforms that receive the clipboard text and return a modified string.

Each provider is implemented with one of two engines:

| Engine | How it works |
|---|---|
| `declarative` | A pure JSON description of transform ops or a predicate tree — no code required. |
| `javascript` | A single JS function in a sandboxed JavaScriptCore runtime. |

---

## Install

### From the marketplace (recommended)

1. Open **Maccay → Settings → Plugins**.
2. Click **Add Marketplace** and paste the URL:
   ```
   https://raw.githubusercontent.com/roypadina/maccay-plugins/main/marketplace.json
   ```
3. Browse and install plugins.

### Local folder (during development)

1. Open **Maccay → Settings → Plugins**.
2. Click **Add Local Folder** and point it at a folder that contains `plugin.json`.

---

## Quickstart: build your first plugin

### Declarative action (no code)

Create `plugins/my-trim/plugin.json`:

```json
{
  "id": "com.yourname.my-trim",
  "name": "My Trim",
  "version": "1.0.0",
  "description": "Removes leading and trailing whitespace.",
  "capabilities": [],
  "providers": [
    {
      "id": "com.yourname.my-trim.trim",
      "name": "Trim whitespace",
      "description": "Removes leading and trailing whitespace from clipboard text.",
      "kind": "action",
      "engine": "declarative",
      "declarative": {
        "transform": [
          { "op": "trim" }
        ]
      }
    }
  ]
}
```

That's it. Point Maccay at the folder and the action appears immediately.

### JavaScript action

`plugins/my-reverse/plugin.json`:

```json
{
  "id": "com.yourname.my-reverse",
  "name": "Reverse",
  "version": "1.0.0",
  "description": "Reverses the clipboard text character by character.",
  "capabilities": [],
  "providers": [
    {
      "id": "com.yourname.my-reverse.reverse",
      "name": "Reverse text",
      "description": "Reverses the clipboard text character by character.",
      "kind": "action",
      "engine": "javascript",
      "entry": "main.js"
    }
  ]
}
```

`plugins/my-reverse/main.js`:

```js
function transform(text) {
  return text.split("").reverse().join("");
}
```

The runtime calls `transform(text)` by default (configurable via the `function` field). It must return a string.

> **Sandbox:** The JS runtime is bridge-less — no `fetch`, `require`, `XMLHttpRequest`, `setTimeout`, `process`, or filesystem access. Pure ECMAScript only. A 250 ms watchdog terminates runaway scripts. See [docs/javascript-plugins.md](./docs/javascript-plugins.md).

---

## The package/provider model

```
plugin.json          ← one package manifest
  providers[]
    provider 0       ← id, name, description, kind, engine + engine payload
    provider 1
    ...
```

One `plugin.json` = one installable **package**. Capabilities are declared at the package level and consented once. A package can contain any number of providers spanning both kinds (conditions and actions).

See [docs/authoring.md](./docs/authoring.md) for the full schema reference.

---

## Contributing

1. Fork this repo and create a branch.
2. Add your plugin folder under `plugins/<your-plugin-id>/`.
3. Add a corresponding entry to `marketplace.json`.
4. Open a pull request to `main`.

`main` is a protected branch — no direct pushes. Every PR requires maintainer review (CODEOWNERS assigns `@roypadina` as a required reviewer). CI runs `scripts/validate.py` on every push and PR; it must pass before merge.

Full details: [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Repository structure

```
marketplace.json          ← the marketplace index (verified by CI)
plugins/
  <package-id>/
    plugin.json           ← the package manifest
    main.js               ← JS entry file (if needed)
docs/
  authoring.md            ← full manifest + ProviderSpec schema reference
  declarative-plugins.md  ← transform ops + predicate tree reference
  javascript-plugins.md   ← JS sandbox contract, watchdog, named functions
  publishing.md           ← marketplace.json schema, sha256, install flow
  examples.md             ← walkthrough of the 4 example packages
scripts/
  validate.py             ← CI validation script
wiki/                     ← GitHub wiki pages (mirrored from docs/)
.github/
  workflows/
    validate.yml          ← CI workflow
  PULL_REQUEST_TEMPLATE.md
CODEOWNERS
```

---

## Further reading

- [docs/authoring.md](./docs/authoring.md) — full schema reference
- [docs/declarative-plugins.md](./docs/declarative-plugins.md) — all transform ops and predicates
- [docs/javascript-plugins.md](./docs/javascript-plugins.md) — the JS sandbox
- [docs/publishing.md](./docs/publishing.md) — how to publish to the marketplace
- [docs/examples.md](./docs/examples.md) — annotated walkthrough of the 4 example packages

---

## License

MIT — see [LICENSE](./LICENSE).
