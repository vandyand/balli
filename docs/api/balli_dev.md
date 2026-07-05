# `balli.dev`

## `capture-fail!`

Kind: `defn`

Clear and start collecting instrumentation failures reported through this namespace's default reporter.

## `uncapture-fail!`

Kind: `defn`

_No docstring._

## `captured-failures`

Kind: `defn`

_No docstring._

## `register!`

Kind: `defn`

Register function atom `fn-atom` under `k` with function schema `schema`. opts are passed to balli.core/instrument.

## `unregister!`

Kind: `defn`

_No docstring._

## `registered`

Kind: `defn`

_No docstring._

## `start!`

Kind: `defn`

Instrument every registered function atom. Idempotent.

## `stop!`

Kind: `defn`

Restore every registered function atom to its original function.

## `running`

Kind: `defn`

_No docstring._
