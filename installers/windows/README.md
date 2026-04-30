# Windows — Hakka Input Method (Weasel)

This guide walks through installing the Hakka (Huiyang) input method on Windows,
step by step. No technical knowledge is required.

---

## What gets installed

- **Weasel** — the Rime input engine for Windows, which runs in your system tray
  and powers the keyboard.
- **The Hakka schema** — the dictionary and rules that make Weasel understand
  Hakka romanisation (Hagfa Pinyim).

---

## Option A — Setup installer (recommended)

The easiest way. The installer handles everything, including downloading and
installing Weasel automatically if it is not already on your computer.

### 1. Download the installer

Go to the [rime-hakka Releases page](https://github.com/Hydramus/rime-hakka/releases)
and download **`hakka-huiyang-rime-vX.Y.Z-setup.exe`** (under Assets).

> **Screenshot placeholder:** `docs/screenshots/windows-release-download.png`
> *(Take a screenshot of the GitHub Releases page with the .exe highlighted.)*

### 2. Run the installer

Double-click the downloaded `.exe` file.

> **Windows SmartScreen warning:** Windows may show a blue "Windows protected
> your PC" dialog the first time. Click **More info → Run anyway**. This appears
> because the installer is not yet code-signed.

> **Screenshot placeholder:** `docs/screenshots/windows-smartscreen.png`

### 3. Install Weasel (if prompted)

If Weasel is not already installed, the setup will offer to download and install
it automatically (~12 MB). Click **OK** and accept the Windows security prompt
(UAC) that appears — this is normal and required for Weasel to register as an
input method.

> **Screenshot placeholder:** `docs/screenshots/windows-weasel-uac.png`

### 4. Complete the installer

Follow the remaining steps in the installer. When it finishes, tick
**"Deploy Rime schema"** so the Hakka dictionary is built immediately.

> **Screenshot placeholder:** `docs/screenshots/windows-installer-finish.png`

---

## Option B — Manual zip install

Use this if you already have Weasel installed and just want to add the schema.

1. Download `hakka-huiyang-rime-vX.Y.Z.zip` from the
   [Releases page](https://github.com/Hydramus/rime-hakka/releases).
2. Extract the zip — you will get two files:
   - `hakka_huiyang.schema.yaml`
   - `hakka_huiyang.dict.yaml`
3. Press **`Win + R`**, type `%APPDATA%\Rime` and press Enter — this opens your
   Rime data folder.
4. Copy both files into that folder.
5. Right-click the **Weasel tray icon** (system tray, bottom-right) →
   **Deploy**.

> **Screenshot placeholder:** `docs/screenshots/windows-rime-folder.png`
> *(Take a screenshot of the %APPDATA%\Rime folder with the files copied in.)*

---

## Activating the Hakka schema in Weasel

After installing, you need to switch on the Hakka schema:

1. Look for the **Weasel tray icon** in the system tray (bottom-right corner of
   the taskbar — you may need to click the **^** arrow to see hidden icons)
2. Right-click the icon → **Schema List** (方案選單)

   > **Screenshot placeholder:** `docs/screenshots/windows-weasel-tray-menu.png`

3. Tick **惠陽客家話 (Hagfa Pinyim)**
4. Click **OK** — Weasel rebuilds and the schema is ready

   > **Screenshot placeholder:** `docs/screenshots/windows-weasel-schema-list.png`

---

## Switching to the Hakka keyboard while typing

Once set up, you can switch to Hakka input at any time in any application:

- Press **`Win + Space`** to cycle through your installed input methods until
  Weasel is selected
- Or click the **language indicator** (e.g. `ENG`) in the taskbar and select
  **中 Weasel**

> **Screenshot placeholder:** `docs/screenshots/windows-language-switcher.png`

When Weasel is active, type in Hagfa Pinyim romanisation and a candidate list
will appear near your cursor. Press a **number key** (1–9) to select a
character, or **Space** to accept the first suggestion.

> **Screenshot placeholder:** `docs/screenshots/windows-candidate-list.png`

---

## Typing guide

| What you type | What appears |
|---|---|
| `ngitteu` | 日頭 |
| `tienho` | 天河 |
| `ciangcoi` | 青菜 |

Tone digits (1–6) are optional. `ngit5teu2` and `ngitteu` both produce 日頭.

---

## Upgrading

Download the latest `setup.exe` from the Releases page and run it — it will
update the schema files and redeploy automatically.

---

## Uninstalling

1. Open **Settings → Apps → Installed apps**
2. Search for **Rime Hakka** and click **Uninstall**

To also remove Weasel, search for **Weasel** in the same list and uninstall it.

---

## Troubleshooting

**"Schema not in list" after installing**
Right-click the Weasel tray icon → **Deploy**, wait a few seconds, then
reopen the Schema List menu.

**Weasel tray icon is not visible**
Click the **^** arrow in the system tray to show hidden icons. If Weasel is
not there at all, try restarting Windows — the input method registers on login.

**Windows shows "Windows protected your PC" and won't let me run anyway**
The installer is not yet code-signed. Click **More info** first — the
**Run anyway** button will then appear.

**"Unknown syllable" or no candidates appear while typing**
The dictionary may not have deployed correctly. Right-click the Weasel tray
icon → **Deploy**, then try typing again. If the problem persists, check
`%APPDATA%\Rime\rime.log` for errors and
[open an issue](https://github.com/Hydramus/rime-hakka/issues).
