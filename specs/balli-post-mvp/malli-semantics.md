# Malli 0.20.0 semantics reference (distilled from source)

Extracted from `~/.m2/repository/metosin/malli/0.20.0/malli-0.20.0.jar` (source at `/tmp/malli-src/malli/`, re-extract with `unzip` if missing). This file is the authoritative semantic contract for the balli-post-mvp phases. Where Balli deviates, the deviation must be documented in the root README "Differences from Malli" section.

---

## A. Transformers (malli.transform + core decode/encode)

### Contract

- A transformer exposes a **chain**: vector of `{:name :decoders :encoders :default-decoder :default-encoder}`.
- `(transformer & ts)` flattens args (maps kept as-is; transformers expanded via their chains) into one chain.
- Per schema node, `-value-transformer` reduces over the chain **in order**; per link resolves an interceptor by priority:
  1. schema property `(get-in props [method name])`, e.g. `{:decode {:string f}}`
  2. schema property under qualified name, e.g. `:decode/string`
  3. `(get (:decoders link) (type schema))` — the per-type map
  4. `:default-decoder` / `:default-encoder`
- Interceptor normalization: plain fn → `{:enter f}`; map with `:compile` → `(compile schema options)` then normalize+merge; `{:enter f :leave g}` as-is. Folding across chain links:
  `enter = new-enter ∘ enter` (chain order), `leave = leave ∘ new-leave` (reverse chain order) — interceptor stack. Decoders conventionally sit in `:enter`, encoders in `:leave` — this produces the documented decode/encode order reversal.

### decode/encode machinery

- Node combinator: final fn = `leave(children(enter(x)))`; absent parts elided; whole-subtree nil ⇒ identity pass-through.
- `:and`/`:maybe`/`:not`: all children's transformers composed in child order, applied to the same value.
- `:map`: guarded by `map?` (non-maps pass through). Transforms only **present** keys; missing keys untouched.
- `:map-of`: rebuild via reduce-kv transforming keys with key-schema transformer, values with value-schema transformer; guarded by `map?`.
- `:vector`/`:set`/`:sequential`: child transformer mapped over elements, rebuilt; guarded by sequential-or-set.
- `:tuple`: per-index transforms.
- `:or`: **decode** — try each child transformer in order, return first result that validates against that child; if none validate, return the **first** child's transformed result. **encode** — first child whose validator accepts the raw value gets its transformer; none match ⇒ unchanged.
- `:multi`: dispatch on the post-enter value; matching branch's transformer; no branch ⇒ pass-through.
- `:ref`: lazy/memoized target transformer (recursion-safe).
- `:enum`/`:=`: `{:compile ...}` that infers the child-value type and reuses that type's coder.

### Built-in transformers (all scalar coercions LENIENT — non-matching input returned unchanged, never throw)

**string-transformer** (name `:string`), decoders:
- `:int`: `"42"` → 42 (integer parse; non-numeric unchanged). `:double`/`:float`/`:number`: `"1.5"` → 1.5.
- `:boolean`: exactly `"true"`→true, `"false"`→false, else unchanged.
- `:keyword`: `"kw"`→:kw, `"ns/kw"`→:ns/kw (no leading-colon stripping in malli; Balli MAY strip a single leading `:` — document). `:symbol` similar. `:uuid`: only if canonical 8-4-4-4-12 hex regex matches, else unchanged.
- `:vector`: sequential→vector; `:set`: sequential→set.
- `:map-of` key DECODING (both string- and json-transformer): map keys are decoded with the key-schema's **string-transformer** decoder — JSON object keys are always strings, so even under json-transformer keys use string coercion rules (`[:map-of :keyword :int]` decodes `{"a" 1}` → `{:a 1}`; `[:map-of :int :string]` decodes `{"1" "x"}` → `{1 "x"}`). A decoded key is kept only when valid per the key schema, else the original key is kept. Encode side: keyword keys → string keys.
- encoders: numbers→str; keyword→name (or "ns/name"); booleans NOT stringified.

**json-transformer** (name `:json`): assumes JSON-parsed input — NO string→number/boolean coercions. Decoders: keyword/symbol/uuid from string; float/double from number; int from number only when integral. `:set` from sequential; `:vector` sequential→vector.

**strip-extra-keys-transformer**: `:map` — dissoc keys not among declared entry keys; applies when `:closed` prop is nil or true (NOT when explicitly `{:closed false}`). `:map-of` — keep only entries valid per key+value schemas (leave-phase for decode).

**key-transformer** `{:decode f :encode g}`: map keys transformed at enter (decode) / leave (encode).

**default-value-transformer** `{:key :default, :defaults {type fn}}`: every schema — nil replaced by `:default` prop (found via `contains?`-style lookup so explicit nil default counts) or `(defaults (type schema))`. `:map` — additionally fills **missing** non-optional keys whose entry (or value-schema) carries the default prop; opt `:add-optional-keys` fills optional too. Both decode and encode.

**collection-transformer**: `:vector`/`:tuple` ← sequential-or-set→vector; `:set` ← sequential→set.

### coerce/coercer

`coercer(s, transformer)` → fn: `decoded = decode(x)`; `valid?(decoded)` ? decoded : throw ex-info with `{:value decoded :schema s :explain (explain decoded)}` and type key (Balli: `:balli.core/coercion`). `coerce` = one-shot.

---

## B. JSON Schema export (malli.json-schema)

Walker-based postwalk. Per node:
```
p = merge(type-properties, properties)
(or (:json-schema p)                                  ; whole-node override
    (merge {:title/:description/:default from p}
           (accept type schema children options)
           (unlift :json-schema/* props)))            ; :json-schema/foo → :foo, wins over accept
```

Type → JSON Schema mapping (children already transformed):
- `:any`/`:fn` → `{}`; `:nil` → `{"type" "null"}`
- `:string` → `{"type" "string"}` + `:min/:max` → minLength/maxLength
- `:int` → `{"type" "integer"}`; `:float`/`:double`/`:number` → `{"type" "number"}`; `:min/:max` → minimum/maximum
- `:boolean` → boolean; `:keyword`/`:symbol` → string; `:uuid` → `{"type" "string" "format" "uuid"}`
- `:=` → `{"const" v}`; `:not` → `{"not" child}`
- `:and` → `{"allOf" [...]}`; `:or` → `{"anyOf" [...]}`; `:orn` → anyOf of child schemas (map last children)
- `:enum` → `{"enum" [...]}` + inferred `"type"` when ALL values are string/keyword/int/double (keywords render as strings)
- `:maybe` → `{"oneOf" [child {"type" "null"}]}`
- `:multi` → `{"oneOf" [branch-schemas]}` (dispatch ignored)
- `:map-of` → `{"type" "object" "additionalProperties" val-child}` + min/maxProperties
- `:vector`/`:sequential` → `{"type" "array" "items" child}` + min/maxItems; `:set` same + `"uniqueItems" true`
- `:tuple` → `{"type" "array" "prefixItems" [...] "items" false}` (draft 2020-12)
- `:re` → `{"type" "string" "pattern" <pattern source string>}`
- `:map` → `"properties"` (insertion order), `"required"` = non-optional keys (omit when empty), `:closed true` → `"additionalProperties" false`. Keyword keys render as name strings.
- `:ref` → `{"$ref" "#/definitions/<name>"}`; definitions collected into top-level `"definitions"`; recursion guarded by inserting a stopper before recursing. Ref name from keyword: `ns/name` → `"ns.name"`-ish (Balli: use `(subs (str kw) 1)`, document).

Output as Basilisp maps with STRING keys (JSON-shaped, ready for `json/dumps` via python interop).

---

## C. malli.util + walk + per-branch :or explain

### walk

Postwalk: `(walk schema f)` where f receives `(schema path walked-children)` bottom-up and returns a replacement. `schema-walker f` rebuilds the schema form with walked children then applies f — schema-form→schema-form postwalk. Refs are NOT entered by default (children of a ref node = the ref keyword). Map entries walk their value schemas with path `(conj path key)`; indexed children with `(conj path i)`.

### util fns (port these; skip subschemas/in->paths/assoc-in)

- `merge s1 s2`: nil either side → other. Both `:map`: props shallow-merged; entries iterate s1's then s2's preserving first-seen order; duplicate key → entry props merged, `:optional` = later entry's requiredness wins (required in s2 ⇒ required), value schemas **recursively merged** (deep merge for nested maps). Not both maps → s2 wins.
- `union s1 s2`: like merge but duplicate-key value schemas: equal forms → s1, else `[:or s1 s2]`; `:optional` = optional in either (required only if required in both).
- `select-keys s ks` / `dissoc s k`: filter/remove `:map` entries.
- `optional-keys s ks?` / `required-keys s ks?`: set/remove `:optional true` on entries (all when ks omitted).
- `closed-schema s` / `open-schema s`: recursive walk; every `:map` without explicit `:closed false` gets `:closed true` / has `:closed` removed.
- `get s k` (map entry schema or indexed child), `get-in s ks`.

### per-branch :or explain (fix MVP simplification)

Malli emits each branch's errors (path gets branch index) when ALL branches fail. Balli MVP emitted one generic error at the node — replace with malli behavior: concat all branches' errors; `:path` extended with branch index, `:in` unchanged.

---

## D. Spell-checking (malli.error)

Opt-in rewrite of explain data BEFORE humanize: `(with-spell-checking explanation)`.
- Levenshtein distance (full-matrix) over `str` of keys. Threshold from shorter key length (leading `:` stripped for length): `<=2→0, <=5→1, <=6→2, <=11→3, <=20→4, else floor(0.2*len)`.
- For each `:extra-key` error: candidates = declared entry keys of that map schema MINUS keys present in the value; find those within threshold; if any → retag error type `:balli.error/misspelled-key`, attach `:balli.error/likely-misspelling-of` = vector of paths `(conj (butlast path) candidate)`.
- For each `:invalid-dispatch-value` on keyword-dispatch `:multi`: same against dispatch keys → `:balli.error/misspelled-value`.
- Then DROP any `:missing-key` error whose path is among the likely-misspelling-of paths.
- Humanize renders: `"should be spelled :x"` (or `:x or :y`) using last path elements.

---

## E. parse/unparse + :orn

- `parse s x` → parsed value or the sentinel `:balli.core/invalid` (keyword compare). `unparse` = exact inverse, same sentinel on mismatch.
- Tag containers: `Tag {key value}` and `Tags {values}` — implement as Basilisp records (`defrecord Tag [key value]`), with helper ctors/predicates exported from `balli.core`.
- `:orn` (new schema type): `[:orn [:tag schema] ...]` — validates like `:or`; parse → `Tag(tag, parsed)` of first matching branch; unparse dispatches on `:key`. Entries like `:map` (props map allowed per entry).
- `:multi` parse → `Tag(dispatch-value, parsed-branch)`; unparse via `:key`.
- `:maybe`: nil → nil, else child parse. `:map`: parse entry values (stays a map); guard rejects Tag/Tags instances. Colls: parse each element. `:and`: parse via the single TRANSFORMING child (one whose parser produces structure: `:orn`/`:multi`/`:catn`/`:altn`/seqex/nested transforming, analyzed THROUGH refs via the registry) when exactly one exists; zero transforming children → first child's parse; **in both cases every remaining child is still validated against the ORIGINAL value** (`[:and :int [:fn even?]]` on 3 → invalid). Two or more transforming children → throw `:balli.core/invalid-schema` at PARSER COMPILE time (not normalize — refs need the registry, which compile has; normalize does not deref refs). Simple schemas: validate → value | invalid.
- seqex parse shapes: see section F.

---

## F. Sequence (regex) schemas

Types: `:cat :catn :alt :altn :? :* :+ :repeat`. Engine: **backtracking CPS parser combinators, iterative thunk-stack driver** (no deep recursion — Python recursion limit!). Driver holds: success flag, stack of parked thunks, and a seen-cache of `(matcher-id, pos, regs)` to dedupe alternatives (prevents exponential blowup). Main loop: run initial thread; while not succeeded and stack non-empty, pop+run thunk.

- Accepts any `sequential?` input (vectors, lists, seqs — not sets/maps/strings). Whole input must be consumed (end matcher).
- **Splicing**: a seqex child of a seqex consumes from the PARENT's element stream: `[:* [:cat :int :string]]` matches flat `[1 "a" 2 "b"]`. A non-seqex child consumes exactly one element via its ordinary validator. `[:schema <seqex>]` forces single-element semantics (escape hatch). Recursive seqex through `:ref` → throw `:balli.core/potentially-recursive-seqex`.
- Combinators: `cat` folds left. `alt` = ordered choice with backtracking (try first, park rest). `?` = alt(child, ε) greedy. `*` = greedy loop with parked ε fallback. `+` = cat(child, *(child)). `repeat {:min :max}` = counted loop; guard `(<= count pos)` bails when child consumes nothing (nullable-child infinite-loop prevention).
- Explain: track errors at the **furthest position reached** (later pos replaces, equal pos appends). Error types: child's own errors at `(conj in pos)`; `:balli.core/end-of-input` (ran out, value nil); `:balli.core/input-remaining` (trailing junk); `:balli.core/invalid-type` (non-sequential). `:path` gets child index (`:cat`/`:alt`) or tag key (`:catn`/`:altn`).
- parse shapes: `:cat` → vector; `:catn` → `Tags{values {tag parsed}}`; `:alt` → matched value; `:altn` → `Tag`; `:?` → value or nil; `:*`/`:+`/`:repeat` → vector. Nested seqex parse nests ( `[:* [:cat :int :string]]` on `[1 "a"]` → `[[1 "a"]]` ) and unparse re-splices (concat).
- `regex-min-max` (needed by `:=>` arities): item {1,1}; `:*` {0,∞}; `:+` {child-min,∞}; `:?` {0,child-max}; `:cat/:catn` sums; `:alt/:altn` min-of-mins/max-of-maxes; `:repeat` multiplies.

---

## G. Function schemas

- `[:=> input output]` (+ optional `guard` 3rd child): input MUST be `:cat` or `:catn` (else `:balli.core/invalid-input-schema`). `[:function =>1 =>2 ...]`: distinct arities, at most one varargs.
- `validate` on `:=>`/`:function` = `(fn? x)` / `ifn?`-equivalent (python/callable), UNLESS opts carry `:balli.core/function-checker` — then generative check: generate N (default 100) input seqs from input-seqex generator, apply, validate outputs; valid iff no failure.
- `instrument {:schema s :scope #{:input :output} :report f}` → wrapped fn validating args-vector against input seqex (report `:balli.core/invalid-input`), arity bounds (`:balli.core/invalid-arity`), and return value (`:balli.core/invalid-output`). Default report = throw ex-info. `:function` instrument: arity→wrapper table, dispatch on arg count, varargs fallback.
- `function-info` from regex-min-max: `{:min :arity (n or :varargs) :input :output (:max)}`.
- Generator for `:=>`: constant fn that ignores args and returns generated output values.

---

## H. Generators (pure Python `random`, no test.check)

`(generate s)` / `(generate s {:seed n :size n})` (size default 30); `(sample s {:size n})` → vector of n samples. Use `random.Random(seed)` instance threaded through.

Property hooks, in priority order: `:gen/return` (constant) → `:gen/elements` (uniform pick) → `:gen/schema` → `:gen/gen`? (skip — no generator objects; document) → type default; then `:gen/fmap` (fn) post-maps. `:gen/min`/`:gen/max` override bounds.

Per type: `:int` uniform in bounds (default ±size²-ish); `:double`/`:float` uniform float in bounds (no NaN/inf); `:string` alphanumeric of length [min,max] (default 0..size/3); `:boolean` coin; `:keyword` short alpha keyword; `:uuid` `random-uuid`; `:nil` nil; `:enum` pick; `:=` constant; `:maybe` 20% nil else child; `:or`/`:orn`/`:multi` pick branch then generate (multi: generated value must carry dispatch — generate the branch schema, which contains the `[:= tag]` entry); `:and` generate first child, retry-until-valid (max 100 → throw `:balli.core/unsatisfiable-schema`); `:not` generate-any + filter (100 tries); `:map` per-entry, optional entries included with p=0.5; `:map-of` distinct keys, count in [min,max] (default 0..size/3); colls length [min,max]; `:tuple` per-child; `:re` → throw `:balli.core/no-generator` unless `:gen/*` props supplied (documented deviation); `:fn` same; `:ref` depth-counter — at cap (default 8? use 5) prefer non-recursive branches (nil for `:maybe`, [] for colls, omit optional keys), else throw unsatisfiable.
Seqex: generate flat via concat-splicing (`:cat` concat of children; non-seqex child → 1-elem list; `:alt` pick; `:*` 0..size/3 reps concat; `:+` ≥1; `:repeat` [min,max] reps; `:?` 0/1).

---

## I. Provider (schema inference)

`(provide samples)` / `(provide samples opts)`. Two passes:
1. Stats fold: classify each value — nil→:nil, map→:map (recurse per key, track per-key presence counts + total), vector/set/sequential→recurse over elements, else :value with the set of scalar type predicates that accept it.
2. Synthesis: single type → that type's schema. Scalar: most specific type among those accepting ALL samples, preference order `[:int :double :keyword :symbol :string :boolean :uuid]` (Balli order; no predicates registry). Colls → `[type elem-schema]` (empty→`[:vector :any]`). Map → `[:map [k (maybe {:optional true}) v-schema] ...]`, optional iff present in fewer samples than total. Types + :nil → `[:maybe ...]`; multiple non-nil types → `[:or ...]` (stable order).
- `:map-of` heuristic: when ≥ `:map-of-threshold` (default 3) map samples AND all key schemas equal AND all value schemas equal AND keys mostly distinct across samples (`distinct-count > n^0.7`), emit `[:map-of k v]`.
- No `:enum` inference by default.
