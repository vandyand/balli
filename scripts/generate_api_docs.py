#!/usr/bin/env python3
"""Generate a lightweight Markdown API reference from Balli namespaces."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "balli"
OUT = ROOT / "docs" / "api"

NS_RE = re.compile(r"^\(ns\s+([^\s\)]+)", re.MULTILINE)
DEF_RE = re.compile(r"^\((defn|def)\s+([^\s\)]+)(?:\s+\"([^\"]*)\")?", re.MULTILINE)


def namespace_for(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = NS_RE.search(text)
    if match:
        return match.group(1)
    return "balli." + path.stem.replace("_", "-")


def public_defs(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text(encoding="utf-8")
    defs: list[tuple[str, str, str]] = []
    for kind, name, doc in DEF_RE.findall(text):
        if name.startswith("-") or name.endswith("-") or name.startswith("^:private"):
            continue
        if name.startswith("*"):
            continue
        defs.append((kind, name, " ".join(doc.split()) if doc else ""))
    return defs


def page_name(ns: str) -> str:
    return ns.replace(".", "_").replace("-", "_") + ".md"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pages: list[tuple[str, str]] = []
    for path in sorted(SRC.glob("*.lpy")):
        ns = namespace_for(path)
        defs = public_defs(path)
        target = OUT / page_name(ns)
        pages.append((ns, target.name))
        lines = [f"# `{ns}`", ""]
        if not defs:
            lines.append("_No public definitions found._")
        else:
            for kind, name, doc in defs:
                lines.append(f"## `{name}`")
                lines.append("")
                lines.append(f"Kind: `{kind}`")
                lines.append("")
                lines.append(doc or "_No docstring._")
                lines.append("")
        target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    index = ["# API Reference", "", "Generated from `src/balli/*.lpy`.", ""]
    for ns, file_name in pages:
        index.append(f"- [`{ns}`]({file_name})")
    (OUT / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
