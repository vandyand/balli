# Release Process

Balli releases are intended to be published as Python packages.

## Prerequisites

- CI is green on `main`.
- `pyproject.toml` has the target version.
- `CHANGELOG.md` has release notes.
- PyPI trusted publishing is configured for the GitHub repository environment
  named `pypi`.

## Cut A Release

```bash
basilisp run scripts/compile_check.lpy
basilisp test
python -m build
git diff --check
git tag vX.Y.Z
git push origin vX.Y.Z
```

The `Release` workflow builds distributions and publishes to PyPI using trusted
publishing.

## Verify

After publishing:

```bash
python -m pip install --upgrade balli
basilisp run -c "(require '[balli.core :as b]) (println b/version)"
```
