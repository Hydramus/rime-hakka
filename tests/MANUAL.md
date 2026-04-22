# Manual verification matrix

After every release candidate, a human runs through this checklist on
each frontend. The five test phrases are the same across all rows so
results are directly comparable.

## Test phrases

| Toneless input | Expected top candidate |
|---|---|
| `ngitteu`  | 日頭 |
| `tienho`   | 天河 |
| `ciangcoi` | 青菜 |
| `sitfan`   | 食飯 |
| `ngietgong` | 月光 |

Also verify the toned forms (`ngit5teu2`, `tien1ho2`, etc.) produce the same result.

## Matrix

| Frontend | OS | Status | Notes |
|---|---|---|---|
| Weasel | Windows 10/11 | ☐ | Drop zip on `rime-install.bat`, redeploy, test in Notepad. |
| Squirrel | macOS 13+ | ☐ | Install `.pkg`, run `Squirrel → Deploy`, test in TextEdit. |
| fcitx5-rime | Linux / KDE Plasma 6 | ☐ | Install `.deb` or Arch pkg, add in Fcitx5 config, test in Kate. |
| fcitx5-rime | Linux / GNOME 46 | ☐ | Same install; test in GNOME Text Editor. Confirm the IME switches via Super+Space. |
| Trime | Android 14 | ☐ | Import zip via Schema Management, test in Messages. |
| Hamster | iOS 17+ | ☐ | URL-import zip, enable in Settings → Keyboards, test in Notes. |

## Release-sign-off criteria

All six rows must show the expected top candidate for all five phrases
before a release is tagged.
