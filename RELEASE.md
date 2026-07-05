# Release Process

Balli releases are intended to be published as Python packages.

## Prerequisites

- CI is green on `main`.
- `pyproject.toml` has the target version.
- `CHANGELOG.md` has release notes.
- PyPI trusted publishing is configured for the GitHub repository environment
  named `pypi`.

## PyPI Trusted Publisher

Configure a PyPI trusted publisher before cutting the first release:

- PyPI project: `balli`
- Owner: `vandyand`
- Repository name: `balli`
- Workflow name: `release.yml`
- Environment name: `pypi`

The GitHub environment `pypi` exists in this repository. A manual release
workflow run on July 5, 2026 reached the PyPI publish step and failed with
`invalid-publisher` because PyPI did not yet have a matching trusted publisher.
The OIDC claims PyPI reported were:

```text
sub: repo:vandyand/balli:environment:pypi
repository: vandyand/balli
workflow_ref: vandyand/balli/.github/workflows/release.yml@refs/heads/main
environment: pypi
```

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
