# Deployment

Balli has the core public deployment pieces in place:

- Package: <https://pypi.org/project/balli/>
- Documentation: <https://vandyand.github.io/balli/>
- Source and CI: <https://github.com/vandyand/balli>
- Release workflow: `.github/workflows/release.yml`

## Current Status

`0.6.0` is published to PyPI through trusted publishing. GitHub Pages serves
the MkDocs site from the repository docs workflow. The repository also has a
quick user suite for fresh clones:

```bash
python -m pip install -e ".[dev]"
scripts/user_suite.sh
```

## Release Checklist

Before a release:

```bash
scripts/release_check.sh
```

Then tag and push:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

The release workflow builds distributions, publishes to PyPI with trusted
publishing, creates a GitHub release, generates release notes, and attaches the
wheel and source distribution.

After a release, verify:

- CI and the tag release workflow are green.
- The GitHub release exists and has artifacts attached.
- `pip index versions balli` lists the new version.
- A fresh virtualenv can install and import Balli.
- The hosted docs are live.

## Custom Domain

Balli does not currently use a custom docs domain. To add one later:

1. Choose the domain or subdomain, for example `balli.example.org`.
2. Configure DNS for GitHub Pages.
3. Add a `docs/CNAME` file containing only the domain name.
4. Set the same custom domain in the repository Pages settings.
5. Update `site_url` in `mkdocs.yml`.

This is intentionally left unconfigured until there is a real domain to point
at the project.
