# Generation and Testing

```clojure
(require '[balli.generator :as bg])

(def schema [:map [:id :uuid] [:n [:int {:min 0 :max 9}]]])

(bg/generate schema {:seed 1})
;; => deterministic value

(bg/sample schema {:seed 1 :n 3})
;; => three deterministic examples
```

Use explicit seeds in tests so failures are reproducible.
