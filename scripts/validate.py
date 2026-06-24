#!/usr/bin/env python3
"""
Maccay plugin marketplace validator.

Validates every plugins/*/plugin.json manifest and verifies that every entry
in marketplace.json has a sha256 that matches the committed plugin.json.

Exit 0 on success, nonzero on any failure.
"""

import hashlib
import json
import os
import sys

# ---------------------------------------------------------------------------
# Constants matching PluginManifest.swift / PluginCore.swift exactly
# ---------------------------------------------------------------------------

KNOWN_CAPABILITIES = {"network", "fileRead", "fileWrite", "storage"}
KNOWN_ENGINES = {"declarative", "javascript"}  # "native" is rejected
KNOWN_KINDS = {"action", "condition"}
DESCRIPTION_MAX_LEN = 120

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_of_file(path: str) -> str:
    """Lowercase hex SHA-256 of a file (mirrors MarketplaceResolver.sha256Hex)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def err(path: str, msg: str) -> str:
    return f"  ERROR [{path}]: {msg}"


# ---------------------------------------------------------------------------
# Plugin manifest validation
# (mirrors PluginManifest.validate() + ProviderSpec validation in Swift)
# ---------------------------------------------------------------------------

def validate_provider(spec: dict, plugin_folder: str) -> list[str]:
    """Validate one provider spec. Returns a list of error strings."""
    errors: list[str] = []
    label = spec.get("id") or "(no id)"

    # Required string fields — must be present and non-blank
    for field in ("id", "name", "description"):
        val = spec.get(field)
        if not val or not str(val).strip():
            errors.append(err(label, f"provider.{field} is missing or blank"))

    # description length
    desc = spec.get("description", "")
    if len(desc) > DESCRIPTION_MAX_LEN:
        errors.append(
            err(label, f"provider.description is {len(desc)} chars (max {DESCRIPTION_MAX_LEN})")
        )

    # kind
    kind = spec.get("kind")
    if kind not in KNOWN_KINDS:
        errors.append(err(label, f"provider.kind must be one of {sorted(KNOWN_KINDS)}, got {kind!r}"))

    # engine — "native" is explicitly rejected
    engine = spec.get("engine")
    if engine == "native":
        errors.append(err(label, "provider.engine must not be 'native' (reserved for built-in providers)"))
    elif engine not in KNOWN_ENGINES:
        errors.append(err(label, f"provider.engine must be one of {sorted(KNOWN_ENGINES)}, got {engine!r}"))
    elif engine == "declarative":
        if spec.get("declarative") is None:
            errors.append(err(label, "engine is 'declarative' but 'declarative' key is missing"))
    elif engine == "javascript":
        entry = spec.get("entry")
        if not entry or not str(entry).strip():
            errors.append(err(label, "engine is 'javascript' but 'entry' is missing or blank"))
        else:
            # Verify the entry file actually exists in the plugin folder
            entry_path = os.path.join(plugin_folder, entry)
            if not os.path.isfile(entry_path):
                errors.append(
                    err(label, f"entry file '{entry}' does not exist in {plugin_folder}")
                )

    return errors


def validate_plugin_json(path: str) -> list[str]:
    """Validate one plugin.json. Returns a list of error strings."""
    errors: list[str] = []
    plugin_folder = os.path.dirname(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as exc:
        return [err(path, f"invalid JSON: {exc}")]
    except OSError as exc:
        return [err(path, f"cannot read file: {exc}")]

    if not isinstance(manifest, dict):
        return [err(path, "top-level value must be a JSON object")]

    # Package-level required fields
    for field in ("id", "name", "version", "description"):
        val = manifest.get(field)
        if not val or not str(val).strip():
            errors.append(err(path, f"{field} is missing or blank"))

    # Package description length
    desc = manifest.get("description", "")
    if len(desc) > DESCRIPTION_MAX_LEN:
        errors.append(
            err(path, f"description is {len(desc)} chars (max {DESCRIPTION_MAX_LEN})")
        )

    # capabilities — must be an array of known values (or absent/null treated as [])
    caps = manifest.get("capabilities")
    if caps is not None:
        if not isinstance(caps, list):
            errors.append(err(path, "capabilities must be an array"))
        else:
            for cap in caps:
                if cap not in KNOWN_CAPABILITIES:
                    errors.append(
                        err(path, f"unknown capability {cap!r}; known: {sorted(KNOWN_CAPABILITIES)}")
                    )

    # providers — must be a non-empty array
    providers = manifest.get("providers")
    if not isinstance(providers, list) or len(providers) == 0:
        errors.append(err(path, "providers must be a non-empty array"))
    else:
        for spec in providers:
            if not isinstance(spec, dict):
                errors.append(err(path, "each provider must be a JSON object"))
                continue
            errors.extend(validate_provider(spec, plugin_folder))

    return errors


# ---------------------------------------------------------------------------
# Marketplace index validation
# (mirrors Marketplace.swift + MarketplaceResolver)
# ---------------------------------------------------------------------------

def validate_marketplace(marketplace_path: str, plugins_dir: str) -> list[str]:
    """
    Validate marketplace.json:
    - Every entry points to an existing plugin folder.
    - The sha256 of the committed plugin.json matches the entry's sha256.
    """
    errors: list[str] = []

    try:
        with open(marketplace_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    except json.JSONDecodeError as exc:
        return [err(marketplace_path, f"invalid JSON: {exc}")]
    except OSError as exc:
        return [err(marketplace_path, f"cannot read file: {exc}")]

    if not isinstance(index, dict):
        return [err(marketplace_path, "top-level value must be a JSON object")]

    entries = index.get("plugins")
    if not isinstance(entries, list):
        return [err(marketplace_path, "'plugins' must be an array")]

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(err(marketplace_path, "each plugin entry must be a JSON object"))
            continue

        entry_id = entry.get("id", "(no id)")

        # Resolve the plugin folder from the source
        source = entry.get("source")
        if not isinstance(source, dict):
            errors.append(err(marketplace_path, f"[{entry_id}] source must be an object"))
            continue

        source_type = source.get("type")
        if source_type == "github":
            path_in_repo = source.get("path", "")
            if path_in_repo:
                # path_in_repo is relative to repo root, e.g. "plugins/example-shout"
                plugin_folder = os.path.join(
                    os.path.dirname(marketplace_path), path_in_repo
                )
            else:
                plugin_folder = os.path.dirname(marketplace_path)
        elif source_type == "url":
            # For url sources we cannot resolve a local folder — skip folder checks
            plugin_folder = None
        else:
            errors.append(
                err(marketplace_path, f"[{entry_id}] unknown source type {source_type!r}")
            )
            continue

        if plugin_folder is not None:
            plugin_json_path = os.path.join(plugin_folder, "plugin.json")
            if not os.path.isdir(plugin_folder):
                errors.append(
                    err(marketplace_path, f"[{entry_id}] plugin folder does not exist: {plugin_folder}")
                )
                continue
            if not os.path.isfile(plugin_json_path):
                errors.append(
                    err(marketplace_path, f"[{entry_id}] plugin.json not found in {plugin_folder}")
                )
                continue

            # Verify sha256
            declared_sha = entry.get("sha256", "")
            actual_sha = sha256_of_file(plugin_json_path)
            if declared_sha.lower() != actual_sha.lower():
                errors.append(
                    err(
                        marketplace_path,
                        f"[{entry_id}] sha256 mismatch\n"
                        f"    declared: {declared_sha}\n"
                        f"    actual:   {actual_sha}",
                    )
                )

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # Resolve paths relative to the script's location (repo root expected to
    # contain plugins/ and marketplace.json alongside scripts/).
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    plugins_dir = os.path.join(repo_root, "plugins")
    marketplace_path = os.path.join(repo_root, "marketplace.json")

    all_errors: list[str] = []
    plugins_validated = 0

    # --- Validate every plugin.json ---
    if os.path.isdir(plugins_dir):
        for pkg_name in sorted(os.listdir(plugins_dir)):
            pkg_path = os.path.join(plugins_dir, pkg_name)
            if not os.path.isdir(pkg_path):
                continue
            plugin_json = os.path.join(pkg_path, "plugin.json")
            if not os.path.isfile(plugin_json):
                all_errors.append(
                    err(pkg_path, f"plugin folder '{pkg_name}' has no plugin.json")
                )
                continue
            errs = validate_plugin_json(plugin_json)
            if errs:
                all_errors.extend(errs)
            else:
                plugins_validated += 1
    else:
        print(f"WARNING: plugins/ directory not found at {plugins_dir}")

    # --- Validate marketplace.json ---
    if os.path.isfile(marketplace_path):
        errs = validate_marketplace(marketplace_path, plugins_dir)
        all_errors.extend(errs)
    else:
        print(f"WARNING: marketplace.json not found at {marketplace_path}")

    # --- Report ---
    if all_errors:
        print(f"FAIL — {len(all_errors)} error(s) found:\n")
        for e in all_errors:
            print(e)
        return 1

    print(
        f"OK — {plugins_validated} plugin(s) valid; "
        f"marketplace.json sha256 hashes verified."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
