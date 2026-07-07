# `balli.integrations`

Python ecosystem adapters for Balli schemas. These helpers keep Balli's core plain-data model while making common Python boundaries easier to validate.

## `annotation-schema`

Kind: `defn`

Best-effort Balli schema for a Python type annotation.

## `dataclass-schema`

Kind: `defn`

Infer a closed Balli :map schema from a Python dataclass class.

## `validator`

Kind: `defn`

Return a Python-callable validator for schema `s`.

## `assert-valid`

Kind: `defn`

Validate `value` at a Python boundary and return it, throwing on failure.
