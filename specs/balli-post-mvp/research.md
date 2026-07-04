# Balli Post-MVP - Research

## Problem Statement

Balli MVP (shipped 2026-07-04, PR #1, merged `0c74750`) covers validate/explain/humanize/registry — the Tier-1 core. The design doc (`docs/basilisp balli from malli.md`) and the MVP spec's "Out" list defer the rest of Malli's feature surface. This spec closes the gap: **transformers, schema walking + utilities, per-branch `:or` explain, JSON Schema export, key spell-checking, parse/unparse (+ `:orn`), sequence schemas, function schemas, generators, and schema inference (provider)** — the complete remaining tier list, in the design doc's recommended order adjusted for real dependencies (parse before seqex, seqex before generators, generators before function-checking).

Goal framing unchanged: Malli-shaped, not byte-for-byte. Semantics are pinned against **Malli 0.20.0 source** (extracted from `~/.m2/repository/metosin/malli/0.20.0/malli-0.20.0.jar`), distilled into [malli-semantics.md](malli-semantics.md) — the per-phase semantic contract.

## Codebase Context

Current library (post-MVP merge, 93 tests):

- `src/balli/normalize.lpy` — form→AST multimethod; AST nodes `{:type :properties :children :form}`; map/multi children are entry maps `{:key :properties :schema}`; bounds/cardinality/dispatch checked at boundary.
- `src/balli/compile.lpy` — `compile-validator` + `compile-explainer` closure-tree compilers; per-compilation ref cache atoms (eager target compile + fn-indirection recursion guard); explain errors `{:path :in :schema :value :type}`.
- `src/balli/core.lpy` — schema objects `{:balli/schema true :form :ast :registry :cache}`; `validate/validator/explain/explainer/assert-valid`; bounded raw-form cache keyed `[form registry-id]`.
- `src/balli/registry.lpy` — builtin-types set, `default-registry`, `registry` (variadic merge), `resolve-ref`.
- `src/balli/error.lpy` — humanize: tree-build+render, `:balli/error` reserved key for mixed levels, `split-form` property reader.

Extension points this spec relies on:
- New schema types (`:orn`, `:cat`…`:repeat`, `:=>`, `:function`) enter via `normalize` defmethods + `builtin-types` + `case` branches in both compilers. The compilers' `case` dispatch means each phase touches `compile.lpy` in additive branches.
- AST `:form` on every node lets walkers/exporters rebuild original forms without inverse-normalization.
- The seqex engine must be a NEW module (`balli.regex`) — CPS thunk-stack driver, iterative (Python recursion limit ~1000 frames; the driver design from malli.impl.regex is already iterative: parked-thunk stack + memo cache).

## REPL Findings

Verified live against Basilisp 0.5.0 during MVP (carried forward): multimethods, transients, `ex-info`/`ex-data`, atoms, metadata, regex, `python/callable`. New probes needed at Phase 0 (spike):
- `defrecord` (for `Tag`/`Tags` parse containers) — expected to work per Basilisp docs; verify field access + equality.
- `random` module interop (`random.Random(seed)`, `.randint`, `.uniform`, `.choice`) for generators.
- Closure allocation cost in tight thunk loops (seqex driver) — sanity only.
- `volatile!` availability (driver mutable state) — else use atoms or Python lists.
- `defprotocol` (optional — engine can be plain fns).

## Requirements

### Functional Requirements

1. **`balli.transform`**: transformer chain contract, interceptor enter/leave composition, property overrides (`:decode/string` etc.), built-ins: `string-transformer`, `json-transformer`, `strip-extra-keys-transformer`, `key-transformer`, `default-value-transformer`, `collection-transformer`, `transformer` (composition). Core API: `decode`, `decoder`, `encode`, `encoder`, `coerce`, `coercer` per semantics §A.
2. **`balli.util`**: `merge`, `union`, `select-keys`, `dissoc`, `optional-keys`, `required-keys`, `closed-schema`, `open-schema`, `get`, `get-in`; `balli.core/walk` postwalk + `schema-walker`. Semantics §C.
3. **Per-branch `:or` explain** replacing the MVP single-error simplification (§C) — README difference entry removed.
4. **`balli.json-schema/transform`**: full type mapping, `:json-schema/*` property overrides, `"definitions"`+`$ref` for registry refs with recursion guard; string-keyed output (§B).
5. **Spell-checking** in `balli.error`: `with-spell-checking` explain rewrite + humanize messages (§D).
6. **parse/unparse** in `balli.core` + new `:orn` type: `Tag`/`Tags` records, `:balli.core/invalid` sentinel, semantics §E.
7. **Sequence schemas** `:cat :catn :alt :altn :? :* :+ :repeat` in new `balli.regex` engine: validate/explain/parse/unparse, splicing, `[:schema ...]` escape hatch, recursion rejection, `regex-min-max` (§F).
8. **Function schemas** `:=>`/`:function`: callable-check validate, `instrument`, optional generative `function-checker` (§G).
9. **`balli.generator`**: `generate`/`sample`, pure Python `random`, `:gen/*` props, seeded determinism, ref depth-cap, seqex splicing generation (§H).
10. **`balli.provider/provide`**: schema inference from samples with `:map-of` heuristic and optional-key detection (§I).
11. Root README: new sections per feature; "Differences from Malli" updated (removals: `:or` explain simplification; additions: no `:gen/gen` generator objects, `:re`/`:fn` generation requires `:gen/*` props, no sci eval of property code — fns only, no `:andn`, old-parse-format not provided, JSON Schema definitions path fixed).

### Non-Functional Requirements

- Pure Basilisp + Python stdlib (`re`, `random`, `uuid`). No test.check, no sci: schema property values that malli would `eval` must be actual fns in Balli (document).
- Seqex engine iterative (no unbounded Python recursion); memoized alternatives (no exponential blowup on `[:* [:* :int]]`-style pathologies).
- Deterministic generators under `:seed`.
- All existing 93 tests stay green; each phase adds its own test file; `basilisp test` + `scripts/compile_check.lpy` are the gates.

## Options Considered

**A. One spec, dependency-ordered phases (chosen)** — parse→seqex→gen→fn-schemas dependency chain makes separate specs artificial; single branch/PR keeps the review surface coherent.

**B. Spec-per-tier (5+ PRs)** — cleaner review units but massive orchestration overhead and cross-PR dependency friction (generators PR needs seqex PR merged first, etc.). Rejected for an autonomous run.

**C. Skip hardest tiers (seqex/function schemas)** — rejected: goal explicitly says "all remaining post-MVP tiers"; the design doc's difficulty analysis (docs §"Which aspects...") warns these are hard, which is why the semantics were pinned from source first.

## Recommendation

Option A. New namespaces: `balli.transform`, `balli.util`, `balli.json-schema`, `balli.regex`, `balli.generator`, `balli.provider`; extensions to `balli.core` (decode/encode/coerce/parse/unparse/walk/instrument), `balli.normalize`, `balli.compile`, `balli.error`, `balli.registry` (new builtin types).

Phase order: 0 spike → 1 transformers → 2 walk/util/:or-explain → 3 json-schema → 4 spell-check → 5 parse/unparse+:orn → 6 seqex → 7 generators → 8 function schemas → 9 provider → 10 docs+sweep.

## Open Questions

1. ~~Does Basilisp support `defrecord`?~~ Resolve at Phase 0 spike; fallback: plain maps with a marker key `{:balli/tag true :key k :value v}` (document).
2. `:gen/fmap`/property fns: malli evals sexprs via sci. **Decision: Balli accepts actual fns only** (Basilisp has real fns in data; no eval needed). Documented difference.
3. Old-parse-format (`Tag`→vector): **Decision: skip**; provide `tag->vec` helper only if trivial.
4. `:andn`: **Decision: skip** (rare, adds Tags complexity to :and); documented.
5. JSON Schema draft target: **Decision: 2020-12** (`prefixItems`); `definitions` under top-level `"definitions"` with `"#/definitions/"` path (malli default).

## References

- [malli-semantics.md](malli-semantics.md) — distilled Malli 0.20.0 semantics (authoritative for this spec)
- Malli source: `/tmp/malli-src/malli/{transform,util,json_schema,error,generator,provider,core}.cljc`, `/tmp/malli-src/malli/impl/regex.cljc`
- MVP spec + retro: `specs/balli-mvp/` (esp. retro TL;DR: test compositions, not just units; schema-boundary validation class)
- Design doc: `docs/basilisp balli from malli.md` (tier ordering + difficulty ranking)

## North-Star Orientation

No north-star doc (standalone root spec). Parent goal: `/goal` — "Implement all remaining post-MVP tiers … optimally shore up discrepancies between balli and malli."
