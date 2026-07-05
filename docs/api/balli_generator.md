# `balli.generator`

## `generator?`

Kind: `defn`

True when `x` is a Balli generator object.

## `generator`

Kind: `defn`

Return a small generator object for schema `s`. The object is data and can be stored in :gen/gen; use `generate*`, `sample*`, or `shrink*` to run it.

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

## `function-checker`

Kind: `defn`

Generative checker for :=>/:function schemas, for use as the :balli.core/function-checker opt of balli.core/schema (baked) or raw-form validate/explain (cache-bypassing). Returns (fn [schema-form-or-ast value registry]) -> nil | failure map which generates `:iterations` (default 100) input argument seqs from the :=> input seqex (at the default generation size, fresh unseeded Random per check), applies `value` to each, and validates every return against the output schema. nil when all iterations pass; on the first failure a map {:balli.core/result <return value, or the raised exception> :input <the generated argument vector> :output-errors <explain error vector, or nil when the call raised>} A :function schema checks each :=> child in order and returns the first failure. Guards are NOT exercised by the checker (instrument's concern); input generation follows generate's seqex semantics, so :re/:fn inputs without :gen/* hooks throw :balli.core/no-generator.
