# Windows installer (Weasel)

Users install [Weasel](https://rime.im/download/) first, then add our
schema package. Two supported paths:

## Option A — Inno Setup installer (recommended)

1. Grab `hakka-huiyang-rime-vX.Y.Z-setup.exe` from the GitHub Release.
2. Double-click. The installer:
   - Detects the Weasel user directory (`%APPDATA%\Rime`).
   - Copies `hakka_huiyang.schema.yaml` + `hakka_huiyang.dict.yaml`.
   - Invokes `WeaselDeployer.exe /deploy` to rebuild the prism.
3. Right-click the Weasel tray icon → **Schema List** → tick
   **惠陽客家話 (Hagfa Pinyim)**.

Build the `.exe` locally:

```powershell
iscc installers\windows\rime-hakka.iss
```

## Option B — plum's `rime-install.bat`

1. Install the [plum Windows bootstrap](https://github.com/rime/plum-windows-bootstrap).
2. Download `hakka-huiyang-rime-vX.Y.Z.zip` from the GitHub Release.
3. Drag the zip onto the `rime-install.bat` shortcut.
4. The deployer auto-runs.

## Troubleshooting

- **"Schema not in list"** — run `WeaselDeployer.exe /deploy` manually,
  then reopen the schema-list menu.
- **"Unknown syllable" beeps while typing** — the dict didn't build.
  Check `%APPDATA%\Rime\rime.log` for parse errors and open an issue.
