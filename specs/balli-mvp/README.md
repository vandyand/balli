---
title: "Balli MVP — Malli-inspired schemas for Basilisp"
status: in-progress
date: 2026-07-04
priority: 10
---
# Balli MVP — Malli-inspired schemas for Basilisp

Balli is a data-driven schema library for Basilisp: schemas are plain data in Malli's vector syntax, compiled into validator/explainer closures, with Malli-shaped explain data, humanized errors, and a registry with refs. Pure Basilisp, no Python deps beyond stdlib. Positioning is honest: **Malli-inspired subset**, not byte-for-byte parity.

```clojure
(require '[balli.core :as b])

(b/validate [:map
             [:id :string]
             [:age {:optional true} [:int {:min 0}]]]
            {:id "abc" :age 3})
;; => true

(b/explain [:vector :int] [1 "x"])
;; => {:schema [:vector :int] :value [1 "x"]
;;     :errors [{:path [0] :in [1] :schema :int :value "x" :type :balli.core/invalid-type}]}

(require '[balli.error :as be])
(be/humanize (b/explain [:string {:min 3}] "ab"))
;; => ["should be at least 3 characters"]
```

See [research.md](research.md) for codebase context and REPL findings, and the [implementation plan](implementation-plan.md) for phased tasks.

## Scope

**In (MVP):** schema types `:any :nil :string :int :float :double :number :boolean :keyword :symbol :uuid :map :map-of :vector :sequential :set :tuple :enum := :maybe :and :or :not :fn :multi :re :ref`; properties (`:min`/`:max`, `:closed`, `:optional`, `:error/message`, `:dispatch`); core API (`schema`, `schema?`, `form`, `properties`, `children`, `validate`, `validator`, `explain`, `explainer`, `assert-valid`); Malli-shaped explain data; `balli.error/humanize`; default + custom registries; `:ref` incl. recursive.

**Out (post-MVP, per design doc tiers):** transformers (decode/encode/coerce), JSON Schema export, generators, sequence schemas (`:cat`/`:alt`/`:*`), function schemas, parsing/unparsing, spell-checking, schema inference, Python dict/list acceptance, msgspec acceleration.

## Key Decisions

| Decision | Choice | Alternative rejected | Why |
|---|---|---|---|
| Architecture | Pure-Basilisp normalize→AST→compiled-closures | Python compiler backend; wrapping msgspec/pydantic | Design doc: "correct Balli first, then fast Balli"; plain-data schemas are the product |
| Validated data | Basilisp data structures only | Also accepting Python dict/list | Verified at REPL: Basilisp predicates reject host collections; Malli validates Clojure data — same stance. Interop layer is post-MVP |
| Map default | Open; `{:closed true}` opts in | Closed by default | Malli compatibility; real usage (ascolais) writes `:closed true` explicitly anyway |
| `:float`/`:double` | Aliases for Python float; `:number` = int or float | Strict `:double` only | Python has one float type; verified `(float? 1)` → false |
| `:multi` dispatch | Keyword or fn `{:dispatch ...}` | Keyword only | Matches Malli; fn dispatch is cheap once keyword works |
| Raw forms in API | `validate`/`explain` accept forms or schema objects, compile+cache on demand | Require explicit `schema` call | Matches Malli ergonomics |
| Error semantics | `:path` into schema form, `:in` into value | Single path | Malli parity — downstream humanize depends on `:in` |
| Test runner | `basilisp test` (pytest wrapper), `tests/test_*.lpy` | Raw pytest | Reference repo warns raw pytest hits stale importer caches |
| Lint | `scripts/compile_check.lpy` imports every ns | None | No clj-kondo for Basilisp; compile-check is the reference-repo pattern |
| Git identity | `vandyand` | venturevd / avd-lockbox | User directive 2026-07-04 |

## Implementation Status

- [x] Phase 0: Project scaffold + toolchain spike
- [ ] Phase 1: Normalize + builtin registry (form → AST)
- [ ] Phase 2: Validator compiler + public core API
- [ ] Phase 3: Explainer + explain data + assert-valid
- [ ] Phase 4: Humanize
- [ ] Phase 5: Custom registries, :ref, recursion, caching
- [ ] Phase 6: Docs, compile-check, packaging polish
