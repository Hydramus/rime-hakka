"""
package.py — Build the release zip consumed by Weasel, Squirrel,
fcitx5-rime, Trime, and Hamster.

The resulting zip contains schema.yaml + dict.yaml + opencc/ at the root
(matches the plum / Trime / Hamster "import schema" convention).

Usage:
  python build/package.py huiyang
  python build/package.py huiyang --version 0.1.0
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"


def _read_version(schema_path: Path) -> str:
    m = re.search(r'^\s*version:\s*"([^"]+)"', schema_path.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "0.0.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--version", default=None, help="override version string")
    args = parser.parse_args(argv)

    schema_dir = REPO_ROOT / "schemas" / args.slug
    if not schema_dir.is_dir():
        print(f"[error] missing schema dir: {schema_dir}", file=sys.stderr)
        return 1

    schema_files = list(schema_dir.glob("*.schema.yaml"))
    if not schema_files:
        print(f"[error] no schema.yaml in {schema_dir}", file=sys.stderr)
        return 1

    version = args.version or _read_version(schema_files[0])
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"hakka-{args.slug}-rime-v{version}.zip"

    payload: list[Path] = []
    payload.extend(schema_dir.glob("*.schema.yaml"))
    payload.extend(schema_dir.glob("*.dict.yaml"))
    opencc_dir = schema_dir / "opencc"
    if opencc_dir.is_dir():
        payload.extend(p for p in opencc_dir.rglob("*") if p.is_file() and p.name != ".gitkeep")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in payload:
            arcname = p.relative_to(schema_dir).as_posix()
            zf.write(p, arcname)

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (DIST_DIR / (zip_path.name + ".sha256")).write_text(
        f"{digest}  {zip_path.name}\n", encoding="utf-8"
    )

    print(f"[ok] {zip_path.relative_to(REPO_ROOT)}")
    print(f"[ok] sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
