# `balli.normalize`

## `ast-syntax?`

Kind: `defn`

True when `x` is Malli-style map syntax / schema AST input.

## `from-ast-form`

Kind: `defn`

Convert Malli-style map syntax into Balli vector syntax. This accepts the common AST shape {:type t :properties p :children [...]} plus entry maps {:key k :schema s}. It also accepts :=> :input/:output/:guard fields.

## `to-ast`

Kind: `defn`

Return a Malli-style map syntax view of normalized AST node `node`.

## `fn-like?`

Kind: `defn`

True when `x` is function-like: a Basilisp fn, or a Python callable that is not a Basilisp collection, keyword, or symbol. Bare `python/callable` is too broad — keywords, maps, sets, vectors, and symbols all implement __call__ in Basilisp. Canonical home of this predicate (balli.compile aliases it).

## `ifn-like?`

Kind: `defn`

Clojure-idiom predicate position: real fns plus keywords, maps, and sets (all callable lookups routinely used as predicates). Vectors and symbols are callable in Basilisp too but are rejected — they are far more likely to be schema-authoring mistakes than intentional predicates.

## `predicates`

Kind: `def`

pred-key symbol -> canonical validation fn for every predicate schema.

## `pred-form-key`

Kind: `defn`

The pred-key symbol when `x` is a registered predicate schema head (a core fn by identity, or its quoted symbol); nil otherwise. Public: balli.error uses it to key humanize messages off an error's :schema form head.

## `regex-min-max`

Kind: `defn`

Matched-element count bounds for seqex AST node `ast`: {:min n :max m}, :max absent when unbounded (:*/:+/unbounded :repeat). Any non-seqex node counts as one element {:min 1 :max 1} -- including [:schema ...] wrappers, which is exactly their point. Phase 8 uses this for :=>/:function arities.

## `normalize`

Kind: `defn`

Normalize schema `form` to an AST node map. `opts` may carry {:registry r}. A vector form whose properties carry {:registry {kw form ...}} has the local schemas layered over the effective registry — resolved ONCE here as (or (:registry opts) live-default) — for its whole subtree, and its AST node gains :local-registry (see the section comment above). Unknown or invalid forms throw ex-info with {:type :balli.core/invalid-schema}.
