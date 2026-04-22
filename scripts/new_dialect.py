"""
new_dialect.py — Scaffold a new schemas/<slug>/ folder from _template.

Usage:
  python scripts/new_dialect.py meixian --name "梅縣客家話"

Creates:
  schemas/<slug>/hakka_<slug>.schema.yaml
  schemas/<slug>/hakka_<slug>.dict.yaml   (stub; run build_dict.py to populate)
  schemas/<slug>/README.md
  schemas/<slug>/opencc/.gitkeep
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "schemas" / "_template"
SCHEMAS_DIR = REPO_ROOT / "schemas"


SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _render(template: str, slug: str, name: str) -> str:
    return template.replace("{{DIALECT_SLUG}}", slug).replace("{{DIALECT_NAME}}", name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="lowercase slug, e.g. meixian")
    parser.add_argument("--name", required=True, help="display name, e.g. 梅縣客家話")
    args = parser.parse_args(argv)

    if not SLUG_RE.match(args.slug):
        print(f"[error] invalid slug {args.slug!r}; use [a-z][a-z0-9_]*", file=sys.stderr)
        return 2

    target = SCHEMAS_DIR / args.slug
    if target.exists():
        print(f"[error] {target} already exists", file=sys.stderr)
        return 1

    target.mkdir(parents=True)
    (target / "opencc").mkdir()
    (target / "opencc" / ".gitkeep").write_text("", encoding="utf-8")

    schema_src = (TEMPLATE_DIR / "hakka_{{DIALECT_SLUG}}.schema.yaml").read_text(encoding="utf-8")
    (target / f"hakka_{args.slug}.schema.yaml").write_text(
        _render(schema_src, args.slug, args.name), encoding="utf-8"
    )

    readme_src = (TEMPLATE_DIR / "README.md").read_text(encoding="utf-8")
    (target / "README.md").write_text(
        _render(readme_src, args.slug, args.name), encoding="utf-8"
    )

    stub_dict = (
        "# Rime dictionary — GENERATED FILE.\n"
        f"# Populate sources/chars-{args.slug}.csv and optionally\n"
        f"# sources/flashcards-{args.slug}.csv, then run:\n"
        f"#   python build/build_dict.py {args.slug}\n"
        "# SPDX-License-Identifier: CC-BY-SA-4.0\n"
        "# encoding: utf-8\n"
        "\n"
        "---\n"
        f"name: hakka_{args.slug}\n"
        'version: "0.1.0"\n'
        "sort: by_weight\n"
        "use_preset_vocabulary: false\n"
        "...\n"
    )
    (target / f"hakka_{args.slug}.dict.yaml").write_text(stub_dict, encoding="utf-8")

    print(f"[ok] scaffolded {target.relative_to(REPO_ROOT)}")
    print(f"[next] add sources/chars-{args.slug}.csv, then:")
    print(f"        python build/build_dict.py {args.slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
