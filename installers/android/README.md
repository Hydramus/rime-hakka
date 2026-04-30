# Android

Two Rime-based keyboards are available for Android. Both use the same
`librime` engine, so the exact same release zip works unmodified on either.

---

## Option 1 — fcitx5-android (recommended)

[fcitx5-android](https://github.com/fcitx5-android/fcitx5-android) is actively
maintained and available on Google Play and F-Droid.

### Install

1. Install **fcitx5-android** from
   [Google Play](https://play.google.com/store/apps/details?id=org.fcitx.fcitx5.android)
   or [F-Droid](https://f-droid.org/packages/org.fcitx.fcitx5.android).
2. Open the app → **Add-ons** → enable **RIME**.
   - If RIME is not listed, install the
     [RIME plugin APK](https://github.com/fcitx5-android/fcitx5-android/releases)
     from the GitHub releases page, then re-open Add-ons.
3. Download `hakka-huiyang-rime-vX.Y.Z.zip` from our GitHub Release and
   unzip it somewhere you can browse (e.g. your Downloads folder).
4. Copy all `.yaml` files from the zip into the fcitx5 Rime user data
   directory. The easiest ways:

   **Via the Files app (no PC needed):**
   Navigate to
   `Internal Storage → Android → data → org.fcitx.fcitx5.android → files → data → rime`
   and paste the `.yaml` files there.
   > On Android 11+ you may need a third-party file manager (e.g. **MiXplorer**,
   > **MT Manager**, or **Solid Explorer**) to access the `Android/data/` path,
   > since the stock Files app restricts access to other apps' data folders.

   **Via ADB (PC):**
   ```bash
   adb push *.yaml \
     /sdcard/Android/data/org.fcitx.fcitx5.android/files/data/rime/
   ```

5. Back in the fcitx5-android app → **Add-ons → RIME → Redeploy** (or tap the
   RIME entry and choose **Deploy**).
6. In the app's input method list, tick **惠陽客家話 (Hagfa Pinyim)**.
7. Android Settings → **System → Languages & Input → On-screen keyboards →
   Manage on-screen keyboards** → enable **fcitx5**.

---

## Option 2 — Trime (F-Droid only)

[Trime](https://github.com/osfans/trime) wraps the same `librime` engine.
The Google Play listing is no longer active; install from F-Droid instead.

### Install

1. Install Trime from [F-Droid](https://f-droid.org/packages/com.osfans.trime).
2. Download `hakka-huiyang-rime-vX.Y.Z.zip` from our GitHub Release.
3. Open Trime → **☰ → Schema Management → Import from ZIP**.
4. Select the downloaded zip. Trime copies the schema + dict into its
   user data and redeploys.
5. In Trime → **Keyboard → Select Schema**, tick **惠陽客家話 (Hagfa Pinyim)**.
6. Android Settings → **System → Languages & Input → On-screen keyboards →
   Manage on-screen keyboards** → enable Trime.

---

## Submission to Gboard (separate workstream)

See [`../../gboard-submission/README.md`](../../gboard-submission/README.md).
That is documentation-only and does not produce any code artifact here.
