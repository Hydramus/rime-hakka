"""
validate_schema.py — sanity-check a schemas/<slug>/ folder.

Checks:
  - schema.yaml and dict.yaml both exist and parse as YAML.
  - speller.alphabet contains every letter used in dict codes.
  - speller.alphabet contains digits 1-6 (required for tone input).
  - `derive/([1-6])//` rule is present (toneless default UX).
  - Every dict code matches `[a-z]+[1-6]?( [a-z]+[1-6]?)*`.
  - Tone digits are in the range 1..6.
  - No duplicate (text, code) pairs.

Exit code 0 = all good, 1 = failures (printed to stderr).

Usage:
  python build/validate_schema.py schemas/huiyang
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("[error] PyYAML required: pip install -r build/requirements.txt\n")
    raise

CODE_RE = re.compile(r"^[a-z]+[1-6]?(?: [a-z]+[1-6]?)*$")
TONELESS_RULE = re.compile(r"derive/\(\[1-6\]\)//")


def _load_yaml_documents(path: Path) -> list[dict]:
    """Split Rime's `--- ... \n...\n` document streams and return parsed docs."""
    text = path.read_text(encoding="utf-8")
    docs = list(yaml.safe_load_all(text))
    return [d for d in docs if isinstance(d, dict)]


def _parse_dict_yaml(path: Path) -> tuple[dict, list[tuple[str, str, int]]]:
    """Parse the YAML header and tab-separated entry rows."""
    text = path.read_text(encoding="utf-8")
    # Rime dict format: YAML header ending with '...' then tab-separated rows.
    if "\n...\n" in text:
        header_text, body_text = text.split("\n...\n", 1)
    elif "\n..." in text:
        header_text, body_text = text.split("\n...", 1)
    else:
        header_text, body_text = text, ""
    header_text = re.sub(r"^---\s*\n", "", header_text, flags=re.M).strip()
    header = yaml.safe_load(header_text) if header_text else {}
    entries: list[tuple[str, str, int]] = []
    for lineno, line in enumerate(body_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        text_val = parts[0].strip()
        code = parts[1].strip()
        weight = int(parts[2]) if len(parts) > 2 and parts[2].strip().isdigit() else 0
        entries.append((text_val, code, weight))
    return header or {}, entries


def validate(schema_dir: Path) -> list[str]:
    errors: list[str] = []

    schema_files = list(schema_dir.glob("*.schema.yaml"))
    dict_files = list(schema_dir.glob("*.dict.yaml"))
    if not schema_files:
        errors.append(f"no *.schema.yaml in {schema_dir}")
        return errors
    if not dict_files:
        errors.append(f"no *.dict.yaml in {schema_dir}")
        return errors

    schema_path = schema_files[0]
    dict_path = dict_files[0]

    try:
        schema_docs = _load_yaml_documents(schema_path)
    except yaml.YAMLError as e:
        errors.append(f"{schema_path.name}: YAML parse error: {e}")
        return errors

    schema = next((d for d in schema_docs if "schema" in d or "speller" in d), {})
    speller = schema.get("speller") or {}
    alphabet = speller.get("alphabet") or ""
    algebra = speller.get("algebra") or []

    for d in "123456":
        if d not in alphabet:
            errors.append(f"{schema_path.name}: tone digit {d!r} missing from speller.alphabet")

    if not any(TONELESS_RULE.search(str(rule)) for rule in algebra):
        errors.append(
            f"{schema_path.name}: toneless-default rule `derive/([1-6])//` "
            "missing from speller.algebra"
        )

    try:
        header, entries = _parse_dict_yaml(dict_path)
    except yaml.YAMLError as e:
        errors.append(f"{dict_path.name}: YAML parse error: {e}")
        return errors

    if not entries:
        errors.append(f"{dict_path.name}: no dictionary entries found")

    seen: set[tuple[str, str]] = set()
    alphabet_set = set(alphabet.lower())

    for i, (text_val, code, _weight) in enumerate(entries, start=1):
        if not CODE_RE.match(code):
            errors.append(f"{dict_path.name}: entry {i} `{text_val}`: malformed code {code!r}")
            continue
        for ch in code:
            if ch == " ":
                continue
            if ch not in alphabet_set:
                errors.append(
                    f"{dict_path.name}: entry {i} `{text_val}`: char {ch!r} in code "
                    f"{code!r} not in speller.alphabet"
                )
                break
        key = (text_val, code)
        if key in seen:
            errors.append(f"{dict_path.name}: duplicate entry `{text_val}` with code {code!r}")
        seen.add(key)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema_dir", type=Path,
                        help="path to schemas/<slug>/")
    args = parser.parse_args(argv)

    schema_dir = args.schema_dir
    if not schema_dir.is_dir():
        print(f"[error] not a directory: {schema_dir}", file=sys.stderr)
        return 2

    errors = validate(schema_dir)
    if errors:
        for e in errors:
            print(f"[fail] {e}", file=sys.stderr)
        print(f"[fail] {len(errors)} error(s) in {schema_dir}", file=sys.stderr)
        return 1
    print(f"[ok] {schema_dir} validates cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
