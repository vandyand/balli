# Balli MVP — Implementation Plan

## Overview

Seven phases building a Malli-inspired schema library for Basilisp, in dependency order: toolchain → normalize → validate → explain → humanize → registry/refs → docs. Each phase lands with narrow tests green (`basilisp test tests/<file>`) and live checkpoints verified via `basilisp run -c`.

**Verification protocol (all phases):** checkpoints below are Basilisp expressions run as `basilisp run -c '<expr>'` from the repo root (with `pip install -e .` done in Phase 0, or `PYTHONPATH=src`). Expected values are stated with each checkpoint. Narrow test commands are per-phase; the full `basilisp test` sweep is the completion-preflight gate, not inner-loop.

## Prerequisites

- Basilisp 0.5.0 installed (verified: `basilisp version` → 0.5.0)
- `pip install --break-system-packages` required on this system
- Git identity: vandyand (configured)

## Phase 0: Project scaffold + toolchain spike

Goal: an installable, testable, empty-but-real Basilisp library. Proves the toolchain before any schema code.

- [ ] Create `pyproject.toml`: setuptools build, name `balli`, version `0.1.0`, `dependencies = ["basilisp>=0.5.0"]`, optional dev extra with `pytest>=8.0`; `[tool.pytest.ini_options]` with `testpaths = ["tests"]`; package dir `src/` layout (`[tool.setuptools.packages.find] where = ["src"]` — note: `.lpy` files need `[tool.setuptools.package-data] balli = ["*.lpy"]`)
- [ ] Create `basilisp.edn` containing `{}`
- [ ] Create `src/balli/core.lpy` stub: `(ns balli.core)` with `(def version "0.1.0")`
- [ ] Create `tests/test_toolchain.lpy`: `(ns tests.test-toolchain (:require [basilisp.test :refer [deftest is]] [balli.core :as b]))` with a trivial `(deftest smoke (is (= "0.1.0" b/version)))`
- [ ] Create `.gitignore` (`__pycache__/`, `*.lpyc`, `.venv/`, `*.egg-info/`, `dist/`)
- [ ] Install editable: `pip install -e . --break-system-packages` (if editable install fails to expose `.lpy` files, fall back to setting `pythonpath = ["src", "."]` in pytest config and document it)
- [ ] Verify test run: `basilisp test` → 1 passed

**Checkpoints:**
- `basilisp run -c '(require (quote [balli.core :as b])) (println b/version)'` → prints `0.1.0`
- `basilisp test` exits 0, `1 passed`

## Phase 1: Normalize + builtin registry (form → AST)

Goal: every MVP schema form normalizes to a uniform AST map `{:type <kw> :properties <map> :children <vector>}`.

- [ ] `src/balli/registry.lpy`: `(def builtin-types #{:any :nil :string :int :float :double :number :boolean :keyword :symbol :uuid :map :map-of :vector :sequential :set :tuple :enum := :maybe :and :or :not :fn :multi :re :ref})`; `default-registry` returns `{:types builtin-types :schemas {}}`; `registry` merges custom `{kw schema-form}` maps into `:schemas`; `resolve-ref` looks up `:schemas`
- [ ] `src/balli/normalize.lpy`: `normalize` multimethod dispatching on `(cond (keyword? form) form (vector? form) (first form) :else ::unknown)`
- [ ] Every AST node carries `:form` — the original schema-form fragment it was normalized from (Phase 3's explain errors report `:schema` as the original form, not the AST)
- [ ] Scalars (`:any :nil :string :int :float :double :number :boolean :keyword :symbol :uuid`): bare keyword or `[kw props]` → `{:type kw :properties props-or-{} :children []}`
- [ ] `:enum` / `:=`: children are the literal values (`:enum` optional props map as 2nd element must be distinguished from an enum value that is a map — rule: props map only counts when ≥1 further child follows, matching Malli)
- [ ] `:maybe :not :vector :sequential :set`: single child schema, optional props
- [ ] `:and :or :tuple`: N child schemas, optional props
- [ ] `:map`: entries `[k schema]` or `[k props schema]` → children `{:key k :properties props :schema <ast>}`; map-level props supported
- [ ] `:map-of`: exactly 2 children (key-schema, value-schema), optional props
- [ ] `:fn`: predicate fn stored as the single element of `:children`; props incl. `:error/message`. Both `[:fn pred]` and `[:fn {:error/message "..."} pred]` forms supported
- [ ] `:re`: child is a regex pattern or string (compile strings via `re-pattern`)
- [ ] `:multi`: props require `:dispatch`; children like map entries `[dispatch-value schema]` → `{:key v :schema <ast>}`
- [ ] `:ref`: `[:ref <kw>]` → `{:type :ref :ref <kw> :properties {} :children []}`
- [ ] Unknown form → `(throw (ex-info "Unknown schema" {:type :balli.core/invalid-schema :form form}))`
- [ ] Keywords registered in a custom registry normalize as refs to their registered schema
- [ ] `tests/test_normalize.lpy` covering every type + property placement + error on garbage

**Checkpoints:**
- `(normalize [:map [:id :string] [:age {:optional true} :int]] {})` → `{:type :map :properties {} :children [{:key :id :properties {} :schema {:type :string ...}} {:key :age :properties {:optional true} :schema {:type :int ...}}]}`
- `(normalize [:enum "A" "B"] {})` → children `["A" "B"]`
- `(normalize :string {})` → `{:type :string :properties {} :children []}`
- Narrow test: `basilisp test tests/test_normalize.lpy` green

## Phase 2: Validator compiler + public core API

Goal: `balli.core/validate` works for every MVP type with properties enforced.

- [ ] `src/balli/compile.lpy`: `compile-validator [ast registry]` → fn of one arg returning boolean. Case per `:type`:
  - scalars: predicate + `:min`/`:max` where applicable (`:string` length bounds, `:int`/`:float`/`:double`/`:number` value bounds)
  - `:nil` → `nil?`; `:any` → always true; `:float`/`:double` → `float?`; `:number` → int or float; `:uuid` → `uuid?`
  - `:enum` → membership set; `:=` → `=` to literal
  - `:maybe` → nil or child; `:not` → complement; `:and` → every; `:or` → some
  - `:vector`/`:sequential`/`:set` → coll predicate + every child valid + `:min`/`:max` count bounds
  - `:tuple` → vector? + exact count + positional children
  - `:map` → map? + required keys present + entry schemas + `:closed` extra-key rejection
  - `:map-of` → map? + every key/value pair valid
  - `:fn` → call pred, treat thrown exception as invalid (wrap in try/catch, Malli behavior)
  - `:re` → string? + `re-find` full-match via `re-matches`
  - `:multi` → dispatch (keyword as fn or fn) → child schema by dispatch value; unknown dispatch → invalid
  - `:ref` → resolve at compile time, lazily wrap (delay/promise or fn indirection) so recursion doesn't loop
- [ ] `src/balli/core.lpy`: `schema` (form+opts → schema map `{:balli/schema true :form ... :ast ... :registry ... :cache (atom {})}`), `schema?`, `form`, `properties`, `children`, `validator` (compiles + caches in schema's `:cache` atom), `validate` (accepts raw form or schema object)
- [ ] `tests/test_core.lpy`: validate happy/sad paths for every type, property bounds, closed maps, optional keys, nested structures, `:multi` with keyword dispatch

**Checkpoints:**
- `(b/validate [:map {:closed true} [:id :string]] {:id "x"})` → `true`; with `{:id "x" :extra 1}` → `false`
- `(b/validate [:tuple :string :int] ["a" 1])` → `true`; `["a" "b"]` → `false`
- `(b/validate [:multi {:dispatch :kind} [:dm [:map [:kind [:= :dm]] [:text :string]]]] {:kind :dm :text "hi"})` → `true`
- `(b/validate [:int {:min 1 :max 5}] 0)` → `false`
- `(let [v (b/validator [:vector :int])] [(v [1 2]) (v [1 "x"])])` → `[true false]`
- Narrow test: `basilisp test tests/test_core.lpy` green

## Phase 3: Explainer + explain data + assert-valid

Goal: Malli-shaped explain data with correct `:path`/`:in` for every type.

- [ ] `compile-explainer [ast registry]` in `compile.lpy`: fn `[value path in]` → vector of error maps `{:path :in :schema <original-sub-form> :value :type}`. Error `:schema` carries the **original form fragment** (store original form on AST nodes during normalize as `:form`), not the AST
- [ ] Error types: `:balli.core/invalid-type`, `:balli.core/missing-key`, `:balli.core/extra-key`, `:balli.core/invalid-dispatch-value`, `:balli.core/limits` (min/max violations), `:balli.core/enum-mismatch`, `:balli.core/not-eq`, `:balli.core/invalid` (generic, `:fn`/`:not`/`:or` failure)
- [ ] Path semantics: map entry → key appended to both `:path` and `:in`; vector/set/sequential element → index appended to `:in`, `0` to `:path`; tuple element → index to both; `:map-of` → key into `:in`; `:and`/`:or` branch index into `:path` only; `:maybe`/`:multi` child transparent in `:in`
- [ ] `:or` failure emits one error at the `:or` node (Malli emits per-branch errors; MVP: single `:balli.core/invalid` error at the node — documented simplification)
- [ ] Transients for error accumulation inside map/vector explainers (verified working at REPL)
- [ ] `balli.core/explainer` and `explain` (nil on success; `{:schema form :value value :errors [...]}` on failure), cached like validator
- [ ] `balli.core/assert-valid`: returns value or `(throw (ex-info "Validation failed" <explain-map-plus :type :balli.core/invalid-input>))`
- [ ] `tests/test_explain.lpy`: exact explain shapes for nested map/vector failures, missing/extra keys, multi dispatch miss, min/max, success → nil

**Checkpoints:**
- `(b/explain [:vector :int] [1 "x"])` → errors `[{:path [0] :in [1] :schema :int :value "x" :type :balli.core/invalid-type}]`
- `(b/explain [:map [:id :string]] {})` → one `:balli.core/missing-key` error with `:in [:id]`
- `(b/explain :string "ok")` → `nil`
- `(try (b/assert-valid :int "x") (catch python/Exception e (:type (ex-data e))))` → `:balli.core/invalid-input`
- Narrow test: `basilisp test tests/test_explain.lpy` green

## Phase 4: Humanize

Goal: `balli.error/humanize` turns explain maps into human-readable structures mirroring the value shape.

- [ ] `src/balli/error.lpy`: default message table keyed by error `:type` (with min/max interpolation, e.g. "should be at least 3 characters" for string `:limits`, "should be at least 1" for int); `:error/message` property on the failing schema overrides; unknown type → "invalid value"
- [ ] `humanize [explain-map]`: nil → nil; assemble nested output following each error's `:in` — map keys → nested maps, indices → sparse vectors (Malli semantics: `{:a ["error"]}`, `[nil ["error"]]`); root-level errors → flat vector of messages
- [ ] Multiple errors at same `:in` accumulate into one vector
- [ ] `tests/test_error.lpy`: root scalar failure, nested map, vector index, `:error/message` override, missing-key message "missing required key"

**Checkpoints:**
- `(be/humanize (b/explain [:string {:min 3}] "ab"))` → `["should be at least 3 characters"]`
- `(be/humanize (b/explain [:map [:x :int]] {:x "s"}))` → `{:x ["should be an integer"]}`
- `(be/humanize (b/explain [:fn {:error/message "must be even"} even?] 3))` → `["must be even"]`
- `(be/humanize nil)` → `nil`
- Narrow test: `basilisp test tests/test_error.lpy` green

## Phase 5: Custom registries, :ref, recursion, caching

Goal: registered schemas resolve by keyword, recursive schemas terminate, compiled fns are cached.

- [ ] `balli.registry/registry`: `(reg/registry {:user/id [:string {:min 1}] :user/address [:map ...]})` merged over defaults; passed via opts `{:registry r}` through `schema`/`validate`/`explain`
- [ ] Normalize: qualified keyword forms resolve against registry `:schemas` → `{:type :ref :ref kw}`; `[:ref kw]` same
- [ ] Compile: ref compilation is lazy (fn indirection through a compile-time cache atom keyed by ref kw) so self/mutually-recursive schemas (`:user/tree` referencing itself) compile and validate without stack overflow on finite data
- [ ] Unresolved ref at compile time → `(throw (ex-info "Unresolved ref" {:type :balli.core/unresolved-ref :ref kw}))` (fail fast, not fail-at-validate)
- [ ] Validator/explainer caching: schema objects cache compiled fns in their `:cache` atom; raw-form API calls compile through a bounded global cache atom in `balli.core` keyed by `[form registry-id]` (registry-id via `identical?`-based token; simplest correct thing — document)
- [ ] `tests/test_registry.lpy`: custom scalar ref, nested ref, recursive `[:maybe [:map [:children [:vector [:ref :tree/node]]]]]` validates a 3-level tree, unresolved ref throws, explain through refs keeps `:in` correct

**Checkpoints:**
- `(b/validate [:ref :user/id] "abc" {:registry (reg/registry {:user/id [:string {:min 1}]})})` → `true`
- Recursive tree schema validates `{:children [{:children []}]}` → `true`, and `{:children [{:children [42]}]}` → `false`
- `(try (b/validate [:ref :nope] 1) (catch python/Exception e (:type (ex-data e))))` → `:balli.core/unresolved-ref`
- Narrow test: `basilisp test tests/test_registry.lpy` green

## Phase 6: Docs, compile-check, packaging polish

Goal: usable open-source-shaped library.

- [ ] Root `README.md`: positioning ("Data-driven schemas for Basilisp — Malli-inspired"), install, quick start (validate/explain/humanize/registry examples, all copy-paste runnable), supported schema reference table, differences-from-Malli section (out-of-scope list, `:or` explain simplification, Basilisp-data-only), development section (test/lint commands)
- [ ] `scripts/compile_check.lpy`: import every ns under `src/` via importlib (reference-repo pattern); `scripts/test.sh` wrapper (`exec basilisp test "$@"`)
- [ ] Verify `pip install -e . --break-system-packages` from clean state ships `.lpy` files (import from a different cwd works)
- [ ] `LICENSE` (MIT, Andrew VanDyke)
- [ ] Full sweep: `basilisp test` all green; `basilisp run scripts/compile_check.lpy` exits 0

**Checkpoints:**
- `cd /tmp && basilisp run -c '(require (quote [balli.core :as b])) (println (b/validate [:map [:x :int]] {:x 1}))'` → `true` (proves install works outside repo cwd)
- `basilisp run scripts/compile_check.lpy` → exits 0, lists all namespaces OK
- `basilisp test` → all tests pass

## Verification

Full-suite gate at completion: `basilisp test` (all files) + `basilisp run scripts/compile_check.lpy`. Both must exit 0 before PR.

## Rollback

Greenfield repo — rollback is `git revert`/branch deletion; no external systems touched.
