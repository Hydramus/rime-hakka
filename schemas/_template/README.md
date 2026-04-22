# {{DIALECT_NAME}}

Template for a new Hakka dialect. Use `scripts/new_dialect.py <slug>
--name "<display name>"` to instantiate.

Requires:

1. `sources/chars-<slug>.csv` — single-character readings.
2. `sources/flashcards-<slug>.csv` — phrase-level entries (optional).

Then run:

```bash
python build/build_dict.py <slug>
python build/validate_schema.py schemas/<slug>
```
