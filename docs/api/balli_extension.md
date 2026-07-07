# `balli.extension`

Custom schema type extension registry. Extension specs are maps keyed by a custom schema keyword: {:validate (fn [value props children] boolean) :generate (fn [node registry rnd size gen-child] value) :decode (fn [value props child-transformers] value) :encode (fn [value props child-transformers] value) :json-schema (fn [node child-json] string-keyed-map) :describe (fn [node child-descriptions] string) :message \"humanized default message\"} `children` passed to :validate are compiled child validator fns. Most simple extension types are leaf schemas and ignore them.

## `register-type!`

Kind: `defn`

Register custom schema type keyword `k` with extension `spec`. Returns k.

## `unregister-type!`

Kind: `defn`

Remove the custom schema type keyword `k` from the extension registry.

## `type-spec`

Kind: `defn`

Return the registered extension spec for custom schema type keyword `k`.

## `custom-type?`

Kind: `defn`

Return true when `k` is registered as a custom schema type.

## `clear-types!`

Kind: `defn`

Clear all custom schema type registrations.
