# Releases

Balli releases are versioned Python packages and matching GitHub releases.

## Automation

Pushing a `vX.Y.Z` tag runs the `Release` workflow:

- build source and wheel distributions
- publish to PyPI using trusted publishing
- skip already-published files on rerun
- create a GitHub release
- generate release notes
- attach the built distribution artifacts

Release notes should still be curated in `CHANGELOG.md` before the tag. GitHub
generated notes are useful for PR links and artifact discoverability; the
changelog remains the human-maintained summary.

## Verification Commands

```bash
python -m venv /tmp/balli-release-check
/tmp/balli-release-check/bin/python -m pip install --upgrade pip
/tmp/balli-release-check/bin/python -m pip install balli
/tmp/balli-release-check/bin/python -m pip check
/tmp/balli-release-check/bin/basilisp run -c "(require '[balli.core :as b]) (println b/version)"
```

For source releases:

```bash
scripts/release_check.sh
```

The smaller clone-friendly check is:

```bash
scripts/user_suite.sh
```
