# `balli.provider`

## `provide`

Kind: `defn`

Infer a schema FORM from `samples` (any seqable of values). `opts` supports {:map-of-threshold n} (default 3) for the [:map-of ...] heuristic. Every sample validates against the returned form. No samples -> :any.
