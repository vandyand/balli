# Balli Tier 3 - Research

## Problem Statement

Balli 0.2.0 (PR #2, merged `71e3bfb`) covers Malli's core + post-MVP surface. Five practical gaps remain, identified in the post-ship assessment and confirmed by the user ("implement 1-5"):

1. **Local registries in schema properties** — self-contained recursive schemas (`[:schema {:registry {::node ...}} ::node]`); the anchor feature.
2. **`:balli.core/default` branches** — `:map` residual-map entry + `:multi` fallback branch.
3. **`balli.time`** — date/time/duration schemas + ISO transformers on Python's `datetime` stdlib.
4. **Predicate + comparator schemas** — `int?`/`string?`/... fn+symbol forms, `:> :>= :< :<= :not=`.
5. **Mutable/composite default registry** — `set-default-registry!`, `register!`, live default lookup.

Semantics pinned against Malli 0.20.0 source in [malli-semantics.md](malli-semantics.md) (§1–§5).

## Codebase Context

0.2.0 substrate (298 tests, 11 namespaces). Extension points and hazards per feature:

- **§1 local registries** touch every ref-resolving surface: `normalize` (bare-keyword→ref resolution uses opts registry), `compile` (validator/explainer/parser ref caches keyed by keyword — **shadowing hazard**: same keyword, different layer → cache must key on `[kw layer]`), `transform` (ref lazy caches), `generator` (ref resolution + depth cap), `json_schema` (definitions collection — name-collision rule needed for shadowed refs).
- **§2 defaults**: `compile.lpy` map validator/explainer/parser + `transform.lpy` map/multi descent + strip-extra-keys accept-fn + `normalize` (a `:balli.core/default` map entry's "key" is the sentinel — entry validation must allow it in `:map` and `:multi`).
- **§3 time**: new ns; `-simple-schema`-style registration means normalize/compile need an extension mechanism OR explicit `:time/*` cases. Balli has no custom-type API — **decision: explicit builtin handling** (add `:time/*` to builtin-types + normalize scalar-style + compile cases via a small type-table in `balli.time` consumed by compile) — keep it a table, not 5× copy-paste.
- **§4 predicates**: normalize dispatch is `(cond (keyword? form) form (vector? form) (first form) :else ::unknown)` — must learn fn-value dispatch (identity lookup in a predicate table) and quoted-symbol dispatch.
- **§5 mutable default**: `balli.registry` atom + core's raw-form cache invalidation (`registry-tokens` pattern exists; add cache clear on mutation).

## REPL Findings

Carried from prior phases: records are `map?`; keyword `identical?` unreliable; `python/callable` too broad; Python-native mutables for hot paths; `sort-by str` for deterministic folds. New probes needed at spike (Phase 0):

- `datetime.fromisoformat` behavior on Basilisp/py3.12: `"2024-01-01T00:00:00Z"` (Z suffix), aware vs naive detection (`.tzinfo`), `date.fromisoformat`, `time.fromisoformat`.
- `isinstance(datetime-instance, date)` → True (subclass) — `:time/local-date` must exclude datetimes.
- `timedelta` comparison, arithmetic; NO stdlib ISO-8601 duration parser — custom parser required (regex).
- Basilisp availability of each §4 predicate (`ident?`, `indexed?`, `seqable?`, `simple-keyword?`, ...).
- Fn values as map keys with identity semantics (predicate table lookup): `(get {int? :x} int?)` — do Basilisp core fns hash/equal stably?
- `inst?` on Python datetime.

## Requirements

### Functional

Per [malli-semantics.md](malli-semantics.md) §1–§5, in full. Public API additions:
- `balli.registry`: `set-default-registry!`, `register!`, `composite` (internal ok), live `default-registry`.
- `balli.time`: LEAF ns — type table + ISO parsers only (transformer construction lives in `balli.transform` as `bt/time-transformer`); types `:time/instant :time/local-date :time/local-time :time/local-date-time :time/duration`.
- Everything else lands inside existing namespaces (normalize/compile/transform/generator/json-schema/error/util).

### Non-Functional

- All 298 existing tests stay green (except intentionally updated `:closed`+default interactions — none expected; strip-keys tests unaffected since no existing test uses default entries).
- Full suite run under 3 `PYTHONHASHSEED`s at completion preflight (post-MVP retro action).
- Version 0.3.0.

## Options Considered

- **§3 as custom-type extension API vs explicit builtins**: an IntoSchema-style plugin API is the "right" long-term shape but triples this spec's size; explicit `:time/*` builtins with a data table in `balli.time` gets users the feature now and the table can become the plugin API later. **Chosen: explicit builtins.**
- **§1 cache strategy**: fresh sub-cache per registry layer vs `[kw layer-token]` keys. **Chosen: layer-token keys** (single cache, tokens via monotonic counter per layered-registry construction) — simpler eviction story, keeps the eager-compile+recursion-guard pattern intact.
- **§5 baked-object staleness**: invalidate schema objects on registry mutation vs document snapshot semantics. **Chosen: document snapshots** (matches the existing "baked config wins" opts rule); raw-form cache cleared on mutation.

## Recommendation

Six phases: 0 spike (datetime/predicates probes) → 1 predicates+comparators (§4) → 2 mutable/composite default registry (§5) → 3 local property registries (§1, builds on §5 composite) → 4 default branches (§2) → 5 balli.time (§3) → 6 docs/0.3.0/sweep.

## Open Questions

1. Which §4 predicates exist in Basilisp → resolved at spike; register the intersection.
2. `fromisoformat` Z-handling on py3.12 → spike.
3. Duration format edge cases (negative durations, fractional seconds) → spike decides the regex + round-trip rule.

## References

- [malli-semantics.md](malli-semantics.md) — the contract
- Malli source: `/tmp/malli-src/malli/{core,registry,transform}.cljc`, `experimental/time.cljc`, `experimental/time/transform.cljc`
- Prior retros: `specs/balli-mvp/retro.md`, `specs/balli-post-mvp/retro.md` (composition rule: feature×feature AND form×object; PYTHONHASHSEED preflight)

## North-Star Orientation

No north star (standalone root spec). Parent goal: user-approved items 1–5 from the post-0.2.0 gap assessment.
