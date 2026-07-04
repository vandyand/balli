# Balli Post-MVP — Implementation Plan

## Overview

Eleven phases closing the Malli feature gap, dependency-ordered: spike → transformers → walk/util → json-schema → spell-check → parse → seqex → generators → function schemas → provider → docs. Semantic contract per phase: the matching section of [malli-semantics.md](malli-semantics.md) (§A–§I). Each phase: narrow test file green (`basilisp test tests/<file>`), live checkpoints via `basilisp run -c` from repo root, zero regressions in the full suite.

**Composition rule (from the MVP retro):** every phase's checkpoints must include at least one cross-feature composition case (e.g. transformer through a ref, seqex inside a map, generator over a registry schema), not just per-type units. Schema-boundary validation (malformed schema → `:balli.core/invalid-schema` at normalize) applies to every new schema type.

## Prerequisites

- MVP merged to main (`0c74750`); branch `balli-post-mvp`; 93 tests green.
- Malli source at `/tmp/malli-src/` (re-extract: `cd /tmp/malli-src && unzip -oq ~/.m2/repository/metosin/malli/0.20.0/malli-0.20.0.jar`).

## Phase 0: Substrate spike

Goal: prove the Basilisp facilities the hard phases depend on, before building on them.

- [x] `defrecord Tag [key value]` + `Tags [values]`: construction, field access (`:key`, `(.-key r)`), value equality, `instance?` checks, printing. If defrecord is unusable, decide fallback (marker maps `{:balli/tag true ...}`) and record it here + in research.md
- [x] Python `random` interop: `(random/Random 42)` seeded instance, `.randint`, `.uniform`, `.choice` on a Basilisp vector (may need `(vec ...)`→python list conversion — verify), determinism across two same-seed instances
- [x] Thunk-stack loop viability: a `loop/recur` driver popping closures from a Python list (or Basilisp vector in an atom/volatile) — run 100k thunk iterations, confirm no recursion error and <2s
- [x] `volatile!`/`vswap!` availability (else atoms)
- [x] `sequential?` on lists/vectors/lazy-seqs/ranges; NOT strings/sets/maps
- [x] Record findings in this file under "Phase 0 findings"; adjust later-phase notes if invalidated

**Checkpoints:** each bullet is its own `basilisp run -c` probe; report exact outputs. No test file (spike only).

## Phase 1: Transformers

Goal: `balli.transform` + core decode/encode/coerce per semantics §A.

- [x] `src/balli/transform.lpy`: transformer representation `{:balli/transformer true :chain [{:name :decoders :encoders :default-decoder :default-encoder} ...]}`; `(transformer & ts)` flattening maps/transformers into one chain (commit: 28660d9)
- [x] Interceptor normalization: fn → `{:enter f}`; `{:compile f}` → `(f schema-ast opts)` then normalize+merge; `{:enter :leave}` as-is. Chain fold: enter composes in chain order, leave in reverse (commit: 28660d9)
- [x] `compile-transformer [ast registry transformer method opts]` in a new `balli.compile` section (or `transform.lpy`): per-node resolution priority (schema props `{:decode {:string f}}` → `:decode/string` qualified prop → type table → default), node combinator `leave∘children∘enter`, per-type descent: `:map` (present keys only, `map?` guard), `:map-of` (keys+vals), colls, `:tuple` (per-index), `:and`/`:maybe`/`:not` (children composed in order), `:or` (decode try-validate-first / encode first-valid-branch), `:multi` (dispatch post-enter), `:enum`/`:=` (infer child type, reuse coder), `:ref` (lazy memoized target), seqex types absent until Phase 6 (pass-through)
- [x] Built-ins per §A: `string-transformer`, `json-transformer`, `strip-extra-keys-transformer`, `key-transformer`, `default-value-transformer`, `collection-transformer`. All scalar coercions lenient (unchanged on mismatch, try/catch)
- [x] `balli.core`: `decoder`/`decode`/`encoder`/`encode` (raw-form + schema-object, cached per `[method transformer-identity]` in schema cache), `coercer`/`coerce` (decode→validate→return-or-throw ex-info `{:type :balli.core/coercion :value :schema :explain}`)
- [x] `tests/test_transform.lpy`: string decode of int/double/boolean/keyword/uuid/enum; json decode excludes string→int; encode reversals; strip-extra-keys open/closed/`{:closed false}`; default-value nil-vs-missing + map fill; key-transformer; composition order (two transformers, decode chain order vs encode reversal); property override `:decode/string` on a schema; `:or`/`:multi`/ref descent; coerce success + throw; **composition case: `[:ref :user]` in registry decoding nested map keys' values** (commit: 28660d9)

**Checkpoints:**
- `(b/decode [:map [:age :int] [:tags [:set :keyword]]] {:age "42" :tags ["a" "b"]} (bt/string-transformer))` → `{:age 42 :tags #{:a :b}}`
- `(b/decode :int "42" (bt/json-transformer))` → `"42"` (json does NOT parse number strings)
- `(b/decode [:map [:x :int]] {:x 1 :junk 2} (bt/strip-extra-keys-transformer))` → `{:x 1}`
- `(b/decode [:map [:x {:default 7} :int]] {} (bt/default-value-transformer))` → `{:x 7}`
- `(try (b/coerce :int "x" (bt/json-transformer)) (catch python/Exception e (:type (ex-data e))))` → `:balli.core/coercion`
- Narrow: `basilisp test tests/test_transform.lpy`

## Phase 2: Walk + util + per-branch :or explain

Goal: semantics §C.

- [x] `balli.core/walk`: form-level postwalk — `(walk s f)` / `(walk s f opts)`; f receives `[form path walked-children-form]`-rebuilt schema form; `schema-walker` helper. Walk map entries with key in path, indexed children with index; do NOT enter refs (ref child stays the keyword)
- [x] `src/balli/util.lpy`: `merge`, `union`, `select-keys`, `dissoc`, `optional-keys`, `required-keys`, `closed-schema`, `open-schema`, `get`, `get-in` — form→form fns per §C (accept forms or schema objects, return forms; normalize internally for entry introspection)
- [x] Per-branch `:or` explain in `compile.lpy`: all-branches-fail → concat each branch's errors with branch index appended to `:path` (`:in` unchanged); delete the single-generic-error simplification; update affected MVP tests (`tests/test_explain.lpy` :or cases) and the README difference bullet (commit: c82fed3)
- [x] `tests/test_util.lpy`: merge (props, duplicate keys, requiredness later-wins, deep nested-map merge, non-map s2-wins), union (equal forms, differing → `[:or]`, optional-in-either), select-keys/dissoc/optional-keys/required-keys/closed-schema (recursive, respects explicit `:closed false`)/open-schema/get/get-in; walk postwalk order + path correctness; **composition: `(closed-schema (u/merge A B))` then validate** (commit: c82fed3)

**Checkpoints:**
- `(u/merge [:map [:x :int]] [:map [:x :string] [:y :int]])` → `[:map [:x :string] [:y :int]]`
- `(u/union [:map [:x :int]] [:map [:x :string]])` → `[:map [:x [:or :int :string]]]`
- `(u/closed-schema [:map [:a [:map [:b :int]]]])` → both maps get `{:closed true}`
- `(:errors (b/explain [:or :int :string] :kw))` → 2 errors, paths `[0]` and `[1]`
- Narrow: `basilisp test tests/test_util.lpy` + updated `tests/test_explain.lpy`

## Phase 3: JSON Schema export

Goal: `balli.json-schema/transform` per §B.

- [x] `src/balli/json_schema.lpy`: `transform` (form or schema object, optional opts) → string-keyed Basilisp map. Full type mapping table from §B incl. min/max property translations per type family; `:title`/`:description`/`:default` passthrough; `:json-schema` whole-node override; `:json-schema/foo` unlift (wins over generated keys)
- [x] Refs: `$ref` to `#/definitions/<name>` where name = `(subs (str kw) 1)` with full JSON Pointer escaping — `~` → `~0` FIRST, then `/` → `~1` (so `:tree/node` → `"$ref" "#/definitions/tree~1node"`, definitions key `"tree/node"`); definitions atom collected during transform; recursion stopper before recursing into a ref target; emit top-level `"definitions"` only when non-empty; tests assert the exact namespaced `$ref` string, the tilde case, AND that the definitions key matches the unescaped name (commit: 2c6c8f2)
- [x] Keyword values render as name strings (`:enum` of keywords, map keys, `:=` keyword const)
- [x] `tests/test_json_schema.lpy`: every type mapping, optional keys → required array, closed → additionalProperties false, min/max translations, `:maybe` oneOf, `:multi` oneOf, tuple prefixItems, `:re` pattern source, `:json-schema/format` unlift override, recursive registry ref → definitions + $ref, **composition: output of `(u/merge ...)` exports correctly; python `json.dumps` round-trips the output** (json.dumps needs a clj->py conversion — Basilisp maps/vectors are not directly dumpable; `basilisp.json/write-str` takes them as-is)

**Checkpoints:**
- `(bjs/transform [:map [:id :string] [:age {:optional true} [:int {:min 0}]]])` → `{"type" "object" "properties" {"id" {"type" "string"} "age" {"type" "integer" "minimum" 0}} "required" ["id"]}`
- `(bjs/transform [:ref :tree/node] {:registry <recursive tree>})` → `$ref` + `"definitions"` containing the tree schema (terminates)
- `(json/dumps (bjs/transform [:tuple :string :int]) )` via interop → valid JSON string
- Narrow: `basilisp test tests/test_json_schema.lpy`

## Phase 4: Key spell-checking

Goal: §D in `balli.error`.

- [x] `levenshtein` (full-matrix, iterative); threshold table per §D (commit: 02a6bb2)
- [x] `with-spell-checking [explain-map]`: rewrite `:extra-key` → `:balli.error/misspelled-key` (+ `:balli.error/likely-misspelling-of` paths) when within threshold of an absent declared key; `:invalid-dispatch-value` on keyword-dispatch `:multi` → `:balli.error/misspelled-value`; drop `:missing-key` errors whose path is a likely-misspelling target; needs schema-fragment entry-key introspection (reuse `split-form`) and value keys at `(butlast in)` (commit: 02a6bb2)
- [x] Humanize messages: `"should be spelled :x"` / `"should be spelled :x or :y"` (commit: 02a6bb2)
- [x] `tests/test_spell.lpy`: `{:closed true}` map with `:naem` → misspelled-key naming `:name`, missing-key for `:name` dropped; below-threshold typo stays extra-key; multi dispatch typo; humanize renders; **composition: spell-check explain from a `:multi` branch inside a closed map** (commit: 02a6bb2)

**Checkpoints:**
- `(-> (b/explain [:map {:closed true} [:name :string]] {:nam "x"}) be/with-spell-checking be/humanize)` → `{:nam ["should be spelled :name"]}` (`:naem` is distance 2 — above threshold, stays extra-key; verified against real malli)
- Same without spell-checking → extra-key + missing-key both present
- Narrow: `basilisp test tests/test_spell.lpy`

## Phase 5: parse/unparse + :orn

Goal: §E. (Phase 0 decided the Tag/Tags representation.)

- [x] `Tag`/`Tags` records (or fallback) in `balli.core` + `tag`/`tag?`/`tags`/`tags?` ctors/preds; `:balli.core/invalid` sentinel + `invalid?` (records physically live in `balli.compile` — core requires compile, so defining them in core would be a circular require; core's ctor/pred fns are the public surface. `invalid?` compares with `=` not `identical?`: keyword literals loaded from cached namespace bytecode are NOT globally interned in Basilisp, so keyword identity does not hold across modules)
- [x] New type `:orn` in normalize (`entry vectors like :map`, ≥1 child) + registry + both compilers (validate/explain like `:or` with tag in `:path`)
- [x] `compile-parser [ast registry]` + `compile-unparser` in compile.lpy: simple types → validate-then-value; `:orn` → Tag of first match; `:multi` → Tag(dispatch, parsed); `:maybe`/`:or` (first match, untagged)/colls (per-element)/`:map` (entry values; Tag/Tags guard)/`:tuple`/`:map-of`/`:ref` (commit: 2a84b74)
- [x] `:and` parse per §E: parse via the single TRANSFORMING child (parser produces structure; analysis derefs refs via registry) when exactly one exists; zero → first child's parse; in BOTH cases all remaining children validate against the original value; ≥2 transforming → `:balli.core/invalid-schema` at parser COMPILE time (registry available there). Track a `transforming-parser?` analysis fn (ast, registry, visited-ref-set) → bool — ref cycles count as non-transforming (no infinite analysis loop); tests: ref-hidden-transforming case AND recursive non-transforming ref under `:and` (commit: 2a84b74)
- [x] `balli.core`: `parse`/`parser`/`unparse`/`unparser` (cached)
- [x] Additive integration of `:orn` into earlier phases' surfaces: json-schema (`anyOf` of branch schemas), transformers (branch-select like `:or`), walk/util (entry-style children), humanize (tag in `:path` only)
- [x] `tests/test_parse.lpy`: round-trip `(unparse s (parse s x)) = x` for every type; `:orn`/`:multi` Tag shapes; invalid → sentinel both directions; map containing user data that *looks* like a Tag is rejected by the guard; **composition: `[:map [:result [:orn [:ok :int] [:err :string]]]]` round-trip** (commit: 2a84b74)

**Checkpoints:**
- `(b/parse [:orn [:num :int] [:str :string]] 42)` → Tag with `:key :num :value 42`
- `(b/unparse [:orn [:num :int] [:str :string]] (b/parse [:orn [:num :int] [:str :string]] 42))` → `42`
- `(b/parse :int "x")` → `:balli.core/invalid`
- Narrow: `basilisp test tests/test_parse.lpy`

## Phase 6: Sequence schemas

Goal: §F — the hardest phase. New module `src/balli/regex.lpy`.

- [x] Driver: iterative loop, thunk stack (Python list via interop or atom+vector), memo cache set of `[matcher-id pos regs]`, success box. NO Python recursion proportional to input length (commit: fac37a1)
- [x] Combinators: `item` (single element via child validator/parser/explainer), `cat*`, `alt*`, `opt*` (?), `star*` (*), `plus*` (+), `repeat*` (min/max with regs counter + nullable-child guard), `end`. Validator, parser, and explainer variants (explainer tracks furthest-pos errors per §F)
- [x] Normalize + registry for `:cat :catn :alt :altn :? :* :+ :repeat` (catn/altn entries like :map/:orn; `:repeat` requires child + optional `{:min :max}` numeric props; boundary-validate)
- [x] Compile integration: `-regex-op?` on AST nodes; seqex child of seqex splices; non-seqex child = item; `[:schema <seqex>]`... MVP has no `:schema` wrapper type — ADD `:schema` type (single child, transparent validate/explain/parse, forces item semantics in seqex context); ref into seqex throws `:balli.core/potentially-recursive-seqex` at compile (commit: fac37a1)
- [x] Top-level seqex validate/explain/parse: sequential? guard, whole-input consumption, error types `:balli.core/end-of-input` / `:balli.core/input-remaining` / invalid-type; parse shapes per §E/§F; unparsers re-splice (concat)
- [x] `regex-min-max [ast]` fn (Phase 8 dependency)
- [x] Transformer + walk pass-through for seqex types and `:schema` (extend Phase 1/2 code additively); json-schema: seqex types → `{"type" "array"}` best-effort with `"items"` when single-child (document as lossy), `:schema` transparent (commit: fac37a1)
- [x] `tests/test_regex.lpy`: validate/explain/parse/unparse for each combinator; splicing `[:* [:cat :int :string]]` flat + parse nesting `[[1 "a"] ...]`; `[:schema [:cat ...]]` single-element; greedy backtracking case `[:cat [:* :int] :int]` on `[1 2 3]`; pathological memo case `[:* [:* :int]]` on 30 elements terminates <2s; catn Tags round-trip; explain furthest-position + end-of-input + input-remaining; empty `[:cat]`; `:repeat` bounds; ref-in-seqex throws; **composition: seqex inside `[:map [:args [:cat :keyword [:* :int]]]]`** (commit: fac37a1)

**Checkpoints:**
- `(b/validate [:cat :int [:* :string]] [1 "a" "b"])` → `true`; `[1 "a" 2]` → `false`
- `(b/parse [:* [:cat :int :string]] [1 "a" 2 "b"])` → `[[1 "a"] [2 "b"]]` (or Tags-free vector nesting)
- `(b/parse [:catn [:n :int] [:s :string]] [1 "x"])` → Tags `{:n 1 :s "x"}`; unparse → `[1 "x"]`
- `(:type (first (:errors (b/explain [:cat :int] []))))` → `:balli.core/end-of-input`
- `(b/validate [:cat [:* :int] :int] [1 2 3])` → `true` (backtracking)
- Narrow: `basilisp test tests/test_regex.lpy`

## Phase 7: Generators

Goal: §H, `src/balli/generator.lpy`.

- [x] `generate` (1/2-arity, opts `{:seed :size}`), `sample` (`{:size n}` count); `random.Random` instance threaded; deterministic under seed (commit: fddbbc9)
- [x] Per-type strategies per §H incl. bounds, `:and` retry-100, `:not` filter, `:map` optional-p=0.5, `:map-of` distinct keys, `:multi`/`:or`/`:orn` branch pick, `:maybe` 20% nil, `:ref` depth counter (cap 5; at cap: target `:maybe` → nil, else throw `:balli.core/unsatisfiable-schema`; at cap `:map` omits optional entries and coll/rep counts collapse to their minimum, so optional-key/0-min-coll recursion terminates by omission), `:re`/`:fn`/`:=>`-less throw `:balli.core/no-generator` (commit: fddbbc9)
- [x] `:gen/return`/`:gen/elements`/`:gen/schema`/`:gen/fmap` (real fns)/`:gen/min`/`:gen/max` property hooks (commit: fddbbc9)
- [x] Seqex generation: flat splicing per §H (ref directly in seqex child position throws `:balli.core/potentially-recursive-seqex`, mirroring the compilers); `:=>` gen deferred to Phase 8 (commit: fddbbc9)
- [x] `tests/test_generator.lpy`: for each type — `(b/validate s (bg/generate s {:seed k}))` over several seeds; determinism (same seed twice → equal); bounds respected; recursive tree schema terminates and validates; `:gen/*` hooks; no-generator throws; **composition: generate `[:map [:cmd [:cat :keyword [:* :int]]]]` and validate it** (commit: fddbbc9)

**Checkpoints:**
- `(let [v (bg/generate [:int {:min 1 :max 5}] {:seed 7})] (and (int? v) (<= 1 v 5)))` → `true`
- `(= (bg/generate <big map schema> {:seed 42}) (bg/generate <same> {:seed 42}))` → `true`
- `(b/validate [:cat :int [:* :string]] (bg/generate [:cat :int [:* :string]] {:seed 3}))` → `true`
- Recursive `:tree/node` generation validates and terminates
- Narrow: `basilisp test tests/test_generator.lpy`

## Phase 8: Function schemas + instrument

Goal: §G.

- [x] Types `:=>` (2-3 children; input must normalize to `:cat`/`:catn` else `:balli.core/invalid-input-schema`) and `:function` (≥1 `:=>` children, distinct arities via `regex-min-max`, ≤1 varargs) in normalize/registry/compilers (commit: 0d39a29)
- [x] Validate: `python/callable`; with the `:balli.core/function-checker` opt → generative (checker from `balli.generator/function-checker`: N=100 generated input seqs → apply → validate output; explain carries `:balli.core/invalid-output` + failing pair)
- [x] **Checker/caching contract (explicit):** `:balli.core/function-checker` is an opts-map key accepted by `schema` and by `validate`/`explain` for RAW forms only. Schema objects bake it at construction (cached fns in the object's own cache atom include it); **call-time opts on a schema object are IGNORED** (consistent with the existing MVP rule "opts ignored when s is already a schema object — its baked-in registry wins"). Raw-form calls whose opts carry a checker BYPASS the global raw-form cache entirely (compile fresh per call) — no cache poisoning. Tests: plain→checked→plain on the same raw form returns callable-true / generative-false / callable-true; schema-object with baked checker stays generative; schema-object WITHOUT baked checker + call-time checker opt → still callable-check (opt ignored)
- [x] `balli.core/instrument [props-map f?]`-style: `(instrument {:schema s :scope #{:input :output} :report f} f)` → wrapped fn per §G; `:function` arity dispatch table + varargs fallback (commit: 0d39a29)
- [x] `function-info` public fn (commit: 0d39a29)
- [x] Generator for `:=>`: constant fn returning generated outputs (uses output schema gen)
- [x] `tests/test_function.lpy`: `:=>` validates callables and rejects non-callables; checker catches a wrong fn (e.g. schema says int→int, fn returns str); instrument throws typed ex-info on bad args/output/arity; `:function` multi-arity dispatch; generated fn from `:=>` produces valid outputs; **composition: instrumented fn whose input seqex uses `[:* :int]` varargs** (commit: 0d39a29)

**Checkpoints:**
- `(b/validate [:=> [:cat :int] :int] inc)` → `true`; `(b/validate [:=> [:cat :int] :int] 5)` → `false`
- `(b/validate [:=> [:cat :int] :int] str {:balli.core/function-checker (bg/function-checker)})` → `false`
- `(try ((b/instrument {:schema [:=> [:cat :int] :int]} inc) "x") (catch python/Exception e (:type (ex-data e))))` → `:balli.core/invalid-input`
- Narrow: `basilisp test tests/test_function.lpy`

## Phase 9: Provider

Goal: §I, `src/balli/provider.lpy`.

- [x] `provide [samples]` / `[samples opts]`: stats fold + synthesis per §I; scalar preference order `[:int :double :keyword :symbol :string :boolean :uuid]`; `:maybe`/`[:or]` merging; optional-key detection; `:map-of` heuristic (`:map-of-threshold` default 3, equal key+val schemas, distinct-keys > n^0.7); empty coll → `[:vector :any]`; vectors of equal arity NOT tuple-ized (skip malli's tuple hint — document) (commit: 9dc4d26)
- [x] `tests/test_provider.lpy`: scalars, mixed → `:or`, nil-mixed → `:maybe`, nested maps with optional keys, map-of detection (id→val dicts) vs record maps, colls, **composition: `(b/validate (bp/provide samples) sample)` for every sample in a gnarly fixture** (commit: 9dc4d26)

**Checkpoints:**
- `(bp/provide [{:x 1} {:x 2 :y "a"}])` → `[:map [:x :int] [:y {:optional true} :string]]`
- `(bp/provide [1 2 nil])` → `[:maybe :int]`
- `(bp/provide [{"a" 1 "b" 2} {"c" 3} {"d" 4 "e" 5}])` → `[:map-of :string :int]`
- Narrow: `basilisp test tests/test_provider.lpy`

## Phase 10: Docs + full sweep

- [x] Root README: new sections (Transformers, Utilities, JSON Schema, Spell-checking, Parsing, Sequence schemas, Function schemas, Generators, Inference) — every example run-verified via `basilisp run`; schema reference table extended to all 39 types; API reference extended, grouped by namespace (commit: 3ca671a)
- [x] "Differences from Malli" updated: REMOVE `:or` single-error bullet (already gone since Phase 2); ADD: fns-not-sexprs for property code, no `:andn`, no old-parse-format, `:re`/`:fn` gen needs `:gen/*`, no shrinking, no sci/dev/experimental modules, provider never tuple-izes + mixed int/float → `[:or :int :double]`, `:?` unparse stricter, JSON-Pointer-escaped ref names, `:multi` keyword-dispatch via get, instrument always arity-checks, baked schema-object opts (commit: 3ca671a)
- [x] Version bump `0.2.0` in pyproject.toml + `balli.core/version` (+ tests/test_toolchain.lpy expectation)
- [x] Full sweep: `basilisp test` 293 green, `basilisp run scripts/compile_check.lpy` 11 namespaces OK exit 0, wheel `balli-0.2.0` ships all 11 `.lpy` files, out-of-cwd `balli.generator` import smoke OK (commit: 3ca671a)

**Checkpoints:**
- `basilisp test` → all pass (target ≥ 200 tests)
- `basilisp run scripts/compile_check.lpy` → 11 namespaces OK
- `cd /tmp && basilisp run -c '(require (quote [balli.generator :as bg])) ...'` → works outside repo

## Verification

Completion gate: full `basilisp test` + compile_check + README examples spot-run. Both exit 0 before PR.

## Rollback

Single branch `balli-post-mvp`; rollback = branch deletion. Main holds shipped MVP.

## Phase 0 findings

Probed 2026-07-04 on Basilisp 0.5.0 (WSL2, Python 3), via `basilisp run -c` / `/tmp` scripts. All probes ran clean; exact outputs below.

### 1. defrecord — USABLE. Decision: Tag/Tags = defrecord (no fallback needed)

`(defrecord Tag [key value])`, `(defrecord Tags [values])`:
- Construction: `(->Tag :num 42)`, `(Tag. :num 42)`, `(map->Tag {...})` all work.
- Access: `(:key r)` → `:num`; `(.-key r)` → `:num`. Both fine.
- Value equality: `(= (->Tag :num 42) (->Tag :num 42))` → `true`; hashes equal; `(= r (->Tag :num 43))` → `false`; `(= r {:key :num :value 42})` → `false` (record ≠ plain map — good, the guard can't be fooled by equality).
- `(instance? Tag r)` → `true`; cross-type → `false`. `record?` → `true`.
- Printing: `#basilisp.user.Tag{:key :num, :value 42}`.
- **`(map? r)` → `true` — records ARE map? in Basilisp (same as Clojure).** The Phase 5 `:map` parse guard MUST exclude records explicitly: `(and (map? x) (not (instance? Tag x)) (not (instance? Tags x)))` (or `(not (record? x))`).
- `assoc` preserves record type; `keys`/`vals`/`seq` work.
- **Basilisp record quirks (avoid these patterns on records):**
  - `(get r :missing :default)` → `nil` (default IGNORED); same for `(:missing r :default)` → `nil`. Do not rely on get-with-default against a record.
  - `(contains? r :key)` → `:key` (returns the key, truthy but not `true`); `(contains? r :missing)` → `false` correctly. Fine in boolean position only.

### 2. Python random interop — WORKS, `.choice` takes Basilisp vectors directly

- `(import random)` + `(random/Random 42)` fine. `(.randint r 1 10)` → `2`, `(.uniform r 0 1)` → `0.025010755222666936` (seed 42), `.gauss`/`.random` fine.
- **`(.choice r [:a :b :c])` works on a Basilisp vector directly** — no python list conversion needed (vectors implement the Python sequence protocol). Also works on python lists and strings.
- Determinism: two fresh `(random/Random 7)` instances produce identical 20-draw `.randint` sequences (`true`). Phase 7 seed threading is safe.

### 3. Thunk-stack driver — VIABLE. Decision: raw Python list via interop

100k thunk executions where each thunk pushes the next (self-replenishing chain), driver = top-level `loop/recur` popping until empty:
- Python list (`.append`/`.pop`): **100,000 thunks in ~3.27 s, no RecursionError** (repeatable: 3.27/3.28 s).
- `collections.deque`: 3.64 s — no better than list.
- Atom + Basilisp vector (`swap! conj`/`peek`/`pop`): **30.9 s — 10x slower. Rejected.**
- Baselines explaining the budget: empty `loop/recur` 100k ≈ 5.1–5.8 s (Basilisp per-iteration overhead ~50 µs; raw Python while-loop is 0.011 s); `vswap!` or `swap!` add ~70–90 µs/op (100k vswap! loop ≈ 12–14 s). Scaling is linear (10k ≈ 0.60 s).
- **Plan edit: the Phase 0 "<2 s per 100k" target is not achievable on this substrate — revise expectation to "no RecursionError, linear scaling, ≲4 s per 100k thunks".** Realistic seqex inputs are orders of magnitude below 100k thunks; the Phase 6 pathological-memo test budget (`[:* [:* :int]]` on 30 elements < 2 s) remains comfortably safe.
- **Hot-loop rule for Phase 6:** stack, memo set, and success box should be Python-native mutables (`python/list`, `python/set`) mutated via interop; avoid `vswap!`/`swap!` inside the driver loop.

### 4. volatile! — EXISTS

`volatile!`, `vswap!`, `vreset!`, `volatile?` all present and correct (`@v` after `(vswap! v inc)` `(vswap! v + 10)` → `11`). But per timing above, volatiles are no cheaper than atoms in Basilisp (~70+ µs/op) — prefer Python list/set mutation in hot paths; volatiles fine for cold-path cells.

### 5. sequential? — Clojure-consistent, plus interop caveats

| value | sequential? |
|---|---|
| `[1 2 3]` | true |
| `(list 1 2 3)` | true |
| `(map inc [1 2])` (lazy seq) | true |
| `(range 3)` | true |
| `"abc"` | false |
| `#{1 2}` | false |
| `{:a 1}` | false |
| `nil` | false |
| record instance | false |
| `python/list`, `python/tuple` | **false** |

Python lists/tuples are NOT `sequential?` — the Phase 6 top-level seqex guard will reject raw Python sequences (acceptable; matches the Basilisp data model; document if it ever surfaces).

### 6. Bonus probes

- `(str :ns/kw)` → `":ns/kw"` (leading colon, namespace included); `(name :ns/kw)` → `"kw"`, `(namespace :ns/kw)` → `"ns"`. JSON-schema `$ref` naming via `(subs (str kw) 1)` works as planned.
- `(keyword "a" "b")` → `:a/b`; `(keyword "c")` → `:c`.
- **`(python/callable :kw)` → `true`** — and also `true` for maps, sets, vectors, and symbols (they all implement `__call__`). **Plan edit for Phase 8:** bare `python/callable` is too broad for `:=>` validate (a keyword or map would validate as a function). `fn?` is too narrow (`false` for Python builtins like `operator/add` and bound methods, which are legitimate callables in Basilisp interop). `ifn?` is Clojure-like (`true` for keywords/maps). Use a combined predicate, e.g. `(or (fn? x) (and (python/callable x) (not (coll? x)) (not (keyword? x)) (not (symbol? x))))` — finalize exact shape in Phase 8; the existing checkpoints (`inc` → true, `5` → false) hold either way.
- `sorted-by` does NOT exist (`resolve` → nil); `sort-by` does, including comparator arity (`(sort-by :k > ...)` works).
- `format` works with Python-style `%s`/`%d` (`(format "x=%s n=%d" :kw 42)` → `"x=:kw n=42"`); plain `str` concatenation renders keywords with colons — good for humanize messages like `"should be spelled :name"`.
- `update-in` (map and vector paths) and `reduce-kv` (maps AND vectors, index as key) both work.

### Decisions summary

| Question | Decision |
|---|---|
| Tag/Tags representation | `defrecord` in `balli.core` (Phase 5 as planned) |
| `:map` parse guard | `map?` alone insufficient — add `(not (record? x))` / instance checks |
| Mutable stack for regex driver | Raw `python/list` via interop; Python-native mutables for all driver-hot state |
| volatile! availability | Available; use freely outside hot loops |
| Thunk budget | Revise "<2 s/100k" → "≲4 s/100k, no RecursionError"; Phase 6 test budgets unaffected |
| `:=>` callable check (Phase 8) | Not bare `python/callable`; combined `fn?`-or-filtered-callable predicate |
| Generator RNG (Phase 7) | `random.Random` instance; `.choice` on Basilisp vectors directly, no conversion |
