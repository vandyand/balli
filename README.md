# Balli

Data-driven schemas for [Basilisp](https://github.com/basilisp-lang/basilisp), inspired by [Malli](https://github.com/metosin/malli).

Schemas are plain data in Malli's vector syntax — no macros, no protocols to implement. Balli covers most of Malli's surface: validation and Malli-shaped explain data with `:path`/`:in`, humanized errors with key spell-checking and localized/custom messages, value transformation (decode/encode/coerce), parse/unparse with tagged branches, sequence (regex) schemas with an iterative backtracking engine, function schemas with generative checking and instrumentation, deterministic seeded generators with regex generation and heuristic shrinking, JSON Schema/OpenAPI/Swagger/DOT/PlantUML/description export, schema utilities (`merge`/`union`/`closed-schema`/...), form walking, safe schema serialization through named function refs, custom schema type extensions, schema inference from sample data, predicate/comparator schemas, time schemas, default branches, self-contained local registries, and mutable/lazy/dynamic custom registries with recursive refs. Malli-inspired, not a strict port — see [Differences from Malli](#differences-from-malli). Pure Basilisp; no Python dependencies beyond the standard library.

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

Make a schema self-contained with a local `:registry` property. The registry
scopes over the whole subtree, including recursive refs:

```clojure
(def local-tree
  [:schema {:registry {:tree/node [:maybe [:map
                                           [:value :int]
                                           [:children [:vector [:ref :tree/node]]]]]}}
   :tree/node])

(b/validate local-tree {:value 1 :children [{:value 2 :children []}]})
;; => true
```

Use `:balli.core/default` entries for residual map keys or fallback `:multi`
branches:

```clojure
(def with-default
  [:map {:closed true}
   [:id :int]
   [:balli.core/default [:map-of :keyword :string]]])

(b/validate with-default {:id 1 :extra "ok"})
;; => true

(be/humanize (b/explain with-default {:id 1 :extra 2}))
;; => {:extra ["should be a string"]}
```

Decode time values with the separate time transformer:

```clojure
(require '[balli.transform :as bt])

(def decoded
  (b/decode [:map [:created :time/instant] [:ttl :time/duration]]
            {:created "2024-06-01T12:00:00+00:00" :ttl "PT15M"}
            (bt/transformer (bt/json-transformer) (bt/time-transformer))))

(b/validate [:map [:created :time/instant] [:ttl :time/duration]] decoded)
;; => true
```

Predicate functions/symbols and comparators are schemas:

```clojure
(b/validate int? 1)     ;; => true
(b/validate 'int? "x")  ;; => false
(b/validate [:> 10] 11) ;; => true

(be/humanize (b/explain [:<= 10] 11))
;; => ["should be at most 10"]
```

Assert, getting the value back or an `ex-info` carrying the explain map:

```clojure
(b/assert-valid :int 5)
;; => 5

(try (b/assert-valid :int "x")
     (catch python/Exception e (:type (ex-data e))))
;; => :balli.core/invalid-input
```

Decode values with a transformer:

```clojure
(require '[balli.transform :as bt])

(b/decode [:map [:age :int] [:tags [:set :keyword]]]
          {:age "42" :tags ["a" "b"]}
          (bt/string-transformer))
;; => {:age 42 :tags #{:a :b}}
```

Parse into tagged branches (and back):

```clojure
(b/parse [:orn [:num :int] [:str :string]] 42)
;; => #balli.compile.Tag{:key :num :value 42}

(b/parse :int "x")
;; => :balli.core/invalid
```

Validate sequences with regex schemas:

```clojure
(b/validate [:cat :int [:* :string]] [1 "a" "b"])
;; => true

(b/validate [:cat :int [:* :string]] [1 "a" 2])
;; => false
```

Generate values, deterministically under a seed:

```clojure
(require '[balli.generator :as bg])

(bg/generate [:map [:id :uuid] [:n [:int {:min 0 :max 9}]]] {:seed 1})
;; => {:id #uuid "4283fefc-63f0-cd0e-873a-0000c6d07ef7" :n 5}
```

Infer a schema from sample data:

```clojure
(require '[balli.provider :as bp])

(bp/provide [{:x 1} {:x 2 :y "a"}])
;; => [:map [:x :int] [:y {:optional true} :string]]
```

## Supported schemas

All 56 builtin schema type keywords, each with a validating example. Predicate
schemas are supported too, but they are not builtin keywords: the schema is the
predicate fn or quoted symbol itself, e.g. `int?` or `'int?`.

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
| `:time/instant` | `(b/validate :time/instant (datetime/datetime 2024 1 1 0 0 0 0 ** :tzinfo datetime.timezone/utc))` |
| `:time/offset-date-time` | aware `datetime.datetime` |
| `:time/zoned-date-time` | aware `datetime.datetime` whose `tzinfo` is `zoneinfo.ZoneInfo` |
| `:time/local-date-time` | `(b/validate :time/local-date-time (datetime/datetime 2024 1 1))` |
| `:time/local-date` | `(b/validate :time/local-date (datetime/date 2024 1 1))` |
| `:time/local-time` | `(b/validate :time/local-time (datetime/time 10 0 0))` |
| `:time/offset-time` | offset-aware `datetime.time` |
| `:time/duration` | `(b/validate :time/duration (datetime/timedelta ** :seconds 900))` |
| `:time/period` | map `{:years int :months int :days int}` |
| `:time/zone-id` | IANA zone string accepted by `zoneinfo.ZoneInfo` |
| `:time/zone-offset` | `datetime.timezone` |
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
| `:andn` | `(b/validate [:andn [:type :int] [:positive [:> 0]]] 7)` |
| `:or` | `(b/validate [:or :int :string] "x")` |
| `:orn` | `(b/validate [:orn [:num :int] [:str :string]] 42)` (named branches; parses to a `Tag`) |
| `:not` | `(b/validate [:not :string] 1)` |
| `:fn` | `(b/validate [:fn {:error/message "must be even"} even?] 4)` (thrown exceptions count as invalid) |
| `:multi` | `(b/validate [:multi {:dispatch :kind} [:cat [:map [:kind [:= :cat]]]]] {:kind :cat})` |
| `:re` | `(b/validate [:re #"\d+"] "123")` (full match; string patterns compiled via `re-pattern`) |
| `:ref` | `(b/validate [:ref :user/id] "abc" {:registry (reg/registry {:user/id :string})})` |
| `:cat` | `(b/validate [:cat :int :string] [1 "a"])` (sequence concatenation) |
| `:catn` | `(b/validate [:catn [:n :int] [:s :string]] [1 "x"])` (named `:cat`; parses to `Tags`) |
| `:alt` | `(b/validate [:alt :int :string] ["x"])` (one-element alternatives, in a sequence) |
| `:altn` | `(b/validate [:altn [:n :int] [:s :string]] [1])` (named `:alt`; parses to a `Tag`) |
| `:?` | `(b/validate [:? :int] [])` (zero or one) |
| `:*` | `(b/validate [:* :int] [1 2 3])` (zero or more) |
| `:+` | `(b/validate [:+ :int] [1])` (one or more) |
| `:repeat` | `(b/validate [:repeat {:min 1 :max 3} :int] [1 2])` (bounded repetition) |
| `:schema` | `(b/validate [:schema :int] 5)` (transparent wrapper; stops seqex splicing) |
| `:=>` | `(b/validate [:=> [:cat :int] :int] inc)` (function schema: input seqex + output) |
| `:function` | `(b/validate [:function [:=> [:cat :int] :int] [:=> [:cat :int :int] :int]] +)` (multi-arity) |
| `:>` | `(b/validate [:> 10] 11)` |
| `:>=` | `(b/validate [:>= 10] 10)` |
| `:<` | `(b/validate [:< 10] 9)` |
| `:<=` | `(b/validate [:<= 10] 10)` |
| `:not=` | `(b/validate [:not= 10] 11)` |

## Properties

| Property | Applies to | Meaning |
|---|---|---|
| `:min` / `:max` | `:string` (length), `:int`/`:float`/`:double`/`:number` (value), `:time/*` (value), `:vector`/`:sequential`/`:set`/`:map-of` (element count), `:repeat` (repetition count) | Inclusive bounds; violations produce `:balli.core/limits` errors |
| `:closed` | `:map` | When `true`, keys not declared in the schema are rejected (`:balli.core/extra-key`); maps are open by default |
| `:optional` | `:map` entries (entry-level props: `[:k {:optional true} schema]`) | Key may be absent; when present its value must still match |
| `:error/message` | any schema | Overrides the default humanized message for errors at that schema |
| `:dispatch` | `:multi` (required) | Keyword or function used to pick the child schema; unknown dispatch values are invalid (`:balli.core/invalid-dispatch-value`) |
| `:registry` | any vector-form schema | Local `{qualified-keyword schema-form}` registry scoped to that schema subtree |
| `:default` | any schema / `:map` entries | Replacement for nil (and missing map keys) under `default-value-transformer` |
| `:decode/<name>` / `:encode/<name>` | any schema | Per-schema transformer override for the transformer named `<name>` (e.g. `:decode/string`); a real fn or `{:enter f :leave g}` map |
| `:gen/return` `:gen/elements` `:gen/schema` `:gen/fmap` `:gen/min` `:gen/max` | any schema | Generator hooks — constant, uniform pick, alternate schema, post-map fn, bound overrides |

## Self-contained schemas and local registries

Any vector-form schema may carry `{:registry {qualified-keyword schema-form}}`
in its properties. The local registry is layered over the effective registry
for that whole subtree, including nested map entries, refs, transformers,
generators, and JSON Schema export. Local entries can refer to each other and
to outer entries, so recursive schemas can be shipped as one self-contained
form:

```clojure
(def local-tree
  [:schema {:registry {:tree/node [:maybe [:map
                                           [:value :int]
                                           [:children [:vector [:ref :tree/node]]]]]}}
   :tree/node])

(b/validate local-tree {:value 1 :children [{:value 2 :children []}]})
;; => true
```

Shadowed ref names stay distinct in JSON Schema definitions:

```clojure
(require '[balli.json-schema :as bjs])

(bjs/transform
 [:schema {:registry {:x :int}}
  [:map
   [:outer [:ref :x]]
   [:inner [:schema {:registry {:x :string}} [:ref :x]]]]])
;; => {"type" "object"
;;     "properties" {"outer" {"$ref" "#/definitions/x"}
;;                   "inner" {"$ref" "#/definitions/x__2"}}
;;     "required" ["outer" "inner"]
;;     "definitions" {"x" {"type" "integer"}
;;                    "x__2" {"type" "string"}}}
```

## Default branches

In a `:map`, an entry keyed `:balli.core/default` validates the residual map
of keys not explicitly declared. A default entry disables `:closed` extra-key
checking because undeclared keys are claimed by the default schema:

```clojure
(def with-default
  [:map {:closed true}
   [:id :int]
   [:balli.core/default [:map-of :keyword :string]]])

(b/validate with-default {:id 1 :extra "ok"}) ;; => true
(b/validate with-default {:id 1 :extra 2})    ;; => false
```

In a `:multi`, `:balli.core/default` is the fallback branch for dispatch
misses:

```clojure
(def multi-default
  [:multi {:dispatch :kind}
   [:user [:map [:kind [:= :user]] [:name :string]]]
   [:balli.core/default [:map [:kind :keyword]]]])

(:key (b/parse multi-default {:kind :system}))
;; => :balli.core/default
```

## Time schemas

`balli.time` maps Malli-style time schemas onto Python `datetime` types:

| Schema | Python value |
|---|---|
| `:time/instant` | aware `datetime.datetime` (`tzinfo` not nil) |
| `:time/offset-date-time` | aware `datetime.datetime` |
| `:time/zoned-date-time` | aware `datetime.datetime` with `zoneinfo.ZoneInfo` |
| `:time/local-date-time` | naive `datetime.datetime` |
| `:time/local-date` | `datetime.date`, excluding `datetime.datetime` |
| `:time/local-time` | naive `datetime.time` |
| `:time/offset-time` | aware `datetime.time` |
| `:time/duration` | `datetime.timedelta` |
| `:time/period` | `{:years int :months int :days int}` |
| `:time/zone-id` | IANA zone string accepted by `zoneinfo.ZoneInfo` |
| `:time/zone-offset` | `datetime.timezone` |

Comparable time schemas support inclusive `:min`/`:max`, seeded generation,
JSON Schema formats, and a separate transformer. The time transformer is intentionally
not folded into `string-transformer` or `json-transformer`; compose it where
you want string parsing or ISO encoding:

```clojure
(require '[balli.transform :as bt])

(def decoded
  (b/decode [:map [:created :time/instant] [:ttl :time/duration]]
            {:created "2024-06-01T12:00:00+00:00" :ttl "PT15M"}
            (bt/transformer (bt/json-transformer) (bt/time-transformer))))

(b/validate [:map [:created :time/instant] [:ttl :time/duration]] decoded)
;; => true

(b/encode :time/duration (:ttl decoded) (bt/time-transformer))
;; => "PT15M"
```

## Predicate and comparator schemas

The 41 Basilisp core predicates in `balli.normalize/predicates` are schemas
when used as a function value or quoted symbol. Predicate calls are
exception-safe: a thrown host exception means invalid, not a thrown validator.

```clojure
(b/validate int? 1)     ;; => true
(b/validate 'int? "x")  ;; => false
(b/validate [:vector pos-int?] [1 2 3])
;; => true
```

Comparators validate by comparing the input value to their child value. They
are leaves: the child is a literal value, not a nested schema.

```clojure
(b/validate [:> 10] 11) ;; => true

(be/humanize (b/explain [:<= 10] 11))
;; => ["should be at most 10"]
```

## Mutable registry

The default registry is mutable. `register!` adds schemas to the live default
registry and bumps an epoch so raw-form calls pick up the new meaning
immediately. Schema objects keep snapshot semantics: they bake the registry
seen at construction.

```clojure
(reg/register! :demo/id :int)
(def baked (b/schema :demo/id))

(reg/register! :demo/id :string)

(b/validate :demo/id "x") ;; => true  (live default)
(b/validate baked 1)      ;; => true  (snapshot)
(b/validate baked "x")    ;; => false
```

`reg/composite` eagerly merges registries with first-hit schema lookup and
unioned builtin type sets. `set-default-registry!` replaces the live default;
tests that mutate it should restore the old default in `try`/`finally`.

## Transformers

`balli.transform` provides value transformation driven by the schema. `decode` transforms input toward the schema, `encode` away from it; both are **lenient** — mismatching values pass through unchanged, never throw:

```clojure
(require '[balli.core :as b]
         '[balli.transform :as bt])

(b/decode :int "42" (bt/json-transformer))
;; => "42"   (JSON already has numbers -- json-transformer does NOT parse number strings)

(b/encode [:map [:age :int]] {:age 42} (bt/string-transformer))
;; => {:age "42"}
```

`coerce` is decode-then-validate: it returns the decoded value or throws `ex-info` with `{:type :balli.core/coercion :value ... :schema ... :explain ...}`:

```clojure
(b/coerce :int "42" (bt/string-transformer))
;; => 42

(try (b/coerce :int "x" (bt/json-transformer))
     (catch python/Exception e (:type (ex-data e))))
;; => :balli.core/coercion
```

The seven built-ins:

| Transformer | Behavior |
|---|---|
| `string-transformer` | Decode scalars from strings (int/double/boolean/keyword/symbol/uuid/enum), sequentials into vectors/sets; encode scalars to strings |
| `json-transformer` | Assumes JSON-parsed input: no string→number/boolean coercion; keyword/symbol/uuid from string, sets from sequentials, `:map-of` keys via string rules |
| `time-transformer` | Decode/encode `:time/*` values with ISO strings; parse failures and awareness-policy misses pass through unchanged |
| `strip-extra-keys-transformer` | `:map` — drop undeclared keys (unless explicitly `{:closed false}`); `:map-of` — drop entries failing the key/value schemas |
| `key-transformer` | `{:decode f :encode g}` applied to map keys |
| `default-value-transformer` | Replace nil (and fill missing required map keys) from the `:default` property; opts `{:key ... :defaults {type f} :add-optional-keys bool}` |
| `collection-transformer` | Coerce between collection kinds (sequential↔set↔vector) |

```clojure
(b/decode [:map [:x :int]] {:x 1 :junk 2} (bt/strip-extra-keys-transformer))
;; => {:x 1}

(b/decode [:map [:x {:default 7} :int]] {} (bt/default-value-transformer))
;; => {:x 7}

(b/decode [:map [:x :int]] {"x" 1} (bt/key-transformer {:decode keyword}))
;; => {:x 1}

(b/decode [:set :int] [1 1 2] (bt/collection-transformer))
;; => #{1 2}
```

Schemas can override a transformer per node with `:decode/<name>` / `:encode/<name>` properties (real fns, or `{:enter f :leave g}` maps):

```clojure
(b/decode [:string {:decode/string (fn [s] (.upper s))}]
          "kikka" (bt/string-transformer))
;; => "KIKKA"
```

Transformers compose with `bt/transformer` — decode runs the chain in order, encode in reverse:

```clojure
(b/decode [:map [:x :int]] {:x "1" :junk 2}
          (bt/transformer (bt/strip-extra-keys-transformer)
                          (bt/string-transformer)))
;; => {:x 1}
```

`decoder`/`encoder`/`coercer` return the compiled 1-arg fns (cached per schema + transformer identity) when you transform many values.

## Schema utilities

`balli.util` is the `malli.util` port: form→form functions over `:map` schemas (they accept forms or schema objects and return forms):

```clojure
(require '[balli.util :as u])

(u/merge [:map [:x :int]] [:map [:x :string] [:y :int]])
;; => [:map [:x :string] [:y :int]]     (last-one-wins, entry order preserved)

(u/union [:map [:x :int]] [:map [:x :string]])
;; => [:map [:x [:or :int :string]]]

(u/select-keys [:map [:x :int] [:y :string]] [:x])   ;; => [:map [:x :int]]
(u/dissoc [:map [:x :int] [:y :string]] :y)          ;; => [:map [:x :int]]
(u/optional-keys [:map [:x :int] [:y :string]] [:y])
;; => [:map [:x :int] [:y {:optional true} :string]]

(u/closed-schema [:map [:a [:map [:b :int]]]])
;; => [:map {:closed true} [:a [:map {:closed true} [:b :int]]]]

(u/get-in [:map [:a [:map [:b :int]]]] [:a :b])
;; => :int
```

Also: `required-keys`, `open-schema`, `get`. `u/get`/`get-in` address `:map`/`:multi`/`:orn`/`:catn`/`:altn` children by entry key and all indexed types (`:and`/`:or`/`:tuple`/colls/seqex/...) by integer index.

`balli.core/walk` is a form-level postwalk — at every node, children first, the rebuilt form and its path are passed to your fn, whose return value replaces the node:

```clojure
(let [acc (atom [])]
  (b/walk [:map [:x [:vector :int]]]
          (fn [form path] (swap! acc conj [path form]) form))
  @acc)
;; => [[[:x 0] :int] [[:x] [:vector :int]] [[] [:map [:x [:vector :int]]]]]
```

`(b/walk s (b/schema-walker f))` adapts a 1-arg form fn, mirroring Malli's `(m/walk s (m/schema-walker f))`. Refs are not entered (the ref node is a leaf).

## JSON Schema export

`balli.json-schema/transform` exports any schema as a JSON Schema (draft 2020-12 style, string-keyed Basilisp map — `basilisp.json/write-str` takes it as-is):

```clojure
(require '[balli.json-schema :as bjs])

(bjs/transform [:map [:id :string] [:age {:optional true} [:int {:min 0}]]])
;; => {"type" "object"
;;     "properties" {"id" {"type" "string"}
;;                   "age" {"type" "integer" "minimum" 0}}
;;     "required" ["id"]}

(bjs/transform [:tuple :string :int])
;; => {"type" "array" "prefixItems" [{"type" "string"} {"type" "integer"}] "items" false}
```

Refs become `$ref` pointers with a top-level `"definitions"` map (recursion terminates); ref names are JSON-Pointer-escaped in the `$ref` string but unescaped as definitions keys:

```clojure
(bjs/transform [:ref :tree/node] {:registry tree-registry})
;; => {"$ref" "#/definitions/tree~1node"
;;     "definitions" {"tree/node" {"type" "object"
;;                                 "properties" {"value" {"type" "integer"}
;;                                               "children" {"type" "array"
;;                                                           "items" {"$ref" "#/definitions/tree~1node"}}}
;;                                 "required" ["value" "children"]}}}
```

`:title`/`:description`/`:default` properties pass through; a `:json-schema` property replaces the generated node wholesale and `:json-schema/foo` properties unlift into it (winning over generated keys). Sequence schemas export as a lossy `{"type" "array"}` best-effort.

## Humanized errors and spell-checking

`balli.error/humanize` renders explain data into messages mirroring the value shape (see Quick start). `with-spell-checking` rewrites explain errors before humanizing: an extra key within edit distance of an absent declared key becomes `:balli.error/misspelled-key` (and the corresponding missing-key error is dropped); an unknown `:multi` dispatch value near a declared one becomes `:balli.error/misspelled-value`:

```clojure
(-> (b/explain [:map {:closed true} [:name :string]] {:nam "x"})
    be/with-spell-checking
    be/humanize)
;; => {:nam ["should be spelled :name"]}
```

`be/levenshtein` (the underlying edit distance) is public too: `(be/levenshtein "nam" "name")` → `1`.

## Parsing

`parse` destructures a value against a schema; `unparse` is the exact inverse. Both return the sentinel `:balli.core/invalid` on mismatch (test with `b/invalid?`, never `identical?`). Non-transforming schemas parse as validate-then-value; named branches produce records:

- `:orn`/`:multi`/`:altn` → a `Tag` record `{:key branch-key :value parsed}` (`b/tag`, `b/tag?`)
- `:catn` → a `Tags` record `{:values {tag parsed ...}}` (`b/tags`, `b/tags?`)

```clojure
(b/parse [:catn [:n :int] [:s :string]] [1 "x"])
;; => #balli.compile.Tags{:values {:n 1 :s "x"}}

(b/unparse [:catn [:n :int] [:s :string]]
           (b/parse [:catn [:n :int] [:s :string]] [1 "x"]))
;; => [1 "x"]

(b/unparse [:orn [:num :int] [:str :string]] (b/tag :num 42))
;; => 42
```

`Tag`/`Tags` are records — user data that merely looks like `{:key ... :value ...}` is not confused with them by the `:map` parser guard. `parser`/`unparser` return the compiled (cached) 1-arg fns.

## Sequence schemas

`:cat`/`:catn`/`:alt`/`:altn`/`:?`/`:*`/`:+`/`:repeat` describe *sequences* and are compiled to an iterative backtracking regex engine (no Python recursion on input length, memoized against pathological backtracking):

```clojure
(b/validate [:cat [:* :int] :int] [1 2 3])          ;; => true (backtracks)
(b/validate [:map [:args [:cat :keyword [:* :int]]]]
            {:args [:add 1 2]})                     ;; => true (seqex nested in a map)
```

Seqex children of seqex **splice** — `[:* [:cat :int :string]]` matches a flat `[1 "a" 2 "b"]` — while parse output nests per combinator:

```clojure
(b/parse [:* [:cat :int :string]] [1 "a" 2 "b"])
;; => [[1 "a"] [2 "b"]]
```

Wrap a seqex in `[:schema ...]` to escape splicing and match one nested sequence element instead:

```clojure
(b/validate [:cat :int [:schema [:cat :int :string]]] [1 [2 "a"]])
;; => true
```

Explain reports the furthest failure position with dedicated error types:

```clojure
(:type (first (:errors (b/explain [:cat :int] []))))     ;; => :balli.core/end-of-input
(:type (first (:errors (b/explain [:cat :int] [1 2]))))  ;; => :balli.core/input-remaining
```

A `:ref` directly in seqex child position throws `:balli.core/potentially-recursive-seqex` at compile time (unbounded recursion cannot be compiled); wrap the ref in `[:schema [:ref ...]]` for one nested element.

## Function schemas

`[:=> input-seqex output-schema guard?]` describes a function; `:function` groups `:=>` children with distinct arities. Plain `validate` only checks callability:

```clojure
(b/validate [:=> [:cat :int] :int] inc)   ;; => true
(b/validate [:=> [:cat :int] :int] 5)     ;; => false
```

Pass a **function checker** to validate generatively (100 generated input vectors, outputs validated):

```clojure
(require '[balli.generator :as bg])

(b/validate [:=> [:cat :int] :int] str
            {:balli.core/function-checker (bg/function-checker)})
;; => false   (str returns strings, not ints)
```

The checker opt is honored on raw forms (bypassing the raw-form cache) and can be baked into a schema object at construction — call-time opts on an existing schema object are ignored.

`instrument` wraps a fn with per-call arity/input/output/guard validation, throwing typed `ex-info` (`:balli.core/invalid-arity` / `invalid-input` / `invalid-output` / `invalid-guard`) or routing failures to your `:report` fn:

```clojure
(try ((b/instrument {:schema [:=> [:cat :int] :int]} inc) "x")
     (catch python/Exception e (:type (ex-data e))))
;; => :balli.core/invalid-input
```

`function-info` extracts arity/shape data:

```clojure
(b/function-info (b/schema [:=> [:cat :int :int] :int]))
;; => {:min 2 :max 2 :arity 2 :input [:cat :int :int] :output :int}
```

A `:=>` whose input does not normalize to `:cat`/`:catn` throws `:balli.core/invalid-input-schema`. Generating from a `:=>` yields a constant-ish function producing valid outputs.

## Generators

`balli.generator` generates schema-satisfying values with pure `random.Random` — equal seeds give equal values:

```clojure
(bg/generate [:int {:min 0 :max 100}] {:seed 1})       ;; deterministic
(bg/sample [:int {:min 0 :max 100}] {:seed 1 :size 5}) ;; => [17 72 97 8 32]

(= (bg/generate [:map [:a :int] [:b [:vector :string]]] {:seed 42})
   (bg/generate [:map [:a :int] [:b [:vector :string]]] {:seed 42}))
;; => true
```

`:size` (default 30) scales magnitudes and collection lengths. Seqex schemas generate flat sequences (`(bg/generate [:cat :int [:* :string]] {:seed 3})` validates against its own schema). Recursive refs are depth-capped and escape through `:maybe`/optional keys/zero-min collections, else throw `:balli.core/unsatisfiable-schema` (as does `:and`/`:not` filtering after 100 retries).

Common `:re` forms generate strings directly (`\d`, `\w`, literal characters, simple character classes, `+`/`*`/`?`/`{m,n}`, and anchors). `:fn` schemas still have no default generator and throw `:balli.core/no-generator` unless you supply `:gen/*` property hooks:

```clojure
(bg/generate [:re #"\d+"] {:seed 3})
;; => "398"

(bg/generate [:re {:gen/elements ["a1" "b2"]} #"[ab]\d"] {:seed 3})
;; => "a1"

(bg/generate [:int {:gen/fmap str}] {:seed 0})
;; => "829"
```

Hooks (highest priority first): `:gen/return` (constant), `:gen/elements` (uniform pick), `:gen/schema` (generate an alternate schema), `:gen/fmap` (post-map with a real fn), `:gen/min`/`:gen/max` (bound overrides).

`shrink` returns smaller valid candidates, optionally retaining only values that satisfy a failure predicate:

```clojure
(bg/shrink [:int {:min 0}] 10)
;; => [0 5 9]
```

## Schema inference

`balli.provider/provide` infers a schema form from sample values — every sample validates against the result:

```clojure
(bp/provide [{:x 1} {:x 2 :y "a"}])
;; => [:map [:x :int] [:y {:optional true} :string]]

(bp/provide [1 2 nil])
;; => [:maybe :int]

(bp/provide [{"a" 1 "b" 2} {"c" 3} {"d" 4 "e" 5}])
;; => [:map-of :string :int]
```

Maps with many distinct keys but uniform key/value shapes become `[:map-of k v]` (tune with `{:map-of-threshold n}`, default 3); mixed scalars become `[:or ...]`; nil-mixed become `[:maybe ...]`.

## API

`s` is a raw schema form or a schema object; `opts` supports `{:registry r}` and is ignored when `s` is already a schema object (its baked-in registry — and baked-in checker — win). Compiled fns are cached on schema objects, or in a bounded global cache for raw forms.

### `balli.core`

| Function | Signature | Description |
|---|---|---|
| `schema` | `(schema form)` `(schema form opts)` | Wrap a form into a schema object (normalized AST + registry + compile cache). Idempotent on schema objects. `opts` may carry `:balli.core/function-checker`. |
| `schema?` | `(schema? x)` | True when `x` is a balli schema object. |
| `form` | `(form s)` | The original schema form. |
| `properties` | `(properties s)` | Properties map of the root node, e.g. `{:closed true}`. |
| `children` | `(children s)` | AST children of the root node. |
| `validator` / `validate` | `(validator s opts?)` / `(validate s value opts?)` | Compiled 1-arg boolean validator / one-shot boolean. |
| `explainer` / `explain` | `(explainer s opts?)` / `(explain s value opts?)` | nil when valid, else `{:schema :value :errors}`; each error is `{:path :in :schema :value :type}`. |
| `assert-valid` | `(assert-valid s value opts?)` | Returns `value`, or throws `ex-info` with the explain map plus `{:type :balli.core/invalid-input}`. |
| `decoder` / `decode` | `(decoder s t opts?)` / `(decode s value t opts?)` | Transform toward the schema with transformer `t`; lenient (mismatches pass through). |
| `encoder` / `encode` | `(encoder s t opts?)` / `(encode s value t opts?)` | Transform away from the schema; lenient. |
| `coercer` / `coerce` | `(coercer s t opts?)` / `(coerce s value t opts?)` | Decode then validate; returns the decoded value or throws `:balli.core/coercion`. |
| `parser` / `parse` | `(parser s opts?)` / `(parse s value opts?)` | Value → parsed value or `:balli.core/invalid`; `Tag`/`Tags` for named branches. |
| `unparser` / `unparse` | `(unparser s opts?)` / `(unparse s value opts?)` | Exact inverse of `parse`; same sentinel. |
| `tag` / `tag?` | `(tag k v)` / `(tag? x)` | Construct/detect the `Tag` parse container (`:orn`/`:multi`/`:altn`). |
| `tags` / `tags?` | `(tags m)` / `(tags? x)` | Construct/detect the `Tags` parse container (`:catn`). |
| `invalid?` | `(invalid? x)` | True when `x` is the parse failure sentinel (`=`-compared). |
| `walk` | `(walk s f opts?)` | Form-level postwalk; `f` is `(fn [rebuilt-form path] form')`. |
| `schema-walker` | `(schema-walker f)` | Adapt a 1-arg form fn for `walk`. |
| `function-info` | `(function-info s opts?)` | `{:min :max? :arity :input :output :guard?}` for a `:=>` schema; nil otherwise. |
| `instrument` | `(instrument props f)` | Wrap `f` per `{:schema s :scope #{:input :output} :report rf}` — typed failures per call. |
| `version` | var | The library version string. |

### `balli.transform`

| Function | Description |
|---|---|
| `transformer` | Compose chain-link maps / transformers / 0-arg fns into one transformer (decode in chain order, encode reversed). |
| `transformer?` / `into-transformer` | Predicate / coercion into a transformer object. |
| `string-transformer` `json-transformer` `time-transformer` `strip-extra-keys-transformer` `key-transformer` `default-value-transformer` `collection-transformer` | The built-ins (see [Transformers](#transformers)). |

### `balli.util`

| Function | Description |
|---|---|
| `merge` / `union` | Combine two `:map` forms — last-wins / `[:or]`-combining. |
| `select-keys` / `dissoc` | Keep / remove `:map` entries. |
| `optional-keys` / `required-keys` | Set / clear `:optional` on entries (all, or a key seq). |
| `closed-schema` / `open-schema` | Recursively add / remove `{:closed true}` (explicit `{:closed false}` is respected). |
| `get` / `get-in` | Sub-schema form by entry key or child index; nil when absent. |

### Other namespaces

| Function | Description |
|---|---|
| `balli.json-schema/transform` | `(transform s opts?)` — JSON Schema as a string-keyed map, `"definitions"` when refs are reached. |
| `balli.error/humanize` | `(humanize explain-map)` — messages mirroring the value shape; nil in, nil out. |
| `balli.error/with-spell-checking` | `(with-spell-checking explain-map)` — rewrite extra-key/dispatch errors as misspellings. |
| `balli.error/levenshtein` | `(levenshtein a b)` — edit distance. |
| `balli.generator/generate` | `(generate s opts?)` — one value; `{:seed :size :registry}`. |
| `balli.generator/sample` | `(sample s opts?)` — vector of values; `:size` is the count (default 10). |
| `balli.generator/shrink` / `shrink-candidates` | Smaller valid candidates for a value; `{:predicate f}` keeps only still-failing values. |
| `balli.generator/function-checker` | `(function-checker opts?)` — generative `:=>`/`:function` checker; `{:iterations n}` (default 100). |
| `balli.openapi/schema` / `openapi` / `request-body` / `response` / `parameter` | Export OpenAPI 3 schema objects, minimal documents, and operation fragments. |
| `balli.swagger/schema` / `swagger` / `parameter` / `response` | Export Swagger 2 schema objects, minimal documents, and operation fragments. |
| `balli.dot/transform` | Export a Graphviz DOT string for a schema graph. |
| `balli.plantuml/transform` | Export a PlantUML wrapper for a schema graph. |
| `balli.describe/describe` | Return a small English description for a schema. |
| `balli.extension/register-type!` / `unregister-type!` / `type-spec` / `custom-type?` / `clear-types!` | Register custom schema keywords with validate/generate/transform/export/message callbacks. |
| `balli.serial/register-function!` / `unregister-function!` / `serialize` / `deserialize` / `write-string` / `read-string` | EDN-safe schema serialization with named function references and regex pattern round-tripping. |
| `balli.dev/register!` / `unregister!` / `start!` / `stop!` / `running` / `capture-fail!` / `captured-failures` | Explicit development instrumentation for atoms holding functions. |
| `balli.provider/provide` | `(provide samples opts?)` — infer a schema form; `{:map-of-threshold n :infer-enums true :enum-threshold n :infer-tuples true}`. |
| `balli.registry/registry` | `(registry & schema-maps)` — layer `{qualified-kw form}` maps over the default registry. |
| `balli.registry/lazy-registry` | `(lazy-registry provider)` / `(lazy-registry base provider)` — provider-on-miss registry with memoized forms. |
| `balli.registry/dynamic-registry` | `(dynamic-registry source)` — read an atom/fn source at raw-form lookup time. |
| `balli.registry/default-registry` | `(default-registry)` — returns the current mutable default registry. |
| `balli.registry/register!` | `(register! kw form)` / `(register! {kw form ...})` — merge schemas into the current default registry. |
| `balli.registry/set-default-registry!` | `(set-default-registry! r)` — replace the mutable default registry. |
| `balli.registry/composite` | `(composite r1 r2 ...)` — eager first-hit registry merge. |
| `balli.registry/mutation-epoch` | atom — bumped by default-registry mutations; raw-form caches use it for invalidation. |
| `balli.registry/resolve-ref` | `(resolve-ref reg k)` — registered form or nil. |
| `balli.registry/builtin-types` | var — the set of 56 builtin type keywords. |

Unknown or malformed schema forms throw `ex-info` with `:type :balli.core/invalid-schema`; a `:ref` to an unregistered keyword throws `:balli.core/unresolved-ref` at compile time (fail fast, not at validate).

## Differences from Malli

Balli covers most of Malli's core surface but is Malli-**inspired**, not a port. Not implemented:

- **No executable sexpr property code** — schema properties take real Basilisp fns (`:fn` children, `:dispatch`, `:gen/fmap`, `:decode/*` overrides, ...); safe serialization is explicit via `balli.serial` named function refs and never evals code.
- **No old (pre-0.18) parse format** shim.
- **No var registry** — Balli has plain registry maps, eager `composite`, local `:registry` properties, a mutable default registry, lazy registries, and explicit dynamic registries.
- **Time schemas use Python's stdlib model** — offset/zoned distinctions follow Python `datetime`/`zoneinfo`, and `:time/period` is a map of calendar fields.
- **Heuristic shrinking, not test.check shrinking** — `balli.generator/shrink` returns practical smaller candidates, but Balli does not expose test.check generator objects.
- **`:fn` generation requires `:gen/*` props** — otherwise `:balli.core/no-generator` is thrown.
- **No `malli.experimental` or clj-kondo modules.**

Behavioral deviations:

- **Basilisp data only** — validators check Basilisp data structures. Python `dict`/`list` values are *not* accepted; convert at the interop boundary first.
- **`walk` is form-level** — `f` is `(fn [rebuilt-form path] form')` over forms, not Malli's 4-arg walker over schema objects; `schema-walker` keeps the familiar call shape. Refs are not entered.
- **Schema-object opts and registries are baked** — call-time opts (registry, `:balli.core/function-checker`) are ignored when the schema argument is already a schema object; bake them at `(b/schema form opts)`. Mutating the default registry affects future raw-form calls but not existing schema objects. Raw-form calls carrying a checker bypass the global raw-form cache.
- **`instrument` always arity-checks** — the argument-count check against the input seqex bounds runs on every call regardless of `:scope`.
- **`:multi` keyword dispatch uses `get`** — a keyword `:dispatch` is looked up with `(get value k)` (nil on non-associative values → `:balli.core/invalid-dispatch-value`); it is not invoked as an arbitrary ifn. Fn dispatch must be Python-callable.
- **`ifn?` uses `ifn-like?`** — real fns plus keywords, maps, and sets count as ifn-like; vectors and symbols are rejected even though Python/Basilisp callability is broader.
- **Provider tuple/enum inference is opt-in** — pass `{:infer-tuples true}` or `{:infer-enums true}` for narrower hints. Mixed int/float samples infer `[:or :int :double]` (Basilisp `float?` rejects ints, so no single scalar type covers both).
- **`:?` unparse is stricter** — the child unparser is tried first; only a nil the child rejects unparses to `[]`, and shape mismatches return `:balli.core/invalid` rather than best-effort output.
- **JSON Schema ref names are JSON-Pointer-escaped** in `$ref` strings (`:tree/node` → `"#/definitions/tree~1node"`) with unescaped `"definitions"` keys; local-registry shadow collisions get `__2`, `__3`, ... suffixes; seqex types export as lossy `{"type" "array"}`.
- **Set element `:in`** uses the element's seq-order ordinal (sets are unordered; the index identifies which element in seq order failed, not a stable position).
- **Mixed-level humanize uses `:balli/error`** — when a value has errors of its own *and* nested child errors (e.g. `[:vector {:min 3} :int]` on `[1 "x"]`), `humanize` renders that level as a map with child entries plus the level's own messages under the reserved `:balli/error` key: `{1 ["should be an integer"] :balli/error ["should have at least 3 elements"]}`.

## Development

```bash
# quick confidence suite for fresh clones
scripts/user_suite.sh   # or: basilisp test tests/test_user_suite.lpy

# run the test suite (pytest via basilisp)
basilisp test            # or: scripts/test.sh

# lint = compile-check every namespace under src/
basilisp run scripts/compile_check.lpy
```

`tests/test_user_suite.lpy` is a small public-surface smoke suite intended for
users validating a clone quickly. `basilisp test` is the comprehensive developer
suite. There is no clj-kondo for Basilisp; the compile-check script (which
imports every `src/**/*.lpy` namespace and fails on any compile error) is the
lint step.

## License

[MIT](LICENSE) © 2026 Andrew VanDyke
