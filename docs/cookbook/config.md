# Config Validation

Application and CLI config should usually be closed maps: unknown keys are
often misspellings, stale settings, or deployment mistakes.

```clojure
(require '[balli.core :as b])
(require '[balli.error :as be])

(def config-schema
  [:map {:closed true}
   [:host [:string {:min 1}]]
   [:port [:int {:min 1 :max 65535}]]
   [:debug {:optional true} :boolean]])

(def config
  {:host "localhost"
   :port 8080
   :debug false})

(if (b/validate config-schema config)
  config
  (throw (ex-info "Invalid config"
                  {:errors (be/humanize
                            (b/explain config-schema config))})))
```

Run the complete example with:

```bash
basilisp run examples/config_validation.lpy
```
