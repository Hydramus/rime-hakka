#!/usr/bin/env bash
# Build a macOS .pkg installer for rime-hakka that drops schema + dict
# into ~/Library/Rime and redeploys Squirrel.
#
# Usage:
#   bash installers/macos/build-pkg.sh 0.1.0

set -euo pipefail

VERSION="${1:-0.1.0}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STAGE="$(mktemp -d)/rime-hakka"
SCRIPTS="$(mktemp -d)/scripts"

mkdir -p "$STAGE"
mkdir -p "$SCRIPTS"

cp "$ROOT/schemas/huiyang/hakka_huiyang.schema.yaml" "$STAGE/"
cp "$ROOT/schemas/huiyang/hakka_huiyang.dict.yaml"   "$STAGE/"

cat > "$SCRIPTS/postinstall" <<'POSTINSTALL'
#!/usr/bin/env bash
set -euo pipefail
USER_NAME="${USER:-$(stat -f %Su /dev/console)}"
USER_HOME="$(dscl . -read "/Users/$USER_NAME" NFSHomeDirectory | awk '{print $2}')"
RIME_DIR="$USER_HOME/Library/Rime"
mkdir -p "$RIME_DIR"
cp -f "/tmp/rime-hakka/hakka_huiyang.schema.yaml" "$RIME_DIR/"
cp -f "/tmp/rime-hakka/hakka_huiyang.dict.yaml"   "$RIME_DIR/"
chown -R "$USER_NAME" "$RIME_DIR"
SQUIRREL="/Library/Input Methods/Squirrel.app/Contents/MacOS/Squirrel"
if [ -x "$SQUIRREL" ]; then
  sudo -u "$USER_NAME" "$SQUIRREL" --reload || true
fi
exit 0
POSTINSTALL
chmod +x "$SCRIPTS/postinstall"

mkdir -p "$ROOT/dist"
PKG="$ROOT/dist/hakka-huiyang-rime-v$VERSION.pkg"

pkgbuild \
  --root "$STAGE" \
  --install-location "/tmp/rime-hakka" \
  --scripts "$SCRIPTS" \
  --identifier "im.rime.hakka.huiyang" \
  --version "$VERSION" \
  "$PKG"

shasum -a 256 "$PKG" | tee "$PKG.sha256"
echo "[ok] wrote $PKG"
