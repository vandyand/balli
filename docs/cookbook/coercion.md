# Coercion and Transforms

```clojure
(require '[balli.core :as b])
(require '[balli.transform :as bt])

(def schema [:map [:age :int] [:tags [:set :keyword]]])

(b/decode schema
          {:age "42" :tags ["a" "b"]}
          (bt/string-transformer))
;; => {:age 42 :tags #{:a :b}}
```

Compose transformers when data crosses multiple representation boundaries.

```clojure
(bt/transformer (bt/json-transformer)
                (bt/time-transformer)
                (bt/string-transformer))
```

For common boundaries, use the named presets:

```clojure
(bt/env-transformer)          ;; environment/CLI config maps
(bt/query-params-transformer) ;; query/form parameter maps
(bt/json-api-transformer)     ;; JSON API request/response bodies
```
