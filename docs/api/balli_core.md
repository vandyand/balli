# `balli.core`

Public API for balli - Malli for Basilisp. Schemas are plain data (Malli vector syntax). `schema` wraps a form into a schema object {:balli/schema true :form ... :ast ... :registry ... :cache (atom {})}; `validator`/`validate` accept either a raw form or a schema object. Compiled validators/explainers are cached: on the schema object's :cache atom, or (for raw forms) in a bounded global cache keyed by [form registry-id], where registry-id is an identity token assigned per registry map (default registry = token 0). The raw cache records the balli.registry/mutation-epoch it was filled under and clears itself when the default registry is mutated (register!/set-default-registry!), so raw forms always compile against the live default; schema objects keep their construction-time registry snapshot.

## `version`

Kind: `def`

0.6.0

## `schema?`

Kind: `defn`

True when `x` is a balli schema object.

## `schema`

Kind: `defn`

Wrap schema `form` into a schema object. `opts` supports {:registry r} (defaults to the CURRENT default registry) and {:balli.core/function-checker chk} -- a function checker (see balli.generator/function-checker) BAKED into the object at construction: every validator/explainer compiled for this object checks :=>/:function generatively. Passing an existing schema object returns it unchanged (its baked-in registry AND checker win; opts are ignored). Snapshot semantics: schema objects bake their registry at construction — mutating the default registry (balli.registry/register! / set-default-registry!) does NOT affect existing schema objects; raw-form calls always see the live default.

## `form`

Kind: `defn`

The original schema form of `s` (raw form or schema object).

## `ast`

Kind: `defn`

Return a Malli-style map syntax view of `s`'s normalized schema AST.

## `from-ast`

Kind: `defn`

Create a schema object from Malli-style map syntax / schema AST `a`.

## `properties`

Kind: `defn`

The properties map of the root of `s` (raw form or schema object).

## `children`

Kind: `defn`

The AST children of the root of `s` (raw form or schema object).

## `validator`

Kind: `defn`

Compiled 1-arg boolean validator for `s` (raw form or schema object). `opts` supports {:registry r} and {:balli.core/function-checker chk}, and is ignored when `s` is already a schema object (its baked-in registry and checker win). Raw-form calls whose opts carry a checker BYPASS the global raw-form cache entirely -- compiled fresh per call, so checked and plain compilations of the same form never poison each other; hoist `(schema form {::function-checker chk})` into a def for hot paths.

## `explainer`

Kind: `defn`

Compiled 1-arg explainer for `s` (raw form or schema object): returns nil on success, else {:schema <original form> :value <input> :errors [...]} where each error is {:path :in :schema <form fragment> :value :type}. `opts` supports {:registry r} and {:balli.core/function-checker chk}, and is ignored when `s` is already a schema object. Cached like `validator` (incl. the checker raw-cache bypass -- see `validator`).

## `validate`

Kind: `defn`

Validate `value` against `s` (raw form or schema object). Returns boolean. `opts` supports {:registry r} and is ignored when `s` is a schema object.

## `explain`

Kind: `defn`

Explain why `value` fails `s` (raw form or schema object). Returns nil when valid, else {:schema <original form> :value <input> :errors [...]}. `opts` supports {:registry r} and is ignored when `s` is a schema object.

## `decoder`

Kind: `defn`

Compiled 1-arg decode fn for `s` (raw form or schema object) using transformer `t` (transformer object, chain-link map, 0-arg fn returning a transformer, or nil for identity). `opts` supports {:registry r} for raw forms (ignored when `s` is a schema object -- its baked-in registry wins).

## `encoder`

Kind: `defn`

Compiled 1-arg encode fn for `s` using transformer `t`. See `decoder`.

## `decode`

Kind: `defn`

Decode `value` against `s` with transformer `t`. Never throws on mismatching values -- coercions are lenient (unchanged on mismatch).

## `encode`

Kind: `defn`

Encode `value` against `s` with transformer `t`. Lenient like `decode`.

## `coercer`

Kind: `defn`

Fn that decodes with `t` then validates: returns the decoded value when valid, else throws ex-info {:type :balli.core/coercion :value <decoded> :schema <form> :explain <explain map>}.

## `coerce`

Kind: `defn`

One-shot `coercer`: decode `value` with `t`, return it when it validates against `s`, else throw ex-info {:type :balli.core/coercion ...}.

## `tag`

Kind: `defn`

Construct a Tag record {:key k :value v} -- the parse container for :orn/:multi (and, from Phase 6, :altn) branch results.

## `tag?`

Kind: `defn`

True when `x` is a Tag record.

## `tags`

Kind: `defn`

Construct a Tags record {:values m} -- the parse container for :catn (Phase 6).

## `tags?`

Kind: `defn`

True when `x` is a Tags record.

## `invalid?`

Kind: `defn`

True when `x` is the parse/unparse failure sentinel :balli.core/invalid. Compared with = rather than identical?: Basilisp keyword literals loaded from cached namespace bytecode are not globally interned, so keyword identity does not hold across modules (keyword = is a cheap name/ns compare and IS reliable).

## `parser`

Kind: `defn`

Compiled 1-arg parser for `s` (raw form or schema object): value -> parsed value | :balli.core/invalid. `opts` supports {:registry r} and is ignored when `s` is already a schema object. Cached like `validator` (schema-object cache under :parser, raw forms in the bounded global cache). An :and schema with two or more transforming children (:orn/:multi, directly or through refs) throws ex-info {:type :balli.core/invalid-schema} at compile time.

## `unparser`

Kind: `defn`

Compiled 1-arg unparser for `s` -- the exact inverse of `parser`: parsed value -> original value | :balli.core/invalid. Cached under :unparser. See `parser`.

## `parse`

Kind: `defn`

Parse `value` against `s`: the value itself for non-transforming schemas (validate-then-value), Tag records for :orn/:multi branches, or :balli.core/invalid on mismatch. `opts` supports {:registry r} and is ignored when `s` is a schema object.

## `unparse`

Kind: `defn`

Unparse `value` (a parse result) against `s` back into the original value, or :balli.core/invalid on mismatch. Exact inverse of `parse`.

## `walk`

Kind: `defn`

FORM-level postwalk over schema `s` (raw form or schema object). At every node — children first — the form is rebuilt from the walked children and `(f rebuilt-form path)` is called; f's return value replaces the node's form in its parent. Returns f's result at the root. `opts` supports {:registry r} for raw forms (ignored when `s` is a schema object). :map, :multi, :orn, :catn, and :altn entry value schemas are visited with (conj path key); indexed children (incl. :cat/:alt/:?/:*/:+/:repeat and :schema) with (conj path i); refs are not entered (leaf, form unchanged).

## `schema-walker`

Kind: `defn`

Adapt a 1-arg form->form fn `f` into a walk fn, so (walk s (schema-walker f)) mirrors Malli's (m/walk s (m/schema-walker f)). See the walk section comment for the full signature deviation note.

## `assert-valid`

Kind: `defn`

Return `value` when it validates against `s`, else throw ex-info \

## `function-info`

Kind: `defn`

Arity/shape info for a :=> schema `s` (raw form or schema object): {:min n :max m? :arity <n or :varargs> :input <form> :output <form> :guard <form?>} from regex-min-max on the input seqex. :max is absent (and :arity :varargs) when the input is unbounded; :arity is also :varargs for bounded-but-variable inputs (min < max, e.g. [:cat :int [:? :int]]). nil when `s` is not a :=> schema.

## `instrument`

Kind: `defn`

Wrap fn `f` with validation per `props`: {:schema s ;; :=> or :function (raw form or object) :scope #{:input :output} ;; default both :report (fn [type data] ..)} ;; default: throw ex-info Per call: arity check against the input seqex bounds (:balli.core/invalid-arity), argument-vector validation against the input seqex (:balli.core/invalid-input, with :explain data), the call, return validation (:balli.core/invalid-output), and -- when the :=> has a guard child -- [args ret] guard validation (:balli.core/invalid-guard). A :function schema dispatches on (count args) over its :=> children's regex-min-max ranges (bounded arities first, the varargs child as fallback); an argument count matching no child reports :balli.core/invalid-arity and then calls `f` unwrapped. `props` may also carry {:registry r} for raw-form schemas.
