# Query Parameters

Query and form parameters often combine string keys, string scalar values, and
repeated values. `query-params-transformer` composes key decoding, string
scalar decoding, and collection coercion.

```clojure
(require '[balli.core :as b])
(require '[balli.transform :as bt])

(def query-schema
  [:map {:closed true}
   [:limit [:int {:min 1 :max 100}]]
   [:tags {:optional true} [:set :keyword]]
   [:q {:optional true} :string]])

(b/decode query-schema
          {"limit" "25" "tags" ["new" "paid"] "q" "balli"}
          (bt/query-params-transformer))
;; => {:limit 25 :tags #{:new :paid} :q "balli"}
```

Run the complete example with:

```bash
basilisp run examples/query_params_validation.lpy
```
