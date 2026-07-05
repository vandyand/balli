# `balli.error`

## `levenshtein`

Kind: `defn`

Levenshtein edit distance between (str a) and (str b). Iterative full-matrix dynamic programming (row by row) — no recursion.

## `with-spell-checking`

Kind: `defn`

Rewrite an explain map's :errors with key/value spell-checking: - :balli.core/extra-key within threshold of an absent declared key -> :balli.error/misspelled-key + :balli.error/likely-misspelling-of (vector of value paths to the likely intended keys, best match first) - :balli.core/invalid-dispatch-value on a keyword-dispatch :multi -> :balli.error/misspelled-value + :balli.error/likely-misspelling-of - :balli.core/missing-key errors whose :in is a likely-misspelling target are dropped (the key isn't missing — it's misspelled). nil (valid input) passes through; explain maps with no matching errors are returned unchanged.

## `humanize`

Kind: `defn`

Turn an explain map (from balli.core/explain) into a human-readable structure mirroring the value shape. nil in -> nil out. When a level has both its own errors and nested child errors (e.g. a collection :min violation alongside a bad element), the level renders as a map and its own messages live under the reserved :balli/error key.
