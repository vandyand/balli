# `balli.clj-kondo`

## `function-config`

Kind: `defn`

Return analyzer-friendly arity metadata for a :=> or :function schema. Root :=> schemas return a single arity map. Root :function schemas return {:arities [...]}.

## `lint-config`

Kind: `defn`

Return a map of symbol -> function-config for schema entries.
