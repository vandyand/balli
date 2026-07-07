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

## `set-entry`

Kind: `defn`

Set or append a :map entry `k` to schema `v`. `entry-props` defaults to {}. Root map properties and existing entry order are preserved; new keys append to the end. This is the non-shadowing Balli equivalent of malli.util/assoc.

## `update-entry`

Kind: `defn`

Update the value schema of :map entry `k` with `(f current-form & args)`. Throws when `k` is absent. Entry/root properties and order are preserved.

## `rename-keys`

Kind: `defn`

Rename :map entries according to `kmap` while preserving entry order and metadata. Later collisions keep the later rewritten entry.

## `transform-entries`

Kind: `defn`

Apply `(f entry-map)` to every :map entry and rebuild the schema. `f` should return {:key k :properties props :schema form}; nil drops the entry.

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

## `path-map`

Kind: `defn`

Return {path schema-form} for every schema node in `s` using Balli walk path conventions. Refs are left as ref nodes.

## `update-at`

Kind: `defn`

Update the schema node at `path` with `(f form & args)`. Throws when the path is not present. This is a form-level counterpart to Malli utility workflows that rewrite nested schemas by path.

## `diff`

Kind: `defn`

Compare two schemas by path and return data about added, removed, and changed schema nodes. Paths are the same vectors used by `walk`/`explain`.
