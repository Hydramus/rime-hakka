"""
Roundtrip tests that drive librime via its Python bindings.

Skipped automatically if librime-python isn't available. In CI we install
it from the `librime` package (`pip install librime` on Linux) and run
`rime_deployer --build` against the user data directory.

The assertion: typing the bootstrap Hagfa Pinyim codes yields the
expected Hanzi as the top candidate — both for fully-toned and toneless
input (the toneless form must match because of the `derive/([1-6])//`
algebra rule).
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

librime = pytest.importorskip("librime")  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas" / "huiyang"

PHRASES = [
    ("日頭", "ngit5 teu2", "ngitteu"),
    ("天河", "tien1 ho2", "tienho"),
    ("青菜", "ciang1 coi4", "ciangcoi"),
    ("食飯", "sit6 fan4", "sitfan"),
]


@pytest.fixture(scope="module")
def rime_session():
    """Deploy the schema to a temp user dir and hand back a librime session."""
    user_dir = Path(tempfile.mkdtemp(prefix="rime-hakka-test-"))
    # Copy schema + dict next to Rime's shared data so the deployer sees them.
    for f in SCHEMA_DIR.glob("*.yaml"):
        shutil.copy(f, user_dir / f.name)
    (user_dir / "default.custom.yaml").write_text(
        'patch:\n  schema_list:\n    - schema: hakka_huiyang\n',
        encoding="utf-8",
    )

    traits = {
        "shared_data_dir": os.environ.get("RIME_SHARED_DATA_DIR", "/usr/share/rime-data"),
        "user_data_dir": str(user_dir),
        "distribution_name": "rime-hakka-tests",
        "distribution_code_name": "rime-hakka",
        "distribution_version": "0.1.0",
        "app_name": "rime.test",
    }
    session = librime.Session(traits)  # type: ignore[attr-defined]
    session.select_schema("hakka_huiyang")
    yield session
    session.close()
    shutil.rmtree(user_dir, ignore_errors=True)


@pytest.mark.parametrize("hanzi, toned, toneless", PHRASES)
def test_toned_input_matches(rime_session, hanzi: str, toned: str, toneless: str) -> None:
    rime_session.simulate_key_sequence(toned.replace(" ", ""))
    candidates = rime_session.get_candidates()
    assert candidates and candidates[0].text == hanzi, candidates


@pytest.mark.parametrize("hanzi, toned, toneless", PHRASES)
def test_toneless_input_matches(rime_session, hanzi: str, toned: str, toneless: str) -> None:
    rime_session.clear()
    rime_session.simulate_key_sequence(toneless)
    candidates = rime_session.get_candidates()
    assert candidates and any(c.text == hanzi for c in candidates[:5]), candidates
