# `balli.transform`

Value transformers (decode/encode) for balli, per Malli 0.20 semantics. A transformer is a plain map: {:balli/transformer true :id <int> ; identity token for caching in core :chain [{:name <kw> :decoders {type interceptor} :encoders {type interceptor} :default-decoder interceptor :default-encoder interceptor} ...]} An interceptor is one of: - a plain fn -> {:enter f} - {:enter f :leave g} -> as-is (either key optional) - {:compile (fn [ast opts] ..)} -> compiled per schema node, result normalized + merged (real fns, no eval) Per schema node the chain folds IN ORDER: enter composes in chain order, leave in reverse chain order (interceptor stack). Per link, the interceptor resolves by priority: schema prop {:decode {:string f}} -> qualified prop :decode/string -> per-type table -> :default-decoder/:default-encoder. `compile-transformer` compiles an AST + registry + transformer + method into a single 1-arg fn, or nil when the whole subtree has no transformations (nil collapses to identity at the API layer -- no identity-fn wrapping).

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

## `env-transformer`

Kind: `defn`

Preset for flat environment/config maps with string keys and string values: string keys decode to keywords, scalar values decode with string rules, and encode turns keyword keys back into names.

## `query-params-transformer`

Kind: `defn`

Preset for query/form parameter maps: string keys decode to keywords, string scalar values decode with string rules, and repeated/list values can be coerced into vectors or sets via collection rules.

## `json-api-transformer`

Kind: `defn`

Preset for JSON API request/response bodies. Decode strips undeclared map keys, decodes JSON-friendly scalar representations including time values, and coerces collection shapes. Encode applies the reverse scalar/time conversions and strips extra keys.
