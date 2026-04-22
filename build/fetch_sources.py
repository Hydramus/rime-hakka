"""
fetch_sources.py — Download upstream source CSVs into sources/.

Currently pulls:
  - hkilang/TTS chars.csv  →  sources/chars-hkilang.csv  (single-char readings)

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

HKILANG_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/hkilang/TTS/{ref}/src/res/chars.csv"
)


def fetch_hkilang(ref: str = "main") -> bytes:
    url = HKILANG_URL_TEMPLATE.format(ref=ref)
    print(f"[info] fetching {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (static URL)
        return resp.read()


def extract_huiyang_readings(csv_bytes: bytes) -> list[tuple[str, str]]:
    """Return (char, hagfa_pinyim) pairs from hkilang chars.csv.

    The upstream format is: id,char,other_romanization,hagfa_pinyim,hint.
    We keep the right-hand Hagfa Pinyim column.
    """
    rows: list[tuple[str, str]] = []
    reader = csv.reader(io.StringIO(csv_bytes.decode("utf-8")))
    for row in reader:
        if not row or len(row) < 4:
            continue
        if not row[0].strip().isdigit():
            continue
        char = row[1].strip()
        hagfa = row[3].strip()
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

    try:
        raw = fetch_hkilang(args.commit)
    except Exception as e:  # noqa: BLE001
        print(f"[error] fetch failed: {e}", file=sys.stderr)
        return 1

    # Cache the raw upstream file for attribution / diff purposes.
    (SOURCES_DIR / ".cache").mkdir(exist_ok=True)
    (SOURCES_DIR / ".cache" / f"hkilang-chars-{args.commit}.csv").write_bytes(raw)

    pairs = extract_huiyang_readings(raw)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["char", "code"])
        writer.writerows(pairs)

    print(f"[ok] wrote {len(pairs)} rows to {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
