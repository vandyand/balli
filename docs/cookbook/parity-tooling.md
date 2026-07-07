# Parity Tooling

Balli includes Malli-style helper APIs for schema inference, coercion evidence,
schema surgery, generated checks, and static analysis. The runnable version of
this workflow lives in `examples/parity_tooling.lpy`.

```clojure
(require '[balli.core :as b])
(require '[balli.experimental :as exp])
(require '[balli.generator :as bg])
(require '[balli.provider :as bp])
(require '[balli.transform :as bt])
(require '[balli.util :as u])

(def samples
  [{:id 1 :name "Ada"}
   {:id 2}])

(def inferred
  (bp/provide-report samples {:closed-maps true
                              :optional-threshold 0.5}))

(def user-schema
  (-> (:schema inferred)
      (u/set-entry :active :boolean)
      (u/update-at [:id] (fn [s] [:and s [:>= 0]]))))

(def transformer
  (bt/transformer (bt/string-transformer)
                  (bt/collection-transformer)))

(b/coercion-report user-schema
                   {:id "7" :name "Grace" :active true}
                   transformer)

(bg/check user-schema user-schema {:iterations 10 :seed 42})

(exp/risk-report user-schema)

(u/diff (:schema inferred) user-schema)
```

Use these helpers when evolving schemas in application code:

- `provide-report` proves inferred schemas still validate all source samples.
- `coercion-report` gives decoded values and explain data without throwing.
- `path-map`, `update-at`, and `diff` make schema rewrites auditable.
- `check` and `check-roundtrip` give small property-check reports without a
  Clojure `test.check` runtime.
- `dependency-graph`, `migration-impact`, and `risk-report` are data-only
  analysis helpers for registries and schema reviews.
