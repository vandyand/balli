# API Reference

Generated from `src/balli/*.lpy`.

- [`balli.clj-kondo`](balli_clj_kondo.md) - Static-analysis metadata exports
- [`balli.compile`](balli_compile.md) - AST -> compiled validator + explainer closures
- [`balli.core`](balli_core.md) - Public API for balli - Malli for Basilisp
- [`balli.describe`](balli_describe.md) - Small English schema descriptions.
- [`balli.destructure`](balli_destructure.md) - Schema-guided destructuring helpers
- [`balli.dev`](balli_dev.md) - Development-time instrumentation registry
- [`balli.dot`](balli_dot.md) - Graphviz DOT export for Balli schemas.
- [`balli.edn`](balli_edn.md) - EDN-style schema persistence wrappers
- [`balli.error`](balli_error.md) - Humanized error messages for balli explain maps
- [`balli.extension`](balli_extension.md) - Custom schema type extension registry
- [`balli.generator`](balli_generator.md) - Schema-driven value generation (Phase 7, malli-semantics section H)
- [`balli.json-schema`](balli_json_schema.md) - Schema -> JSON Schema export (Malli's malli.json-schema)
- [`balli.lite`](balli_lite.md) - Small data-spec-style schema shorthand
- [`balli.normalize`](balli_normalize.md) - Schema form -> AST normalization
- [`balli.openapi`](balli_openapi.md) - OpenAPI 3 export helpers built on balli.json-schema
- [`balli.plantuml`](balli_plantuml.md) - PlantUML class-style schema visualization.
- [`balli.pretty`](balli_pretty.md) - Pretty development-time error rendering.
- [`balli.provider`](balli_provider.md) - Schema inference (Malli's malli.provider): `provide` takes a collection of sample values and returns a schema FORM that validates all of them
- [`balli.regex`](balli_regex.md) - Backtracking regex-of-sequences engine (Malli's malli.impl.regex, ported to an iterative thunk-stack driver -- Python has no TCO and a low recursion limit, so parked continuatio...
- [`balli.registry`](balli_registry.md) - Builtin type table, custom registries, the MUTABLE default registry, and ref resolution for balli
- [`balli.sci`](balli_sci.md) - SCI-style namespace data for embedding Balli in restricted evaluators
- [`balli.serial`](balli_serial.md) - Safe schema serialization helpers
- [`balli.swagger`](balli_swagger.md) - Swagger/OpenAPI 2.0 export helpers built on balli.json-schema.
- [`balli.time`](balli_time.md) - Pure Python datetime helpers for Balli time schemas
- [`balli.transform`](balli_transform.md) - Value transformers (decode/encode) for balli, per Malli 0.20 semantics
- [`balli.util`](balli_util.md) - Schema utilities (Malli's malli.util, form->form)
