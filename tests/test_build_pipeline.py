"""
Unit tests for the build pipeline. These do NOT require librime — they
exercise the Python builder and validator against the committed YAML.

The full roundtrip test that actually deploys the schema via librime and
types `ngit5 teu2` to check that `日頭` is the top candidate lives in
`test_roundtrip_librime.py` (skipped by default when librime isn't
available — enabled in CI with a librime build step).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_build_dict_check_huiyang() -> None:
    result = _run(["build/build_dict.py", "huiyang", "--check"])
    assert result.returncode == 0, result.stderr


def test_validate_huiyang_schema() -> None:
    result = _run(["build/validate_schema.py", "schemas/huiyang"])
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("fixture", [
    ("日頭", "ngit5 teu2"),
    ("天河", "tien1 ho2"),
    ("青菜", "ciang1 coi4"),
    ("食飯", "sit6 fan4"),
])
def test_dict_contains_bootstrap_entries(fixture: tuple[str, str]) -> None:
    """Bootstrap entries from the committed dict yaml must be present."""
    text, code = fixture
    dict_path = REPO_ROOT / "schemas" / "huiyang" / "hakka_huiyang.dict.yaml"
    body = dict_path.read_text(encoding="utf-8")
    needle = f"{text}\t{code}\t"
    assert needle in body, f"missing bootstrap entry: {needle!r}"
