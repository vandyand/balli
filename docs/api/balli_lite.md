# `balli.lite`

## `form`

Kind: `defn`

Convert a lite schema into a Balli schema form. Rules: - plain maps become [:map [k schema] ...] - one-element vectors become homogeneous [:vector schema] - vectors with more than one element become [:tuple ...] - sets become [:enum ...] - everything else is already a schema form

## `schema`

Kind: `defn`

Create a Balli schema object from lite syntax.
