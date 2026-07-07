# Install

## From PyPI

Install the latest published release from PyPI:

```bash
python -m pip install balli
```

Balli is published at <https://pypi.org/project/balli/> and depends on
Basilisp. The Basilisp dependency is declared in `pyproject.toml`.

## From Source

```bash
git clone https://github.com/vandyand/balli.git
cd balli
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev,docs]"
```

## Verify A Clone

Run the quick user suite:

```bash
python -m pip install -e ".[dev]"
scripts/user_suite.sh
```

Run the full local gate:

```bash
basilisp run scripts/compile_check.lpy
basilisp test
python -m build --wheel
git diff --check
```
