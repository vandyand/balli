# Validation and Errors

```clojure
(require '[balli.core :as b])
(require '[balli.error :as be])

(def schema [:map [:id :int] [:name [:string {:min 1}]]])

(b/validate schema {:id 1 :name "Ada"})
;; => true

(be/humanize (b/explain schema {:id "1" :name ""}))
;; => {:id ["should be an integer"], :name ["should be at least 1 characters"]}
```

Use `b/assert-valid` at boundaries where invalid data should throw.
