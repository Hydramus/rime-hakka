# iOS (Hamster)

iOS doesn't allow custom IME engines to be published as libraries, but
[Hamster](https://github.com/imfuxiao/Hamster) is a librime-based
keyboard extension shipping on the App Store. Because it uses the same
engine, our release zip works without modification.

## Install

1. Install **仓输入法 (Hamster)** from the App Store.
2. In Hamster, open the built-in web server (**☰ → File Upload**).
3. From a desktop browser on the same Wi-Fi network, visit the URL
   Hamster shows and drag `hakka-huiyang-rime-vX.Y.Z.zip` onto the page.
   Hamster will unpack it into its Rime user dir.
4. Alternatively: download the zip into the iOS Files app and use
   Hamster's **Files Import** option.
5. In Hamster → **Schema Selection**, tick **惠陽客家話 (Hagfa Pinyim)** → **Deploy**.
6. iOS **Settings → General → Keyboard → Keyboards → Add New Keyboard →
   Hamster**, then enable **Allow Full Access**.

## Notes

- Hamster's App Store build lags the open-source HEAD. If a schema
  requires features not in the released build, the user must wait
  for Hamster's next update — we don't ship a custom iOS binary.
- There is no official Apple-side workaround for Gboard on iOS; users
  who want Hamster must install it as a third-party keyboard.
