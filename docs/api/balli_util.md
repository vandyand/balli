# `balli.util`

Schema utilities (Malli's malli.util, form->form). Every fn accepts a raw schema form or a balli schema object and returns a plain schema FORM (never a schema object). Entry introspection goes through balli.normalize; `opts` (where accepted) supports {:registry r} for raw forms — schema objects use their baked-in registry. Refs are never dereferenced: a ref-valued entry participates as its form (the bare keyword or [:ref k]), matching balli.core/walk's refs-not-entered rule.

## `merge`

Kind: `defn`

Merge two :map schema forms (nil either side => the other). Root props shallow-merge (s2 wins); s1's entries keep their order, s2-only entries append in s2 order; duplicate keys merge entry props, requiredness follows the LATER entry, and value schemas deep-merge when both are :map (else s2's wins). Not both :map => s2's form.

## `union`

Kind: `defn`

Union of two schema forms. Like `merge`, but duplicate-key (and not-both-:map) value schemas combine as: equal forms => s1's, differing => [:or s1 s2]; an entry is optional when optional in EITHER side (required only when required in both).

## `select-keys`

Kind: `defn`

Keep only the :map entries of `s` whose key is in `ks` (root props preserved, entry order preserved).

## `dissoc`

Kind: `defn`

Remove the :map entry of `s` keyed `k`.

## `optional-keys`

Kind: `defn`

Set {:optional true} on the given :map entries (all entries when `ks` is omitted or nil).

## `required-keys`

Kind: `defn`

Remove :optional from the given :map entries (all entries when `ks` is omitted or nil).

## `entries`

Kind: `defn`

Return map-entry metadata for `s` in schema order. Each entry is {:key k :properties props :schema value-form :optional bool}. Throws when `s` is not a :map schema.

## `keys`

Kind: `defn`

Return the declared :map entry keys of `s` in schema order.

## `optional-key?`

Kind: `defn`

Return true when :map schema `s` has key `k` marked optional.

## `required-key?`

Kind: `defn`

Return true when :map schema `s` has required key `k`.

## `closed-schema`

Kind: `defn`

Recursively add {:closed true} to every :map schema in `s` that does not explicitly carry {:closed false}. Returns a form.

## `open-schema`

Kind: `defn`

Recursively remove :closed from every :map schema in `s`, except maps explicitly marked {:closed false} (kept as-is). Returns a form.

## `get`

Kind: `defn`

Sub-schema form of `s` at key/index `k`: :map/:multi/:orn/:catn/:altn entries by entry key (tag), indexed children (:and/:or/:tuple/:maybe/:not/ colls/:map-of/:cat/:alt/:?/:*/:+/:repeat/:schema) by integer index. nil when absent. Refs are not dereferenced.

## `get-in`

Kind: `defn`

`get` repeatedly along `ks`; nil as soon as any step is absent. Empty `ks` returns the form of `s` itself.
