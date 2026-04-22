# Linux packaging (fcitx5-rime)

On Linux, we drop the schema into `/usr/share/rime-data/` — the shared
data directory used by **both** KDE Plasma (fcitx5-rime via Plasma
IM integration) and GNOME (fcitx5-rime as the input method framework).

## Users

### Debian / Ubuntu

```bash
wget https://github.com/<owner>/rime-hakka/releases/download/vX.Y.Z/rime-hakka-huiyang_X.Y.Z_all.deb
sudo dpkg -i rime-hakka-huiyang_X.Y.Z_all.deb
```

Then:

1. Open **Fcitx5 Configuration** (or `fcitx5-configtool`).
2. **Input Method → Add Input Method → Rime → Hakka (Huiyang) Hagfa Pinyim**.
3. Right-click the Fcitx5 tray icon → **Deploy** to rebuild.

### Arch / Manjaro (AUR)

```bash
yay -S rime-hakka-huiyang
```

### Manual (any distro)

```bash
sudo mkdir -p /usr/share/rime-data
sudo cp schemas/huiyang/*.yaml /usr/share/rime-data/
fcitx5-remote -r   # redeploy
```

## Building packages

- `.deb`:   `dpkg-buildpackage -us -uc` from `installers/linux/debian/`.
- Arch:     `makepkg -s` against `installers/linux/PKGBUILD`.

## KDE vs GNOME

Both desktops use fcitx5-rime as the backend, so the same package works
on both. The only difference is the configurator:

- KDE: System Settings → Regional Settings → Input Method.
- GNOME: install `fcitx5-configtool` separately (GNOME does not ship a
  native IME configurator).
