# Android (Trime)

Gboard does not accept third-party IME plugins, so the Android path
is [Trime](https://github.com/osfans/trime), which wraps the same
`librime` engine as Weasel, Squirrel, and fcitx5-rime. That means the
exact same release zip works unmodified.

## Install

1. Install Trime from [F-Droid](https://f-droid.org/packages/com.osfans.trime)
   -or [Google Play](https://play.google.com/store/apps/details?id=com.osfans.trime).-
2. Download `hakka-huiyang-rime-vX.Y.Z.zip` from our GitHub Release.
3. Open Trime → **☰ → Schema Management → Import from ZIP**.
4. Select the downloaded zip. Trime copies the schema + dict into its
   user data and redeploys.
5. In Trime → **Keyboard → Select Schema**, tick **惠陽客家話 (Hagfa Pinyim)**.
6. Android Settings → **System → Languages & Input → On-screen keyboards →
   Manage on-screen keyboards** → enable Trime.

## Submission to Gboard (separate workstream)

See [`../../gboard-submission/README.md`](../../gboard-submission/README.md).
That is documentation-only and does not produce any code artifact here.
