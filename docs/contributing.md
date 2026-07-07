# Contributing

## Local Setup

```bash
python -m pip install -e ".[dev,docs]"
```

## Verification

Before opening a pull request:

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

## Compatibility Changes

When adding Malli-compatible behavior, update:

- `docs/malli-compatibility.md`
- `tests/test_malli_parity.lpy`
- `tests/test_fuzz_stress.lpy` when the behavior should survive generated stress coverage

## Third-Party Review

Balli tracks external review as part of Malli parity work. See
[Reviewer Outreach](reviewer-outreach.md) for the current plan to recruit a
broad set of Malli, Basilisp, testing, docs, and packaging reviewers without
mass-tagging people.
