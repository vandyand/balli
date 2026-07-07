# `balli.compile`

AST -> compiled validator + explainer closures. Entry points: (compile-validator ast registry) -> 1-arg fn returning boolean (compile-explainer ast registry) -> fn [value path in] returning a vector of error maps {:path :in :schema <original-form-fragment> :value :type} (compile-parser ast registry) -> 1-arg fn returning the parsed value or the sentinel :balli.core/invalid (compile-unparser ast registry) -> exact inverse of the parser, same sentinel on mismatch Compilation walks the AST once, producing a closure tree — no per-call interpretation. Refs resolve eagerly at compile time (unresolved refs throw ex-info {:type :balli.core/unresolved-ref}) but their targets compile lazily through a per-compilation cache atom (fn indirection), so recursive schemas (Phase 5) terminate on finite data. Local {:registry ...} schema properties layer the registry per subtree (balli.registry/push-layer); ref caches are keyed [kw layer-token] so shadowed keywords never share compiled fns (see compile-ref).

## `regex-op?`

Kind: `defn`

True when AST node `node` is a sequence (regex) operator whose combinator splices into a parent seqex's element stream.

## `regex-min-max`

Kind: `def`

Matched-element count bounds for seqex AST node `ast`: {:min n :max m}, :max absent when unbounded. Moved to balli.normalize in Phase 8 (so :function normalization can check arity distinctness); re-exported here at its original Phase 6 home.

## `fn-like?`

Kind: `def`

Return true for callable values Balli can treat as functions.

## `compile-validator`

Kind: `defn`

Compile AST node `ast` against `registry` into a 1-arg validator fn returning a boolean. Refs are resolved via the registry; unresolved refs throw ex-info {:type :balli.core/unresolved-ref}. `opts` supports {:balli.core/function-checker chk} -- when present, :=>/:function validate generatively through the checker instead of by callable check.

## `compile-explainer`

Kind: `defn`

Compile AST node `ast` against `registry` into an explainer fn [value path in] returning a vector of error maps (empty when valid). Error :schema carries the original form fragment stored on the AST node as :form, not the AST itself. `opts` supports {:balli.core/function-checker chk} -- see compile-validator.

## `compile-parser`

Kind: `defn`

Compile AST node `ast` against `registry` into a 1-arg parser fn: value -> parsed value | :balli.core/invalid. :orn/:multi parse into Tag records; everything else is structure-preserving. An :and with two or more transforming children throws ex-info {:type :balli.core/invalid-schema} here (compile time), not at normalize -- the analysis derefs refs, which needs the registry.

## `compile-unparser`

Kind: `defn`

Compile AST node `ast` against `registry` into a 1-arg unparser fn -- the exact inverse of compile-parser: parsed value -> original value | :balli.core/invalid.
