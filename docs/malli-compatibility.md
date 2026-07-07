# Malli Compatibility Matrix

Balli is a Malli clone for Basilisp. This matrix tracks the major Malli feature
families Balli covers and calls out runtime or ecosystem differences where
Basilisp/Python diverge from Clojure/JVM.

| Area | Balli status |
|---|---|
| Vector syntax | Supported |
| Map syntax / schema AST | Supported via raw schema input, `balli.core/ast`, and `balli.core/from-ast` |
| Lite syntax | Supported explicitly via `balli.lite/form` and `balli.lite/schema` |
| Validation / explain / humanize | Supported |
| Spell checking and custom messages | Supported, including schema messages, locale maps, caller overrides, and global message formatting |
| Value transformation / coercion | Supported |
| Integration transformer presets | Supported for env/config maps, query params, and JSON API payloads |
| Parse / unparse | Supported |
| Sequence regex schemas | Supported |
| `:seqable` / `:every` | Supported, including bounded-prefix `:every` checks |
| Function schemas / instrumentation | Supported, including `:->`, `:=>`, and `:function` |
| Generative function checking | Supported |
| Value generation / sampling | Supported |
| Reusable generator objects | Supported via `balli.generator/generator` and `:gen/gen` |
| Shrinking | Heuristic Balli shrinker; not Clojure test.check shrinking |
| Provider inference | Supported |
| Provider closed-map inference | Supported via `{:closed-maps true}` |
| Destructuring | Supported via `balli.destructure` |
| Immutable/custom registries | Supported |
| Mutable default registry | Supported |
| Dynamic registry | Supported |
| Lazy registry | Supported |
| Local property registry | Supported |
| Var registry | Supported via derefable schema refs |
| JSON Schema export | Supported |
| OpenAPI / Swagger export | Supported |
| DOT / PlantUML visualization | Supported |
| English descriptions | Supported |
| `malli.util`-style map introspection | Supported via `entries`, `keys`, `required-key?`, and `optional-key?` |
| EDN schema persistence | Supported safely via named function refs |
| SCI integration | Data-only host context via `balli.sci`; no Clojure SCI runtime |
| clj-kondo / static analyzer integration | Data export via `balli.clj-kondo`; no Clojure analyzer runtime |
| `malli.experimental` | Not ported as executable Clojure experimental APIs |

## Compatibility Corpus Categories

The executable corpus in `tests/test_compatibility_corpus.lpy` uses three
working categories:

- **Supported**: behavior Balli implements and tests directly.
- **Intentionally different**: behavior Balli documents where Python/Basilisp
  semantics differ from JVM/Clojure, such as scalar type distinctions.
- **Not applicable**: Clojure runtime ecosystem APIs that do not have a direct
  Basilisp/Python equivalent, such as browser/ClojureScript integrations.

## Evidence

Compatibility claims are backed by CI tests where practical. See
[Compatibility Evidence](compatibility-evidence.md) and
`tests/test_compatibility_corpus.lpy` for the executable corpus.
