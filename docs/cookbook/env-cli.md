# Environment and CLI Config

Environment variables and CLI option maps usually arrive as string-keyed maps
with string values. `env-transformer` handles that boundary directly.

```clojure
(require '[balli.core :as b])
(require '[balli.transform :as bt])

(def env-schema
  [:map {:closed true}
   [:host [:string {:min 1}]]
   [:port [:int {:min 1 :max 65535}]]
   [:debug :boolean]])

(b/decode env-schema
          {"host" "localhost" "port" "8080" "debug" "false"}
          (bt/env-transformer))
;; => {:host "localhost" :port 8080 :debug false}
```

The schema can be reused for validation, humanized errors, and documentation.

```bash
basilisp run examples/env_config_validation.lpy
```
