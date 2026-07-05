# Contributing

Thanks for helping improve Balli.

## Setup

```bash
python -m pip install -e ".[dev,docs]"
```

## Required Checks

Run these before opening a pull request:

```bash
basilisp run scripts/compile_check.lpy
basilisp test
python -m build --wheel
git diff --check
```

For documentation changes:

```bash
python scripts/generate_api_docs.py
mkdocs build --strict
```

## Compatibility Work

For Malli parity changes, update the tests and docs together:

- `tests/test_compatibility_corpus.lpy`
- `tests/test_malli_parity.lpy`
- `tests/test_fuzz_stress.lpy`
- `docs/malli-compatibility.md`
- `docs/compatibility-evidence.md`
