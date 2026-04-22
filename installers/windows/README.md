# Windows installer (Weasel)

Users install [Weasel](https://rime.im/download/) first, then add our
schema package. Two supported paths:

## Option A — Manual zip install

1. Download `hakka-huiyang-rime-vX.Y.Z.zip` from the GitHub Release.
2. Extract the zip — you will get:
   - `hakka_huiyang.schema.yaml`
   - `hakka_huiyang.dict.yaml`
3. Copy both files into `%APPDATA%\Rime`.
4. Right-click the Weasel tray icon → **Deploy** to rebuild the prism.
5. Right-click the Weasel tray icon → **Schema List** → tick
   **惠陽客家話 (Hagfa Pinyim)**.

## Option B — plum's `rime-install.bat`

1. Install the [plum Windows bootstrap](https://github.com/rime/plum-windows-bootstrap).
2. Download `hakka-huiyang-rime-vX.Y.Z.zip` from the GitHub Release.
3. Drag the zip onto the `rime-install.bat` shortcut.
4. The deployer auto-runs.

## Option C — Inno Setup installer (developer build only)

The setup `.exe` is **not published to GitHub Releases** — it must be built
locally with [Inno Setup](https://jrsoftware.org/isinfo.php):

```powershell
iscc installers\windows\rime-hakka.iss
```

The output `dist\hakka-huiyang-rime-vX.Y.Z-setup.exe` can then be distributed
manually.

## Troubleshooting

- **"Schema not in list"** — run `WeaselDeployer.exe /deploy` manually,
  then reopen the schema-list menu.
- **"Unknown syllable" beeps while typing** — the dict didn't build.
  Check `%APPDATA%\Rime\rime.log` for parse errors and open an issue.
