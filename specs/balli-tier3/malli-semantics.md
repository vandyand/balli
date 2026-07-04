# Malli 0.20.0 semantics — tier-3 features (distilled from source)

Source at `/tmp/malli-src/malli/` (re-extract: `cd /tmp/malli-src && unzip -oq ~/.m2/repository/metosin/malli/0.20.0/malli-0.20.0.jar`). Contract for the balli-tier3 phases. Deviations get documented in the root README Differences section.

## §1 Local registries in schema properties

- ANY vector-form schema may carry `{:registry {kw form ...}}` in its properties. Effect: for the whole subtree, the effective registry = local entries layered OVER the current registry (inner shadows outer; nesting layers again, inner-first lookup).
- Local entries see the outer registry AND each other; recursion/mutual recursion between local keys goes through `[:ref kw]` (lazy target resolution — cycles must not eagerly expand).
- `form` round-trips: the `:registry` property is preserved with values as FORMS.
- `[:schema {:registry {::node ...}} ::node]` is the canonical self-contained recursive schema idiom (`:schema` wrapper is transparent; its child resolves under the layered registry).
- **Balli mapping:** normalize validates the `:registry` prop (map of keyword→schema-form, else `:balli.core/invalid-schema`), stores it verbatim in `:properties`, and threads a LAYERED registry (local `:schemas` merged over outer) down the subtree — bare registered keywords inside the subtree normalize to refs against the layered registry. Every ref-resolving surface (compile validator/explainer/parser/unparser, transformer, generator, json-schema) must extend its registry when descending through a node whose properties carry `:registry`.
- **Shadowing-correctness requirement:** per-compilation ref caches are currently keyed by ref keyword alone; with shadowing (`::node` meaning different things at different depths), cache keys MUST incorporate the registry layer (e.g. `[kw layer-token]`) or a fresh sub-cache per layer — a shadowed-ref test is mandatory.
- JSON Schema: refs from local registries emit into `"definitions"` like global refs; shadowed duplicate names may NOT silently collide — suffix or qualify (document the chosen rule; malli has the same collision kludge problem).

## §2 `:balli.core/default` branches

Balli uses `:balli.core/default` as the sentinel entry key (malli: `:malli.core/default`).

**`:map` default entry** — `[:map [:x :int] [:balli.core/default [:map-of :keyword :string]]]`:
- Validate: default schema validates THE RESIDUAL MAP (input minus explicit keys) ONCE — not per-entry. Explicit entries validate as usual.
- A default entry DISABLES `:closed` enforcement entirely (validate + explain).
- Explain: default explainer runs at schema-path `(conj path :balli.core/default)` with the residual map and the ORIGINAL `in` (no key appended).
- Parse: default parser on residual; success merges back `(merge parsed-residual (select-keys m explicit-keys))`; invalid residual → whole map invalid.
- Transform (decode/encode): default-schema transformer on residual, result merged UNDER untouched explicit-key values; explicit entries transform via normal map descent.
- strip-extra-keys-transformer: presence of a default entry means NOTHING is stripped.

**`:multi` default branch** — `[:multi {:dispatch :kind} [:a ...] [:balli.core/default ...]]`:
- Dispatch lookup falls back to the default branch (validate/explain/parse/transform); the default branch receives the WHOLE value.
- Parse tags the default branch as `Tag(:balli.core/default, parsed)`.
- No match and no default → `:balli.core/invalid-dispatch-value` as today.

## §3 Time schemas (`balli.time`) — Python mapping

Malli's `malli.experimental.time` uses java.time classes with `-simple-schema` + inclusive min/max via compareTo + ISO DateTimeFormatter transformers (name `:time`). Balli ports a Python-stdlib subset:

| Type | Python check | min/max | decode string | encode |
|---|---|---|---|---|
| `:time/instant` | `datetime.datetime` with `tzinfo` NOT None (aware) | native `<=` | `datetime.fromisoformat` (py3.11 handles `Z`); result must be aware else pass-through-unchanged | `.isoformat()` |
| `:time/local-date-time` | `datetime.datetime` with `tzinfo` None (naive) | native | `fromisoformat`; must be naive | `.isoformat()` |
| `:time/local-date` | `datetime.date` (and NOT datetime — Python subclass gotcha: `isinstance(datetime, date)` is True, must exclude) | native | `date.fromisoformat` | `.isoformat()` |
| `:time/local-time` | `datetime.time`, `tzinfo` None | native | `time.fromisoformat` | `.isoformat()` |
| `:time/duration` | `datetime.timedelta` | native | ISO-8601 duration parse (custom — stdlib has none): `PnW`/`PnDTnHnMnS` with fractional seconds, optional sign | ISO-8601 duration format (custom) |

- Skipped (documented): `:time/offset-date-time`/`:time/zoned-date-time` (Python has one aware-datetime class — `:time/instant` covers it), `:time/offset-time`, `:time/period` (no calendar-period stdlib type), `:time/zone-id`/`:time/zone-offset`.
- min/max properties: inclusive both ends, values must be instances of the same time type (schema-boundary check: wrong-typed bound → `:balli.core/invalid-schema`). Aware/naive comparison mismatch cannot arise because bounds are type-checked.
- Transformers: mirror malli — a SEPARATE composable transformer (name `:time`), NOT folded into string/json built-ins. Construction lives in `balli.transform` as `bt/time-transformer` (consuming balli.time's leaf table; transform→time is the acyclic require direction). Users compose: `(bt/transformer (bt/json-transformer) (bt/time-transformer))`. Decoders lenient (parse failure → input unchanged). Encoders emit strings.
- Generator: `:time/*` types generate uniformly between `:min`/`:max` when both present, else between sensible defaults (e.g. 2000-01-01..2030-01-01, durations 0..1000000s); seeded via the threaded Random.
- Humanize: invalid-type messages ("should be an instant", "should be a date", ...); limits messages reuse the between/at-least/at-most pattern with ISO-rendered bounds.
- JSON Schema: instant/local-date-time → `{"type" "string" "format" "date-time"}`; local-date → `"date"`; local-time → `"time"`; duration → `"duration"`.

## §4 Predicate + comparator schemas

**Predicates** — registered under BOTH the quoted symbol and the FUNCTION VALUE (in Balli forms, `[:vector int?]` evaluates `int?` to the fn — normalize must dispatch on known fn identities; `[:vector 'int?]` quoted symbols too). No predicate takes `:min`/`:max` (bare `[pred]`/pred only; props map allowed but only generic props like `:error/message`, `:gen/*`).

Balli set (Basilisp-available predicates): `any? some? number? integer? int? pos-int? neg-int? nat-int? pos? neg? float? double? boolean? string? ident? keyword? simple-keyword? qualified-keyword? symbol? simple-symbol? qualified-symbol? uuid? inst? seqable? indexed? map? vector? list? seq? set? nil? false? true? zero? coll? associative? sequential? fn? ifn? empty?` — verify each exists in Basilisp at spike time; register only the ones that do. `empty?` uses malli's special pred `(and (seqable? x) (empty? x))`. `inst?` → Basilisp inst? (Python datetime). `ifn?` in Basilisp ≈ callable — use `ifn-like?` from normalize (documented deviation).

- Validate = the predicate, exception-safe (throw → false).
- Explain error `:type :balli.core/invalid-type`? No — malli predicate failures produce standard errors with the pred symbol as `:schema`; Balli: `:type :balli.core/invalid` with `:schema` = the original form (fn or symbol); humanize via a per-predicate message table where easy (`int?` → "should be an integer"), else "invalid value".
- Generator: map each predicate to an existing type generator where obvious (int?→:int, string?→:string, boolean?→:boolean, keyword?→:keyword, uuid?→:uuid, nil?→nil, pos-int?→[:int {:min 1}], neg-int?→[:int {:max -1}], nat-int?→[:int {:min 0}], zero?→0, true?/false? constants, double?/float?/number?, coll?/vector?/sequential?→[:vector :any], map?→[:map-of :any... keep simple: [:map-of :keyword :any]... decide: vector of :any], set?→[:set :any], seqable?/seq?/list?/indexed?→vector-ish, inst?→:time/instant); unmappable (some? ident? associative? fn? ifn? empty? etc.) → `:balli.core/no-generator` unless `:gen/*`.
- JSON Schema: map to obvious types where possible, else `{}`.

**Comparators** `:> :>= :< :<= :not=` (`:=` exists): exactly ONE child; validate `(op x child)` wrapped exception-safe (non-comparable → false, never throws). Numbers-oriented for `:> :>= :< :<=` (Python comparison on mixed types throws → safely false); `:not=` any values. Form `[:> 5]`. Props map allowed 2nd element when ≥1 child follows (standard rule). Explain `:type :balli.core/limits`? Use dedicated messages: "should be larger than 5", "should be at least 5", "should be smaller than 5", "should be at most 5", "should not be equal to x" (malli's humanize wording). JSON Schema: `:>` exclusiveMinimum, `:>=` minimum, `:<` exclusiveMaximum, `:<=` maximum, `:not=` `{}`. Generator: `:>`/`:>=` → int/float above child (int default), `:<`/`:<=` below, `:not=` → any-gen filtered.

## §5 Mutable + composite default registry

- `composite-registry & rs`: lookup = first hit across registries in order. Balli registries are maps `{:types set :schemas map}` — composite = a seq of them; `resolve-ref` walks in order; `:types` unioned.
- Mutable default: module-level atom in `balli.registry` holding the CURRENT default registry (seeded with builtins). `default-registry` derefs it (a live view — every schema/validate call picks up mutations). `set-default-registry!` replaces it (value = registry map or composite); `register!` convenience: `(register! kw form)` / `(register! {kw form ...})` merges into the current default's `:schemas`.
- `registry` (existing fn, layers customs over defaults) now layers over the CURRENT default (deref at call time).
- Caching hazard: balli.core's global raw-form cache must not serve stale compiled fns after default-registry mutation. Contract (cycle-free): `balli.registry` owns a public monotonic `mutation-epoch` atom bumped by `set-default-registry!`/`register!`; balli.core's raw cache records the epoch it was filled under and, on lookup, clears itself when the epoch has moved. Schema OBJECTS keep their construction-time snapshot (documented: objects are immutable snapshots; malli's mutable registry is also lookup-time for raw forms but baked objects keep resolved refs — Balli matches by clearing raw cache only).
- Skipped (documented): var-registry, dynamic-registry (no dynamic binding story worth it), lazy-registry (provider-on-miss).
