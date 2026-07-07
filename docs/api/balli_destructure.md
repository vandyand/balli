# `balli.destructure`

Schema-guided destructuring helpers. `destructure` validates/parses a value and returns a smaller shape keyed by schema names: map entries become maps, :catn becomes its tag map, and :orn/:multi/:altn become a one-entry map keyed by the matched branch.

## `destructure`

Kind: `defn`

Validate and destructure `value` according to schema `s`. Returns :balli.core/invalid when parsing fails.

## `paths`

Kind: `defn`

Return [path schema-form] pairs for named schema positions.
