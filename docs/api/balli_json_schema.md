# `balli.json-schema`

## `transform`

Kind: `defn`

Export schema `s` (raw form or schema object) as a JSON Schema: a string-keyed Basilisp map. `opts` supports {:registry r} for raw forms (ignored when `s` is a schema object). When any refs were reached, the top-level map carries \
