# Balli MVP - Research

## Problem Statement

Basilisp (Clojure-on-Python, v0.5.0) has no Malli equivalent — no data-driven schema/validation library. Projects like stevetrading-basilisp validate ad-hoc or not at all. **Balli** is a Malli-inspired schema library for Basilisp: schemas as plain data (Malli vector syntax), compiled validators, structured explain data, humanized errors, and a registry with refs.

Goal framing (from `docs/basilisp balli from malli.md`): "Malli-shaped, not byte-for-byte parity." Preserve the Malli mental model — data-first schemas, `validate`/`explain`/`humanize` — implemented natively in Basilisp with no external Python dependencies for the MVP.

This is a **greenfield library** in a fresh repo (`/home/kingjames/balli`, branch `balli-mvp`, git identity `vandyand`).

## Codebase Context

The repo contains only `docs/basilisp balli from malli.md` (the full design conversation). Everything else is net-new. Conventions are imported from two reference codebases:

### Basilisp project conventions (from `~/contracting/upwork/steven-tran/stevetrading-basilisp/`)

- **pyproject.toml**: setuptools build; `dependencies = ["basilisp==0.5.x", "pytest>=8.0"]`; `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `pythonpath` listing source roots.
- **basilisp.edn**: empty map `{}` at repo root (marks root for tooling).
- **Namespace↔path mapping**: `balli.core` → `src/balli/core.lpy` (dashes in ns become underscores in path).
- **Tests**: plain pytest discovery of `tests/test_*.lpy`; basilisp registers itself as a pytest plugin. Test ns form: `(ns tests.balli.test-core (:require [basilisp.test :refer [deftest is testing]] [balli.core :as b]))`. Run via `basilisp test` (a pytest wrapper — use it, not raw pytest, to avoid stale importer/cache issues).
- **Lint substitute**: no clj-kondo; reference repo uses a compile-check script that imports every `.lpy` namespace via importlib. We replicate: `scripts/compile_check.lpy`.
- **Interop idioms**: `(:import re datetime)` with plain Python module names; `python/isinstance`; `(throw (ex-info "msg" {...}))` (works — verified); `(catch python/Exception e ...)`; kwargs via `**` marker.

### Real-world Malli usage (from `~/ascolais`, a Clojure polylith using metosin/malli)

Feature frequency in production code — this calibrates MVP scope:

- **Heavy**: closed maps `[:map {:closed true} ...]` (near-universal), `:enum`, `[:= :literal]` discriminators, `[:multi {:dispatch :kind} ...]`, `{:optional true}` entries, `m/validate` + `m/explain` + `me/humanize`, `ex-info` carrying `:explain` payloads.
- **Moderate**: `[:maybe ...]`, `[:tuple ...]`, `[:or ...]`, `[:map-of :keyword fn?]`, `[:fn {:error/message "..."} pred]`, int bounds `[:int {:min 1 :max 5}]`, `mu/merge`.
- **Rare**: transformers (only `mt/default-value-transformer` via `m/decode` once). No custom malli registry usage found.

Implication: `:multi`, `:map-of`, `:fn` with `:error/message`, and humanize are **must-haves** (they appear constantly in real code); transformers are a stretch goal; JSON Schema export / generators / sequence schemas are out of scope.

## REPL Findings

Live probes against Basilisp 0.5.0 (`basilisp run -c ...`):

| Probe | Result | Implication |
|---|---|---|
| `(int? true)` | `false` | Basilisp already excludes bool from int — no manual bool-guard needed (unlike raw Python where `bool ⊂ int`) |
| `(vector? (python/list [1 2]))` | `false` | Basilisp predicates reject host Python collections. MVP validates **Basilisp data structures** (as Malli validates Clojure data). Python dict/list acceptance deferred. |
| `(map? (python/dict))` | `false` | same |
| `(float? 1)` | `false` | int/float are distinct — `:float` won't accept ints (Malli's `:double` accepts ints on JVM only via `:double` semantics; we keep strict) |
| defmulti/defmethod dispatch on `(if (keyword? form) form (first form))` | works | normalize can be multimethod-based per design doc |
| `(transient [])` + `conj!`/`persistent!` | works | explain error accumulation can use transients |
| `(throw (ex-info "bad" {:a 1}))` → `(catch python/Exception e (ex-data e))` | returns `{:a 1}` | coerce-or-throw uses idiomatic ex-info |
| `(re-matches #"a+" "aaa")` | works | `:re` schema / `:string` pattern property viable with native regex |
| `meta`/`with-meta`, `atom`, qualified keywords, `uuid?`, `random-uuid` | all work | registry cache in atom; `:uuid` schema viable |
| `sorted-map` | **does not exist** | avoid; use plain maps |
| `java.time.Instant` | N/A (Python host) | use Python `datetime` module for any time schemas — deferred past MVP anyway |

## Requirements

### Functional Requirements

1. **Schema forms** (Malli vector syntax, canonical): `:any`, `:nil`, `:string`, `:int`, `:float`, `:number`, `:boolean`, `:keyword`, `:symbol`, `:uuid`, `:map`, `:map-of`, `:vector`, `:sequential`, `:set`, `:tuple`, `:enum`, `:=`, `:maybe`, `:and`, `:or`, `:not`, `:fn`, `:multi`, `:re`, `:ref`.
2. **Properties**: optional second element map — `[:string {:min 1 :max 10}]`, `[:map {:closed true} ...]`, `[:int {:min 0}]`, map entries `[:age {:optional true} :int]`, `[:fn {:error/message "..."} pred]`, `[:multi {:dispatch :kind} ...]`.
3. **Core API** (`balli.core`): `schema`, `schema?`, `form`, `properties`, `children`, `validate`, `validator`, `explain`, `explainer`, `assert-valid` (aka `coerce`-without-transform: returns value or throws ex-info with explain data).
4. **Explain data** shaped like Malli: `{:schema <form> :value <input> :errors [{:path [...] :in [...] :schema <form> :value <failing> :type :balli.core/...}]}`; `explain` returns `nil` on success.
5. **Humanize** (`balli.error/humanize`): explain map → human-readable nested structure mirroring the input shape (Malli `me/humanize` semantics), honoring `:error/message` property.
6. **Registry** (`balli.registry`): default registry of builtins; `registry` fn to layer custom schemas; `[:ref :user/id]` resolution; recursive refs must not infinite-loop at compile time (lazy compile through refs).
7. **Validator compilation**: `validator` returns a compiled fn (schema → closure tree, no interpretation per call); `validate` = `(validator s) value`. Compiled validators cached on schema objects.

### Non-Functional Requirements

- Pure Basilisp — no Python deps beyond stdlib (`re` for regex); no msgspec/pydantic in MVP.
- Installable package: `pyproject.toml`, `pip install -e .` works with `--break-system-packages`.
- Tests via `basilisp test` (pytest under the hood); every schema type has validate + explain + humanize coverage.
- Compile-check script imports all namespaces (lint substitute).
- README documenting API with examples, honest "Malli-inspired, subset" positioning.

## Options Considered

**A. Pure-Basilisp compiler (normalize → AST → compiled closures)** — the design doc's recommendation. Pros: idiomatic, schemas stay plain data, no host-boundary design questions, matches Malli architecture. Cons: slower than a Python hot path (irrelevant at MVP scale).

**B. Python compiler backend (`balli/compiler.py`)** — hot path in Python, API in Basilisp. Pros: faster. Cons: two-language maintenance, keyword/data marshaling complexity, premature optimization. Design doc's own final recommendation ("build correct Balli first, then fast Balli") rejects this for v0.

**C. Wrap an existing Python validator (msgspec/pydantic)** — rejected: their type-annotation models are not Malli-shaped; would dictate the schema model and kill the plain-data property.

## Recommendation

Option A. Namespaces:

- `src/balli/core.lpy` — public API (schema, validate, validator, explain, explainer, assert-valid, form, properties, children)
- `src/balli/registry.lpy` — builtin type table, custom registries, ref resolution
- `src/balli/normalize.lpy` — multimethod form→AST normalization
- `src/balli/compile.lpy` — AST→validator and AST→explainer compilers
- `src/balli/error.lpy` — humanize
- `tests/test_core.lpy`, `tests/test_explain.lpy`, `tests/test_error.lpy`, `tests/test_registry.lpy`

Error path/in semantics follow Malli: `:in` is the path into the *value*, `:path` is the path into the *schema form*. For MVP, map keys contribute the key to both; vector/set elements contribute index to `:in`.

## Open Questions

1. ~~Does `ex-info`/`ex-data` roundtrip through `catch python/Exception`?~~ **Resolved at REPL: yes.**
2. ~~Do transients work for error accumulation?~~ **Resolved at REPL: yes.**
3. `:multi` dispatch: support `{:dispatch <keyword-or-fn>}` — keyword dispatch covers all observed real usage; fn dispatch is a bonus. **Decision: support both (keyword called as fn on value; fn called directly), matching Malli.**
4. Closed-map default: Malli defaults **open**; ascolais usage is near-universally `{:closed true}` explicitly. **Decision: default open, honor `:closed true`** (Malli compatibility wins; explicitness observed in practice anyway).
5. `:float` vs `:double`: Malli has `:double`; Python has one float type. **Decision: support both `:float` and `:double` as aliases for Python float; `:number` accepts int or float.**
6. Should `validate` accept raw forms (uncompiled)? **Decision: yes — `validate`/`explain` accept both raw forms and schema objects, compiling (with cache) as needed, matching Malli.**

## References

- Design doc: `docs/basilisp balli from malli.md` (architecture, API sketch, tier ordering, difficulty analysis)
- Malli: https://github.com/metosin/malli (API semantics reference)
- Basilisp test conventions: `~/contracting/upwork/steven-tran/stevetrading-basilisp/tests/test_toolchain.lpy`, `scripts/test.sh`, `scripts/compile_check.lpy`, `pyproject.toml`
- Real Malli usage: `~/ascolais/agents/ideation-cog/src/ideation_cog/brief_schema.clj`, `~/ascolais/bases/pixel-world/src/ascolais/pixel_world/interface.clj`, `~/ascolais/components/clojure-cog/src/ascolais/clojure_cog/config.clj`
- Basilisp docs: https://basilisp.readthedocs.io/ (pyinterop, concepts)

## North-Star Orientation

No north-star doc exists (standalone root spec in a fresh repo). Parent goal is the `/goal` invocation: "Make balli - malli for basilisp," grounded in the docs/ design conversation.
