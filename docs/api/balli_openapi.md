# `balli.openapi`

OpenAPI 3 export helpers built on balli.json-schema. `schema` exports a Balli schema as an OpenAPI Schema Object, moving JSON Schema definitions under components/schemas and rewriting refs. `openapi` wraps schemas into a minimal OpenAPI document.

## `schema`

Kind: `defn`

Return an OpenAPI 3 schema object. Reached refs are emitted under {\

## `openapi`

Kind: `defn`

Build a minimal OpenAPI 3.1 document. opts: :info string-keyed info map, default {\

## `request-body`

Kind: `defn`

OpenAPI requestBody object for schema `s`.

## `response`

Kind: `defn`

OpenAPI response object for schema `s`.

## `parameter`

Kind: `defn`

OpenAPI parameter object for a scalar schema.
