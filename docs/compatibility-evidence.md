# Compatibility Evidence

Balli keeps compatibility claims tied to executable tests:

| Claim Area | Evidence |
|---|---|
| Matrix smoke corpus | `tests/test_compatibility_corpus.lpy` |
| Malli syntax, `:seqable`, `:every`, `:->`, var registry, generator objects | `tests/test_malli_parity.lpy` |
| Broad generated schema behavior | `tests/test_fuzz_stress.lpy` |
| User clone smoke coverage | `tests/test_user_suite.lpy` |
| Core runtime APIs | `tests/test_core.lpy`, `tests/test_parse.lpy`, `tests/test_transform.lpy` |
| Exporters | `tests/test_json_schema.lpy`, `tests/test_tier5.lpy` |
| Registries | `tests/test_registry.lpy`, `tests/test_registry_mut.lpy`, `tests/test_local_registry.lpy` |

The CI gate runs compile checks, full tests, wheel builds, and whitespace
validation on pull requests and pushes to `main`.
