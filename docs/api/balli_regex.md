# `balli.regex`

## `item-validator`

Kind: `defn`

Consume one element iff `valid?` accepts it.

## `item-explainer`

Kind: `defn`

Consume one element via compiled child explainer `ef` (fn [x path in] -> error vector). `rel-path` is this child's schema path relative to the seqex root (absolute paths only exist at runtime); `form` is the child's original form for :balli.core/end-of-input errors.

## `item-parser`

Kind: `defn`

Consume one element via child parser `pf` (value -> parsed | :balli.core/invalid); k receives the parsed value.

## `cat*`

Kind: `defn`

Catenation: children run left to right, each feeding the next its position. Empty -> epsilon.

## `alt*`

Kind: `defn`

Ordered choice with backtracking: both alternatives are parked, the preferred one LAST so it pops (LIFO) first.

## `opt*`

Kind: `defn`

? -- greedy option: child preferred over epsilon.

## `star*`

Kind: `defn`

* -- greedy Kleene star: epsilon fallback parked first, then the child runs; each successful child iteration parks the loop continuation (memoized on (id, pos, regs), which is what terminates nullable children).

## `plus*`

Kind: `defn`

+ = cat(child, *(child)).

## `repeat*`

Kind: `defn`

{min,max} counted repetition. Pushes a fresh counter onto regs on entry (regs snapshots into the memo key, so different iteration counts never alias). Compulsory iterations (< count min) park noncaching trampolining steps; optional iterations park an epsilon fallback plus the increment step. The (<= count pos) guard bails out of optional looping when the child consumes nothing (nullable-child infinite-loop prevention, per semantics section F). `mx` may be infinite (python float inf).

## `pure-parser`

Kind: `defn`

Match nothing, produce `v`.

## `fmap-parser`

Kind: `defn`

Map `f` over `p`'s parse result.

## `cat-parser`

Kind: `defn`

Catenation producing a vector of child parse results.

## `catn-parser`

Kind: `defn`

Catenation producing (->tags {tag parsed}). `entries` is [[tag parser] ...]; `->tags` is balli's Tags constructor, passed in to avoid a cyclic require.

## `alt-parser`

Kind: `defn`

Ordered choice; the matched branch's parse result passes through untagged.

## `altn-parser`

Kind: `defn`

Ordered choice producing (->tag branch-tag parsed). `entries` is [[tag parser] ...].

## `opt-parser`

Kind: `defn`

? -- child's parse result, or nil when the child does not match.

## `star-parser`

Kind: `defn`

* -- vector of child parse results (greedy).

## `plus-parser`

Kind: `defn`

+ -- non-empty vector of child parse results.

## `repeat-parser`

Kind: `defn`

{min,max} repetition producing a vector of child parse results. Same structure (and nullable-child guard) as repeat*.

## `validator`

Kind: `defn`

Wrap combinator `p` into a 1-arg boolean validator over whole sequential inputs (non-sequential -> false; trailing elements -> false).

## `explainer`

Kind: `defn`

Wrap explainer combinator `p` into a compile-layer explainer fn [x path in] -> error vector (empty when valid). `form` is the seqex root's original form. Non-sequential input -> a single :balli.core/invalid-type error; failed runs report the errors recorded at the furthest position reached (trailing input fails as :balli.core/input-remaining via the end matcher).

## `parser`

Kind: `defn`

Wrap parser combinator `p` into a 1-arg parser: sequential input -> parse shape | :balli.core/invalid (also on non-sequential input or unconsumed trailing elements).

## `item-unparser`

Kind: `defn`

Unparse one element via child unparser `uf`; wraps the result in a 1-element vector for splicing.

## `cat-unparser`

Kind: `defn`

Parse shape: vector of exactly (count ups) child results.

## `catn-unparser`

Kind: `defn`

Parse shape: Tags whose :values has exactly the declared tags. `entries` is [[tag unparser] ...] in declared order (Tags value maps are unordered); `tags?` is balli's Tags predicate, passed in to avoid a cyclic require.

## `alt-unparser`

Kind: `defn`

First branch whose unparse is valid.

## `altn-unparser`

Kind: `defn`

Parse shape: Tag with a declared :key; unparses :value via that branch. `tag?` is balli's Tag predicate.

## `opt-unparser`

Kind: `defn`

Parse shape: child value or nil. Child-first (so a child that itself accepts nil round-trips); a nil the child rejects unparses to [].

## `star-unparser`

Kind: `defn`

Parse shape: vector (any repetition count).

## `plus-unparser`

Kind: `defn`

Parse shape: vector of >= 1 repetitions.

## `repeat-unparser`

Kind: `defn`

Parse shape: vector of min..max repetitions (repetition count, not element count -- child splices may be multi-element).
