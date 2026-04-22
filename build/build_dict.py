"""
build_dict.py — Generate schemas/<slug>/hakka_<slug>.dict.yaml from CSV sources.

Inputs:
  sources/chars-<slug>.csv          Single-character readings. One row per
                                    (character, reading). CSV columns (flexible):
                                    either
                                        char,code
                                    or the hkilang/TTS format
                                        id,char,left_col,right_col,hint
                                    where right_col is the Hagfa Pinyim reading
                                    we want.
  sources/flashcards-<slug>.csv     Phrase entries. CSV columns:
                                    普通中文,客家汉字,Hakka Pronunciation,English Definition
                                    Only the 客家汉字 and Hakka Pronunciation
                                    columns are used.
  sources/phrases/<slug>/*.csv      Optional additional phrase files, same
                                    schema as flashcards CSV.

Output:
  schemas/<slug>/hakka_<slug>.dict.yaml

Weights:
  - Single-character entries: 10.
  - Phrase entries:           500 (boosted — these are the common phrases
                                   users want to type first).

Usage:
  python build/build_dict.py huiyang
  python build/build_dict.py huiyang --check   # validate inputs, don't write.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
SOURCES_DIR = REPO_ROOT / "sources"

CHAR_WEIGHT = 10
PHRASE_WEIGHT = 500

# Hagfa Pinyim: lowercase ascii letters + optional trailing tone digit 1-6.
# Syllables are space-separated inside `code`.
CODE_RE = re.compile(r"^[a-z]+[1-6]?(?: [a-z]+[1-6]?)*$")


@dataclass(frozen=True)
class Entry:
    text: str
    code: str
    weight: int

    def line(self) -> str:
        return f"{self.text}\t{self.code}\t{self.weight}"


def _normalize_code(raw: str) -> str | None:
    """Lowercase, collapse whitespace, validate. Returns None if invalid."""
    if raw is None:
        return None
    code = " ".join(raw.strip().lower().split())
    if not code:
        return None
    if not CODE_RE.match(code):
        return None
    return code


def _read_chars_csv(path: Path) -> list[Entry]:
    """Read single-char readings.

    Supports two layouts:
      (a) minimal: char,code[,weight[,hint]]
      (b) hkilang/TTS: id,char,other,hagfa_pinyim,hint
    """
    entries: list[Entry] = []
    if not path.exists():
        print(f"[warn] chars CSV not found: {path}", file=sys.stderr)
        return entries
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        first = next(reader, None)
        if first is None:
            return entries
        # Detect layout by probing the first non-header row.
        def looks_like_hkilang(row: list[str]) -> bool:
            return len(row) >= 4 and row[0].strip().isdigit() and len(row[1].strip()) == 1

        rows = [first] + list(reader)
        # Skip header row if present (non-numeric first cell).
        if rows and not rows[0][0].strip().isdigit():
            rows = rows[1:]

        for row in rows:
            if not row or len(row) < 2:
                continue
            if looks_like_hkilang(row):
                char = row[1].strip()
                code = _normalize_code(row[3] if len(row) > 3 else "")
            else:
                char = row[0].strip()
                code = _normalize_code(row[1])
            if not char or not code:
                continue
            entries.append(Entry(char, code, CHAR_WEIGHT))
    return entries


def _read_phrases_csv(path: Path) -> list[Entry]:
    entries: list[Entry] = []
    if not path.exists():
        return entries
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            hanzi = (row.get("客家汉字") or row.get("客家漢字") or "").strip()
            code = _normalize_code(row.get("Hakka Pronunciation", ""))
            if not hanzi or not code:
                continue
            entries.append(Entry(hanzi, code, PHRASE_WEIGHT))
    return entries


def collect_entries(slug: str) -> list[Entry]:
    entries: list[Entry] = []
    entries.extend(_read_chars_csv(SOURCES_DIR / f"chars-{slug}.csv"))
    entries.extend(_read_phrases_csv(SOURCES_DIR / f"flashcards-{slug}.csv"))
    phrases_dir = SOURCES_DIR / "phrases" / slug
    if phrases_dir.is_dir():
        for csv_file in sorted(phrases_dir.glob("*.csv")):
            entries.extend(_read_phrases_csv(csv_file))
    return entries


def dedupe(entries: list[Entry]) -> list[Entry]:
    """Drop exact duplicates, keeping the highest-weighted copy."""
    best: dict[tuple[str, str], Entry] = {}
    for e in entries:
        key = (e.text, e.code)
        prev = best.get(key)
        if prev is None or e.weight > prev.weight:
            best[key] = e
    return sorted(best.values(), key=lambda e: (-e.weight, e.text, e.code))


def render_dict_yaml(slug: str, entries: list[Entry], version: str) -> str:
    header = (
        "# Rime dictionary — GENERATED FILE. Do not edit by hand.\n"
        "# Regenerate via: python build/build_dict.py " + slug + "\n"
        "# SPDX-License-Identifier: CC-BY-SA-4.0\n"
        "# encoding: utf-8\n"
        "\n"
        "---\n"
        f"name: hakka_{slug}\n"
        f'version: "{version}"\n'
        "sort: by_weight\n"
        "use_preset_vocabulary: false\n"
        "...\n\n"
    )
    body = "\n".join(e.line() for e in entries)
    return header + body + "\n"


def _read_version(slug: str) -> str:
    """Pull the version from the schema yaml so we keep them in sync."""
    schema_path = SCHEMAS_DIR / slug / f"hakka_{slug}.schema.yaml"
    if not schema_path.exists():
        return "0.1.0"
    m = re.search(r'^\s*version:\s*"([^"]+)"', schema_path.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "0.1.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="dialect slug, e.g. huiyang")
    parser.add_argument("--check", action="store_true",
                        help="validate inputs without writing the dict file")
    args = parser.parse_args(argv)

    entries = collect_entries(args.slug)
    if not entries:
        print(f"[error] no entries collected for slug={args.slug!r}", file=sys.stderr)
        return 1

    entries = dedupe(entries)
    version = _read_version(args.slug)
    out_path = SCHEMAS_DIR / args.slug / f"hakka_{args.slug}.dict.yaml"

    print(f"[info] slug={args.slug} entries={len(entries)} version={version}")
    if args.check:
        print("[info] --check mode; not writing.")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_dict_yaml(args.slug, entries, version), encoding="utf-8")
    print(f"[info] wrote {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
