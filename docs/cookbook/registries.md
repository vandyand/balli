# Registries

```clojure
(require '[balli.core :as b])
(require '[balli.registry :as reg])

(def registry
  (reg/registry {:user/id :uuid
                 :user/user [:map [:id :user/id] [:name :string]]}))

(b/validate :user/user {:id (random-uuid) :name "Ada"} {:registry registry})
;; => true
```

Use local registries when a schema should be self-contained:

```clojure
[:schema {:registry {:tree/node [:maybe [:map
                                         [:value :int]
                                         [:children [:vector [:ref :tree/node]]]]]}}
 :tree/node]
```
