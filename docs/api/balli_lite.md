# `balli.lite`

Small data-spec-style schema shorthand. This is intentionally explicit: call `lite/schema` to turn plain data into Balli schema forms. Raw map literals remain invalid as ordinary schemas so `:=` and `:enum` keep unambiguous literal semantics.

## `form`

Kind: `defn`

Convert a lite schema into a Balli schema form. Rules: - plain maps become [:map [k schema] ...] - one-element vectors become homogeneous [:vector schema] - vectors with more than one element become [:tuple ...] - sets become [:enum ...] - everything else is already a schema form

## `schema`

Kind: `defn`

Create a Balli schema object from lite syntax.
