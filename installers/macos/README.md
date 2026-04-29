# macOS — Hakka Input Method (Squirrel)

This guide walks through installing the Hakka (Huiyang) input method on macOS,
step by step. No technical knowledge is required.

---

## What gets installed

- **Squirrel** (`squirrel-app`) — the Rime input engine for macOS, which runs in
  your menu bar and powers the keyboard.
- **The Hakka schema** — the dictionary and rules that make Squirrel understand
  Hakka romanisation (Hagfa Pinyim).

---

## Option A — Install via Homebrew (recommended)

Homebrew is a free package manager for macOS. If you already have it, this is
the easiest path.

### 1. Install Homebrew (skip if already installed)

Open **Terminal** (search "Terminal" in Spotlight — press `⌘ Space`) and paste:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen prompts.

### 2. Install the Hakka input method

Paste both lines into Terminal one at a time:

```bash
brew tap Hydramus/tap
brew install --cask rime-hakka-huiyang
```

Homebrew will automatically install Squirrel first, then the Hakka schema on top
of it. You do not need to install Squirrel separately.

> **Screenshot placeholder:** `docs/screenshots/macos-brew-install.png`
> *(Take a screenshot of Terminal after the install completes.)*

---

## Option B — Manual install (without Homebrew)

### 1. Install Squirrel

Download and install **Squirrel** from the [Squirrel releases page](https://github.com/rime/squirrel/releases).
Open the `.pkg` and follow the installer.

### 2. Install the Hakka schema

Download `hakka-huiyang-rime-vX.Y.Z.pkg` from the
[rime-hakka Releases page](https://github.com/Hydramus/rime-hakka/releases).

Double-click to open it. If macOS blocks it ("unidentified developer"), instead
**right-click → Open**, then click **Open** in the dialog.

> **Screenshot placeholder:** `docs/screenshots/macos-gatekeeper-open.png`
> *(Take a screenshot of the Gatekeeper "unidentified developer" dialog.)*

Follow the installer steps. The schema files are automatically copied into
`~/Library/Rime/` and Squirrel is reloaded.

---

## First-time setup: enabling Squirrel as an input source

After installing Squirrel, you need to tell macOS to use it.

1. Open **System Settings** → **Keyboard**
2. Click **Text Input → Edit…** next to Input Sources

   > **Screenshot placeholder:** `docs/screenshots/macos-system-settings-keyboard.png`

3. Click **+** (bottom-left of the panel)
4. In the search box type **Cantonese** or scroll to find **鼠鬚管 Squirrel** under
   Chinese
5. Click **Add**

   > **Screenshot placeholder:** `docs/screenshots/macos-add-input-source.png`

6. Make sure **Show Input menu in menu bar** is ticked — this adds the keyboard
   icon to your menu bar so you can switch languages easily.

---

## Activating the Hakka schema in Squirrel

Once Squirrel is running, you need to switch on the Hakka schema:

1. Look for the **Squirrel icon** (a chipmunk / 鼠) in your menu bar
2. Click it → **Schema List** (輸入方案選單)

   > **Screenshot placeholder:** `docs/screenshots/macos-squirrel-menu.png`

3. Tick **惠陽客家話 (Hagfa Pinyim)**
4. Click **OK** — Squirrel redeploys and the schema is ready

   > **Screenshot placeholder:** `docs/screenshots/macos-squirrel-schema-list.png`

---

## Switching to the Hakka keyboard while typing

Once set up, you can switch to Hakka input at any time:

- Click the **input source icon** in the menu bar and select **鼠鬚管 Squirrel**
- Or press **`Ctrl + Space`** or **`Caps Lock`** to cycle through your input sources

> **Screenshot placeholder:** `docs/screenshots/macos-input-menu.png`

When Squirrel is active, type in Hagfa Pinyim romanisation and a candidate list
will appear above the cursor. Press a **number key** (1–9) to select a character,
or **Space** to accept the first suggestion.

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

When a new version is released, run:

```bash
brew upgrade --cask rime-hakka-huiyang
```

If you installed manually, download the new `.pkg` from the Releases page and
run it — it overwrites the old schema files automatically.

---

## Uninstalling

**Homebrew:**

```bash
brew uninstall --cask rime-hakka-huiyang
```

This removes the Hakka schema. To also remove Squirrel:

```bash
brew uninstall --cask squirrel-app
```

**Manual:** Delete these files from `~/Library/Rime/`:

- `hakka_huiyang.schema.yaml`
- `hakka_huiyang.dict.yaml`

Then remove Squirrel from System Settings → Keyboard → Input Sources if desired.

---

## Building the .pkg (for developers)

```bash
bash installers/macos/build-pkg.sh <version>
```

Produces `dist/hakka-huiyang-rime-v<version>.pkg`. Requires Xcode command-line
tools (`pkgbuild`).
