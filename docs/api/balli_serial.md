# `balli.serial`

## `register-function!`

Kind: `defn`

Register function `f` under keyword `k`. Returns k.

## `unregister-function!`

Kind: `defn`

_No docstring._

## `clear-functions!`

Kind: `defn`

_No docstring._

## `serialize`

Kind: `defn`

Return EDN-friendly schema data. Registered functions become [:balli.fn/ref kw], regex patterns become [:balli.re/pattern source].

## `deserialize`

Kind: `defn`

Resolve data emitted by `serialize` back into a usable Balli schema.

## `write-string`

Kind: `defn`

_No docstring._

## `read-string`

Kind: `defn`

_No docstring._
