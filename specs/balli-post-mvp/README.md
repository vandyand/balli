---
title: "Balli Post-MVP — close the Malli feature gap"
status: in-progress
date: 2026-07-04
priority: 10
---
# Balli Post-MVP — close the Malli feature gap

Implements every remaining post-MVP tier from the design doc, pinned against Malli 0.20.0 source semantics ([malli-semantics.md](malli-semantics.md)): **transformers** (decode/encode/coerce with string/json/strip-keys/key/default-value transformers), **schema walking + malli.util ports** (merge/union/select-keys/closed-schema/...), **per-branch `:or` explain**, **JSON Schema export**, **key spell-checking**, **parse/unparse + `:orn`**, **sequence schemas** (`:cat :catn :alt :altn :? :* :+ :repeat` via an iterative backtracking engine), **function schemas** (`:=>`/`:function` + instrument), **generators** (pure `random`, seeded), and **schema inference** (`balli.provider/provide`).

```clojure
(b/decode [:map [:age :int]] {:age "42"} (bt/string-transformer))   ;; => {:age 42}
(bjs/transform [:map [:id :string] [:tags [:set :keyword]]])        ;; => JSON Schema map
(b/parse [:orn [:num :int] [:str :string]] 42)                      ;; => Tag{:key :num :value 42}
(b/validate [:cat :int [:* :string]] [1 "a" "b"])                   ;; => true
(bg/generate [:map [:id :uuid] [:n [:int {:min 0 :max 9}]]] {:seed 1})
(bp/provide [{:x 1} {:x 2 :y "a"}])                                 ;; => [:map [:x :int] [:y {:optional true} :string]]
```

See [research.md](research.md) and the [implementation plan](implementation-plan.md).

## Scope

**In:** everything in the MVP's "Out" list except the items below.
**Still out (documented):** Python dict/list acceptance (Malli doesn't validate host-foreign data either); sci-eval of property code (Balli takes real fns); `:andn`; old-parse-format shim; test.check-style shrinking; `:re`/`:fn` generation without `:gen/*` props; OpenAPI/Swagger/DOT exporters; clj-kondo integration; `malli.dev` tooling; `malli.experimental`; destructuring.

## Key Decisions

| Decision | Choice | Alternative rejected | Why |
|---|---|---|---|
| Semantics source | Malli 0.20.0 source, distilled to [malli-semantics.md](malli-semantics.md) | Docs/memory | Exact transformer ordering, seqex splicing, parse shapes are subtle; source is ground truth |
| Seqex engine | Iterative CPS thunk-stack + memo cache (`balli.regex`), port of malli.impl.regex architecture | Recursive descent; NFA compilation | Python recursion limit kills recursion; malli's driver is already iterative and memoized |
| Parse containers | `defrecord Tag/Tags` (Phase 0 verifies; fallback marker maps) | Plain vectors/maps | Malli 0.20 shape; records distinguish `Tag` from user data in `:map` guard |
| Property code | Real fns only, no eval | Port sci | Basilisp schemas are live data; fns embed naturally; eval adds a dependency for zero user value |
| Generators | Pure Python `random.Random(seed)` | Hypothesis backend | Zero deps, deterministic seeding; shrinking explicitly out of scope |
| `:re`/`:fn` generation | Throw `:balli.core/no-generator` unless `:gen/*` props given | Regex string synthesis | Malli itself dynaloads test.chuck for this; synthesis is a project on its own |
| Function-schema validate | `python/callable` unless `:balli.core/function-checker` opt | Always generative | Malli behavior exactly |
| JSON Schema draft | 2020-12 (`prefixItems`), string-keyed maps | draft-07 | Matches malli 0.20; string keys are `json/dumps`-ready |
| Phasing | Single spec, 11 phases, parse→seqex→gen→fn order | Spec per tier | Dependency chain (gen needs seqex, fn-checker needs gen) makes separate PRs artificial |

## Implementation Status

- [x] Phase 0: Substrate spike (defrecord, random, driver-loop viability)
- [x] Phase 1: Transformers (balli.transform + core decode/encode/coerce)
- [ ] Phase 2: Walk + util + per-branch :or explain
- [ ] Phase 3: JSON Schema export
- [ ] Phase 4: Key spell-checking
- [ ] Phase 5: parse/unparse + :orn
- [ ] Phase 6: Sequence schemas (balli.regex)
- [ ] Phase 7: Generators
- [ ] Phase 8: Function schemas + instrument
- [ ] Phase 9: Provider (schema inference)
- [ ] Phase 10: Docs + full sweep
