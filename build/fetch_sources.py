"""
fetch_sources.py — Download upstream source CSVs into sources/.

Currently pulls:
  - hkilang/TTS chars.csv        →  sources/chars-huiyang.csv  (single-char readings)
  - hkilang/TTS hakka_words.csv  →  sources/words-huiyang.csv  (multi-char vocabulary)

The upstream URL is pinned to `main`. For reproducible builds, set
--commit <sha> to pin a specific revision.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "sources"

HKILANG_CHARS_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/hkilang/TTS/{ref}/src/res/chars.csv"
)
HKILANG_WORDS_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/hkilang/TTS/{ref}/src/res/hakka_words.csv"
)


def fetch_hkilang(ref: str = "main") -> bytes:
    url = HKILANG_CHARS_URL_TEMPLATE.format(ref=ref)
    print(f"[info] fetching {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (static URL)
        return resp.read()


def fetch_hkilang_words(ref: str = "main") -> bytes:
    url = HKILANG_WORDS_URL_TEMPLATE.format(ref=ref)
    print(f"[info] fetching {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (static URL)
        return resp.read()


def extract_words(csv_bytes: bytes) -> list[tuple[str, str]]:
    """Return (word, pron) pairs from hkilang hakka_words.csv.

    The upstream format has NO header row: each line is `word,pron` where
    pron is space-separated Hagfa Pinyim syllables.
    """
    rows: list[tuple[str, str]] = []
    reader = csv.reader(io.StringIO(csv_bytes.decode("utf-8")))
    for row in reader:
        if len(row) < 2:
            continue
        word = row[0].strip()
        pron = row[1].strip()
        if not word or not pron:
            continue
        rows.append((word, pron))
    return rows


def extract_huiyang_readings(csv_bytes: bytes) -> list[tuple[str, str]]:
    """Return (char, hagfa_pinyim) pairs from hkilang chars.csv.

    The upstream format is: char,waitau,hakka,notes.
    We keep the hakka (Hagfa Pinyim) column.
    """
    rows: list[tuple[str, str]] = []
    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    for row in reader:
        char = row.get("char", "").strip()
        hagfa = row.get("hakka", "").strip()
        if not char or not hagfa:
            continue
        rows.append((char, hagfa))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", default="main",
                        help="git ref (branch, tag, or sha) to pull from hkilang/TTS")
    parser.add_argument("--out", default=None,
                        help="output path (default: sources/chars-hkilang.csv)")
    args = parser.parse_args(argv)

    SOURCES_DIR.mkdir(exist_ok=True)
    # The hkilang Hagfa Pinyim readings ARE the Huiyang character set we want,
    # so write directly to chars-huiyang.csv (what build_dict.py reads).
    out = Path(args.out) if args.out else SOURCES_DIR / "chars-huiyang.csv"

    cache_dir = SOURCES_DIR / ".cache"
    cache_dir.mkdir(exist_ok=True)

    try:
        raw_chars = fetch_hkilang(args.commit)
    except Exception as e:  # noqa: BLE001
        print(f"[error] chars fetch failed: {e}", file=sys.stderr)
        return 1

    # Cache the raw upstream file for attribution / diff purposes.
    (cache_dir / f"hkilang-chars-{args.commit}.csv").write_bytes(raw_chars)

    pairs = extract_huiyang_readings(raw_chars)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["char", "code"])
        writer.writerows(pairs)
    print(f"[ok] wrote {len(pairs)} rows to {out.relative_to(REPO_ROOT)}")

    words_out = SOURCES_DIR / "words-huiyang.csv"
    try:
        raw_words = fetch_hkilang_words(args.commit)
    except Exception as e:  # noqa: BLE001
        print(f"[error] words fetch failed: {e}", file=sys.stderr)
        return 1

    (cache_dir / f"hkilang-words-{args.commit}.csv").write_bytes(raw_words)

    word_pairs = extract_words(raw_words)
    with words_out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["char", "pron"])
        writer.writerows(word_pairs)
    print(f"[ok] wrote {len(word_pairs)} rows to {words_out.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
