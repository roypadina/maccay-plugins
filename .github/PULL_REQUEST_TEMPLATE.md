# Plugin submission checklist

Thank you for contributing to maccay-plugins! Please confirm each item before requesting review.

## Plugin manifest

- [ ] `plugin.json` is present in `plugins/<package-id>/`
- [ ] Package `id` is non-empty, reverse-DNS format, and unique in this repo
- [ ] Package `name`, `version`, and `description` are non-empty
- [ ] Package `description` is 120 characters or fewer
- [ ] `providers` array is non-empty
- [ ] Each provider has non-empty `id`, `name`, `description`, `kind`, and `engine`
- [ ] Each provider `description` is 120 characters or fewer
- [ ] Declarative providers include a `declarative` object
- [ ] JavaScript providers include a non-empty `entry` filename
- [ ] The referenced JS entry file (`main.js`, etc.) exists in the plugin folder
- [ ] All declared `capabilities` are from the allowed set: `network`, `fileRead`, `fileWrite`, `storage`
- [ ] No undeclared network or filesystem access in the JS code
- [ ] No `engine: "native"` providers
- [ ] No obfuscated JavaScript

## marketplace.json

- [ ] A new entry has been added to the `plugins` array in `marketplace.json`
- [ ] The entry `id` matches the package `id` in `plugin.json`
- [ ] The entry `version` matches the package `version` in `plugin.json`
- [ ] The `sha256` was computed with: `shasum -a 256 plugins/<id>/plugin.json`
- [ ] The `source` object uses `"type": "github"` with correct `repo`, `ref`, and `path`

## CI

- [ ] `scripts/validate.py` passes locally (`python3 scripts/validate.py` from the repo root)

## Notes

<!-- Describe what this plugin does and why it's useful. Include any caveats or future plans. -->
