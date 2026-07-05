# Function Instrumentation

```clojure
(require '[balli.core :as b])

(def schema [:=> [:cat :int] :int])
(def checked-inc (b/instrument inc schema))

(checked-inc 1)
;; => 2
```

Function schemas validate arity, inputs, outputs, and optional guards.
