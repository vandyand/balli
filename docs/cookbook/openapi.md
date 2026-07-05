# OpenAPI and JSON Schema

```clojure
(require '[balli.json-schema :as json-schema])
(require '[balli.openapi :as openapi])

(def user [:map [:id :uuid] [:name :string]])

(json-schema/transform user)
;; => {"type" "object", ...}

(openapi/schema user)
;; => OpenAPI-compatible schema data
```

Use exported schemas for documentation, contracts, and generated clients.
