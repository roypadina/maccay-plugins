# Example packages walkthrough

This document walks through the four example packages in `plugins/`. They cover the full range of engines, kinds, and patterns.

Related docs: [authoring.md](./authoring.md) · [declarative-plugins.md](./declarative-plugins.md) · [javascript-plugins.md](./javascript-plugins.md)

---

## `example-has-url` — minimal JavaScript condition

**Location:** `plugins/example-has-url/`  
**Files:** `plugin.json`, `main.js`  
**Kind:** condition  
**Engine:** javascript

This is the simplest possible JavaScript condition. The package has one provider that tests whether the clipboard text contains a URL.

`plugin.json`:
```json
{
  "id": "com.maccyplus.example-has-url",
  "name": "Has URL",
  "version": "1.0.0",
  "author": { "name": "MaccyPlus" },
  "description": "True when the clipboard text contains an http or https URL.",
  "capabilities": [],
  "providers": [
    {
      "id": "com.maccyplus.example.has-url",
      "name": "Has URL",
      "description": "True when the clipboard text contains an http or https URL.",
      "kind": "condition",
      "engine": "javascript",
      "entry": "main.js",
      "function": "matches"
    }
  ]
}
```

Key points:
- The `function` field is explicitly set to `"matches"` — for conditions this is also the default, but being explicit is good practice.
- `capabilities: []` because the function reads only the text argument.
- One provider, one JS function.

---

## `example-shout` — minimal declarative action

**Location:** `plugins/example-shout/`  
**Files:** `plugin.json` only (no JS file needed)  
**Kind:** action  
**Engine:** declarative

The simplest declarative action. Uppercases the text and prepends `"SHOUT: "`.

```json
{
  "id": "com.maccyplus.example-shout",
  "name": "Shout",
  "version": "1.0.0",
  "author": { "name": "MaccyPlus" },
  "description": "Uppercases the clipboard text and prepends SHOUT:.",
  "capabilities": [],
  "providers": [
    {
      "id": "com.maccyplus.example.shout",
      "name": "Shout",
      "description": "Uppercases the clipboard text and prepends SHOUT:.",
      "kind": "action",
      "engine": "declarative",
      "declarative": {
        "transform": [
          { "op": "case", "value": "upper" },
          { "op": "prepend", "text": "SHOUT: " }
        ]
      }
    }
  ]
}
```

Key points:
- No JS file at all — `declarative` is self-contained in `plugin.json`.
- The `transform` array is applied left-to-right: uppercase first, then prepend.
- `"SHOUT: "` has a trailing space — `prepend` inserts the string verbatim.

---

## `text-transforms` — multi-provider package mixing engines

**Location:** `plugins/text-transforms/`  
**Files:** `plugin.json`, `main.js`  
**Kind:** action (5 providers)  
**Engines:** declarative (4 providers) + javascript (1 provider)

A package with five action providers: four declarative and one JavaScript, sharing the same `main.js` file.

The four declarative providers are:

| Provider | Transform ops |
|---|---|
| Trim whitespace | `[{"op":"trim"}]` |
| UPPERCASE | `[{"op":"case","value":"upper"}]` |
| lowercase | `[{"op":"case","value":"lower"}]` |
| Strip formatting | `[]` (empty — strips rich-text styling only) |

The fifth provider (`fix-keyboard-layout`) uses JavaScript because the EN ⇄ HE layout mapping requires a lookup table that cannot be expressed as declarative ops:

```json
{
  "id": "com.maccyplus.fix-keyboard-layout",
  "name": "Fix keyboard layout (EN ⇄ HE)",
  "description": "Corrects text typed in the wrong layout by re-mapping between US-QWERTY and Israeli SI-1452. Direction auto-detected.",
  "kind": "action",
  "engine": "javascript",
  "entry": "main.js",
  "function": "transformFixLayout"
}
```

Key points:
- Four providers with `engine: "declarative"` have no `entry` field.
- The fifth provider's `function: "transformFixLayout"` calls a named function in `main.js`.
- The declarative providers do not reference `main.js` at all — the file is only fetched because at least one provider declares `engine: "javascript"`.
- All five providers share one package-level `capabilities: []`.

---

## `unwrap-terminal` — canonical multi-provider package

**Location:** `plugins/unwrap-terminal/`  
**Files:** `plugin.json`, `main.js`  
**Kinds:** 2 conditions + 1 action  
**Engines:** declarative (1) + javascript (2)

This is the most complete example. It shows how a single package can contain a mix of kinds (conditions and actions) and engines, with multiple JS providers sharing one `main.js`.

The three providers:

### 1. Terminal source (condition, declarative)

```json
{
  "id": "com.maccyplus.terminal-source",
  "kind": "condition",
  "engine": "declarative",
  "declarative": {
    "predicate": {
      "any": [
        { "sourceApp": "com.apple.Terminal" },
        { "sourceApp": "com.googlecode.iterm2" },
        { "sourceApp": "dev.warp.Warp-Stable" },
        { "sourceApp": "net.kovidgoyal.kitty" },
        { "sourceApp": "org.alacritty" },
        { "sourceApp": "com.github.wez.wezterm" },
        { "sourceApp": "com.mitchellh.ghostty" },
        { "sourceApp": "com.microsoft.VSCode" }
      ]
    }
  }
}
```

Uses the `any` logical node with `sourceApp` leaves to match a list of known terminal bundle IDs. No JS needed for this.

### 2. Soft-wrapped text (condition, JavaScript)

```json
{
  "id": "com.maccyplus.soft-wrap",
  "kind": "condition",
  "engine": "javascript",
  "entry": "main.js",
  "function": "matchesSoftWrap"
}
```

The heuristic — every line except the last has the same length ≥ 40 — requires logic that the declarative predicate tree cannot express, so JavaScript is used.

### 3. Unwrap (action, JavaScript)

```json
{
  "id": "com.maccyplus.unwrap",
  "kind": "action",
  "engine": "javascript",
  "entry": "main.js",
  "function": "transformUnwrap"
}
```

Both JS providers share the same `main.js` via different `function` values. The app loads `main.js` once and calls `matchesSoftWrap` or `transformUnwrap` as needed.

### Design lesson

This package demonstrates the recommended pattern for complex plugins:
- Use declarative for anything that fits (list of `sourceApp` checks, simple regex, etc.).
- Use JavaScript only where logic is needed.
- Share one JS file across all JS providers in a package — do not create multiple files.
- Keep providers focused: one concern per provider, not one giant provider.
