---
title: "Balli Tier 3 — self-contained schemas, defaults, time, predicates, mutable registry"
status: in-progress
date: 2026-07-04
priority: 10
---
# Balli Tier 3 — self-contained schemas, defaults, time, predicates, mutable registry

Five user-approved features closing the remaining practical Malli gaps, pinned against Malli 0.20.0 source ([malli-semantics.md](malli-semantics.md)):

```clojure
;; 1. Local registries — self-contained recursive schemas
(b/validate [:schema {:registry {::node [:maybe [:map [:kids [:vector [:ref ::node]]]]]}} ::node]
            {:kids [{:kids []}]})
;; 2. Default branches
(b/validate [:map [:x :int] [:balli.core/default [:map-of :keyword :string]]] {:x 1 :extra "ok"})
(b/validate [:multi {:dispatch :kind} [:a [:map [:kind [:= :a]]]] [:balli.core/default :map]] {:kind :other})
;; 3. Time schemas
(b/decode :time/instant "2024-06-01T12:00:00+00:00" (bt/time-transformer))
;; 4. Predicates + comparators
(b/validate [:map [:n pos-int?] [:cap [:<= 100]]] {:n 5 :cap 42})
;; 5. Mutable default registry
(reg/register! :user/email [:re #"^[^@]+@[^@]+$"])
(b/validate :user/email "a@b.c")
```

See [research.md](research.md) and the [implementation plan](implementation-plan.md).

## Key Decisions

| Decision | Choice | Alternative rejected | Why |
|---|---|---|---|
| §3 integration | Explicit `:time/*` builtins driven by a data table in `balli.time` | IntoSchema-style plugin API | Plugin API triples scope; the table can become one later |
| §1 ref-cache correctness | `[kw layer-token]` cache keys, token per layered registry | Fresh sub-cache per layer | Keeps eager-compile + recursion-guard pattern intact |
| §5 baked objects | Snapshot semantics documented; only raw-form cache invalidated on mutation | Invalidate schema objects | Matches existing "baked config wins" opts rule |
| Time subset | instant / local-date / local-time / local-date-time / duration | Full java.time surface | Python has one aware-datetime class; no stdlib Period |
| Duration ISO | Custom regex parser/formatter (stdlib has none) | External lib | Zero-dep rule |
| Predicate dispatch | Fn-identity table + quoted symbols, both registered | Symbols only | Balli forms evaluate `int?` to the fn before normalize sees it |

## Implementation Status

- [x] Phase 0: Spike (datetime ISO, predicate availability, fn-identity lookup)
- [x] Phase 1: Predicate + comparator schemas
- [x] Phase 2: Mutable + composite default registry
- [x] Phase 3: Local registries in schema properties
- [x] Phase 4: :balli.core/default branches (:map + :multi)
- [x] Phase 5: balli.time
- [x] Phase 6: Docs, 0.3.0, full sweep (3× PYTHONHASHSEED)
