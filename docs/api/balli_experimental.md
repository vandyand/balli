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
