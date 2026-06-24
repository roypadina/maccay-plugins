# Declarative plugins

Declarative providers are defined entirely in JSON — no code required. The engine interprets the `declarative` object and either transforms text (actions) or evaluates a predicate (conditions).

Related docs: [authoring.md](./authoring.md) · [javascript-plugins.md](./javascript-plugins.md) · [examples.md](./examples.md)

---

## Actions — transform op list

For an action provider, `declarative` must be an object with a `"transform"` key whose value is an array of op objects. The ops are applied in order; each op receives the output of the previous one.

```json
"declarative": {
  "transform": [
    { "op": "trim" },
    { "op": "case", "value": "upper" }
  ]
}
```

An empty `transform` array (`[]`) is a valid no-op action (useful for a "strip formatting" effect, since the app strips rich-text attributes before passing text to any provider).

### Available transform ops

#### `trim`

Removes leading and trailing whitespace and newlines.

```json
{ "op": "trim" }
```

No additional fields.

#### `case`

Converts the text to uppercase or lowercase.

```json
{ "op": "case", "value": "upper" }
{ "op": "case", "value": "lower" }
```

| Field | Required | Values |
|---|---|---|
| `value` | yes | `"upper"` or `"lower"` |

#### `prepend`

Inserts a fixed string before the text.

```json
{ "op": "prepend", "text": "PREFIX: " }
```

| Field | Required | Notes |
|---|---|---|
| `text` | yes | The string to prepend. |

#### `append`

Appends a fixed string after the text.

```json
{ "op": "append", "text": " (copied)" }
```

| Field | Required | Notes |
|---|---|---|
| `text` | yes | The string to append. |

#### `regexReplace`

Replaces regex matches in the text with a replacement string. Uses `NSRegularExpression` (ICU) syntax. The replacement may use `$0`, `$1`, etc. for capture groups.

```json
{
  "op": "regexReplace",
  "pattern": "\\s+",
  "replacement": " "
}
```

With the optional `flags` field:

```json
{
  "op": "regexReplace",
  "pattern": "hello",
  "replacement": "world",
  "flags": "i"
}
```

| Field | Required | Notes |
|---|---|---|
| `pattern` | yes | ICU regex pattern. |
| `replacement` | yes | Replacement string. Capture groups: `$0` (full match), `$1`, `$2`, etc. |
| `flags` | no | Optional flag string. Currently only `"i"` (case-insensitive) is recognised. |

**Example — collapse runs of whitespace:**

```json
{
  "transform": [
    { "op": "trim" },
    { "op": "regexReplace", "pattern": "\\s+", "replacement": " " }
  ]
}
```

---

## Conditions — predicate tree

For a condition provider, `declarative` must be an object with a `"predicate"` key whose value is a predicate tree node.

```json
"declarative": {
  "predicate": { "regex": "^https?://" }
}
```

### Leaf nodes

Exactly one of these keys must appear in a leaf node object.

#### `regex`

Returns `true` if the clipboard text matches the ICU regular expression.

```json
{ "regex": "^https?://\\S+" }
```

#### `contains`

Returns `true` if the clipboard text contains the given substring (case-insensitive).

```json
{ "contains": "TODO" }
```

Returns `false` if the needle is empty.

#### `kind`

Returns `true` if the clipboard entry's type set includes the given `ValueKind`. Supported values: `"text"`, `"image"`, `"file"`, `"color"`.

```json
{ "kind": "text" }
```

#### `sourceApp`

Returns `true` if the clipboard entry was copied from the app with the given bundle ID.

```json
{ "sourceApp": "com.apple.Terminal" }
```

### Logical nodes

Logical nodes combine child nodes. A child can be any valid node (leaf or logical).

#### `all`

Returns `true` if every child is `true` (short-circuits on first `false`).

```json
{ "all": [ { "regex": "^https?://" }, { "contains": "github" } ] }
```

#### `any`

Returns `true` if at least one child is `true` (short-circuits on first `true`).

```json
{ "any": [ { "sourceApp": "com.apple.Terminal" }, { "sourceApp": "com.googlecode.iterm2" } ] }
```

#### `not`

Returns the logical negation of its single child.

```json
{ "not": { "kind": "image" } }
```

### Combining nodes

```json
{
  "predicate": {
    "all": [
      { "kind": "text" },
      { "not": { "contains": "password" } },
      { "any": [
          { "regex": "^https?://" },
          { "contains": "github.com" }
      ]}
    ]
  }
}
```

---

## Complete declarative examples

### Action: trim + uppercase

```json
{
  "id": "com.yourname.shout",
  "name": "Shout",
  "version": "1.0.0",
  "description": "Trims whitespace then uppercases the text.",
  "capabilities": [],
  "providers": [{
    "id": "com.yourname.shout.action",
    "name": "Shout",
    "description": "Trims whitespace then uppercases the text.",
    "kind": "action",
    "engine": "declarative",
    "declarative": {
      "transform": [
        { "op": "trim" },
        { "op": "case", "value": "upper" }
      ]
    }
  }]
}
```

### Condition: URL detector

```json
{
  "id": "com.yourname.has-url",
  "name": "Has URL",
  "version": "1.0.0",
  "description": "True when the clipboard text contains an http or https URL.",
  "capabilities": [],
  "providers": [{
    "id": "com.yourname.has-url.condition",
    "name": "Has URL",
    "description": "True when the clipboard text contains an http or https URL.",
    "kind": "condition",
    "engine": "declarative",
    "declarative": {
      "predicate": { "regex": "https?://\\S+" }
    }
  }]
}
```
