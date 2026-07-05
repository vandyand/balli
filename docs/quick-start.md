# Quick Start

```clojure
(require '[balli.core :as b])
(require '[balli.error :as be])

(def user-schema
  [:map
   [:id :uuid]
   [:email [:string {:min 3}]]
   [:age {:optional true} [:int {:min 0}]]])

(b/validate user-schema {:id (random-uuid) :email "ada@example.com"})
;; => true

(be/humanize (b/explain user-schema {:email ""}))
;; => {:id ["missing required key"], :email ["should be at least 3 characters"]}
```

Schemas are data. Store them in registries, pass them between namespaces, export
them, and use them to generate test values.
