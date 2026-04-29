# macOS installer (Squirrel)

## End users

1. Download `hakka-huiyang-rime-vX.Y.Z.pkg` from the GitHub Release.
2. Right-click → **Open** (unsigned installers need the Control-Open bypass).
3. The installer copies schemas into `~/Library/Rime/` and runs
   `Squirrel --reload`.
4. Click the Squirrel menubar icon → **Schema List** → tick
   **惠陽客家話 (Hagfa Pinyim)**.

## Homebrew tap

```bash
brew tap Hydramus/tap
brew install --cask rime-hakka-huiyang
```

To upgrade after a new release:

```bash
brew upgrade --cask rime-hakka-huiyang
```

## Building the .pkg

```bash
bash installers/macos/build-pkg.sh <version>
```

This produces `dist/hakka-huiyang-rime-v<version>.pkg`. Requires Xcode
command-line tools (`pkgbuild`, `productbuild`).
