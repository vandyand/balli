# `balli.experimental`

Experimental Balli helpers for Malli-adjacent schema analysis. These APIs are intentionally small and data-only. They avoid Clojure/JVM runtime dependencies while giving Basilisp users practical equivalents for common malli.experimental-style workflows.

## `paths`

Kind: `defn`

Return every schema path in `s` using Balli/Malli path conventions.

## `leaf-paths`

Kind: `defn`

Return path metadata for schemas with no child schemas.

## `coverage`

Kind: `defn`

Summarize schema shape for docs/tests/tooling.

## `refs`

Kind: `defn`

Return refs mentioned directly in schema `s`, without dereferencing them.

## `dependency-graph`

Kind: `defn`

Return {registry-key #{referenced-registry-keys}} for a registry map or a Balli registry object. Non-keyword inline type forms are ignored.

## `migration-impact`

Kind: `defn`

Classify a schema change using a conservative path diff. Returns :unchanged, :additive, :breaking, or :changed. Removed paths are breaking; added paths are additive; changed existing paths are classified as changed.

## `risk-report`

Kind: `defn`

Return conservative static risk flags for schema `s`. This does not execute user predicates; it highlights shapes that often deserve extra tests.
