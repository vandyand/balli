# Does basilisp have a drop in clojure malli replacement?

Basilisp itself does not ship a drop-in replacement for Clojure's Malli library.[^2_1][^2_2] Balli fills that gap as Malli for Basilisp: a Malli clone with documented runtime and ecosystem differences.

## What Basilisp gives you instead

Basilisp focuses on being a Clojure‑compatible(-ish) Lisp on Python, with core language features and data structures that mirror Clojure (persistent collections, macros, protocols, multimethods, transducers, etc.), plus EDN and JSON support.  The docs and release notes list many Clojure core features and extensions, but there is no mention of Malli or a spec/schema library built into Basilisp.[^2_2][^2_1]

## Options for schema/validation in Basilisp

Given that, your practical options are:

- Use Python libraries (e.g., pydantic, marshmallow, attrs-based validation) from Basilisp via Python interop and treat them as your schema/validation layer. Basilisp is designed for “seamless Python interop,” so this is a first‑class path.[^2_1]
- Use Balli as a Malli-style schema/validation DSL for Basilisp, with Python-aware runtime behavior where Basilisp differs from Clojure.
- If you rely heavily on Malli’s specific API, keep that part in Clojure and call Basilisp/Python services over a boundary (HTTP, RPC) rather than trying to duplicate Malli exactly.


## Interop‑first mindset

Because Basilisp runs on Python, its ecosystem story is “use Python’s libraries plus Lisp syntax,” not “reimplement the entire Clojure library ecosystem.” The official docs emphasize compatibility with Clojure core functions but do not promise compatibility with third‑party Clojure libraries like Malli.[^2_2][^2_1]

If you describe how you’re using Malli today (validation only, data modeling, routing, etc.), I can sketch a concrete Basilisp+Python pattern that covers the same use cases.
<span style="display:none">[^2_10][^2_11][^2_12][^2_3][^2_4][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://github.com/DavidVujic/python-polylith/discussions/351

[^2_2]: https://cljdoc.org/d/polylith/clj-poly/0.2.21/doc/source-code

[^2_3]: https://www.reddit.com/r/palemoon/comments/rsz021/what_will_you_replace_basilisk_with/

[^2_4]: https://www.reddit.com/r/MouseReview/comments/1o1pb8m/basilisk_v3_broke_recommendations_for_replacement/

[^2_5]: https://starwars.fandom.com/wiki/Basilisk_war_droid/Legends

[^2_6]: https://www.slant.co/options/34002/alternatives/~basilisk-alternatives

[^2_7]: https://www.ifixit.com/Guide/Razer+Basilisk+V3+Motherboard+Replacement/172299

[^2_8]: https://basilisp.readthedocs.io/en/latest/releasenotes.html

[^2_9]: https://github.com/basilisp-lang

[^2_10]: https://basilisp.readthedocs.io/en/latest/concepts.html

[^2_11]: https://basilisp.readthedocs.io/en/latest/gettingstarted.html

[^2_12]: https://pypi.org/project/basilisp/


---

# I want malli in basilisp - maybe call it balli. how to make this?

Yes — you can make “**Balli**,” but the right goal is **Malli-compatible enough** for Basilisp, not a byte-for-byte port. Malli’s core strengths are data-driven schemas, validation, explain/error data, transformation, registries, and schema-as-data tooling, while Basilisp’s big advantage is seamless Python interop, so Balli should preserve the Malli mental model while leaning on Python for performance, regexes, date types, and maybe generation later.[^3_1][^3_2]

## Scope first

Start with a **Malli core subset**, not the whole feature surface. Malli itself is broad: schema definitions as data, validation, explain data, value transformation, schema registries, parsing/unparsing, JSON Schema export, and generation.  For a v0, implement only:[^3_1]

- Scalar schemas: `:any`, `:string`, `:int`, `:float`, `:bool`, `:keyword`, `:map`, `:vector`, `:set`, `:tuple`, `:maybe`, `:enum`, `:=`, `:and`, `:or`, `:fn`.
- Core API: `schema`, `validate`, `validator`, `explain`, `decode`, `encode`, `coerce`, `form`, `properties`.
- Registries and refs: local registry plus `[:ref ...]`.
- Error output shaped like Malli’s `{:schema ... :value ... :errors [...]}`.[^3_1]

That subset gets you 80% of practical use while keeping the implementation tractable. Malli’s vector syntax is especially worth copying because it keeps schemas serializable and data-first.[^3_1]

## Architecture

Balli should compile schema data into **validator objects/functions**. Malli exposes both direct validation and precompiled validators for performance, and that pattern maps well to Python-hosted Basilisp.  Basilisp can import Python modules, call Python functions, access properties, and pass keyword arguments cleanly, so you can put hot-path compilation/runtime code in Python while keeping the public API in Basilisp.[^3_2][^3_1]

A good split is:

- `balli.core.lpy`: public Basilisp API, schema constructors, registry handling, user-facing ergonomics.
- `balli/compiler.py`: turns schema forms into Python callables or small validator objects.
- `balli/errors.lpy`: explain data and humanization.
- `balli/transform.lpy`: decode/encode/coerce pipeline.
- `balli/json_schema.lpy`: optional exporter later.

That design matches Basilisp’s “Lisp front, Python host” model instead of fighting it.[^3_2]

## Schema model

Use Malli-style vector syntax as the canonical source form. Malli’s default syntax is vector-based, with optional properties as the second element, and that is the most important part to preserve if you want the library to feel familiar.[^3_1]

Example canonical forms:

```clojure
:string
[:string {:min 1 :max 100}]
[:map
 [:id :string]
 [:name [:string {:min 1}]]
 [:age {:optional true} :int]]
[:vector :int]
[:tuple :string :int]
[:enum "A" "B" "C"]
[:maybe :string]
[:and :int [:fn pos?]]
[:ref :user/id]
```

Internally, normalize everything into an AST map like:

```clojure
{:type :map
 :properties {:closed true}
 :children [...]}
```

Malli also supports an AST/map form, and normalizing into an internal AST will make compilation, transforms, and JSON Schema export much easier.[^3_1]

## Core API design

Mirror Malli’s smallest useful API so existing users can transfer intuition quickly. Malli supports validating raw schema forms directly and also working with compiled schema values, so Balli should do the same.[^3_1]

Suggested API:

```clojure
(ns balli.core)

(defn schema [form & [opts]])
(defn schema? [x])
(defn form [schema])
(defn properties [schema])

(defn validate [schema value & [opts]])
(defn validator [schema & [opts]])   ; returns fn
(defn explain [schema value & [opts]])

(defn decode [schema value transformer & [opts]])
(defn encode [schema value transformer & [opts]])
(defn coerce [schema value & [transformer opts]])

(defn register! [registry k schema])
(defn deref-schema [schema registry])
```

Keep `explain` as the backbone. In Malli, humanized errors and coercion failures are downstream of explain-style structured error data, so Balli should also treat explain data as the core artifact.[^3_1]

## Validation strategy

Compile every schema node into a validator fn with a common signature like:

```clojure
(fn [value ctx] ...)
```

where `ctx` carries path, registry, transformer, and error accumulator. Malli’s explain data includes schema path, input path, schema fragment, and failing value, so Balli validators should emit the same categories of information.[^3_1]

A practical error shape:

```clojure
{:schema schema-form
 :value input
 :errors [{:path [:address :zip]
           :in   [:address :zip]
           :schema :int
           :value "33100"
           :type :balli.core/invalid-type}]}
```

Recommended rules:

- `validate` returns boolean.
- `validator` returns a compiled fn for hot paths.
- `explain` returns `nil` on success, explain map on failure.
- `coerce` either returns transformed value or throws an exception carrying explain data, similar to Malli coercion behavior.[^3_1]


## Python interop choices

Use Python for the parts where the host ecosystem is stronger:

- Regex and string constraints via `re`.
- Datetime, UUID, Decimal, IP types via standard/PyPI modules.
- Optional schema generation later via Hypothesis.
- JSON Schema export helpers if useful.

Basilisp can import Python modules, refer module members, call methods with `(. obj method ...)`, and invoke functions with keyword args, so wrapping Python validation helpers from Basilisp is straightforward.  That means Balli can stay Lisp-y at the API level while using Python implementations underneath for speed and breadth.[^3_2]

## MVP roadmap

Build in this order:

1. Reader-compatible schema forms, normalization, and schema object model.[^3_1]
2. Primitive validators: `:any`, `:string`, `:int`, `:float`, `:bool`, `:=`, `:enum`.[^3_1]
3. Composite validators: `:maybe`, `:and`, `:or`, `:vector`, `:tuple`, `:map`.[^3_1]
4. `explain` with stable path reporting and missing-key errors, since Malli-style diagnostics are a major part of the value.[^3_1]
5. Registries and `:ref`.
6. Transformers: `string-transformer`, `json-transformer`, `strip-extra-keys-transformer`, and default values, because Malli’s decode/encode layer is one of its most practical features.[^3_1]
7. Humanized errors.
8. Optional: JSON Schema export, OpenAPI helpers, generators.

Do not start with function schemas, sequence regexes, spell-checking, or full schema inference. Malli has those, but they are expensive features; getting map/vector/transform/coerce right first matters more.[^3_1]

## Example skeleton

A Balli MVP could look like this:

```clojure
(ns balli.core
  (:import [balli.compiler :as c]))

(defn schema [form & [opts]]
  {:form form
   :opts opts
   :compiled nil})

(defn form [s] (:form s))

(defn validator [s & [opts]]
  (let [form (if (map? s) (:form s) s)]
    (c/compile-validator form opts)))

(defn validate [s value & [opts]]
  ((validator s opts) value))

(defn explain [s value & [opts]]
  (let [vf (c/compile-explainer (if (map? s) (:form s) s) opts)]
    (vf value)))
```

And Python hot path:

```python
class Validator:
    def __init__(self, form, opts=None):
        self.form = form
        self.opts = opts or {}

    def validate(self, value):
        return self.explain(value) is None

    def explain(self, value):
        ...
```

This split is natural because Basilisp is built to interoperate directly with Python modules and functions.[^3_2]

## Product decisions

A few choices will determine whether Balli feels good:

- **Compatibility target:** aim for “Malli-shaped,” not exact parity. Malli has years of edge cases and optimization behind it.[^3_1]
- **Keyword model:** decide how Basilisp keywords map into Python dict keys and JSON keys early.
- **Open vs closed maps:** copy Malli’s default of open maps, with a `:closed true` property, because that is a very practical convention.[^3_1]
- **Transformers before magic coercion:** Malli separates decoding/encoding from validation cleanly; Balli should too.[^3_1]
- **Schema as plain data:** never hide schemas behind classes only; preserve round-trippable forms because Malli’s big value is that schemas are editable, persistable data.[^3_1]


## Suggested repo plan

Use a small monorepo layout:

- `src/balli/core.lpy`
- `src/balli/errors.lpy`
- `src/balli/transform.lpy`
- `src/balli/registry.lpy`
- `src/balli/compiler.py`
- `tests/test_core.lpy`
- `tests/test_transform.lpy`
- `tests/test_errors.lpy`

For test fixtures, copy Malli-like examples such as open/closed maps, enums, tuples, maybe values, decode/encode, and explain outputs, since those are central documented behaviors in Malli.[^3_1]

## Naming and positioning

“Balli” is now best framed directly as **Malli for Basilisp**: a Malli clone that ports Malli's schema syntax and core workflows into Python-hosted Basilisp while documenting the runtime and ecosystem differences. Malli’s own positioning centers on data-driven schemas, validation, transformation, error reporting, registries, and schema tooling, and those are the right pillars to preserve.[^3_1]

A crisp project statement could be:

- “Balli is Malli for Basilisp.”
- “Balli is a data-driven schema library for Basilisp.”
- “Schemas are plain data.”
- “Validation, explain data, transformation, and coercion.”
- “Python-powered interop where it helps, Malli-compatible UX where it matters.”[^3_2][^3_1]

Would you like me to draft the actual `balli.core` MVP API and a first-pass compiler for `:map`, `:string`, `:int`, `:maybe`, and `:vector`?
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_3][^3_4][^3_5][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://github.com/DavidVujic/python-polylith/discussions/351

[^3_2]: https://cljdoc.org/d/polylith/clj-poly/0.2.21/doc/source-code

[^3_3]: https://clojurecivitas.org/malli/elements_of_malli.html

[^3_4]: https://www.youtube.com/watch?v=bQDkuF6-py4

[^3_5]: https://sourceforge.net/projects/malli.mirror/

[^3_6]: https://www.reddit.com/r/Clojure/comments/dkwgjr/malliio_the_datadriven_schema_playground/

[^3_7]: https://github.com/metosin/malli

[^3_8]: https://clojureverse.org/t/introducing-malli-a-new-data-validation-and-specification-library-for-clojure-script/6653

[^3_9]: https://www.youtube.com/watch?v=MR83MhWQ61E

[^3_10]: https://basilisp.readthedocs.io/en/latest/pyinterop.html

[^3_11]: https://www.metosin.fi/blog/malli

[^3_12]: https://pypi.org/project/basilisp/

[^3_13]: https://www.reddit.com/r/Clojure/comments/12jvdq0/ann_malli_0110_is_out_a_datadriven_data/

[^3_14]: https://github.com/basilisp-lang

[^3_15]: https://www.youtube.com/watch?v=n6OeKHm4BSQ

[^3_16]: https://www.slideshare.net/slideshow/malli-inside-datadriven-schemas/229446966

[^3_17]: https://www.youtube.com/watch?v=YhP6tI22uQ4


---

# Yes. Also, what aspects of basilisp influence and inform our implementation of balli and how/why? Also, what python libraries should we consider building off of, or are none necessary? Do any make our balli implementation more performant? more elegant? more idiomatic?

Yes — and Basilisp itself should shape Balli pretty strongly. The best design is a **data-first Basilisp API** with a **compilation layer**, plus optional Python backends for fast parsing/decoding where they help; you do not need Python libraries for the Balli core, but a few can make specific parts faster or cleaner.[^4_1][^4_2][^4_3]

## MVP API

Balli should feel like Malli at the call site: schemas as plain data, validation as a boolean, compiled validators for hot paths, and structured explain output. Basilisp’s persistent vectors, maps, sets, keywords, metadata, and reader support make Malli-style schema forms feel natural in source and at the REPL.[^4_2][^4_1]

A good MVP public API:

```clojure
(ns balli.core)

(defn schema
  ([form] (schema form nil))
  ([form opts]) ...)

(defn schema? [x] ...)
(defn form [schema] ...)
(defn properties [schema] ...)
(defn children [schema] ...)

(defn validate
  ([schema value] ...)
  ([schema value opts] ...))

(defn validator
  ([schema] ...)
  ([schema opts] ...)) ; returns fn [value] -> boolean

(defn explain
  ([schema value] ...)
  ([schema value opts] ...)) ; nil on success, map on failure

(defn decoder
  ([schema transformer] ...)
  ([schema transformer opts] ...))

(defn encoder
  ([schema transformer] ...)
  ([schema transformer opts] ...))

(defn decode
  ([schema value transformer] ...)
  ([schema value transformer opts] ...))

(defn encode
  ([schema value transformer] ...)
  ([schema value transformer opts] ...))

(defn coercer
  ([schema] ...)
  ([schema transformer] ...)
  ([schema transformer opts] ...))

(defn coerce
  ([schema value] ...)
  ([schema value transformer] ...)
  ([schema value transformer opts] ...))

(defn default-registry [] ...)
(defn registry [m] ...)
(defn deref-schema [registry ref] ...)
```

Core forms to support first:

```clojure
:any
:string
:int
:float
:bool
:keyword
:map
:vector
:set
:tuple
:enum
:=
:maybe
:and
:or
:fn
:ref
```

Those are enough to validate real request/response payloads and config maps before you tackle advanced features.[^4_3]

## Implementation sketch

The simplest architecture is a three-stage pipeline:

1. `form -> normalized AST`
2. `AST -> compiled validator / explainer / decoder`
3. runtime calls against values.[^4_3]

Suggested internal namespaces:

```clojure
balli.core
balli.registry
balli.normalize
balli.compile
balli.validate
balli.explain
balli.transform
balli.errors
```

And an internal schema record/map like:

```clojure
{:balli/schema true
 :form [:map [:id :int] [:name [:string {:min 1}]]]
 :ast  {:type :map
        :properties {}
        :children [{:key :id :schema {:type :int}}
                   {:key :name :schema {:type :string :properties {:min 1}}}]}
 :registry nil
 :compiled nil}
```

Use a normalized AST even if the user passed a simple keyword like `:string`; it keeps compilation and explain logic uniform. Malli’s strength is that schemas are data first, and Basilisp’s reader and immutable collections make that especially natural.[^4_2][^4_3]

## Basilisp-specific influences

Basilisp affects Balli in several important ways.

- **Persistent immutable collections**: Balli schemas should stay as plain immutable Basilisp data because Basilisp’s vectors, maps, and sets are persistent and thread-safe, which matches the schema-as-data model very well.[^4_2]
- **Keywords as first-class identifiers**: schema tags, property keys, error keys, and registries should use keywords heavily because keywords self-evaluate, are interned, and naturally fit map lookup and dispatch.[^4_4][^4_2]
- **Reader syntax**: schema literals should be optimized for direct source readability, e.g. `[:map [:id :int]]`, because Basilisp’s reader already gives you ergonomic EDN-like literals and tagged data readers if you later want custom literals.[^4_4]
- **Metadata**: metadata is worth using for non-semantic hints like docs, titles, source provenance, and maybe generated JSON Schema hints, because Basilisp collections and symbols support metadata without affecting equality.[^4_4][^4_2]
- **Multimethods and hierarchies**: these make a strong fit for schema compilation and transformer dispatch by schema tag, since Basilisp multimethods dispatch on arbitrary values and support ad hoc hierarchies.[^4_2]
- **Protocols**: use protocols for internal compiled validator behavior when the dispatch is type-shaped and performance-sensitive, because Basilisp notes protocols are generally faster than multimethods for single-argument type-based dispatch.[^4_2]
- **Transients**: use transients internally when constructing large explain trees or transformed maps/vectors, because Basilisp specifically provides transients for efficient local mutation before freezing back to persistent values.[^4_2]
- **Atoms with validators/watchers**: a registry cache can live in an atom, especially compiled-schema caches or instrumentation state; Basilisp atoms support validators and watchers, which is useful for dev tooling and hot-reload behavior.[^4_2]
- **Python interop**: you can cleanly put hot-path code in Python while keeping the user API in Basilisp, because Basilisp directly supports importing modules, calling methods, accessing properties, and passing Python keyword args.[^4_3]


## Why these choices

These choices keep Balli **idiomatic in Basilisp** rather than becoming “Python with parens.” Basilisp is closest to Clojure in its data modeling and macro/reader ergonomics, but it lives on Python, so the sweet spot is Lisp-native schema authoring plus Python-native optimization where needed.[^4_1][^4_3][^4_4][^4_2]

In practice, that means:

- Public API in Basilisp.
- Schema representation in plain Basilisp data.
- Compilation and transformation pipelines written first in Basilisp.
- Optional Python accelerators only after profiling.[^4_3][^4_2]


## Python libraries

You do **not** need a Python library to make Balli work. Basilisp already gives you the core ingredients: persistent collections, regex support via Python `re`, Python native scalar types, and direct interop.  But some libraries are still worth considering depending on the feature.[^4_3][^4_2]

### Strong candidates

| Library | Use in Balli | Why consider it | Tradeoff |
| :-- | :-- | :-- | :-- |
| `msgspec` | Fast decode/validate of JSON-ish payloads into Python structures or typed structs | Its docs emphasize very high performance, built-in validation, and detailed path-aware validation errors like `$.groups[^4_0]`. [^4_5] | Type-annotation-centric model is not Malli-shaped, so use as an accelerator backend, not the public schema model. [^4_5] |
| `pydantic` | Optional coercion/model export/JSON Schema/OpenAPI integration | Large ecosystem and strong ergonomics for Python users; a good bridge if Balli needs Python-facing adapters. | More opinionated model layer; can pull Balli away from plain-data schemas. |
| `attrs` + `cattrs` | Structuring/unstructuring and fast valid-data conversion | Can be elegant for Python object interop and often fast on valid nested payloads according to comparative benchmark reporting. [^4_6] | Weaker fit for Balli-style error explain UX unless you wrap a lot. [^4_6] |
| `jsonschema` | Optional export verification or interoperability tests | Useful when Balli gains JSON Schema export. | Not a great internal engine for Malli-style data-first explain/transform/coerce. |
| `hypothesis` | Generator/property testing later | Helpful if you want Malli-like generation/testing. | Not needed for MVP. |

### My recommendation

- **For core Balli**: no external Python dependency required. Use Basilisp + Python stdlib first.[^4_3][^4_2]
- **For fast JSON decode/coerce paths**: consider `msgspec` as the most interesting backend candidate. Its repo explicitly claims very high-speed validation/decoding and typed error reporting.[^4_5]
- **For ecosystem integration**: consider `pydantic` only as an adapter boundary, not as Balli’s core engine.
- **For typed object interop**: `attrs` + `cattrs` can be elegant if you expect a lot of Python object conversion, but it is less naturally “Balli-like” than a custom compiler.[^4_6]


## Performance vs elegance

These libraries help in different ways:

- **More performant**: `msgspec` is the clearest performance-oriented option from the sources here; it is explicitly designed for high-performance encode/decode/validation and claims large speedups over alternatives for supported cases.[^4_5]
- **More elegant for Python consumers**: `pydantic` is usually the easiest adapter when talking to Python frameworks and typed models, though that elegance is more Pythonic than Basilisp-idiomatic.
- **More idiomatic for Balli itself**: no external library, because Balli’s most idiomatic form is plain Basilisp data compiled by Balli itself using Basilisp dispatch, transients, and interop as needed.[^4_3][^4_2]

So the answer is:

- fastest likely backend: **msgspec**[^4_5]
- most Python-ecosystem-friendly adapter: **pydantic**
- most Balli-idiomatic core: **custom implementation with optional backend hooks**[^4_2][^4_3]


## Concrete compiler pattern

A practical pattern is multimethod-based normalization plus function compilation.

```clojure
(ns balli.normalize)

(defmulti normalize-node
  (fn [form _opts]
    (cond
      (keyword? form) form
      (vector? form) (first form)
      :else :unknown)))

(defmethod normalize-node :string [form _]
  {:type :string :properties {}})

(defmethod normalize-node :int [form _]
  {:type :int :properties {}})

(defmethod normalize-node :vector [[_ child & more] _]
  {:type :vector
   :properties {}
   :children [(normalize-node child nil)]})

(defmethod normalize-node :map [[_ & entries] _]
  {:type :map
   :properties {}
   :children
   (mapv (fn [[k maybe-props schema]]
           (if (= 3 (count [k maybe-props schema]))
             {:key k
              :properties maybe-props
              :schema (normalize-node schema nil)}
             {:key k
              :properties {}
              :schema (normalize-node maybe-props nil)}))
         entries)})
```

Then compile:

```clojure
(ns balli.compile)

(defn compile-validator [ast]
  (case (:type ast)
    :string (fn [x] (string? x))
    :int    (fn [x] (int? x))
    :maybe  (let [vf (compile-validator (first (:children ast)))]
              (fn [x] (or (nil? x) (vf x))))
    :vector (let [vf (compile-validator (first (:children ast)))]
              (fn [x]
                (and (vector? x)
                     (every? vf x))))
    :map    (compile-map-validator ast)
    (fn [_] false)))
```

For `explain`, compile a sibling function that accumulates structured errors rather than just returning false. Use transients inside `compile-map-validator` explainers if you are building many nested errors, then `persistent!` at the boundary. Basilisp documents transients exactly for efficient local collection building.[^4_2]

## Best implementation plan

Build Balli in four passes:

1. **Pure Basilisp core**: normalize, validate, explain, refs, registry.[^4_4][^4_2]
2. **Transformers**: string->int, string->keyword, JSON key handling, closed/open maps.
3. **Performance layer**: cache compiled validators in an atom; use transients internally.[^4_2]
4. **Optional Python backends**: add `msgspec`-powered decode/validate for selected schema subsets only.[^4_5][^4_3]

That sequence gives you a correct Balli first, then a fast Balli, without letting a Python library dictate the design.

## My recommendation

Make Balli a **Basilisp-native schema compiler** with:

- Malli-style schema forms.
- Basilisp multimethod/protocol-driven compilation.
- Persistent data as the canonical representation.
- Transients for internal builders.
- Python stdlib for regex, datetime, uuid, decimal.
- Optional `msgspec` integration later for high-throughput decode/validation paths.[^4_5][^4_3][^4_2]

If you want, next I can write:

1. `balli.core` and `balli.normalize` MVP code,
2. `:map`, `:string`, `:int`, `:maybe`, `:vector` validator/explainer compiler,
3. and a tiny registry/cache design for Basilisp Polylith.
<span style="display:none">[^4_10][^4_11][^4_12][^4_13][^4_14][^4_15][^4_16][^4_17][^4_18][^4_19][^4_20][^4_7][^4_8][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://cljdoc.org/d/polylith/clj-poly/0.2.21/doc/source-code

[^4_2]: https://github.com/DavidVujic/python-polylith/discussions/351

[^4_3]: https://github.com/furkan3ayraktar/clojure-polylith-realworld-example-app

[^4_4]: https://www.youtube.com/watch?v=3cwI_ENLqhU

[^4_5]: https://polylith.gitbook.io/polylith/conclusion/faq

[^4_6]: https://krabarena.com/claims/attrs-cattrs-hits-1-7m-payloads-sec-beating-pydantic-v2-1-9x-and-marshmallow-17

[^4_7]: https://basilisp.readthedocs.io/en/latest/concepts.html

[^4_8]: https://basilisp.readthedocs.io/en/latest/reader.html

[^4_9]: https://jcristharif.com/msgspec/_sources/benchmarks.rst.txt

[^4_10]: https://www.libhunt.com/compare-msgspec-vs-pydantic

[^4_11]: https://github.com/basilisp-lang/basilisp/blob/main/CHANGELOG.md

[^4_12]: https://tomodahinata.com/blog/pydantic-vs-dataclasses-typeddict-attrs-msgspec-comparison-guide

[^4_13]: https://basilisp.readthedocs.io/en/v0.2.3/releasenotes.html

[^4_14]: https://wyfo.github.io/apischema/0.15/benchmark/

[^4_15]: https://github.com/jcrist/msgspec

[^4_16]: https://talkpython.fm/episodes/show/442/ultra-high-speed-message-parsing-with-msgspec

[^4_17]: https://gist.github.com/jcrist/d62f450594164d284fbea957fd48b743

[^4_18]: https://basilisp.readthedocs.io/en/latest/pyinterop.html

[^4_19]: https://www.youtube.com/watch?v=ruGRHYpq448

[^4_20]: https://github.com/basilisp-lang/basilisp


---

# Yes write that stuff. I like where this is going. What more "advanced" features of malli should we port into balli and when and in what order of precedence?

Yes — the next move is to write a **small but real Balli core** and then layer advanced Malli features in an order that compounds well. Malli’s documented surface includes open/closed maps, humanized errors, spell-checking, bidirectional transformation, generators, schema tools, registries, JSON Schema/Swagger support, function schemas, parsing/unparsing, and sequence schemas, while Basilisp gives us the right substrate for a data-first compiler with multimethods, protocols, atoms, transients, and Python interop.[^5_1][^5_2][^5_3]

## MVP code

Below is a good first-pass design for `balli.core`, `balli.normalize`, and a validator/explainer compiler for `:map`, `:string`, `:int`, `:maybe`, and `:vector`. This stays Basilisp-native: schema forms are plain data, normalization is multimethod-friendly, compiled validators are cached, and explain data is structured from the start. Basilisp’s persistent collections and transients make this a natural fit.[^5_3]

```clojure
;;;; src/balli/core.lpy
(ns balli.core
  (:require [basilisp.core :as b]
            [balli.normalize :as norm]
            [balli.compile :as comp]
            [balli.registry :as reg]))

(defn schema
  ([form] (schema form nil))
  ([form opts]
   (let [registry (or (:registry opts) (reg/default-registry))
         ast (norm/normalize form opts)]
     {:balli/schema true
      :form form
      :ast ast
      :opts opts
      :registry registry})))

(defn schema? [x]
  (true? (:balli/schema x)))

(defn form [s]
  (if (schema? s) (:form s) s))

(defn ast [s]
  (if (schema? s) (:ast s) (-> s schema :ast)))

(defn properties [s]
  (:properties (ast s)))

(defn children [s]
  (:children (ast s)))

(defn- ensure-schema [s opts]
  (if (schema? s) s (schema s opts)))

(defn validator
  ([s] (validator s nil))
  ([s opts]
   (let [s* (ensure-schema s opts)]
     (comp/compile-validator (:ast s*) (:registry s*) opts))))

(defn explainer
  ([s] (explainer s nil))
  ([s opts]
   (let [s* (ensure-schema s opts)]
     (comp/compile-explainer (:ast s*) (:registry s*) opts))))

(defn validate
  ([s value] (validate s value nil))
  ([s value opts]
   ((validator s opts) value)))

(defn explain
  ([s value] (explain s value nil))
  ([s value opts]
   ((explainer s opts) value)))

(defn assert-valid
  ([s value] (assert-valid s value nil))
  ([s value opts]
   (if-let [e (explain s value opts)]
     (throw (python/Exception (pr-str e)))
     value)))
```

```clojure
;;;; src/balli/registry.lpy
(ns balli.registry)

(def ^:private builtins
  {:any    {:type :any :properties {} :children []}
   :string {:type :string :properties {} :children []}
   :int    {:type :int :properties {} :children []}
   :maybe  {:type :maybe}
   :vector {:type :vector}
   :map    {:type :map}})

(defn default-registry []
  builtins)

(defn registry [m]
  (merge builtins m))

(defn resolve-schema [registry k]
  (get registry k))
```

```clojure
;;;; src/balli/normalize.lpy
(ns balli.normalize
  (:require [balli.registry :as reg]))

(defn- schema-form?
  [x]
  (or (keyword? x) (vector? x)))

(defmulti normalize
  (fn [form _opts]
    (cond
      (keyword? form) form
      (vector? form) (first form)
      :else :unknown)))

(defmethod normalize :any [_ _]
  {:type :any :properties {} :children []})

(defmethod normalize :string [form _opts]
  (if (vector? form)
    (let [[_ maybe-props] form]
      {:type :string
       :properties (if (map? maybe-props) maybe-props {})
       :children []})
    {:type :string :properties {} :children []}))

(defmethod normalize :int [form _opts]
  (if (vector? form)
    (let [[_ maybe-props] form]
      {:type :int
       :properties (if (map? maybe-props) maybe-props {})
       :children []})
    {:type :int :properties {} :children []}))

(defmethod normalize :maybe [[_ child & more] opts]
  {:type :maybe
   :properties (if (map? (first more)) (first more) {})
   :children [(normalize child opts)]})

(defmethod normalize :vector [[_ child & more] opts]
  {:type :vector
   :properties (if (map? (first more)) (first more) {})
   :children [(normalize child opts)]})

(defn- normalize-map-entry [entry opts]
  (let [[k a b] entry]
    (cond
      (nil? b)
      {:key k
       :properties {}
       :schema (normalize a opts)}

      (map? a)
      {:key k
       :properties a
       :schema (normalize b opts)}

      :else
      {:key k
       :properties {}
       :schema (normalize a opts)})))

(defmethod normalize :map [[_ & entries] opts]
  (let [props (if (map? (first entries)) (first entries) {})
        body  (if (map? (first entries)) (rest entries) entries)]
    {:type :map
     :properties props
     :children (mapv #(normalize-map-entry % opts) body)}))

(defmethod normalize :ref [[_ k & more] _opts]
  {:type :ref
   :properties (if (map? (first more)) (first more) {})
   :ref k
   :children []})

(defmethod normalize :unknown [form _opts]
  (throw (python/Exception (str "Unknown schema form: " form))))
```

```clojure
;;;; src/balli/compile.lpy
(ns balli.compile
  (:require [balli.registry :as reg]))

(defn- pred-string? [x] (python/isinstance x str))
(defn- pred-int? [x] (and (python/isinstance x int)
                          (not (python/isinstance x bool))))
(defn- pred-vector? [x] (or (vector? x) (python/isinstance x list)))
(defn- pred-map? [x] (map? x))

(defn- push-error! [errors err]
  (conj! errors err))

(defn- finalize-errors [schema value errors]
  (let [errs (persistent! errors)]
    (when (seq errs)
      {:schema schema
       :value value
       :errors errs})))

(defn- compile-string-validator [ast]
  (let [min-len (:min (:properties ast))
        max-len (:max (:properties ast))]
    (fn [x]
      (and (pred-string? x)
           (if min-len (<= min-len (count x)) true)
           (if max-len (<= (count x) max-len) true)))))

(defn- compile-string-explainer [ast]
  (let [min-len (:min (:properties ast))
        max-len (:max (:properties ast))]
    (fn [x path in]
      (let [errors (transient [])]
        (when-not (pred-string? x)
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/invalid-type}))
        (when (and (pred-string? x) min-len (< (count x) min-len))
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/string-too-short :min min-len}))
        (when (and (pred-string? x) max-len (> (count x) max-len))
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/string-too-long :max max-len}))
        (persistent! errors)))))

(defn- compile-int-validator [ast]
  (let [min-v (:min (:properties ast))
        max-v (:max (:properties ast))]
    (fn [x]
      (and (pred-int? x)
           (if min-v (<= min-v x) true)
           (if max-v (<= x max-v) true)))))

(defn- compile-int-explainer [ast]
  (let [min-v (:min (:properties ast))
        max-v (:max (:properties ast))]
    (fn [x path in]
      (let [errors (transient [])]
        (when-not (pred-int? x)
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/invalid-type}))
        (when (and (pred-int? x) min-v (< x min-v))
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/int-too-small :min min-v}))
        (when (and (pred-int? x) max-v (> x max-v))
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/int-too-large :max max-v}))
        (persistent! errors)))))

(declare compile-validator)
(declare compile-explainer)

(defn- compile-maybe-validator [ast registry opts]
  (let [vf (compile-validator (first (:children ast)) registry opts)]
    (fn [x] (or (nil? x) (vf x)))))

(defn- compile-maybe-explainer [ast registry opts]
  (let [ef (compile-explainer (first (:children ast)) registry opts)]
    (fn [x path in]
      (if (nil? x) [] (ef x path in)))))

(defn- compile-vector-validator [ast registry opts]
  (let [vf (compile-validator (first (:children ast)) registry opts)]
    (fn [x]
      (and (pred-vector? x)
           (every? vf x)))))

(defn- compile-vector-explainer [ast registry opts]
  (let [ef (compile-explainer (first (:children ast)) registry opts)]
    (fn [x path in]
      (let [errors (transient [])]
        (if-not (pred-vector? x)
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/invalid-type})
          (doseq [[idx item] (map-indexed vector x)]
            (doseq [err (ef item (conj path idx) (conj in idx))]
              (push-error! errors err))))
        (persistent! errors)))))

(defn- compile-map-validator [ast registry opts]
  (let [entries (:children ast)
        closed? (true? (:closed (:properties ast)))
        compiled
        (mapv (fn [{:keys [key properties schema]}]
                {:key key
                 :optional? (true? (:optional properties))
                 :vf (compile-validator schema registry opts)})
              entries)
        declared-keys (set (map :key compiled))]
    (fn [x]
      (and (pred-map? x)
           (every?
            (fn [{:keys [key optional? vf]}]
              (if (contains? x key)
                (vf (get x key))
                optional?))
            compiled)
           (if closed?
             (every? declared-keys (keys x))
             true)))))

(defn- compile-map-explainer [ast registry opts]
  (let [entries (:children ast)
        closed? (true? (:closed (:properties ast)))
        compiled
        (mapv (fn [{:keys [key properties schema]}]
                {:key key
                 :optional? (true? (:optional properties))
                 :ef (compile-explainer schema registry opts)})
              entries)
        declared-keys (set (map :key compiled))]
    (fn [x path in]
      (let [errors (transient [])]
        (if-not (pred-map? x)
          (push-error! errors {:path path :in in :schema ast :value x :type :balli/invalid-type})
          (do
            (doseq [{:keys [key optional? ef]} compiled]
              (if (contains? x key)
                (doseq [err (ef (get x key) (conj path key) (conj in key))]
                  (push-error! errors err))
                (when-not optional?
                  (push-error! errors {:path (conj path key)
                                       :in (conj in key)
                                       :schema ast
                                       :value x
                                       :type :balli/missing-key
                                       :key key}))))
            (when closed?
              (doseq [k (keys x)]
                (when-not (contains? declared-keys k)
                  (push-error! errors {:path (conj path k)
                                       :in (conj in k)
                                       :schema ast
                                       :value (get x k)
                                       :type :balli/extra-key
                                       :key k})))))
        (persistent! errors)))))

(defn compile-validator [ast registry opts]
  (case (:type ast)
    :any    (fn [_] true)
    :string (compile-string-validator ast)
    :int    (compile-int-validator ast)
    :maybe  (compile-maybe-validator ast registry opts)
    :vector (compile-vector-validator ast registry opts)
    :map    (compile-map-validator ast registry opts)
    :ref    (let [target (reg/resolve-schema registry (:ref ast))]
              (if-not target
                (fn [_] false)
                (compile-validator target registry opts)))
    (fn [_] false)))

(defn compile-explainer [ast registry opts]
  (let [node-ef
        (case (:type ast)
          :any    (fn [_ _ _] [])
          :string (compile-string-explainer ast)
          :int    (compile-int-explainer ast)
          :maybe  (compile-maybe-explainer ast registry opts)
          :vector (compile-vector-explainer ast registry opts)
          :map    (compile-map-explainer ast registry opts)
          :ref    (let [target (reg/resolve-schema registry (:ref ast))]
                    (if-not target
                      (fn [x path in]
                        [{:path path :in in :schema ast :value x :type :balli/unresolved-ref}])
                      (compile-explainer target registry opts)))
          (fn [x path in]
            [{:path path :in in :schema ast :value x :type :balli/unknown-schema}]))]
    (fn [value]
      (let [errors (node-ef value [] [])]
        (when (seq errors)
          {:schema ast
           :value value
           :errors errors})))))
```

A few notes:

- I would add `balli.transform` only after this validator/explainer loop is stable, because Malli’s transformer model is powerful but significantly increases surface area. Malli documents decoding, encoding, transformers, named transformers, interceptor phases, and transformation chains, so it deserves its own pass rather than being mixed into v0 validation work.[^5_4]
- I would also add a small `balli.error/humanize` layer next, since Malli emphasizes humanized errors as a first-class feature.[^5_2]


## What to port next

The best precedence order is based on payoff, implementation risk, and how much each feature unlocks other features. Malli’s documented advanced features include humanized/localized errors, spell-checking, bidirectional transformation, generators, schema tools, rich registries, JSON Schema/Swagger support, parsing/unparsing, sequence schemas, and function schemas.[^5_5][^5_6][^5_2]

### Tier 1

Port these first:

- **Humanized errors**: high user value, low to medium complexity, and it builds directly on the explain format you already need. Malli explicitly treats error reporting and humanized/localized errors as core.[^5_2]
- **Open/closed maps plus map utilities**: closed maps, optional keys, key transforms, select/merge/union are extremely practical for API and config work. Malli’s changelog specifically calls out declarative `:merge`, `:union`, and `:select-keys` transformation schemas.[^5_7]
- **Transformers / decode / encode / coercion**: this is one of Malli’s most practical differentiators, and the docs show a mature transformer model with decoding, encoding, interceptors, named transformers, and composition.[^5_4]
- **Better registries and refs**: Malli highlights immutable, mutable, dynamic, lazy, and composite registries; even if Balli starts simpler, richer registry semantics pay off early for modular apps.[^5_2]


### Tier 2

Then:

- **Schema walking and utilities**: walk, subschemas, deref-all, property editing, schema transforms. Malli’s tooling around schema transformation and walking unlocks many other features elegantly.[^5_7]
- **JSON Schema export**: very useful once transform and registry semantics are clear, and Malli explicitly supports JSON Schema and Swagger/OpenAPI-related export.[^5_2]
- **Default value transformer**: very practical for forms/config bootstrapping, and Malli’s changelog shows this as a concrete transformer utility.[^5_7]
- **Spell-checking of keys**: nice DX feature once maps and explain paths are solid. Malli calls this out directly.[^5_2]


### Tier 3

After the above:

- **Generators**: valuable for testing, examples, and fuzzing, but dependent on a stable schema core and registry story. Malli includes value and schema generation and ties generation into refs and utilities.[^5_7][^5_2]
- **Schema inference from sample data**: powerful, but not essential to core correctness. Malli has schema inference/tools, but this is more of a developer convenience layer.[^5_8][^5_5]
- **Parsing/unparsing**: useful, but often downstream of transformation and schema walking. Malli lists parsing/unparsing as a feature area, but it is not where I would start.[^5_5]


### Tier 4

Save for later:

- **Sequence schemas**: these are powerful but tricky. Malli discussion explicitly said sequence schemas and parsing were significant areas of active work.[^5_2]
- **Function schemas**: useful, especially for instrumentation and `defn` wrappers, but they depend on sequence schemas for argument specs and are more advanced ergonomically. Malli’s function schema docs describe `:=>` and `:function` schemas for args and return values, which is great once the sequence machinery exists.[^5_6]
- **Localization/i18n of errors**: nice once humanization exists.
- **Swagger/OpenAPI-specific extras, DOT export, editor integrations**: later ecosystem polish.[^5_2]


## Recommended order

Here is the exact order I would use:

1. Stable core validate/explain for maps, vectors, maybe, refs.
2. Error humanization.
3. Decode/encode/coerce transformers.
4. Registry upgrades: layered/dynamic/lazy/composite refs.
5. Schema walking and utilities.
6. Open/closed map helpers and declarative schema transforms like `:merge`, `:union`, `:select-keys`.
7. JSON Schema export.
8. Default values and richer transformer composition.
9. Key spell-checking.
10. Generators.
11. Schema inference.
12. Parsing/unparsing.
13. Sequence schemas.
14. Function schemas.
15. OpenAPI/Swagger/DOT/editor tooling.

That order keeps Balli useful for real API/data-validation work early, while postponing the deepest complexity until the substrate is proven. Malli’s own feature descriptions suggest that transformation, registries, and tooling are foundational, while sequence/function schemas are more advanced areas.[^5_6][^5_4][^5_2]

## Why this order fits Basilisp

This order also matches Basilisp well:

- Validation, explain data, registries, and schema walkers fit naturally into Basilisp’s data-oriented style and multimethod/protocol dispatch.[^5_3]
- Transformer stages align nicely with Basilisp plus Python interop, since decode/encode often touch host types like datetime, UUID, Decimal, and JSON-ish wire data.[^5_1]
- Generator and inference features can later lean on Python libraries if needed, but they should not dictate the core schema representation.
- Sequence/function schemas are the most semantically subtle, so they should come only after the simpler compiler pipeline is battle-tested.[^5_6][^5_2]


## Python-library guidance

For the code above, no library is necessary. For advanced features:

- **Transformers**: Python stdlib is enough at first, especially `datetime`, `uuid`, `decimal`, `json`, and `re`.[^5_1]
- **Performance-sensitive decode/validation**: `msgspec` is still the best candidate to integrate selectively once Balli’s forms are stable, because it is built for fast serialization and validation.[^5_9]
- **Generators**: use Hypothesis later, if Balli gains a generation layer.
- **JSON Schema/OpenAPI**: maybe no dependency initially; emit maps directly.

So I would keep the current Balli compiler custom, Basilisp-native, and dependency-light, then add optional backend adapters later.

## Next code I’d write

The highest-value next batch is:

- `balli.error/humanize`
- `balli.transform` with `string-transformer`, `json-transformer`, and default-value support
- registry composition and lazy refs
- simple schema walkers

That would move Balli from “validator prototype” to “real schema system” much faster than jumping to sequence or function schemas.[^5_4][^5_7][^5_2]

Would you like me to write the next pass now: `balli.error` plus `balli.transform` with decode/encode/coerce?
<span style="display:none">[^5_10][^5_11][^5_12][^5_13][^5_14][^5_15][^5_16]</span>

<div align="center">⁂</div>

[^5_1]: https://basilisp.readthedocs.io/en/latest/pyinterop.html

[^5_2]: https://clojureverse.org/t/introducing-malli-a-new-data-validation-and-specification-library-for-clojure-script/6653

[^5_3]: https://basilisp.readthedocs.io/en/latest/concepts.html

[^5_4]: https://github.com/metosin/malli/blob/master/docs/value-transformation.md

[^5_5]: https://github.com/metosin/malli

[^5_6]: https://github.com/metosin/malli/blob/master/docs/function-schemas.md

[^5_7]: https://cljdoc.org/d/metosin/malli/0.2.1/doc/changelog

[^5_8]: https://www.reddit.com/r/Clojure/comments/dkwgjr/malliio_the_datadriven_schema_playground/

[^5_9]: https://github.com/jcrist/msgspec

[^5_10]: https://github.com/metosin/malli/blob/master/CHANGELOG.md

[^5_11]: https://www.metosin.fi/blog/malli

[^5_12]: https://github.com/metosin/malli/blob/master/docs/tips.md

[^5_13]: https://clojurecivitas.github.io/malli/elements_of_malli.html

[^5_14]: https://basilisp.readthedocs.io/en/v0.2.3/api/core.html

[^5_15]: https://www.slideshare.net/slideshow/designing-with-malli/239915152?nway-content_model=A

[^5_16]: https://www.slideshare.net/slideshow/malli-inside-datadriven-schemas/229446966


---

# Which aspects of malli do you think would be most difficult to port to balli and why?

The hardest parts to port from Malli to Balli are the features where Malli is not “just validation,” but a **small schema runtime** with parsing semantics, transformation pipelines, instrumentation hooks, and cross-cutting tooling. Based on Malli’s documented features, the most difficult areas are sequence schemas, parsing/unparsing, function schemas, the full transformer/interceptor system, and the broader tooling layer around registries/generators/JSON Schema.[^6_1][^6_2][^6_3]

## Hardest features

### 1. Sequence schemas

These are probably the single hardest feature family to port cleanly. Malli added rich sequence schemas such as `:cat`, `:catn`, `:alt`, `:altn`, `:?`, `:*`, `:+`, and `:repeat`, and those are fundamentally more like parser combinators or regex engines over sequences than ordinary predicate validation.[^6_2][^6_4]

Why hard in Balli:

- They require **ordered consumption semantics**, not just “does every element satisfy X.”[^6_2]
- They blur validation and parsing, because the output may carry structure from named branches and captures.[^6_4]
- Error reporting is trickier, since failure is often about where the parser backtracked, not just which leaf predicate failed.[^6_4]
- If you later want decode/encode to work over sequence schemas, you need stable semantics for transformed positional structures too.[^6_3][^6_4]

This is much more complex than `[:vector :int]`, and it tends to infect function schemas, parsers, and instrumented arity handling downstream.[^6_5][^6_2]

### 2. Parsing and unparsing

Malli explicitly added `m/parse`, `m/parser`, `m/unparse`, and `m/unparser`, which means schemas can describe not only validity but also **structured interpretation** of input values.  That is a big leap from boolean validation.[^6_6][^6_2]

Why hard in Balli:

- Parsing needs a stable model for what a parsed result even is: original value, normalized value, captured structure, named nodes, or transformed output.[^6_2][^6_4]
- Unparsing forces you to define the inverse mapping, which is often much harder than validation alone.[^6_2]
- Once you support parse/unparse, explain data, sequence schemas, and transformers all need to agree on traversal order and node semantics.[^6_3][^6_4]
- Performance matters more, because parsers get used on hot paths and often benefit from compilation/caching. Malli’s parser API explicitly mentions caching parser functions on schemas.[^6_6]

This is where Balli starts becoming a real schema VM, not just a validator.

### 3. Function schemas

Malli’s `:=>` and `:function` schemas describe function arguments and return values, and they depend on sequence-schema-like argument descriptions and instrumentation.  These are conceptually elegant, but hard in practice.[^6_5][^6_2]

Why hard in Balli:

- Function schemas depend on **argument parsing**, including multi-arity and named positional structure.[^6_5]
- They need **instrumentation** or wrapping so schemas actually run at call time. Malli docs and community examples make clear that function schemas are usually collected and instrumented rather than always active.[^6_7][^6_5]
- Basilisp is Clojure-like, but hosted on Python, so wrapping functions, preserving metadata, names, arities, docstrings, and developer ergonomics is more delicate than plain value validation.[^6_8][^6_9]
- If you want function schemas to work on multimethods or macro-defined functions, the complexity goes up again.[^6_7]

This is one of the best examples of a feature that sounds small but actually sits on top of several lower-level systems.

## Medium-hard features

### 4. Full transformer/interceptor system

Simple coercion is not that bad, but Malli’s full transformation model is much richer: decoding, encoding, named transformers, interceptors, enter/leave phases, and composable transformer chains.  That is a whole architecture, not a utility function.[^6_10][^6_3]

Why hard in Balli:

- You need to define when transforms happen: before child validation, after child validation, around refs, before/after collections, and so on.[^6_3]
- Composition must stay predictable even when multiple transformers target the same node.[^6_3]
- Sequence schemas and parsing complicate transformation order even more.[^6_4][^6_3]
- Python-host interop introduces type boundary questions, like when a string should become a Python `datetime`, `UUID`, or Decimal versus staying as plain data.[^6_9]

This feature is very valuable, but it requires a strong internal traversal model first.

### 5. Registries, recursive refs, and schema walking

Basic refs are easy; **good** refs are not. Malli has richer registry semantics and improved handling of schema references across generators, walking, JSON Schema, and Swagger export.[^6_11][^6_12]

Why hard in Balli:

- Recursive schemas need cycle-safe dereferencing and caching.[^6_11]
- Walkers need to know when to deref and when not to deref, which sounds small but becomes central once you add utilities and exporters.[^6_11]
- Composite/dynamic/lazy registry behavior complicates compilation caching and schema identity.
- Advanced features like generators and exporters need consistent ref semantics, so a poor early registry design causes later rework.[^6_12][^6_11]

This is more “architecture hard” than “algorithm hard.”

## Less hard, but still subtle

### 6. Generators

Malli includes value and schema generation.  Balli could lean on Python libraries later, but making generation feel like a natural extension of schema semantics is still nontrivial.[^6_13][^6_12]

Why hard:

- Not every schema is easily generatable, especially custom predicates and open-ended `:fn` nodes.
- Generated values should respect constraints, refs, and maybe transformers.
- Shrinking and reproducibility become important if Balli wants real testing value.

Still, generators are easier than sequence/function schema machinery because they can be added more independently.

### 7. JSON Schema / Swagger / OpenAPI export

Malli supports JSON Schema and Swagger/OpenAPI-related output.  This is very useful, but the main difficulty is semantic mismatch rather than implementation complexity.[^6_12][^6_11][^6_2]

Why hard:

- Some Malli ideas map poorly to JSON Schema, especially predicate-based, function-like, or transformation-aware schemas.
- Refs, unions, recursive schemas, and defaults need careful exporter rules.
- If Balli’s core semantics are not stable yet, exporter output will churn.

Still, this is often more straightforward than parsing/function instrumentation, because it is mostly a projection problem.

## Why these are hard specifically in Basilisp

The difficulty is not only “Malli is complex.” It is also that Balli lives in Basilisp, which is Clojure-like but hosted on Python. Basilisp gives you persistent collections, multimethods, protocols, reader forms, and good interop, which helps a lot for data-first schemas and compiler structure.  But the host boundary makes some Malli features harder to reproduce exactly:[^6_8][^6_9]

- **Host types differ**: Python numbers, dicts, lists, datetimes, and classes are not JVM/Clojure values, so transform and parse semantics need host-aware rules.[^6_9]
- **Instrumentation model differs**: function wrapping and metadata preservation work differently on Python-hosted functions than on JVM Vars/functions.[^6_7][^6_9]
- **Performance profile differs**: some compiled parser/generator strategies that work on the JVM may need different implementation choices on Python.
- **Ecosystem assumptions differ**: Malli can integrate naturally with Clojure libraries like reitit and sci, while Balli would need Python/Basilisp-native equivalents or adapters. Malli changelog notes even mention sci and OpenAPI-related integration points.[^6_11]

So Balli should not aim for exact cloning in the hardest areas; it should aim for equivalent capability with Basilisp-appropriate semantics.

## Difficulty ranking

My ranking from hardest to easiest is:


| Feature | Difficulty | Main reason |
| :-- | :-- | :-- |
| Sequence schemas | Very high | Parser/regex semantics over sequences, backtracking, captures, error locality. [^6_2][^6_4] |
| Parsing / unparsing | Very high | Requires bidirectional structural semantics and caching. [^6_2][^6_6] |
| Function schemas | Very high | Depends on sequence schemas plus instrumentation/wrapping. [^6_5][^6_7] |
| Full transformer system | High | Enter/leave phases, composition, named transformers, host-type boundaries. [^6_3] |
| Advanced registries / recursive refs / walking | High | Cross-cutting architectural effect on compile, cache, export, generation. [^6_12][^6_11] |
| Generators | Medium | Constraint-aware synthesis and later shrinking/testing semantics. [^6_12][^6_13] |
| JSON Schema / Swagger export | Medium | Semantic projection and feature mismatch. [^6_12][^6_2] |
| Humanized errors / spell-checking | Low to medium | Mostly a UX layer on top of solid explain data. [^6_12] |

## What this means for Balli

The implication is:

- Build Balli around **validate/explain/transform/ref/walk** first.
- Delay **sequence schemas, parse/unparse, and function schemas** until the traversal model is proven.
- Treat **advanced exporter/generator features** as secondary layers.
- Accept that a few Malli capabilities may need to be “Balli-native equivalents” rather than literal ports.

That path matches both Malli’s feature structure and Basilisp’s strengths much better than trying to jump straight to the hardest pieces.[^6_8][^6_12][^6_3]

If you want, I can turn this into a concrete Balli roadmap with “easy / medium / hard” milestones and a suggested namespace-by-namespace implementation order.
<span style="display:none">[^6_14][^6_15][^6_16][^6_17][^6_18][^6_19]</span>

<div align="center">⁂</div>

[^6_1]: https://github.com/metosin/malli

[^6_2]: https://cljdoc.org/d/metosin/malli/0.4.0/doc/changelog

[^6_3]: https://github.com/metosin/malli/blob/master/docs/value-transformation.md

[^6_4]: https://www.metosin.fi/blog/malli-regex-schemas

[^6_5]: https://github.com/metosin/malli/blob/master/docs/function-schemas.md

[^6_6]: https://cljdoc.org/d/metosin/malli/0.20.1/api/malli.core

[^6_7]: https://www.wedesoft.de/software/2023/12/25/clojure-function-schemas-with-malli/

[^6_8]: https://basilisp.readthedocs.io/en/latest/concepts.html

[^6_9]: https://basilisp.readthedocs.io/en/latest/pyinterop.html

[^6_10]: https://cljdoc.org/d/metosin/malli/0.2.1

[^6_11]: https://clojureverse.org/t/introducing-malli-a-new-data-validation-and-specification-library-for-clojure-script/6653/5

[^6_12]: https://clojureverse.org/t/introducing-malli-a-new-data-validation-and-specification-library-for-clojure-script/6653

[^6_13]: https://cljdoc.org/d/metosin/malli/0.2.1/doc/changelog

[^6_14]: https://github.com/metosin/malli/blob/master/CHANGELOG.md

[^6_15]: https://basilisp.readthedocs.io/en/v0.2.3/api/core.html

[^6_16]: https://basilisp.readthedocs.io/en/latest/api/io.html

[^6_17]: https://github.com/metabase/metabase/wiki/Backend:-Metabase-Malli-Cheatsheet

[^6_18]: https://cljdoc.org/d/metosin/malli/0.8.8/doc/changelog

[^6_19]: https://github.com/metosin/malli/blob/master/docs/tips.md
