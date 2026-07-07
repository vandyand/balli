# `balli.clj-kondo`

Static-analysis metadata exports. This does not run clj-kondo under Basilisp. It emits data describing function schemas so external tools can generate analyzer config.

## `function-config`

Kind: `defn`

Return analyzer-friendly arity metadata for a :=> or :function schema. Root :=> schemas return a single arity map. Root :function schemas return {:arities [...]}.

## `lint-config`

Kind: `defn`

Return a map of symbol -> function-config for schema entries.
