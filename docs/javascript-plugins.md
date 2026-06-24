# JavaScript plugins

JavaScript providers let you implement arbitrary logic in ECMAScript. The runtime is a sandboxed JavaScriptCore context with no external bridges and a hard execution-time watchdog.

Related docs: [authoring.md](./authoring.md) · [declarative-plugins.md](./declarative-plugins.md) · [examples.md](./examples.md)

---

## The function contract

Your JS file must declare one or more global functions. Each provider references exactly one function via its `function` field in `plugin.json` (defaults: `"transform"` for actions, `"matches"` for conditions).

### Action provider

```js
// Called for every clipboard entry this action runs on.
// Input:  text — the clipboard text as a string
// Output: return a string (the new clipboard value)
function transform(text) {
  return text.trim().toUpperCase();
}
```

The function receives one argument — the clipboard text — and must return a string. Any non-string return value causes an error.

### Condition provider

```js
// Called to decide whether a rule fires.
// Input:  text — the clipboard text as a string
// Output: return a boolean
function matches(text) {
  return /^https?:\/\//.test(text);
}
```

The function receives one argument — the clipboard text — and must return a boolean. Any non-boolean return value causes an error.

---

## Sharing a main.js across multiple providers

Multiple providers in the same package can share one script file by specifying different `function` names. The runtime loads the file once and calls each named function independently.

`plugin.json`:
```json
{
  "providers": [
    {
      "id": "com.yourname.pkg.condition",
      "name": "Is URL",
      "description": "True when the text is a URL.",
      "kind": "condition",
      "engine": "javascript",
      "entry": "main.js",
      "function": "matchesURL"
    },
    {
      "id": "com.yourname.pkg.action",
      "name": "Normalise URL",
      "description": "Lowercases the URL scheme and host.",
      "kind": "action",
      "engine": "javascript",
      "entry": "main.js",
      "function": "normaliseURL"
    }
  ]
}
```

`main.js`:
```js
function matchesURL(text) {
  return /^https?:\/\//i.test(text);
}

function normaliseURL(text) {
  try {
    var u = new URL(text);
    return u.protocol + "//" + u.host.toLowerCase() + u.pathname + u.search + u.hash;
  } catch (_) {
    return text;
  }
}
```

---

## The sandbox — what is NOT available

The JS runtime is **bridge-less**. The following are not available and will throw or return `undefined`:

| Not available | Notes |
|---|---|
| `fetch` | No network access. |
| `XMLHttpRequest` | No network access. |
| `require` / `import` | No module system. |
| `setTimeout` / `setInterval` | No async scheduling. |
| `process` | No Node.js globals. |
| File system APIs | No `fs`, no `Deno.readFile`, etc. |
| `console.log` | Not bridged. Use return values for output. |
| `crypto.subtle` | Not bridged (use pure-JS crypto if needed). |

The runtime is pure ECMAScript: `String`, `Array`, `Object`, `RegExp`, `Math`, `JSON`, `URL`, `Date`, `Map`, `Set`, and other standard built-ins are available.

---

## The 250 ms watchdog

A wall-clock execution-time limit of **250 milliseconds** is enforced via `JSContextGroupSetExecutionTimeLimit`. If your function does not return within 250 ms, the runtime terminates the script and reports a timeout error to the user. The watchdog catches infinite loops.

Keep your functions fast. Avoid:
- Long loops over large strings without a stopping condition.
- Backtracking-heavy regular expressions on long inputs (ReDoS).

---

## Capabilities and the v1 bridge

If your plugin needs network or filesystem access in a future version, declare it in the package's `capabilities` array. In **v1**, the sandbox does not have a network or filesystem bridge regardless of declared capabilities — the bridge is planned for a future release.

Declared capabilities are:
- Shown to the user in the install consent dialog.
- Badged in the plugin list UI.
- **Not enforced at runtime in v1.**

Never try to work around the sandbox (e.g. using `eval` to construct bridge calls). Such plugins are removed from the marketplace.

---

## Error handling

Uncaught exceptions inside your function are captured and shown to the user as an error. Return a sensible fallback instead of throwing when possible:

```js
function transform(text) {
  try {
    return doSomething(text);
  } catch (e) {
    return text;  // return the original on failure
  }
}
```

---

## Complete example — reverse text

`plugin.json`:
```json
{
  "id": "com.yourname.reverse",
  "name": "Reverse",
  "version": "1.0.0",
  "description": "Reverses the clipboard text character by character.",
  "capabilities": [],
  "providers": [{
    "id": "com.yourname.reverse.action",
    "name": "Reverse text",
    "description": "Reverses the clipboard text character by character.",
    "kind": "action",
    "engine": "javascript",
    "entry": "main.js"
  }]
}
```

`main.js`:
```js
function transform(text) {
  return text.split("").reverse().join("");
}
```
