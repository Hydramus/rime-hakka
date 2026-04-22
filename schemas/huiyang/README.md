# Huiyang (惠陽) — Hagfa Pinyim

This folder is the canonical Rime package for the **Huiyang Hakka** dialect.

## Files

| File | Purpose |
|---|---|
| `hakka_huiyang.schema.yaml` | Input schema: speller alphabet, algebra, translator config. |
| `hakka_huiyang.dict.yaml`   | Dictionary — **generated** by `build/build_dict.py huiyang`. |
| `opencc/` | Optional T→S conversion tables (used only when the simplification switch is on). |

## Tone system (Hagfa Pinyim)

Six tones, written as trailing digits `1`–`6`:

| Digit | Name (客家話) | Contour |
|---|---|---|
| 1 | 陰平 (yin1 ping2) | ˧ mid level |
| 2 | 陽平 (yong2 ping2) | ˨˦ rising |
| 3 | 上聲 (song3 seng1) | ˧˩ low falling |
| 4 | 去聲 (hi4 seng1)   | ˥˧ high falling |
| 5 | 陰入 (yim1 ngip6)  | ˥ high checked |
| 6 | 陽入 (yong2 ngip6) | ˨ low checked |

Checked (入聲) syllables end in `-p`, `-t`, `-k` and only carry tones 5 or 6.

## Typing UX

Toneless input is the default. Both of these produce **日頭**:

```
ngitteu       → 日頭   (toneless; preferred)
ngit5 teu2    → 日頭   (toned; disambiguates homophones)
```

The `derive/([1-6])//` rule in `speller.algebra` indexes both forms.

## Regenerating

```bash
python build/build_dict.py huiyang
python build/validate_schema.py schemas/huiyang
```
