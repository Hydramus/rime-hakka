# rime-hakka

Multi-platform Hakka input method based on the [Rime](https://rime.im/) engine.
One YAML schema + dictionary is the single source of truth — the same package
is consumed unchanged by every supported frontend.

- **Launch dialect:** Huiyang (惠陽客家話) using Hagfa Pinyim romanization.
- **Planned dialects:** Meixian, Sixian, and others — see [`schemas/_template/`](schemas/_template/).
- **Input UX:** toneless input is the default; tone digits `1`–`6` are accepted for optional disambiguation.

## Install matrix

| OS / Platform | Frontend | How |
|---|---|---|
| Windows | [Weasel](https://github.com/rime/weasel) | Download release zip → drop onto `rime-install.bat`, or run our Inno Setup installer. See [installers/windows](installers/windows/README.md). |
| macOS | [Squirrel](https://github.com/rime/squirrel) | Install the `.pkg` from Releases, or `brew install --cask rime-hakka` (planned tap). See [installers/macos](installers/macos/README.md). |
| Linux (KDE Plasma + GNOME) | [fcitx5-rime](https://github.com/fcitx/fcitx5-rime) | `.deb` / Arch `PKGBUILD` — schema lands in `/usr/share/rime-data/`. See [installers/linux](installers/linux/README.md). |
| Android | [Trime](https://github.com/osfans/trime) | Install Trime from F-Droid / Play, then **Schema Management → Import** on the release zip. See [installers/android](installers/android/README.md). |
| iOS | [Hamster](https://github.com/imfuxiao/Hamster) | Install Hamster from App Store, then URL-import / Files-import the release zip. See [installers/ios](installers/ios/README.md). |

### About Gboard

Gboard does **not** accept third-party IMEs as plugins. The Android path
here is Trime. Submission of Huiyang Hakka as a first-class Gboard
language is tracked separately in [gboard-submission/](gboard-submission/README.md).

## Quick start (any Rime-based frontend)

```bash
# Linux / macOS
bash <(curl -fsSL https://raw.githubusercontent.com/rime/plum/master/rime-install) <user>/rime-hakka
```

On Windows, drag the release zip onto `rime-install.bat` from the
[plum Windows bootstrap](https://github.com/rime/plum-windows-bootstrap).

After installing, open the Rime deployer (`WeaselDeployer` / `Squirrel →
Deploy` / `fcitx5-configtool`), add **惠陽客家話 (Hagfa Pinyim)** to your
active schemas, and redeploy.

## Typing examples

| Hagfa Pinyim (toned) | Hagfa Pinyim (toneless) | Output |
|---|---|---|
| `ngit5 teu2` | `ngitteu` | 日頭 |
| `tien1 ho2`  | `tienho`  | 天河 |
| `ciang1 coi4` | `ciangcoi` | 青菜 |

## Repository layout

```
rime-hakka/
├── schemas/{huiyang,_template}/   # per-dialect Rime packages
├── sources/                       # upstream CSVs + attribution
├── build/                         # dictionary builder + validator + packager
├── installers/                    # per-OS installer scripts & docs
├── gboard-submission/             # advocacy / language-submission docs
├── tests/                         # librime roundtrip tests
├── scripts/new_dialect.py         # scaffolder for new dialects
├── docs/plan.md                   # architecture plan
└── recipe.yaml                    # plum recipe
```

## Build locally

```bash
pip install -r build/requirements.txt
python build/fetch_sources.py         # downloads chars-hkilang.csv
python build/build_dict.py huiyang    # regenerates schemas/huiyang/hakka_huiyang.dict.yaml
python build/validate_schema.py schemas/huiyang
python build/package.py huiyang       # emits dist/hakka-huiyang-rime-vX.Y.Z.zip
```

## Licensing

- Code, build scripts, installers: **MIT** — see [`LICENSE`](LICENSE).
- Dictionary data (`schemas/**/*.dict.yaml`, `sources/*.csv`): **CC-BY-SA 4.0** — see [`LICENSE-DATA`](LICENSE-DATA).

Upstream attribution: single-character readings are derived from
[hkilang/TTS](https://github.com/hkilang/TTS) (`src/res/chars.csv`), released
under CC-BY-SA-compatible terms. Schema structure is inspired by
[syndict/hakka](https://github.com/syndict/hakka).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Adding a new dialect is as simple as

```bash
python scripts/new_dialect.py meixian --name "梅縣客家話"
```

## Status

Pre-release. Tracking first tag `v0.1.0`.
