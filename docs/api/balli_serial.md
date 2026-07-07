# `balli.serial`

Safe schema serialization helpers. Balli does not eval serialized code. Register functions by keyword, then `serialize` replaces function values with [:balli.fn/ref kw]. `deserialize` rehydrates those references from the same registry.

## `register-function!`

Kind: `defn`

Register function `f` under keyword `k`. Returns k.

## `unregister-function!`

Kind: `defn`

Remove function registry entry `k`.

## `clear-functions!`

Kind: `defn`

Clear every registered serialization function reference.

## `serialize`

Kind: `defn`

Return EDN-friendly schema data. Registered functions become [:balli.fn/ref kw], regex patterns become [:balli.re/pattern source].

## `deserialize`

Kind: `defn`

Resolve data emitted by `serialize` back into a usable Balli schema.

## `write-string`

Kind: `defn`

Serialize `schema` to an EDN string without evaluating code.

## `read-string`

Kind: `defn`

Read an EDN string written by `write-string` back into schema data.
