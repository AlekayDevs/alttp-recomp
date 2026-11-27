# FAQ and common problems

[Español](FAQ.es.md) · Back to the [README](../README.md).

## Which ROM do I need?

The **USA** release of *The Legend of Zelda: A Link to the Past*, CRC32 **`777AAC2F`**. A ROM with a 512-byte copier header (`.smc`) is accepted too: the header is ignored. The European, Japanese and German releases, translations and ROM hacks have a different CRC32 and are refused; support for other regions is on the [roadmap](ROADMAP.md). A `.zip`, `.7z` or `.rar` is not a ROM: extract the `.sfc`/`.smc` first (the launcher says so). When a ROM is refused, the launcher shows its CRC32, its size, whether a header was removed and the usual causes (other region or revision, patch, hack, a file cut short).

To check yours (the checksum of the file without the header, if it has one):

```
python -c "import sys,zlib;d=open(sys.argv[1],'rb').read();d=d[512:] if len(d)%1024==512 else d;print('%08X'%zlib.crc32(d))" alttp_usa.sfc
```

The ROM is never included, uploaded or sent anywhere.

## Windows says "Windows protected your PC" (SmartScreen) or my antivirus blocks it

`alttp-recomp.exe` is not code-signed, and it generates and compiles C code on your machine the first time you open the game, which some antivirus programs distrust. Nothing is downloaded or sent: everything happens locally, and the source is in this repository and in [snes-recomp](https://github.com/ArgoxDevs/snes-recomp).

1. Check that the download is the one published: in PowerShell, `Get-FileHash .\alttp-recomp-X.Y-win64.zip` must match the line for that file in the release's `SHA256SUMS`.
2. SmartScreen: click **More info** and then **Run anyway**.
3. If your antivirus quarantines it, restore it and add the folder where you unzipped the game to its exclusions.

## Android: "Blocked by Play Protect" or "app not installed"

The APK is distributed outside the Play Store, so Android asks before installing it. Allow installs from your browser or file manager when it asks, and on the Play Protect warning choose **More details** and then **Install anyway**. It needs Android 10 or later on a 64-bit ARM phone (arm64); the Linux package is for x86_64 PCs only.

From version 0.12 the Android app has a different identifier, so it installs **next to** the old one and starts without saves; see the notes of that release.

## Where are my saves?

- **Windows:** the `saves\` folder next to `alttp-recomp.exe` (or `%APPDATA%\snes-port\saves` if that folder cannot be written).
- **Linux, the `.tar.gz` package:** `~/.local/share/alttp-recomp/saves` (`$XDG_DATA_HOME/alttp-recomp/saves`); the launcher passes that folder to the game, next to its own settings (language, last ROM). (Built from source with `snes-port`: `saves/` next to `snes-port`, or `~/.local/share/snes-port/saves` if that cannot be written.)
- **Android:** inside the app's own folder.

`.srm` is the game's save, `.sst` a save state and `.thumb` the miniature of a state.

## How do I check that my download is genuine?

Two checks. First, the SHA-256 in `SHA256SUMS` of the release must match your file (`sha256sum -c SHA256SUMS`, or `Get-FileHash` on Windows). Second, from the packages built by the project's CI workflows onwards, the Windows `.zip` and the Linux `.tar.gz` carry a signed *build provenance attestation* that says which workflow and commit produced them: `gh attestation verify <file> -R ArgoxDevs/alttp-recomp` (needs the [GitHub CLI](https://cli.github.com/); it fails if the file was changed by a single byte). Releases up to 0.16 were assembled by hand and have no attestation; the APK is signed with the project's Android key instead. The `.exe` itself is not code-signed, which is why SmartScreen warns (see above).

## Can I use a save from another emulator?

Not tested. Back up your files, copy the emulator's `.srm` over the game's `.srm` (same name as the ROM) and try it. If you do, please tell us in an issue whether it worked.

## Will my save states survive an update?

The in-game saves (`.srm`) always do. Save states (`.sst`) store a format number and the CRC32 of the ROM; if a future version changes the state format, older states will not load (nothing is lost: keep playing from your normal save). Save in the game's own menu before updating if you care about a state.

## What computer do I need?

Any recent PC runs it comfortably. Measured: an i5-13420H keeps 60 fps with the bundled TinyCC compiler with about 8 ms to spare per frame; a machine with half that power is on the edge, and the widescreen option (`wide`) costs extra. Without a window, a Celeron N4000 (about 1.1 GHz base) needs about 12 ms per frame with gcc, below the 16.6 ms budget. On Windows you do not need to install a compiler: TinyCC comes in the package.

## The first start takes a while

The first time, the launcher generates and compiles the game from your ROM (about 3 minutes with gcc, less with the bundled TinyCC on a fast PC). It is cached by the ROM's CRC32; the next starts are instant. `alttp-recomp.exe clean roms\alttp_usa.sfc` clears the cache if a change does not show.

## The game stopped with `UNSUPPORTED …`

That is a bug. Version 0.13 and earlier stop when you enter the rooms `0x01B`, `0x043` and `0x097` (a Link to the Past function was not translated); the fix is in 0.15. If you see it on a newer version, please [open an issue](https://github.com/ArgoxDevs/alttp-recomp/issues/new/choose) with the version, the exact message and where you were. Never attach the ROM, saves or screenshots with game graphics.

## How do I turn on the quality-of-life improvements?

In the **Game** tab of the F1 menu (on Android, Menu → Game options): one row per option, saved in `config.ini` (a help line under the list explains the one under the cursor; in Spanish with `language=es`). For a single run there is also `--game-opt name=value` on the command line (see the README).

## How do I add a language?

See [TRADUCCION.md](TRADUCCION.md) (in Spanish): a `lang/<xx>.txt` file with lines of at most 168 pixels, checked with `scripts/check_text.py`.
