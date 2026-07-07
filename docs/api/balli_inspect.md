# `balli.inspect`

Static inspection helpers for Balli schemas. `problems` is intentionally conservative: it reports malformed schemas, unresolved refs, and export smoke failures without executing user predicate code.

## `problems`

Kind: `defn`

Return a vector of problem maps for schema `s`.

## `valid-schema?`

Kind: `defn`

True when `problems` finds no schema issues.

## `report`

Kind: `defn`

Human-readable inspection report.
