# `balli.registry`

## `builtin-types`

Kind: `def`

The set of schema type keywords balli supports natively. Predicate schemas (:balli/pred) are absent by design: that keyword is an AST-only type — in FORMS a predicate schema is the fn/symbol itself (see balli.normalize's pred table).

## `mutation-epoch`

Kind: `def`

Public monotonic counter (starts 0) bumped by every default-registry mutation (`set-default-registry!` / `register!`). balli.core's raw-form cache compares this against the epoch it was filled under and clears itself on mismatch (see the ns docstring's mutation contract).

## `default-registry*`

Kind: `def`

Atom holding the CURRENT default registry map. Mutate only via `set-default-registry!` / `register!` (they bump `mutation-epoch`).

## `default-registry`

Kind: `defn`

Returns the CURRENT default registry — a live view: every raw-form schema/validate call picks up prior mutations.

## `composite`

Kind: `defn`

Merge registries `rs` into one plain registry map with first-hit lookup semantics: on :schemas key conflicts the EARLIEST registry wins; :types are unioned. Eager by design (see the ns docstring's composite note).

## `set-default-registry!`

Kind: `defn`

Replace the default registry with registry map `r` ({:types <set> :schemas <map>} — e.g. built via `composite`). Bumps `mutation-epoch` so raw-form calls immediately see the new default; existing schema objects keep their construction-time snapshot. Returns `r`.

## `register!`

Kind: `defn`

Merge schema forms into the CURRENT default registry's :schemas: (register! kw form) or (register! {kw form ...}). Keys must be keywords; forms are validated lazily at use, like any registry entry. Bumps `mutation-epoch` so raw-form calls immediately see the new meaning; existing schema objects keep their construction-time snapshot. Returns nil.

## `registry`

Kind: `defn`

Layer custom {keyword schema-form} maps over the CURRENT default registry's :schemas (the default is read live, at call time). With no args, returns the current default registry.

## `dynamic-registry`

Kind: `defn`

Registry whose backing registry is read at lookup time from `source`. `source` may be an atom containing a registry map or schema map, or a 0-arg fn returning either shape. This is intentionally explicit instead of relying on dynamic var binding.

## `lazy-registry`

Kind: `defn`

Registry that calls `(provider k)` when keyword `k` is not eagerly present. A non-nil provider result is memoized for future lookups. With two args, `base` is a registry map or plain schema map layered under the provider.

## `var-registry`

Kind: `defn`

Registry backed by a map of keyword -> derefable schema references. Values are dereferenced on every lookup, matching Malli's var-registry use case without requiring Clojure Vars in Basilisp. Non-derefable values are used as schema forms directly.

## `resolve-ref`

Kind: `defn`

Look up a registered schema form by keyword in registry `reg`. Returns nil when the keyword is not registered.

## `push-layer`

Kind: `defn`

Layer the local {kw form} map `local` over registry (or chain) `r`, returning a chain map: :schemas becomes local merged over r's, and :balli/layers gains a fresh-token layer. A plain registry gets an implicit base layer with the constant token 0, so refs that resolve from the base registry key caches identically whether or not any layering happened.

## `resolve-ref-layered`

Kind: `defn`

Resolve keyword `k` against registry (or chain) `r`, innermost layer first. Returns {:form <schema form> :token <layer token> :registry <chain prefix>} or nil when unregistered. The :registry is the chain prefix ending at the layer that supplied the form -- what the target must normalize/compile against (lexical scoping; see the section comment above). Plain registries resolve at the implicit base layer with token 0.
