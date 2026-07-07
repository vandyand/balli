# JSON API Handlers

`json-api-transformer` is a request/response preset for JSON API-style data.
It strips undeclared map keys, decodes JSON-friendly scalar representations,
decodes time values, and coerces collection shapes.

```clojure
(require '[balli.core :as b])
(require '[balli.error :as be])
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
             :roles ["admin" "user"]
             :ignored "dropped"}
            (bt/json-api-transformer)))

(if (b/validate user-schema decoded)
  {:status 200 :body decoded}
  {:status 400 :errors (be/humanize (b/explain user-schema decoded))})
```

Run the complete example with:

```bash
basilisp run examples/json_api_handler.lpy
```
