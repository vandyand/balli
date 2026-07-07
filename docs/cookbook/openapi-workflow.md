# OpenAPI Export Workflow

Use one schema for runtime validation and API documentation. Keep the schema
near the handler or route definition, then export OpenAPI data from the same
source.

```clojure
(require '[balli.core :as b])
(require '[balli.openapi :as openapi])

(def user-schema
  [:map
   [:id :uuid]
   [:name [:string {:min 1}]]
   [:roles [:set :keyword]]])

(def user-response
  (openapi/response user-schema))

(b/validate user-schema {:id #uuid "4283fefc-63f0-cd0e-873a-0000c6d07ef7"
                         :name "Ada"
                         :roles #{:admin}}))
```

For a standalone export:

```bash
basilisp run examples/openapi_export.lpy
```

The lower-level JSON Schema exporter is available as
`balli.json-schema/transform` when a tool wants JSON Schema without an OpenAPI
wrapper.
