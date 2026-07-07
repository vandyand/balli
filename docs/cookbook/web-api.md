# Web API Validation

Use Balli at request boundaries to decode JSON-like data, validate the decoded
shape, and return humanized errors.

```clojure
(require '[balli.core :as b])
(require '[balli.error :as be])
(require '[balli.transform :as bt])

(def request-schema
  [:map
   [:user/id :uuid]
   [:limit [:int {:min 1 :max 100}]]
   [:tags {:optional true} [:set :keyword]]])

(def raw-request
  {:user/id "4283fefc-63f0-cd0e-873a-0000c6d07ef7"
   :limit "25"
   :tags ["new" "paid"]})

(def decoded
  (b/decode request-schema raw-request
            (bt/transformer (bt/json-transformer)
                            (bt/string-transformer)
                            (bt/collection-transformer))))

(if (b/validate request-schema decoded)
  decoded
  {:status 400
   :errors (be/humanize (b/explain request-schema decoded))})
```

The same flow is available as a runnable example:

```bash
basilisp run examples/web_request_validation.lpy
```
