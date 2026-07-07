# Examples

Runnable examples live in the repository `examples/` directory.

| Example | Purpose |
|---|---|
| `examples/config_validation.lpy` | Validate application config maps |
| `examples/env_config_validation.lpy` | Decode and validate string-keyed environment/config maps |
| `examples/web_request_validation.lpy` | Decode and validate JSON-like request data |
| `examples/query_params_validation.lpy` | Decode and validate query parameter maps |
| `examples/json_api_handler.lpy` | Validate a JSON API-style handler boundary and export OpenAPI response data |
| `examples/openapi_export.lpy` | Generate OpenAPI/JSON Schema data |
| `examples/test_data_generation.lpy` | Generate deterministic sample data |
| `examples/parity_tooling.lpy` | Exercise provider reports, coercion diagnostics, schema diffs, generated checks, and static risk reports |

Run an example with:

```bash
basilisp run examples/config_validation.lpy
```
