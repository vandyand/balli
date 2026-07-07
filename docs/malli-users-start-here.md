# Malli Users Start Here

Balli keeps Malli's schema-as-data workflow while adapting runtime details to
Basilisp and Python.

## Same Mental Model

Use plain data schemas:

```clojure
[:map
 [:id :uuid]
 [:name [:string {:min 1}]]
 [:roles [:set :keyword]]]
```

Validate, explain, transform, generate, and export from the same schema:

```clojure
(require '[balli.core :as b])
(require '[balli.error :as be])
(require '[balli.generator :as bg])
(require '[balli.openapi :as openapi])
(require '[balli.transform :as bt])

(def user-schema
  [:map {:closed true}
   [:id :uuid]
   [:name [:string {:min 1}]]
   [:roles [:set :keyword]]])

(def decoded
  (b/decode user-schema
            {:id "550e8400-e29b-41d4-a716-446655440000"
             :name "Ada"
             :roles ["admin"]}
            (bt/json-api-transformer)))

(b/validate user-schema decoded)
(be/humanize (b/explain user-schema decoded))
(bg/generate user-schema {:seed 1})
(openapi/schema user-schema)
```

## Common Mappings

| Malli idea | Balli entry point |
|---|---|
| `m/validate` | `balli.core/validate` |
| `m/explain` | `balli.core/explain` |
| `me/humanize` | `balli.error/humanize` |
| `m/decode` / `m/encode` | `balli.core/decode` / `balli.core/encode` |
| `mt/string-transformer` | `balli.transform/string-transformer` |
| `mt/json-transformer` | `balli.transform/json-transformer` |
| schema registry | `balli.registry/registry` |
| `malli.util` map helpers | `balli.util` |
| `malli.provider` | `balli.provider/provide` |
| JSON Schema / OpenAPI | `balli.json-schema`, `balli.openapi`, `balli.swagger` |

## Python Boundary Presets

Balli adds presets for common Python-hosted boundaries:

- `env-transformer` for environment/CLI config maps
- `query-params-transformer` for query and form parameter maps
- `json-api-transformer` for JSON API request and response bodies

These are ordinary transformers, so they can still be composed with
`balli.transform/transformer` when a boundary needs custom behavior.

## Differences To Expect

- Balli is Basilisp/Python, not Clojure/JVM or ClojureScript.
- Python type predicates define scalar behavior. For example, Balli keeps int
  and float semantics aligned with Python/Basilisp.
- Safe schema serialization uses registered function references instead of
  evaluating serialized code.
- Some ecosystem integrations are examples or data exports rather than direct
  ports of Clojure libraries.

For a full matrix, see [Balli vs Malli](malli-comparison.md) and
[Malli Compatibility](malli-compatibility.md).
