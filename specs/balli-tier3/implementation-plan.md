# Balli Tier 3 — Implementation Plan

## Overview

Seven phases: spike → predicates/comparators → mutable registry → local registries → default branches → time → docs. Contract per phase: [malli-semantics.md](malli-semantics.md) §1–§5. Gates: narrow test file + full `basilisp test` + `scripts/compile_check.lpy` per phase; completion preflight adds 3× `PYTHONHASHSEED` full runs.

**Composition rules (from both prior retros):** every phase includes (a) at least one feature×feature composition checkpoint AND (b) at least one checkpoint passing a **schema object** (not a raw form) through the new surface. Schema-boundary validation (garbage forms AND garbage property values → `:balli.core/invalid-schema`) for every new type/property.

## Prerequisites

- 0.2.0 merged to main (`71e3bfb`); branch `balli-tier3`; 298 tests green.
- Malli source at `/tmp/malli-src/`.

## Phase 0: Spike

- [ ] `datetime.fromisoformat` on py3.12 via Basilisp: `"2024-01-01T00:00:00Z"`, `"+02:00"` offsets, naive strings; `.tzinfo` aware/naive detection; `date.fromisoformat`, `time.fromisoformat`; fractional seconds
- [ ] `(isinstance <datetime> date)` → confirm True (subclass) — exclusion strategy for `:time/local-date`
- [ ] `timedelta`: comparison ops, negative values, `.total_seconds()`; sketch + probe the ISO-duration regex round-trip on `"PT15M" "P1DT2H3M4.5S" "P2W" "-PT5S"`
- [ ] Basilisp availability of each §4 predicate name; note aliases/missing
- [ ] Fn-identity map lookup: `(get {int? :a} int?)`; stability of core-fn identity across ns requires
- [ ] `inst?` on Python datetime instances
- [ ] Record findings in "Phase 0 findings" section here

**Checkpoints:** each bullet a probe with exact outputs. No test file.

## Phase 1: Predicate + comparator schemas (§4)

- [ ] `balli.normalize`: predicate table (fn-identity → type kw AND quoted-symbol → type kw, per spike list); dispatch extension — a bare fn/symbol in schema position, or `[pred]` / `[pred props]` vector form; AST `{:type :balli/pred :pred-type <kw> ...}` or reuse per-pred types — DESIGN: single `:balli/pred` AST type carrying `:pred-key` (e.g. `int?`) + the fn; only generic props allowed (`:error/message`, `:gen/*`, `:registry`)
- [ ] Comparators `:> :>= :< :<= :not=`: normalize (exactly 1 child, props rule standard), registry builtin-types
- [ ] compile: pred validate = exception-safe pred call; comparator validate = exception-safe `(op x child)`; explainers with `:type :balli.core/invalid` (preds) / comparator-specific messages via error table
- [ ] error.lpy: humanize messages — pred table (int? "should be an integer", string?, boolean?, keyword?, uuid?, pos-int? "should be a positive integer", nat-int?, neg-int?, nil?, coll?, map?, vector?, set?, seqable?, fn?, zero? — others "invalid value"); comparators: `:>` "should be larger than X", `:>=` "should be at least X", `:<` "should be smaller than X", `:<=` "should be at most X", `:not=` "should not be equal to X"
- [ ] generator: pred→schema mapping table per §4 (unmappable → no-generator); comparators (int-based above/below child; `:not=` filter). **`inst?` is no-generator in THIS phase** (its mapping to `:time/instant` lands in Phase 5, which upgrades the table entry) — Phase 1's gate must not depend on Phase 5
- [ ] json-schema: preds → obvious types or `{}`; comparators → exclusiveMinimum/minimum/exclusiveMaximum/maximum/`{}`
- [ ] transform: predicate schemas get string/json coders for int?/integer?/pos-int?/neg-int?/nat-int?/double?/float?/number?/boolean?/keyword?/symbol?/uuid? (malli does). **Dispatch architecture (adversary P1):** transformer per-node lookup currently keys on `(:type ast)`; for `:balli/pred` nodes it must FALL THROUGH to a secondary lookup on `(:pred-key ast)` — i.e. coder tables may contain both type keywords and pred-key symbols; resolution order: props → `(get coders (:pred-key ast))` when type is `:balli/pred` → `(get coders (:type ast))` → default
- [ ] walk/util: preds are leaves; comparators leaf-with-child (walk child? malli treats comparator child as value, not schema — LEAF, child untouched)
- [ ] parse: simple validate-then-value
- [ ] `tests/test_pred.lpy`: every registered pred happy/sad; quoted-symbol form; `[pred props]` with `:error/message`; comparator matrix incl. non-comparable → false; string-decode composition `(b/decode [:map [:n pos-int?]] {:n "5"} (bt/string-transformer))` → `{:n 5}`; **schema-object composition: `(u/merge (b/schema [:map [:n int?]]) ...)` round-trip**; generator validity; humanize wording

**Checkpoints:**
- `(b/validate pos-int? 5)` → `true`; `(b/validate pos-int? 0)` → `false`; `(b/validate [:vector int?] [1 2])` → `true`
- `(b/validate [:> 5] 6)` → `true`; `(b/validate [:> 5] "x")` → `false` (no throw)
- `(be/humanize (b/explain [:<= 100] 200))` → `["should be at most 100"]`
- `(b/decode int? "42" (bt/string-transformer))` → `42`
- Narrow: `basilisp test tests/test_pred.lpy`

## Phase 2: Mutable + composite default registry (§5)

- [ ] `balli.registry`: `composite` (seq-of-registries lookup, first hit, `:types` unioned — internal representation may stay a merged map if lookup-laziness isn't needed; DESIGN: keep registries as maps, composite = ordered vector wrapper `{:balli/composite [r1 r2]}` with `resolve-ref`/type-membership walking in order); module atom `default-registry*` seeded with builtins; `default-registry` derefs; `set-default-registry!` (validates shape) + `register!` (kw+form or map, merges into current `:schemas`); existing `registry` fn layers over live default
- [ ] **Invalidation architecture (adversary P2, no registry→core cycle):** `balli.registry` owns a public `mutation-epoch` atom (monotonic int) bumped by `set-default-registry!`/`register!`. `balli.core`'s raw-form cache stores the epoch it was filled under; on lookup, epoch mismatch → clear cache and recompile. Core already requires registry (legal direction); registry gains no new requires. Document snapshot semantics for baked schema objects (docstring + README later)
- [ ] normalize/compile/etc. must accept composite registries wherever registries flow (resolve-ref + builtin-type membership + normalize bare-keyword resolution)
- [ ] `tests/test_registry_mut.lpy`: register! then validate a raw form using the new key (no opts) — works; re-register! with different schema → raw form picks up NEW meaning (cache invalidated); baked schema object from before mutation keeps OLD meaning (snapshot); set-default-registry! full swap + restore in test teardown (use try/finally or fixture — MUST restore to avoid cross-test pollution); composite lookup order; **composition: register! a schema that itself refs another registered key; schema-object baked pre-mutation validates consistently**

**Checkpoints:**
- `(reg/register! :t3/email [:re #"^[^@]+@[^@]+$"])` then `(b/validate :t3/email "a@b.c")` → `true` (no opts threading)
- Re-register `:t3/email` as `:int` → `(b/validate :t3/email "a@b.c")` → `false`
- Baked object made before re-register still validates the string → `true`
- Narrow: `basilisp test tests/test_registry_mut.lpy`

## Phase 3: Local registries in schema properties (§1)

- [ ] normalize: `:registry` prop validated (map, keyword keys, else invalid-schema) on ANY vector-form schema; layered opts registry (local `:schemas` over outer) threaded through the node's subtree INCLUDING map/multi/orn entry schemas and the prop-registry values themselves (they see outer + each other); `:registry` prop preserved verbatim in `:properties`/`:form`; bare registered keywords inside subtree → refs via layered registry
- [ ] AST: node carries `:local-registry {kw form}` when the prop is present (normalized snapshot NOT stored — ref targets normalize lazily at compile like today)
- [ ] compile (validator/explainer/parser/unparser): descending through a node with `:local-registry` extends the effective registry; ref caches keyed `[kw layer-token]` (token = monotonic id assigned per distinct layered-registry construction during that compilation); recursion guard preserved; SHADOWING test mandatory: `::x` locally bound differently at two depths compiles and validates both meanings
- [ ] **Every ref-identity surface uses `[kw layer-token]`, not bare kw (adversary P2):** validator/explainer/parser/unparser caches, the `transforming-parser?` visited-ref set, transformer lazy ref caches, the generator's ref-identity/depth tracking, AND json-schema's visited set + definitions naming (shadowed same-name refs from different layers must emit distinct definition keys — `<name>__<n>` suffix rule)
- [ ] transform + generator: same layering (generator's ref depth-cap unchanged); json-schema: local-registry refs collected into `"definitions"`; shadowed names get a `__<n>` suffix on collision (documented rule); `[:schema {:registry ...} ::node]` produces `$ref` + definitions
- [ ] core walk: `:registry` prop preserved through rebuild (walk does not enter ref targets, unchanged)
- [ ] `tests/test_local_registry.lpy`: self-contained recursive tree (the README example) validate/explain/parse/generate; mutual recursion between two local keys; **shadowing forced through EVERY surface** (outer `::x` = :int, inner `::x` = :string in ONE schema — assert both subtrees correct via validator, explainer, parser, DECODER (a string-transformer decode where outer-`::x` coerces "5"→5 and inner does not), GENERATOR (generated value validates), and JSON-SCHEMA (two distinct definition keys, `<name>__<n>` suffix present)); local key seeing an OUTER global key; form round-trip preserves `:registry` prop; garbage prop (`{:registry [:not-a-map]}`) → invalid-schema; **schema-object composition: `(b/schema <local-reg form>)` then decode through it with a transformer**

**Checkpoints:**
- `(b/validate [:schema {:registry {::node [:maybe [:map [:kids [:vector [:ref ::node]]]]]}} ::node] {:kids [{:kids []}]})` → `true` — NO opts registry
- Shadowing: outer/inner `::x` both honored (exact checkpoint in tests)
- `(b/form (b/schema <the same>))` round-trips the `:registry` prop
- `(bg/generate <self-contained tree> {:seed 3})` validates
- Narrow: `basilisp test tests/test_local_registry.lpy`

## Phase 4: :balli.core/default branches (§2)

- [ ] normalize: `:map`/`:multi` entries with key `:balli.core/default` are legal (any schema value); at most ONE default entry each (else invalid-schema)
- [ ] compile `:map` (validator/explainer/parser/unparser): residual-map semantics per §2 — validate once on map-minus-explicit-keys; default DISABLES `:closed`; explain at path `(conj path :balli.core/default)` original `in`; parse merge-back
- [ ] compile `:multi`: dispatch fallback branch (validate/explain/parse; parse tags `:balli.core/default`)
- [ ] transform: `:map` default-residual transform + merge-under; `:multi` fallback descent; strip-extra-keys: default entry present → strip nothing
- [ ] json-schema: `:map` default entry → merge default-schema's export as `"additionalProperties"` when it's a `:map-of` (val schema), else best-effort merge per §B of post-mvp semantics (properties/required merged); `:multi` default branch included in `oneOf`
- [ ] error/humanize: default-branch errors render at their `:in` as usual
- [ ] `tests/test_default_branch.lpy`: map+default validate/explain/parse/decode matrix incl. closed-disabled, strip-nothing, residual-invalid; multi fallback validate/explain/parse-tag; two default entries → invalid-schema; **composition: default entry whose schema is a local-registry ref (`[:balli.core/default [:map-of :keyword [:ref ::v]]]` with `:registry` prop); schema-object through decode**

**Checkpoints:**
- `(b/validate [:map {:closed true} [:x :int] [:balli.core/default [:map-of :keyword :string]]] {:x 1 :extra "ok"})` → `true` (closed disabled by default entry)
- `(b/validate [:multi {:dispatch :kind} [:a [:map [:kind [:= :a]]]] [:balli.core/default :map]] {:kind :zzz})` → `true`
- `(:key (b/parse [:multi {:dispatch :kind} [:a [:map [:kind [:= :a]]]] [:balli.core/default :map]] {:kind :zzz}))` → `:balli.core/default`
- Narrow: `basilisp test tests/test_default_branch.lpy`

## Phase 5: balli.time (§3)

- [ ] `src/balli/time.lpy` is a LEAF namespace (adversary P1 — no requires on balli.transform/compile/core, avoiding the cycle compile→time→transform→compile): pure type table `{:time/instant {:check <fn> :decode <fn> :encode <fn> :gen-default [lo hi]} ...}` for the 5 types + ISO-duration regex parser/formatter (per spike findings, incl. negative + fractional). `time-transformer` (name `:time`) lives in **balli.transform** (which may require balli.time; transform→time is acyclic), re-exported or documented as `(bt/time-transformer)`
- [ ] normalize/registry: `:time/*` as builtin scalar-style types (bare kw or `[kw props]`; `:min`/`:max` must be instances of the type — boundary-checked, overriding the numeric-bounds check for these types)
- [ ] compile: validate via `:check` + inclusive min/max via native comparison; explain `:balli.core/invalid-type` / `:balli.core/limits`
- [ ] error: humanize messages ("should be an instant"/"a date"/"a time"/"a date-time"/"a duration"; limits with ISO-rendered bounds)
- [ ] generator: uniform between min/max or table defaults, seeded
- [ ] json-schema: string + format per §3
- [ ] `tests/test_time.lpy`: each type validate happy/sad (incl. aware-vs-naive both directions, date-vs-datetime exclusion), min/max bounds, decode/encode round-trips (string→value→string), duration parser matrix (`PT15M`, `P1DT2H3M4.5S`, `P2W`, `-PT5S`, garbage → unchanged), garbage `:min` → invalid-schema, generator validity + determinism, json-schema formats, **composition: `[:map [:created :time/instant] [:ttl :time/duration]]` json-decode from strings via `(bt/transformer (bt/json-transformer) (bt/time-transformer))` then validate; schema object through generate**

**Checkpoints:**
- `(b/validate :time/instant (datetime/datetime 2024 1 1 ** :tzinfo datetime/timezone.utc))`-style → `true`; naive datetime → `false`
- `(b/decode :time/instant "2024-06-01T12:00:00+00:00" (bt/time-transformer))` → aware datetime; encode back → ISO string
- `(b/decode :time/duration "PT15M" (bt/time-transformer))` → timedelta 900s
- Narrow: `basilisp test tests/test_time.lpy`

## Phase 6: Docs, 0.3.0, full sweep

- [ ] README: new sections (Self-contained schemas/local registries, Default branches, Time schemas, Predicate & comparator schemas, Mutable registry) — every example run-verified; schema table + API reference extended; Differences updated (time subset + skipped types, no var/dynamic/lazy registries, snapshot semantics for baked objects, shadowed-def json-schema suffix rule, ifn? ≈ ifn-like)
- [ ] Version 0.3.0 (pyproject + core/version + toolchain test)
- [ ] Full sweep: `basilisp test` under `PYTHONHASHSEED=1,2,3`; compile_check; wheel check ships `time.lpy`; out-of-cwd smoke using a local-registry schema

**Checkpoints:** 3× seeded full runs green; compile_check 12 namespaces; wheel `.lpy` listing; `/tmp` smoke.

## Verification

Completion gate: the Phase 6 sweep. All exit 0 before PR.

## Rollback

Branch `balli-tier3`; main holds 0.2.0.
