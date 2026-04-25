"""
fetch_mandarin_ranks.py — Download Mandarin character frequency data and
write sources/mandarin-char-ranks.txt.

This file supplements tw-hakka-word-weighting.txt with broad Mandarin
character frequency data so that build_dict.py can assign better weights to
characters that rarely appear in the Hakka-specific Rime essay corpus.

Sources:
  https://hanzicraft.com/lists/frequency         (ranks 1 – ~8 000+)
  https://en.wiktionary.org/wiki/Appendix:Mandarin_Frequency_lists/1-1000

Character pseudo-frequencies are computed as: freq = 100 000 // rank
so that rank 1 → 100 000, rank 100 → 1 000, rank 10 000 → 10, etc.
This Zipf-like distribution integrates naturally with the percentile
bucketing in build_dict.py's load_char_freq().

The output file uses the same tab-separated format as tw-hakka-word-weighting.txt
(essay.txt format) so load_char_freq() can parse it without modification.

Usage:
  python build/fetch_mandarin_ranks.py
  python build/fetch_mandarin_ranks.py --output path/to/custom.txt
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "sources"
OUTPUT_DEFAULT = SOURCES_DIR / "mandarin-char-ranks.txt"

HANZICRAFT_URL = "https://hanzicraft.com/lists/frequency"
WIKTIONARY_URL = (
    "https://en.wiktionary.org/wiki/Appendix:Mandarin_Frequency_lists/1-1000"
)

_CJK_START = "\u4e00"
_CJK_END = "\u9fff"


def _is_cjk(ch: str) -> bool:
    return len(ch) == 1 and _CJK_START <= ch <= _CJK_END


def _fetch(url: str) -> str:
    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 rime-hakka-build/1.0 (build tool)"},
    )
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_hanzicraft(html: str) -> dict[str, int]:
    """Return {char: rank} from the hanzicraft frequency page.

    The page renders list items in the form:
        <li class="list"><a href="/character/的" …>的</a>\n<span>1</span></li>
    """
    pattern = re.compile(
        r'href="/character/([^"]+)"[^>]*>([^<]+)</a>\s*\n?\s*<span>(\d+)</span>'
    )
    ranks: dict[str, int] = {}
    for m in pattern.finditer(html):
        char = m.group(2).strip()
        rank = int(m.group(3))
        if _is_cjk(char) and char not in ranks:
            ranks[char] = rank
    return ranks


def parse_wiktionary(html: str) -> list[str]:
    """Return single CJK characters (simplified) from the Wiktionary top-1000 table.

    The table has columns: Traditional | Simplified | Pinyin | Meaning.
    Simplified cells use <span class="Hans" lang="zh-Hans">.  We collect only
    entries where the simplified form is exactly one CJK character, preserving
    document order (= frequency rank).
    """
    pattern = re.compile(
        r'class="Hans"[^>]*lang="zh-Hans"[^>]*>(?:<[^>]+>)*([^<]+)(?:<[^>]+>)*</span>'
    )
    chars: list[str] = []
    seen: set[str] = set()
    for m in pattern.finditer(html):
        text = m.group(1).strip()
        if len(text) == 1 and _is_cjk(text) and text not in seen:
            chars.append(text)
            seen.add(text)
    return chars


# ---------------------------------------------------------------------------
# Frequency conversion
# ---------------------------------------------------------------------------

def ranks_to_pseudofreqs(ranks: dict[str, int]) -> dict[str, int]:
    """Convert rank → pseudo-frequency using an inverse-rank (Zipf) formula.

    freq = max(1, 100_000 // rank)

    This maps rank 1 → 100 000, rank 100 → 1 000, rank 10 000 → 10,
    preserving relative ordering while staying compatible with the
    percentile-based bucketing in load_char_freq().
    """
    return {char: max(1, 100_000 // rank) for char, rank in ranks.items()}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(OUTPUT_DEFAULT),
        metavar="PATH",
        help=f"Output file path (default: {OUTPUT_DEFAULT.relative_to(REPO_ROOT)})",
    )
    args = parser.parse_args(argv)
    output = Path(args.output)

    # --- hanzicraft.com ---
    print("[info] fetching hanzicraft.com/lists/frequency …", file=sys.stderr)
    try:
        hc_html = _fetch(HANZICRAFT_URL)
    except URLError as exc:
        print(f"[error] could not fetch hanzicraft.com: {exc}", file=sys.stderr)
        return 1

    hc_ranks = parse_hanzicraft(hc_html)
    print(
        f"[info] parsed {len(hc_ranks):,} CJK characters from hanzicraft.com",
        file=sys.stderr,
    )
    if not hc_ranks:
        print(
            "[warn] no characters parsed — the page structure may have changed",
            file=sys.stderr,
        )

    # Polite crawl delay before hitting a second domain
    time.sleep(1)

    # --- Wiktionary top-1000 ---
    print("[info] fetching Wiktionary Mandarin top-1000 list …", file=sys.stderr)
    wikt_chars: list[str] = []
    try:
        wikt_html = _fetch(WIKTIONARY_URL)
        wikt_chars = parse_wiktionary(wikt_html)
        print(
            f"[info] parsed {len(wikt_chars)} single CJK characters from Wiktionary",
            file=sys.stderr,
        )
    except URLError as exc:
        print(f"[warn] could not fetch Wiktionary ({exc}); skipping", file=sys.stderr)

    # --- Merge ---
    # hanzicraft is the primary source. Wiktionary single-char entries
    # fill in any gaps not covered by hanzicraft (rare, but possible).
    merged: dict[str, int] = dict(hc_ranks)
    next_rank = (max(merged.values(), default=0) + 1) if merged else 1
    added_from_wikt = 0
    for ch in wikt_chars:
        if ch not in merged:
            merged[ch] = next_rank
            next_rank += 1
            added_from_wikt += 1
    if added_from_wikt:
        print(
            f"[info] added {added_from_wikt} characters from Wiktionary not in hanzicraft",
            file=sys.stderr,
        )

    if not merged:
        print("[error] no character data collected; aborting", file=sys.stderr)
        return 1

    freq_map = ranks_to_pseudofreqs(merged)
    total = len(freq_map)

    # --- Write output ---
    output.parent.mkdir(parents=True, exist_ok=True)
    sorted_entries = sorted(freq_map.items(), key=lambda kv: -kv[1])
    with output.open("w", encoding="utf-8") as fh:
        fh.write("# Mandarin character frequency data (auto-generated — do not edit)\n")
        fh.write("# Sources: hanzicraft.com/lists/frequency + Wiktionary Mandarin top-1000\n")
        fh.write("# Format: char TAB pseudo-frequency (= 100000 // rank)\n")
        fh.write("# Regenerate: python build/fetch_mandarin_ranks.py\n")
        fh.write("#\n")
        for char, freq in sorted_entries:
            fh.write(f"{char}\t{freq}\n")

    print(
        f"[info] wrote {total:,} entries to {output.relative_to(REPO_ROOT)}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
