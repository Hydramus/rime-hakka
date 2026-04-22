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
  sources/words-<slug>.csv          Multi-character vocabulary (char,pron).
                                    Produced by fetch_sources.py from
                                    hkilang/TTS hakka_words.csv.
  sources/flashcards-<slug>.csv     Phrase entries. CSV columns:
                                    普通中文,客家汉字,Hakka Pronunciation,English Definition
                                    Only the 客家汉字 and Hakka Pronunciation
                                    columns are used.
  sources/phrases/<slug>/*.csv      Optional additional phrase files, same
                                    schema as flashcards CSV.
sources/tw-hakka-word-weighting.txt Optional. Rime character frequency corpus
                                    used to weight single characters by how
                                    commonly they appear in written Chinese.
                                    Source:
                                    https://github.com/rime/rime-essay/blob/master/essay.txt
                                    If present it is loaded automatically.
                                    Override the path with --char-freq.

Output:
  schemas/<slug>/hakka_<slug>.dict.yaml

Weights (four tiers):
  - Curated flashcard phrases:      1000  (hand-checked, always win)
  - Vocabulary words (1-2 chars):    500  (common short words)
  - Vocabulary words (3+ chars):     200  (longer collocations)
  - Single characters, high freq:     90  (top 10% by corpus frequency)
  - Single characters, mid freq:      50  (next 40%)
  - Single characters, low freq:      20  (next 40%)
  - Single characters, no freq data:  10  (not in corpus / very rare)

Usage:
  python build/build_dict.py huiyang
  python build/build_dict.py huiyang --char-freq ./sources/tw-hakka-word-weighting.txt
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

CHAR_WEIGHT_HIGH = 90     # top 10% of characters by corpus frequency
CHAR_WEIGHT_MID = 50      # next 40%
CHAR_WEIGHT_LOW = 20      # next 40%
CHAR_WEIGHT_DEFAULT = 10  # not in corpus / very rare

FLASHCARD_WEIGHT = 1000   # curated hand-checked phrases
WORD_SHORT_WEIGHT = 500   # 1-2 char vocabulary words
WORD_LONG_WEIGHT = 200    # 3+ char vocabulary phrases

# Kept for backwards-compat references.
CHAR_WEIGHT = CHAR_WEIGHT_DEFAULT
PHRASE_WEIGHT = FLASHCARD_WEIGHT

# Default location for the Rime character frequency corpus inside the repo.
# Source: https://github.com/rime/rime-essay/blob/master/essay.txt
ESSAY_DEFAULT = SOURCES_DIR / "tw-hakka-word-weighting.txt"

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


# ---------------------------------------------------------------------------
# Character frequency corpus helpers
# ---------------------------------------------------------------------------

def _is_single_han(text: str) -> bool:
    """True if text is exactly one CJK unified ideograph."""
    return len(text) == 1 and "\u4e00" <= text <= "\u9fff"


def load_char_freq(corpus_path: Path) -> dict[str, int]:
    """Parse a Rime tw-hakka-word-weighting.txt-format file and return a char -> weight mapping.

    Only single Han characters are extracted. Frequencies are bucketed into
    three tiers using percentile cut-offs across characters with frequency > 0:
      top 10%  -> CHAR_WEIGHT_HIGH (90)
      next 40% -> CHAR_WEIGHT_MID  (50)
      rest     -> CHAR_WEIGHT_LOW  (20)
    Characters absent from the file get CHAR_WEIGHT_DEFAULT (10).
    """
    freqs: dict[str, int] = {}
    with corpus_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            char, _, freq_str = line.partition("\t")
            char = char.strip()
            if not _is_single_han(char):
                continue
            try:
                freq = int(freq_str.strip())
            except ValueError:
                continue
            if freq > 0:
                freqs[char] = freq

    if not freqs:
        return {}

    sorted_freqs = sorted(freqs.values(), reverse=True)
    n = len(sorted_freqs)
    high_cutoff = sorted_freqs[max(0, int(n * 0.10) - 1)]
    mid_cutoff = sorted_freqs[max(0, int(n * 0.50) - 1)]

    weights: dict[str, int] = {}
    for char, freq in freqs.items():
        if freq >= high_cutoff:
            weights[char] = CHAR_WEIGHT_HIGH
        elif freq >= mid_cutoff:
            weights[char] = CHAR_WEIGHT_MID
        else:
            weights[char] = CHAR_WEIGHT_LOW
    return weights


# ---------------------------------------------------------------------------


def _read_chars_csv(path: Path, char_freq: dict[str, int] | None = None) -> list[Entry]:
    """Read single-char readings.

    Supports two layouts:
      (a) minimal: char,code[,weight[,hint]]
      (b) hkilang/TTS: id,char,other,hagfa_pinyim,hint

    If char_freq is provided, each character's weight is looked up from it;
    otherwise CHAR_WEIGHT_DEFAULT is used for all characters.
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
            weight = (
                char_freq.get(char, CHAR_WEIGHT_DEFAULT)
                if char_freq is not None
                else CHAR_WEIGHT_DEFAULT
            )
            entries.append(Entry(char, code, weight))
    return entries


def _read_phrases_csv(path: Path, weight: int = FLASHCARD_WEIGHT) -> list[Entry]:
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
            entries.append(Entry(hanzi, code, weight))
    return entries


def _read_words_csv(path: Path) -> list[Entry]:
    """Read words-<slug>.csv (char,pron) produced by fetch_sources.py.

    Short words (1-2 chars) get WORD_SHORT_WEIGHT; longer get WORD_LONG_WEIGHT.
    """
    entries: list[Entry] = []
    if not path.exists():
        return entries
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            word = (row.get("char") or "").strip()
            code = _normalize_code(row.get("pron", ""))
            if not word or not code:
                continue
            weight = WORD_SHORT_WEIGHT if len(word) <= 2 else WORD_LONG_WEIGHT
            entries.append(Entry(word, code, weight))
    return entries


def collect_entries(slug: str, char_freq: dict[str, int] | None = None) -> list[Entry]:
    entries: list[Entry] = []
    entries.extend(_read_chars_csv(SOURCES_DIR / f"chars-{slug}.csv", char_freq))
    entries.extend(_read_words_csv(SOURCES_DIR / f"words-{slug}.csv"))
    entries.extend(_read_phrases_csv(SOURCES_DIR / f"flashcards-{slug}.csv", FLASHCARD_WEIGHT))
    phrases_dir = SOURCES_DIR / "phrases" / slug
    if phrases_dir.is_dir():
        for csv_file in sorted(phrases_dir.glob("*.csv")):
            entries.extend(_read_phrases_csv(csv_file, FLASHCARD_WEIGHT))
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
    parser.add_argument("--char-freq", default=None, metavar="PATH",
                        help=f"character frequency corpus (essay.txt format). "
                             f"Defaults to {ESSAY_DEFAULT.relative_to(REPO_ROOT)} "
                             f"if that file exists.")
    args = parser.parse_args(argv)

    # Resolve the corpus path: explicit flag > default repo location > none.
    corpus_path: Path | None = None
    if args.char_freq:
        corpus_path = Path(args.char_freq)
        if not corpus_path.exists():
            print(f"[error] char-freq file not found: {corpus_path}", file=sys.stderr)
            return 1
    elif ESSAY_DEFAULT.exists():
        corpus_path = ESSAY_DEFAULT

    char_freq: dict[str, int] | None = None
    if corpus_path is not None:
        char_freq = load_char_freq(corpus_path)
        print(f"[info] loaded char frequencies for {len(char_freq)} characters "
              f"from {corpus_path.relative_to(REPO_ROOT)}")
    else:
        print("[info] no character frequency corpus found; using flat char weight")

    entries = collect_entries(args.slug, char_freq)
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
