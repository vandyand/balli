# Balli vs Malli

Balli is Malli for Basilisp: a data-driven schema library that ports Malli's
schema syntax and core workflows into Python-hosted Basilisp code. It is not a
byte-for-byte copy of Malli's Clojure implementation; the differences below are
the places where Basilisp/Python runtime constraints or ecosystem maturity
change the shape of the library.

## What Balli Covers

Balli currently covers most user-facing schema workflows:

- validation and explain data
- humanized errors
- coercion, decoding, encoding, parsing, and unparsing
- map, collection, predicate, comparator, enum, ref, multi, and regex schemas
- function schemas, instrumentation, and generative checking
- deterministic generators and shrinking
- Balli-native generator objects and combinators
- JSON Schema, OpenAPI, Swagger, DOT, PlantUML, and description export
- schema walking, utility operations, and map-entry surgery
- custom registries, local registries, lazy/dynamic/var registries, and
  recursive references
- EDN-style safe serialization through registered function references
- custom extension types
- time schemas
- schema inference and destructuring helpers
- data-only experimental analysis helpers
- Python integration adapters and static schema inspection

## Remaining Differences

Some Malli ecosystem features are intentionally thinner in Balli:

- Malli's ClojureScript/browser ecosystem has no direct Basilisp equivalent.
- Malli's documentation site and community examples are more mature.
- Malli has broader downstream library integrations.
- Malli's advanced provider ecosystem and schema tooling are still deeper, but
  Balli now has provider knobs, static inspection, and data-only experimental
  analysis helpers.
- Balli's package ecosystem is younger because Basilisp's ecosystem is smaller.

## Practical Parity Target

The most important parity target is not copying every implementation detail. It
is making the common production path solid:

- install from PyPI
- learn from hosted docs and examples
- validate and transform data at API/config boundaries
- export OpenAPI/JSON Schema
- run a fast user suite after cloning
- rely on CI, fuzz tests, stress tests, and release checks

That path is now present. The remaining parity work is mostly ecosystem depth:
more tutorials, more integrations, more polished docs, and a custom domain if
the project becomes public-facing enough to justify it.
