# `balli.generator`

Schema-driven value generation (Phase 7, malli-semantics section H). Public surface: (generate s) / (generate s {:seed n :size n}) -> one value (sample s) / (sample s {:seed n :size n}) -> vector of values `generate`'s :size (default 30) scales value magnitude and collection lengths. `sample`'s :size is the COUNT of samples (default 10, each generated at the default generation size 30); a single random.Random is threaded through all n generates, so a seeded sample is deterministic as a whole. All randomness flows through one random.Random instance created per generate/sample call ((random/Random seed) when :seed is supplied, unseeded otherwise), so equal seeds produce equal values. Property hooks, checked in priority order BEFORE the type default: :gen/gen -> Balli generator object or fn [rnd size] -> value :gen/return -> that constant (nil included -- presence-checked) :gen/elements -> uniform .choice from the given collection :gen/schema -> generate that schema instead then :gen/fmap (a real fn, not an s-expression) post-maps whichever result was produced. :gen/min / :gen/max override :min / :max for generated numeric bounds and collection/string sizes. Malli's :gen/gen (test.check generator objects) is NOT supported -- there are no generator objects here. Type defaults (see section H): :int/:float/:double uniform in bounds (default +/- size*size); :number 50/50 int-or-float; :string alphanumeric, length [min, max|size/3]; :keyword/:symbol 1-8 lowercase alpha chars (unqualified); :uuid built from 32 rnd hex digits (seed-deterministic, unlike random-uuid); :any draws from the documented pool {nil, int, string, boolean}; :maybe 20% nil; :map optional entries included with p=0.5; :map-of/:set distinct members via retry (cap 100 duplicate draws -> :balli.core/unsatisfiable-schema); :and generates its first child and retries until the whole :and validates (cap 100); :not generates :any values and filters (cap 100); :multi picks a branch entry and generates its schema -- the branch schema itself must produce the dispatch value (e.g. contain a [:dispatch-key [:= tag]] entry); :re has a small built-in generator for common regex forms; :fn has NO default generator and throws :balli.core/no-generator unless a :gen/* hook is supplied. Predicate schemas (:balli/pred) generate through the pred-gen-forms mapping (unmapped preds, incl. inst? until Phase 5, throw no-generator); comparators generate ints relative to their child value (non-numeric children throw no-generator; :not= filters the :any pool). :=> generates a constant-ish fn that ignores its arguments and returns a freshly generated OUTPUT value per call, drawing from the Random threaded through the enclosing generate/sample call -- determinism holds at generator-CONSTRUCTION level (equal seeds give fns whose successive calls yield equal value sequences), not per call. :function generates from its first :=> child. Sequence schemas generate FLAT vectors by concat-splicing child chunks (:cat/:catn concat, :alt/:altn pick, :? 0-or-1, :* 0..size/3 reps, :+ 1..max(1,size/3), :repeat min..(max|min+size/3) reps); a nested seqex child splices its chunk into the parent, any other child contributes one element. [:schema <seqex>] is a single element whose VALUE is the inner seqex's flat vector. A :ref directly in seqex child position throws :balli.core/potentially-recursive-seqex, mirroring the compilers. :sequential/:seqable/:every generate vectors (vectors satisfy all three predicates; :every generation is finite despite validation's bounded-prefix semantics). Recursion cap (exact behavior): `depth` counts :ref expansions on the current generation path; the cap is 5. Entering a :ref with depth >= 5: when the resolved target normalizes to :maybe the escape value nil is generated; any other target type throws :balli.core/unsatisfiable-schema. Independently, at depth >= 5 generation runs REDUCED: :maybe always nil, :map omits ALL optional entries, and collection/seqex rep counts collapse to their minimum (0 unless :min/:+ says otherwise) -- so recursion hidden behind optional keys or 0-min collections terminates by omission before the ref escape is ever needed.

## `generator?`

Kind: `defn`

True when `x` is a Balli generator object.

## `generator`

Kind: `defn`

Return a small generator object for schema `s`. The object is data and can be stored in :gen/gen; use `generate*`, `sample*`, or `shrink*` to run it.

## `generator-from`

Kind: `defn`

Return a Balli generator object from functions. `generate-fn` receives opts and returns a value. Optional `sample-fn` and `shrink-fn` override default repeated generation and no-op shrinking. This is the Balli-native adapter point for generator ecosystems outside Clojure test.check.

## `return`

Kind: `defn`

Generator object that always returns `value`.

## `elements`

Kind: `defn`

Generator object that picks one value from `xs` using opts :seed when present.

## `fmap`

Kind: `defn`

Map `f` over a generator object or raw schema form.

## `bind`

Kind: `defn`

Monadic bind for Balli generator objects. `(f generated-value)` must return a generator object or raw schema form.

## `generate*`

Kind: `defn`

Run a Balli generator object or a raw schema form.

## `sample*`

Kind: `defn`

Sample from a Balli generator object or a raw schema form.

## `shrink*`

Kind: `defn`

Shrink with a Balli generator object or a raw schema form.

## `generate`

Kind: `defn`

Generate one value satisfying schema `s` (raw form or schema object). `opts` supports {:seed n :size n :registry r} -- :size (default 30) scales magnitudes and collection lengths; equal seeds give equal values; :registry applies to raw forms only (a schema object's baked-in registry wins). Throws ex-info :balli.core/no-generator for :re/:fn without :gen/* hooks and :balli.core/unsatisfiable-schema when a filtered or recursive strategy cannot produce a value (see the ns docstring).

## `sample`

Kind: `defn`

Vector of generated values for schema `s`. `opts` supports {:seed n :size n :registry r} where :size is the COUNT of samples (default 10) -- each value is generated at the default generation size (30). One random.Random threads through all generates, so a seeded sample is deterministic as a whole (and its first element equals (generate s {:seed n})).

## `shrink`

Kind: `defn`

Return schema-valid smaller candidates for `value`. With `:predicate`, only candidates for which predicate returns truthy are kept; this models shrinking a failing generated case while preserving the failure.

## `shrink-trace`

Kind: `defn`

Greedily shrink `value`, returning every accepted step. With `:predicate`, only candidates preserving the predicate are accepted.

## `check`

Kind: `defn`

Generate `:iterations` values from schema/generator `g` and validate them against `schema` (defaults to `g` when `g` is a raw schema form). Returns a report map with failing examples, never throws for ordinary invalid values. Useful as a small Balli-native property check in CI and docs examples.

## `check-roundtrip`

Kind: `defn`

Generate values for `schema`, encode then decode them with transformer `t`, and report any values that do not roundtrip or no longer validate.

## `function-checker`

Kind: `defn`

Generative checker for :=>/:function schemas, for use as the :balli.core/function-checker opt of balli.core/schema (baked) or raw-form validate/explain (cache-bypassing). Returns (fn [schema-form-or-ast value registry]) -> nil | failure map which generates `:iterations` (default 100) input argument seqs from the :=> input seqex (at the default generation size, fresh unseeded Random per check), applies `value` to each, and validates every return against the output schema. nil when all iterations pass; on the first failure a map {:balli.core/result <return value, or the raised exception> :input <the generated argument vector> :output-errors <explain error vector, or nil when the call raised>} A :function schema checks each :=> child in order and returns the first failure. Guards are NOT exercised by the checker (instrument's concern); input generation follows generate's seqex semantics, so :re/:fn inputs without :gen/* hooks throw :balli.core/no-generator.
