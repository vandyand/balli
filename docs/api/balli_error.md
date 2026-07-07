# `balli.error`

Humanized error messages for balli explain maps. (humanize explain-map) turns the output of balli.core/explain into a human-readable structure mirroring the shape of the value (Malli semantics): - nil (valid input) -> nil - root-level errors (:in []) -> flat vector of messages - map keys in :in -> nested maps {:x [\"msg\"]} - integer indices in :in -> sparse vectors [nil [\"msg\"]] - multiple errors at one :in -> accumulate into a single vector Messages come from schema :error/fn, schema :error/messages, schema :error/message, caller opts, locale defaults, and a default table keyed by error :type, with :min/:max interpolation for :balli.core/limits. (with-spell-checking explain-map) is an opt-in pre-humanize rewrite that turns extra-key / invalid-dispatch-value errors caused by likely typos into :balli.error/misspelled-key / :balli.error/misspelled-value errors (levenshtein distance vs the declared keys) and drops the missing-key errors those typos explain.

## `levenshtein`

Kind: `defn`

Levenshtein edit distance between (str a) and (str b). Iterative full-matrix dynamic programming (row by row) — no recursion.

## `with-spell-checking`

Kind: `defn`

Rewrite an explain map's :errors with key/value spell-checking: - :balli.core/extra-key within threshold of an absent declared key -> :balli.error/misspelled-key + :balli.error/likely-misspelling-of (vector of value paths to the likely intended keys, best match first) - :balli.core/invalid-dispatch-value on a keyword-dispatch :multi -> :balli.error/misspelled-value + :balli.error/likely-misspelling-of - :balli.core/missing-key errors whose :in is a likely-misspelling target are dropped (the key isn't missing — it's misspelled). nil (valid input) passes through; explain maps with no matching errors are returned unchanged.

## `humanize`

Kind: `defn`

Turn an explain map (from balli.core/explain) into a human-readable structure mirroring the value shape. nil in -> nil out. When a level has both its own errors and nested child errors (e.g. a collection :min violation alongside a bad element), the level renders as a map and its own messages live under the reserved :balli/error key. Options: :locale locale keyword for built-in and schema :error/messages :messages map of error type -> caller override message :format-message (fn [message error opts] message') post-processor.
