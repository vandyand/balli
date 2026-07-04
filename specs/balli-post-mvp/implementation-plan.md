# Balli Post-MVP — Implementation Plan

## Overview

Eleven phases closing the Malli feature gap, dependency-ordered: spike → transformers → walk/util → json-schema → spell-check → parse → seqex → generators → function schemas → provider → docs. Semantic contract per phase: the matching section of [malli-semantics.md](malli-semantics.md) (§A–§I). Each phase: narrow test file green (`basilisp test tests/<file>`), live checkpoints via `basilisp run -c` from repo root, zero regressions in the full suite.

**Composition rule (from the MVP retro):** every phase's checkpoints must include at least one cross-feature composition case (e.g. transformer through a ref, seqex inside a map, generator over a registry schema), not just per-type units. Schema-boundary validation (malformed schema → `:balli.core/invalid-schema` at normalize) applies to every new schema type.

## Prerequisites

- MVP merged to main (`0c74750`); branch `balli-post-mvp`; 93 tests green.
- Malli source at `/tmp/malli-src/` (re-extract: `cd /tmp/malli-src && unzip -oq ~/.m2/repository/metosin/malli/0.20.0/malli-0.20.0.jar`).

## Phase 0: Substrate spike

Goal: prove the Basilisp facilities the hard phases depend on, before building on them.

- [ ] `defrecord Tag [key value]` + `Tags [values]`: construction, field access (`:key`, `(.-key r)`), value equality, `instance?` checks, printing. If defrecord is unusable, decide fallback (marker maps `{:balli/tag true ...}`) and record it here + in research.md
- [ ] Python `random` interop: `(random/Random 42)` seeded instance, `.randint`, `.uniform`, `.choice` on a Basilisp vector (may need `(vec ...)`→python list conversion — verify), determinism across two same-seed instances
- [ ] Thunk-stack loop viability: a `loop/recur` driver popping closures from a Python list (or Basilisp vector in an atom/volatile) — run 100k thunk iterations, confirm no recursion error and <2s
- [ ] `volatile!`/`vswap!` availability (else atoms)
- [ ] `sequential?` on lists/vectors/lazy-seqs/ranges; NOT strings/sets/maps
- [ ] Record findings in this file under "Phase 0 findings"; adjust later-phase notes if invalidated

**Checkpoints:** each bullet is its own `basilisp run -c` probe; report exact outputs. No test file (spike only).

## Phase 1: Transformers

Goal: `balli.transform` + core decode/encode/coerce per semantics §A.

- [ ] `src/balli/transform.lpy`: transformer representation `{:balli/transformer true :chain [{:name :decoders :encoders :default-decoder :default-encoder} ...]}`; `(transformer & ts)` flattening maps/transformers into one chain
- [ ] Interceptor normalization: fn → `{:enter f}`; `{:compile f}` → `(f schema-ast opts)` then normalize+merge; `{:enter :leave}` as-is. Chain fold: enter composes in chain order, leave in reverse
- [ ] `compile-transformer [ast registry transformer method opts]` in a new `balli.compile` section (or `transform.lpy`): per-node resolution priority (schema props `{:decode {:string f}}` → `:decode/string` qualified prop → type table → default), node combinator `leave∘children∘enter`, per-type descent: `:map` (present keys only, `map?` guard), `:map-of` (keys+vals), colls, `:tuple` (per-index), `:and`/`:maybe`/`:not` (children composed in order), `:or` (decode try-validate-first / encode first-valid-branch), `:multi` (dispatch post-enter), `:enum`/`:=` (infer child type, reuse coder), `:ref` (lazy memoized target), seqex types absent until Phase 6 (pass-through)
- [ ] Built-ins per §A: `string-transformer`, `json-transformer`, `strip-extra-keys-transformer`, `key-transformer`, `default-value-transformer`, `collection-transformer`. All scalar coercions lenient (unchanged on mismatch, try/catch)
- [ ] `balli.core`: `decoder`/`decode`/`encoder`/`encode` (raw-form + schema-object, cached per `[method transformer-identity]` in schema cache), `coercer`/`coerce` (decode→validate→return-or-throw ex-info `{:type :balli.core/coercion :value :schema :explain}`)
- [ ] `tests/test_transform.lpy`: string decode of int/double/boolean/keyword/uuid/enum; json decode excludes string→int; encode reversals; strip-extra-keys open/closed/`{:closed false}`; default-value nil-vs-missing + map fill; key-transformer; composition order (two transformers, decode chain order vs encode reversal); property override `:decode/string` on a schema; `:or`/`:multi`/ref descent; coerce success + throw; **composition case: `[:ref :user]` in registry decoding nested map keys' values**

**Checkpoints:**
- `(b/decode [:map [:age :int] [:tags [:set :keyword]]] {:age "42" :tags ["a" "b"]} (bt/string-transformer))` → `{:age 42 :tags #{:a :b}}`
- `(b/decode :int "42" (bt/json-transformer))` → `"42"` (json does NOT parse number strings)
- `(b/decode [:map [:x :int]] {:x 1 :junk 2} (bt/strip-extra-keys-transformer))` → `{:x 1}`
- `(b/decode [:map [:x {:default 7} :int]] {} (bt/default-value-transformer))` → `{:x 7}`
- `(try (b/coerce :int "x" (bt/json-transformer)) (catch python/Exception e (:type (ex-data e))))` → `:balli.core/coercion`
- Narrow: `basilisp test tests/test_transform.lpy`

## Phase 2: Walk + util + per-branch :or explain

Goal: semantics §C.

- [ ] `balli.core/walk`: form-level postwalk — `(walk s f)` / `(walk s f opts)`; f receives `[form path walked-children-form]`-rebuilt schema form; `schema-walker` helper. Walk map entries with key in path, indexed children with index; do NOT enter refs (ref child stays the keyword)
- [ ] `src/balli/util.lpy`: `merge`, `union`, `select-keys`, `dissoc`, `optional-keys`, `required-keys`, `closed-schema`, `open-schema`, `get`, `get-in` — form→form fns per §C (accept forms or schema objects, return forms; normalize internally for entry introspection)
- [ ] Per-branch `:or` explain in `compile.lpy`: all-branches-fail → concat each branch's errors with branch index appended to `:path` (`:in` unchanged); delete the single-generic-error simplification; update affected MVP tests (`tests/test_explain.lpy` :or cases) and the README difference bullet
- [ ] `tests/test_util.lpy`: merge (props, duplicate keys, requiredness later-wins, deep nested-map merge, non-map s2-wins), union (equal forms, differing → `[:or]`, optional-in-either), select-keys/dissoc/optional-keys/required-keys/closed-schema (recursive, respects explicit `:closed false`)/open-schema/get/get-in; walk postwalk order + path correctness; **composition: `(closed-schema (u/merge A B))` then validate**

**Checkpoints:**
- `(u/merge [:map [:x :int]] [:map [:x :string] [:y :int]])` → `[:map [:x :string] [:y :int]]`
- `(u/union [:map [:x :int]] [:map [:x :string]])` → `[:map [:x [:or :int :string]]]`
- `(u/closed-schema [:map [:a [:map [:b :int]]]])` → both maps get `{:closed true}`
- `(:errors (b/explain [:or :int :string] :kw))` → 2 errors, paths `[0]` and `[1]`
- Narrow: `basilisp test tests/test_util.lpy` + updated `tests/test_explain.lpy`

## Phase 3: JSON Schema export

Goal: `balli.json-schema/transform` per §B.

- [ ] `src/balli/json_schema.lpy`: `transform` (form or schema object, optional opts) → string-keyed Basilisp map. Full type mapping table from §B incl. min/max property translations per type family; `:title`/`:description`/`:default` passthrough; `:json-schema` whole-node override; `:json-schema/foo` unlift (wins over generated keys)
- [ ] Refs: `$ref` to `#/definitions/<name>` where name = `(subs (str kw) 1)` with `/` escaped as `~1` per JSON Pointer (so `:tree/node` → `"$ref" "#/definitions/tree~1node"`, definitions key `"tree/node"`); definitions atom collected during transform; recursion stopper before recursing into a ref target; emit top-level `"definitions"` only when non-empty; test asserts the exact namespaced `$ref` string AND that the definitions key matches the unescaped name
- [ ] Keyword values render as name strings (`:enum` of keywords, map keys, `:=` keyword const)
- [ ] `tests/test_json_schema.lpy`: every type mapping, optional keys → required array, closed → additionalProperties false, min/max translations, `:maybe` oneOf, `:multi` oneOf, tuple prefixItems, `:re` pattern source, `:json-schema/format` unlift override, recursive registry ref → definitions + $ref, **composition: output of `(u/merge ...)` exports correctly; python `json.dumps` round-trips the output**

**Checkpoints:**
- `(bjs/transform [:map [:id :string] [:age {:optional true} [:int {:min 0}]]])` → `{"type" "object" "properties" {"id" {"type" "string"} "age" {"type" "integer" "minimum" 0}} "required" ["id"]}`
- `(bjs/transform [:ref :tree/node] {:registry <recursive tree>})` → `$ref` + `"definitions"` containing the tree schema (terminates)
- `(json/dumps (bjs/transform [:tuple :string :int]) )` via interop → valid JSON string
- Narrow: `basilisp test tests/test_json_schema.lpy`

## Phase 4: Key spell-checking

Goal: §D in `balli.error`.

- [ ] `levenshtein` (full-matrix, iterative); threshold table per §D
- [ ] `with-spell-checking [explain-map]`: rewrite `:extra-key` → `:balli.error/misspelled-key` (+ `:balli.error/likely-misspelling-of` paths) when within threshold of an absent declared key; `:invalid-dispatch-value` on keyword-dispatch `:multi` → `:balli.error/misspelled-value`; drop `:missing-key` errors whose path is a likely-misspelling target; needs schema-fragment entry-key introspection (reuse `split-form`) and value keys at `(butlast in)`
- [ ] Humanize messages: `"should be spelled :x"` / `"should be spelled :x or :y"`
- [ ] `tests/test_spell.lpy`: `{:closed true}` map with `:naem` → misspelled-key naming `:name`, missing-key for `:name` dropped; below-threshold typo stays extra-key; multi dispatch typo; humanize renders; **composition: spell-check explain from a `:multi` branch inside a closed map**

**Checkpoints:**
- `(-> (b/explain [:map {:closed true} [:name :string]] {:naem "x"}) be/with-spell-checking be/humanize)` → `{:naem ["should be spelled :name"]}`
- Same without spell-checking → extra-key + missing-key both present
- Narrow: `basilisp test tests/test_spell.lpy`

## Phase 5: parse/unparse + :orn

Goal: §E. (Phase 0 decided the Tag/Tags representation.)

- [ ] `Tag`/`Tags` records (or fallback) in `balli.core` + `tag`/`tag?`/`tags`/`tags?` ctors/preds; `:balli.core/invalid` sentinel + `invalid?`
- [ ] New type `:orn` in normalize (`entry vectors like :map`, ≥1 child) + registry + both compilers (validate/explain like `:or` with tag in `:path`)
- [ ] `compile-parser [ast registry]` + `compile-unparser` in compile.lpy: simple types → validate-then-value; `:orn` → Tag of first match; `:multi` → Tag(dispatch, parsed); `:maybe`/`:or` (first match, untagged)/colls (per-element)/`:map` (entry values; Tag/Tags guard)/`:tuple`/`:map-of`/`:ref`
- [ ] `:and` parse per §E: parse via the single TRANSFORMING child (parser produces structure) when exactly one exists, validating remaining children against the original value; zero → first child; ≥2 transforming → `:balli.core/invalid-schema` at normalize. Track a `transforming-parser?` flag per AST node type
- [ ] `balli.core`: `parse`/`parser`/`unparse`/`unparser` (cached)
- [ ] Additive integration of `:orn` into earlier phases' surfaces: json-schema (`anyOf` of branch schemas), transformers (branch-select like `:or`), walk/util (entry-style children), humanize (tag in `:path` only)
- [ ] `tests/test_parse.lpy`: round-trip `(unparse s (parse s x)) = x` for every type; `:orn`/`:multi` Tag shapes; invalid → sentinel both directions; map containing user data that *looks* like a Tag is rejected by the guard; **composition: `[:map [:result [:orn [:ok :int] [:err :string]]]]` round-trip**

**Checkpoints:**
- `(b/parse [:orn [:num :int] [:str :string]] 42)` → Tag with `:key :num :value 42`
- `(b/unparse [:orn [:num :int] [:str :string]] (b/parse [:orn [:num :int] [:str :string]] 42))` → `42`
- `(b/parse :int "x")` → `:balli.core/invalid`
- Narrow: `basilisp test tests/test_parse.lpy`

## Phase 6: Sequence schemas

Goal: §F — the hardest phase. New module `src/balli/regex.lpy`.

- [ ] Driver: iterative loop, thunk stack (Python list via interop or atom+vector), memo cache set of `[matcher-id pos regs]`, success box. NO Python recursion proportional to input length
- [ ] Combinators: `item` (single element via child validator/parser/explainer), `cat*`, `alt*`, `opt*` (?), `star*` (*), `plus*` (+), `repeat*` (min/max with regs counter + nullable-child guard), `end`. Validator, parser, and explainer variants (explainer tracks furthest-pos errors per §F)
- [ ] Normalize + registry for `:cat :catn :alt :altn :? :* :+ :repeat` (catn/altn entries like :map/:orn; `:repeat` requires child + optional `{:min :max}` numeric props; boundary-validate)
- [ ] Compile integration: `-regex-op?` on AST nodes; seqex child of seqex splices; non-seqex child = item; `[:schema <seqex>]`... MVP has no `:schema` wrapper type — ADD `:schema` type (single child, transparent validate/explain/parse, forces item semantics in seqex context); ref into seqex throws `:balli.core/potentially-recursive-seqex` at compile
- [ ] Top-level seqex validate/explain/parse: sequential? guard, whole-input consumption, error types `:balli.core/end-of-input` / `:balli.core/input-remaining` / invalid-type; parse shapes per §E/§F; unparsers re-splice (concat)
- [ ] `regex-min-max [ast]` fn (Phase 8 dependency)
- [ ] Transformer + walk pass-through for seqex types and `:schema` (extend Phase 1/2 code additively); json-schema: seqex types → `{"type" "array"}` best-effort with `"items"` when single-child (document as lossy), `:schema` transparent
- [ ] `tests/test_regex.lpy`: validate/explain/parse/unparse for each combinator; splicing `[:* [:cat :int :string]]` flat + parse nesting `[[1 "a"] ...]`; `[:schema [:cat ...]]` single-element; greedy backtracking case `[:cat [:* :int] :int]` on `[1 2 3]`; pathological memo case `[:* [:* :int]]` on 30 elements terminates <2s; catn Tags round-trip; explain furthest-position + end-of-input + input-remaining; empty `[:cat]`; `:repeat` bounds; ref-in-seqex throws; **composition: seqex inside `[:map [:args [:cat :keyword [:* :int]]]]`**

**Checkpoints:**
- `(b/validate [:cat :int [:* :string]] [1 "a" "b"])` → `true`; `[1 "a" 2]` → `false`
- `(b/parse [:* [:cat :int :string]] [1 "a" 2 "b"])` → `[[1 "a"] [2 "b"]]` (or Tags-free vector nesting)
- `(b/parse [:catn [:n :int] [:s :string]] [1 "x"])` → Tags `{:n 1 :s "x"}`; unparse → `[1 "x"]`
- `(:type (first (:errors (b/explain [:cat :int] []))))` → `:balli.core/end-of-input`
- `(b/validate [:cat [:* :int] :int] [1 2 3])` → `true` (backtracking)
- Narrow: `basilisp test tests/test_regex.lpy`

## Phase 7: Generators

Goal: §H, `src/balli/generator.lpy`.

- [ ] `generate` (1/2-arity, opts `{:seed :size}`), `sample` (`{:size n}` count); `random.Random` instance threaded; deterministic under seed
- [ ] Per-type strategies per §H incl. bounds, `:and` retry-100, `:not` filter, `:map` optional-p=0.5, `:map-of` distinct keys, `:multi`/`:or`/`:orn` branch pick, `:maybe` 20% nil, `:ref` depth counter (cap 5; at cap prefer non-recursive alternatives, else throw `:balli.core/unsatisfiable-schema`), `:re`/`:fn`/`:=>`-less throw `:balli.core/no-generator`
- [ ] `:gen/return`/`:gen/elements`/`:gen/schema`/`:gen/fmap` (real fns)/`:gen/min`/`:gen/max` property hooks
- [ ] Seqex generation: flat splicing per §H; `:=>` gen deferred to Phase 8
- [ ] `tests/test_generator.lpy`: for each type — `(b/validate s (bg/generate s {:seed k}))` over several seeds; determinism (same seed twice → equal); bounds respected; recursive tree schema terminates and validates; `:gen/*` hooks; no-generator throws; **composition: generate `[:map [:cmd [:cat :keyword [:* :int]]]]` and validate it**

**Checkpoints:**
- `(let [v (bg/generate [:int {:min 1 :max 5}] {:seed 7})] (and (int? v) (<= 1 v 5)))` → `true`
- `(= (bg/generate <big map schema> {:seed 42}) (bg/generate <same> {:seed 42}))` → `true`
- `(b/validate [:cat :int [:* :string]] (bg/generate [:cat :int [:* :string]] {:seed 3}))` → `true`
- Recursive `:tree/node` generation validates and terminates
- Narrow: `basilisp test tests/test_generator.lpy`

## Phase 8: Function schemas + instrument

Goal: §G.

- [ ] Types `:=>` (2-3 children; input must normalize to `:cat`/`:catn` else `:balli.core/invalid-input-schema`) and `:function` (≥1 `:=>` children, distinct arities via `regex-min-max`, ≤1 varargs) in normalize/registry/compilers
- [ ] Validate: `python/callable`; with the `:balli.core/function-checker` opt → generative (checker from `balli.generator/function-checker`: N=100 generated input seqs → apply → validate output; explain carries `:balli.core/invalid-output` + failing pair)
- [ ] **Checker/caching contract (explicit):** `:balli.core/function-checker` is an opts-map key accepted by `schema`/`validate`/`explain`. Schema objects bake it at construction (cached fns in the object's own cache atom include it). Raw-form calls whose opts carry a checker BYPASS the global raw-form cache entirely (compile fresh per call) — no cache poisoning. Tests: plain→checked→plain on the same raw form returns callable-true / generative-false / callable-true; schema-object with baked checker stays generative
- [ ] `balli.core/instrument [props-map f?]`-style: `(instrument {:schema s :scope #{:input :output} :report f} f)` → wrapped fn per §G; `:function` arity dispatch table + varargs fallback
- [ ] `function-info` public fn
- [ ] Generator for `:=>`: constant fn returning generated outputs (uses output schema gen)
- [ ] `tests/test_function.lpy`: `:=>` validates callables and rejects non-callables; checker catches a wrong fn (e.g. schema says int→int, fn returns str); instrument throws typed ex-info on bad args/output/arity; `:function` multi-arity dispatch; generated fn from `:=>` produces valid outputs; **composition: instrumented fn whose input seqex uses `[:* :int]` varargs**

**Checkpoints:**
- `(b/validate [:=> [:cat :int] :int] inc)` → `true`; `(b/validate [:=> [:cat :int] :int] 5)` → `false`
- `(b/validate [:=> [:cat :int] :int] str {:balli.core/function-checker (bg/function-checker)})` → `false`
- `(try ((b/instrument {:schema [:=> [:cat :int] :int]} inc) "x") (catch python/Exception e (:type (ex-data e))))` → `:balli.core/invalid-input`
- Narrow: `basilisp test tests/test_function.lpy`

## Phase 9: Provider

Goal: §I, `src/balli/provider.lpy`.

- [ ] `provide [samples]` / `[samples opts]`: stats fold + synthesis per §I; scalar preference order `[:int :double :keyword :symbol :string :boolean :uuid]`; `:maybe`/`[:or]` merging; optional-key detection; `:map-of` heuristic (`:map-of-threshold` default 3, equal key+val schemas, distinct-keys > n^0.7); empty coll → `[:vector :any]`; vectors of equal arity NOT tuple-ized (skip malli's tuple hint — document)
- [ ] `tests/test_provider.lpy`: scalars, mixed → `:or`, nil-mixed → `:maybe`, nested maps with optional keys, map-of detection (id→val dicts) vs record maps, colls, **composition: `(b/validate (bp/provide samples) sample)` for every sample in a gnarly fixture**

**Checkpoints:**
- `(bp/provide [{:x 1} {:x 2 :y "a"}])` → `[:map [:x :int] [:y {:optional true} :string]]`
- `(bp/provide [1 2 nil])` → `[:maybe :int]`
- `(bp/provide [{"a" 1 "b" 2} {"c" 3} {"d" 4 "e" 5}])` → `[:map-of :string :int]`
- Narrow: `basilisp test tests/test_provider.lpy`

## Phase 10: Docs + full sweep

- [ ] Root README: new sections (Transformers, Utilities, JSON Schema, Parsing, Sequence schemas, Function schemas, Generators, Inference) — every example run-verified; schema reference table extended with new types; API reference extended
- [ ] "Differences from Malli" updated: REMOVE `:or` single-error bullet; ADD: fns-not-sexprs for property code, no `:andn`, no old-parse-format, `:re`/`:fn` gen needs `:gen/*`, no shrinking, no sci/dev/experimental modules, provider never tuple-izes
- [ ] Version bump `0.2.0` in pyproject.toml + `balli.core/version`
- [ ] Full sweep: `basilisp test` all green, `basilisp run scripts/compile_check.lpy` exit 0, wheel build ships new `.lpy` files, out-of-cwd import smoke

**Checkpoints:**
- `basilisp test` → all pass (target ≥ 200 tests)
- `basilisp run scripts/compile_check.lpy` → 11 namespaces OK
- `cd /tmp && basilisp run -c '(require (quote [balli.generator :as bg])) ...'` → works outside repo

## Verification

Completion gate: full `basilisp test` + compile_check + README examples spot-run. Both exit 0 before PR.

## Rollback

Single branch `balli-post-mvp`; rollback = branch deletion. Main holds shipped MVP.
