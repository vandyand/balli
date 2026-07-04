# Balli

Data-driven schemas for [Basilisp](https://github.com/basilisp-lang/basilisp), inspired by [Malli](https://github.com/metosin/malli).

Schemas are plain data in Malli's vector syntax — no macros, no protocols to implement. Balli normalizes a schema form into an AST and compiles it into fast validator/explainer closures, produces Malli-shaped explain data with `:path`/`:in`, humanizes errors into structures that mirror your value, and supports custom registries with (recursive) refs. Pure Basilisp; no Python dependencies beyond the standard library.

## Install

From source:

```bash
git clone https://github.com/vandyand/balli.git
cd balli
pip install .
```

On PEP-668 ("externally managed environment") systems, either use a virtualenv or add `--break-system-packages`:

```bash
pip install . --break-system-packages
```

## Quick start

Validate:

```clojure
(require '[balli.core :as b])

(b/validate [:map
             [:id :string]
             [:age {:optional true} [:int {:min 0}]]]
            {:id "abc" :age 3})
;; => true
```

Explain why a value fails (nil when it doesn't):

```clojure
(b/explain [:vector :int] [1 "x"])
;; => {:schema [:vector :int]
;;     :value [1 "x"]
;;     :errors [{:path [0] :in [1] :schema :int :value "x"
;;               :type :balli.core/invalid-type}]}
```

Humanize explain data into messages shaped like the value:

```clojure
(require '[balli.error :as be])

(be/humanize (b/explain [:map [:x :int]] {:x "s"}))
;; => {:x ["should be an integer"]}

(be/humanize (b/explain [:string {:min 3}] "ab"))
;; => ["should be at least 3 characters"]
```

Register schemas by qualified keyword and reference them — directly or via `[:ref ...]`:

```clojure
(require '[balli.registry :as reg])

(def r (reg/registry {:user/id   [:string {:min 1}]
                      :user/user [:map [:id :user/id]]}))

(b/validate :user/user {:id "abc"} {:registry r})
;; => true

(b/validate [:ref :user/id] "" {:registry r})
;; => false
```

Recursive schemas terminate on finite data:

```clojure
(def tree-registry
  (reg/registry {:tree/node [:map
                             [:value :int]
                             [:children [:vector [:ref :tree/node]]]]}))

(b/validate [:ref :tree/node]
            {:value 1 :children [{:value 2 :children []}]}
            {:registry tree-registry})
;; => true

(b/validate [:ref :tree/node]
            {:value 1 :children [{:value "x" :children []}]}
            {:registry tree-registry})
;; => false
```

Assert, getting the value back or an `ex-info` carrying the explain map:

```clojure
(b/assert-valid :int 5)
;; => 5

(try (b/assert-valid :int "x")
     (catch python/Exception e (:type (ex-data e))))
;; => :balli.core/invalid-input
```

## Supported schemas

All 27 schema types, each with a validating example:

| Type | Example |
|---|---|
| `:any` | `(b/validate :any 42)` |
| `:nil` | `(b/validate :nil nil)` |
| `:string` | `(b/validate [:string {:min 1}] "hi")` |
| `:int` | `(b/validate [:int {:min 0 :max 10}] 5)` |
| `:float` | `(b/validate :float 1.5)` |
| `:double` | `(b/validate :double 1.5)` (alias of `:float` — Python has one float type) |
| `:number` | `(b/validate :number 1)` (int or float) |
| `:boolean` | `(b/validate :boolean true)` |
| `:keyword` | `(b/validate :keyword :a)` |
| `:symbol` | `(b/validate :symbol 'foo)` |
| `:uuid` | `(b/validate :uuid (random-uuid))` |
| `:map` | `(b/validate [:map [:x :int] [:y {:optional true} :string]] {:x 1})` |
| `:map-of` | `(b/validate [:map-of :keyword :int] {:a 1 :b 2})` |
| `:vector` | `(b/validate [:vector :int] [1 2 3])` |
| `:sequential` | `(b/validate [:sequential :int] '(1 2))` |
| `:set` | `(b/validate [:set :int] #{1 2})` |
| `:tuple` | `(b/validate [:tuple :string :int] ["a" 1])` |
| `:enum` | `(b/validate [:enum "S" "M" "L"] "M")` |
| `:=` | `(b/validate [:= 42] 42)` |
| `:maybe` | `(b/validate [:maybe :int] nil)` |
| `:and` | `(b/validate [:and :int [:fn even?]] 4)` |
| `:or` | `(b/validate [:or :int :string] "x")` |
| `:not` | `(b/validate [:not :string] 1)` |
| `:fn` | `(b/validate [:fn {:error/message "must be even"} even?] 4)` (thrown exceptions count as invalid) |
| `:multi` | `(b/validate [:multi {:dispatch :kind} [:cat [:map [:kind [:= :cat]]]]] {:kind :cat})` |
| `:re` | `(b/validate [:re #"\d+"] "123")` (full match; string patterns compiled via `re-pattern`) |
| `:ref` | `(b/validate [:ref :user/id] "abc" {:registry (reg/registry {:user/id :string})})` |

## Properties

| Property | Applies to | Meaning |
|---|---|---|
| `:min` / `:max` | `:string` (length), `:int`/`:float`/`:double`/`:number` (value), `:vector`/`:sequential`/`:set`/`:map-of` (element count) | Inclusive bounds; violations produce `:balli.core/limits` errors |
| `:closed` | `:map` | When `true`, keys not declared in the schema are rejected (`:balli.core/extra-key`); maps are open by default |
| `:optional` | `:map` entries (entry-level props: `[:k {:optional true} schema]`) | Key may be absent; when present its value must still match |
| `:error/message` | any schema | Overrides the default humanized message for errors at that schema |
| `:dispatch` | `:multi` (required) | Keyword or function used to pick the child schema; unknown dispatch values are invalid (`:balli.core/invalid-dispatch-value`) |

## API

All functions live in `balli.core` unless noted. `s` is a raw schema form or a schema object; `opts` supports `{:registry r}` and is ignored when `s` is already a schema object (its baked-in registry wins).

| Function | Signature | Description |
|---|---|---|
| `schema` | `(schema form)` `(schema form opts)` | Wrap a form into a schema object (normalized AST + registry + compile cache). Idempotent on schema objects. |
| `schema?` | `(schema? x)` | True when `x` is a balli schema object. |
| `form` | `(form s)` | The original schema form. |
| `properties` | `(properties s)` | Properties map of the root node, e.g. `{:closed true}`. |
| `children` | `(children s)` | AST children of the root node. |
| `validator` | `(validator s)` `(validator s opts)` | Compiled 1-arg boolean validator. Cached on the schema object, or in a bounded global cache for raw forms. |
| `validate` | `(validate s value)` `(validate s value opts)` | Boolean. |
| `explainer` | `(explainer s)` `(explainer s opts)` | Compiled 1-arg explainer: nil on success, else `{:schema :value :errors}`. Cached like `validator`. |
| `explain` | `(explain s value)` `(explain s value opts)` | nil when valid, else the explain map. Each error is `{:path :in :schema :value :type}` where `:path` indexes into the schema form and `:in` into the value. |
| `assert-valid` | `(assert-valid s value)` `(assert-valid s value opts)` | Returns `value`, or throws `ex-info` with the explain map plus `{:type :balli.core/invalid-input}`. |
| `balli.error/humanize` | `(humanize explain-map)` | Human-readable messages mirroring the value shape; nil in, nil out. |
| `balli.registry/registry` | `(registry & schema-maps)` | Layer `{qualified-kw schema-form}` maps over the default registry. |
| `balli.registry/default-registry` | `(default-registry)` | Builtin types, no custom schemas. |
| `balli.registry/resolve-ref` | `(resolve-ref reg k)` | Registered schema form for `k`, or nil. |
| `balli.registry/builtin-types` | var | The set of 27 builtin type keywords. |

Unknown schema forms throw `ex-info` with `:type :balli.core/invalid-schema`; a `:ref` to an unregistered keyword throws `:balli.core/unresolved-ref` at compile time (fail fast, not at validate).

## Differences from Malli

Balli is an honest **subset** of Malli — the core validate/explain/humanize/registry workflow — not a port:

- **No transformers** — no `decode`/`encode`/coercion.
- **No generators** — no `mg/generate`, no test.check integration.
- **No JSON Schema export** (or Swagger, or schema inference).
- **No sequence schemas** (`:cat`/`:alt`/`:*`/`:+`/`:?`/`:repeat`) and **no function schemas** (`:=>`, instrumentation).
- **Basilisp data only** — validators check Basilisp data structures (maps, vectors, sets, ...). Python `dict`/`list` values are *not* accepted; convert at the interop boundary first.
- **Set element `:in`** uses the element's seq-order ordinal (sets are unordered; the index identifies which element in seq order failed, not a stable position).
- **Mixed-level humanize uses `:balli/error`** — when a value has errors of its own *and* nested child errors (e.g. `[:vector {:min 3} :int]` on `[1 "x"]`), `humanize` renders that level as a map with child entries plus the level's own messages under the reserved `:balli/error` key: `{1 ["should be an integer"] :balli/error ["should have at least 3 elements"]}`.

## Development

```bash
# run the test suite (pytest via basilisp)
basilisp test            # or: scripts/test.sh

# lint = compile-check every namespace under src/
basilisp run scripts/compile_check.lpy
```

There is no clj-kondo for Basilisp; the compile-check script (which imports every `src/**/*.lpy` namespace and fails on any compile error) is the lint step.

## License

[MIT](LICENSE) © 2026 Andrew VanDyke
