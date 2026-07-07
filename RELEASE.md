# Release Process

Balli releases are intended to be published as Python packages.

## Prerequisites

- CI is green on `main`.
- `pyproject.toml` has the target version.
- `CHANGELOG.md` has release notes.
- PyPI trusted publishing is configured for the GitHub repository environment
  named `pypi`.

## PyPI Trusted Publisher

PyPI trusted publishing is configured with:

- PyPI project: `balli`
- Owner: `vandyand`
- Repository name: `balli`
- Workflow name: `release.yml`
- Environment name: `pypi`

The GitHub environment `pypi` exists in this repository. The first PyPI release,
`0.6.0`, was published successfully through the `Release` workflow on July 7,
2026.

## Cut A Release

```bash
scripts/release_check.sh
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
