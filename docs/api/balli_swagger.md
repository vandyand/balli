# `balli.swagger`

Swagger/OpenAPI 2.0 export helpers built on balli.json-schema.

## `schema`

Kind: `defn`

Return a Swagger 2.0-compatible schema object. Balli's JSON Schema export already uses top-level definitions and #/definitions refs, which Swagger 2 accepts for schema definitions.

## `swagger`

Kind: `defn`

Build a minimal Swagger 2.0 document. opts: :info string-keyed info map, default {\

## `parameter`

Kind: `defn`

Swagger 2 parameter object. For body parameters, puts schema under \

## `response`

Kind: `defn`

Swagger 2 response object for schema `s`.
