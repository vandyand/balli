# `balli.transform`

## `transformer?`

Kind: `defn`

True when `x` is a balli transformer object.

## `into-transformer`

Kind: `defn`

Coerce `x` into a transformer object: nil -> nil, transformer -> itself, chain-link map -> single-link transformer, 0-arg callable -> its result.

## `transformer`

Kind: `defn`

Compose `ts` (chain-link maps, transformers, 0-arg fns returning transformers, or nils) into a single transformer by flattening every argument's chain, in order. Returns nil when the resulting chain is empty.

## `compile-transformer`

Kind: `defn`

Compile `ast` + `registry` + transformer `t` + `method` (:decode/:encode) into a single 1-arg fn, or nil when nothing transforms (identity). `opts` is passed through to {:compile ...} interceptors, augmented with the registry under :registry.

## `string-transformer`

Kind: `defn`

Decode scalars from strings (int/double/boolean/keyword/symbol/uuid/enum), sequentials into vectors/sets; encode scalars to strings (booleans excepted).

## `json-transformer`

Kind: `defn`

Assumes JSON-parsed input: NO string->number/boolean coercions. Decodes keyword/symbol/uuid from string, int from integral number, float/double from number, sets from sequentials; :map-of keys decode via string rules (JSON object keys are always strings).

## `time-transformer`

Kind: `defn`

Decode/encode :time/* schemas. Decoders are lenient: parse or type-policy misses return the original value unchanged. Compose explicitly with string/json transformers when desired.

## `strip-extra-keys-transformer`

Kind: `defn`

On :map -- dissoc keys not among the declared entry keys; applies when the :closed property is nil or true (NOT when explicitly {:closed false}), and NEVER when the map has a :balli.core/default entry (the default entry claims every undeclared key, so nothing is extra -- strip nothing). On :map-of -- keep only entries valid per the key AND value schemas (leave phase for decode, enter phase for encode, matching malli).

## `key-transformer`

Kind: `defn`

{:decode f :encode g :types <set-or-:default>} -- map keys transformed with f at decode enter, g at encode leave. Default types #{:map}; :types :default installs the key transforms as the chain link's default coders.

## `default-value-transformer`

Kind: `defn`

Every schema: nil replaced by the :default property (contains?-based lookup, so an explicit nil default counts) or (get defaults (:type ast)) applied to the ast. :map additionally fills MISSING non-optional keys whose entry properties or value-schema properties carry the default -- opt :add-optional-keys fills optional entries too. Applies on both decode and encode. Opts: {:key <prop-kw> :defaults {type (fn [ast] default)} :add-optional-keys <bool>}. Value-schema default wins over entry-props default (malli parity); a :ref value schema is dereffed for its default.

## `collection-transformer`

Kind: `defn`

Coerce between collection kinds: :vector/:tuple/:seqable/:every from sequential-or-set, :set from sequential, :sequential from vector/set. Both decode and encode.
