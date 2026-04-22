# Contributing to rime-hakka

## Reporting issues

- Typo in a reading → open an issue with the character, expected Hagfa Pinyim, citation if any.
- Missing phrase → open a PR adding the row to `sources/flashcards-<dialect>.csv`
  or a new file under `sources/phrases/`.
- Installer bug on a specific OS → attach OS version, Rime frontend version, and the deploy log.

## Adding a new dialect

```bash
python scripts/new_dialect.py <slug> --name "<Chinese display name>"
```

This creates:

- `schemas/<slug>/hakka_<slug>.schema.yaml` from the template
- `schemas/<slug>/hakka_<slug>.dict.yaml` stub (run `build_dict.py <slug>` to populate)
- `schemas/<slug>/README.md`

Then:

1. Provide `sources/chars-<slug>.csv` — one row per reading, columns: `char,code,weight?,hint?`.
2. Provide `sources/flashcards-<slug>.csv` — same format as Huiyang's: `普通中文,客家汉字,Hakka Pronunciation,English Definition`.
3. Run `python build/build_dict.py <slug>` and `python build/validate_schema.py schemas/<slug>`.
4. Submit a PR. CI will rebuild the dict and run roundtrip tests.

## Dictionary format

Each `*.dict.yaml` has a YAML header block followed by tab-separated rows:

```
<text>\t<code>\t<weight>
```

- `text` — the Hanzi string (traditional by default; simplification is opt-in via the `简化字` switch).
- `code` — space-separated syllables with tone digits 1–6, e.g. `ngit5 teu2`.
- `weight` — integer frequency weight; phrases get a higher boost than single-char entries.

## Toneless-default design

The `speller.algebra` in each schema contains `derive/([1-6])//`, which
indexes both the toned and toneless forms of every entry into the prism.
Users can type either way. **Do not remove the tone digits from dictionary
entries** — keep the dict fully toned and let the algebra handle the
toneless form at build time.

## Running tests locally

```bash
pip install -r build/requirements.txt
pytest tests/
```

The `test_roundtrip.py` test is skipped automatically if `librime-python`
isn't installed. In CI it runs against `librime` built from source.
