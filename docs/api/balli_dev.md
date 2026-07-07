# `balli.dev`

Development-time instrumentation registry. Register atoms that hold functions, then start!/stop! wraps/restores them. This is explicit and Pythonic: Balli does not mutate namespace vars.

## `capture-fail!`

Kind: `defn`

Clear and start collecting instrumentation failures reported through this namespace's default reporter.

## `uncapture-fail!`

Kind: `defn`

Stop collecting failures and return the captured failure data.

## `captured-failures`

Kind: `defn`

Return the currently captured instrumentation failure data.

## `register!`

Kind: `defn`

Register function atom `fn-atom` under `k` with function schema `schema`. opts are passed to balli.core/instrument.

## `unregister!`

Kind: `defn`

Unregister instrumentation entry `k` and restore its original function.

## `registered`

Kind: `defn`

Return the set of registered instrumentation keys.

## `start!`

Kind: `defn`

Instrument every registered function atom. Idempotent.

## `stop!`

Kind: `defn`

Restore every registered function atom to its original function.

## `running`

Kind: `defn`

Return true when development instrumentation is currently active.
