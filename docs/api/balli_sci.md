# `balli.sci`

SCI-style namespace data for embedding Balli in restricted evaluators. Basilisp does not ship SCI, so this namespace exposes ordinary data maps of safe public Vars that a host can choose to install in its evaluator.

## `namespaces`

Kind: `def`

SCI namespace map exposing Balli public APIs.

## `sci-context`

Kind: `defn`

Return a simple context map suitable for host evaluators.
