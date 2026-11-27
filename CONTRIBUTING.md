# Contributing

[Español](CONTRIBUTING.es.md)

This repository is the game (*A Link to the Past*, USA): its profile, the C that improves it and the scripts. The recompiler, the runtime and the launcher live in the engine, [`snes-recomp`](https://github.com/ArgoxDevs/snes-recomp), whose general rules (OpenSpec, clean-room, tests) are in its [CONTRIBUTING.md](https://github.com/ArgoxDevs/snes-recomp/blob/main/CONTRIBUTING.md). Anything about the translator, the PPU, the sound, the menu or the launcher goes there; anything specific to this game comes here.

## Rules that are not negotiable

- **Never the ROM or anything derived from it**: not in commits, issues or pull requests. That includes VRAM/WRAM dumps, screenshots with the game's graphics, the generated C, and table bytes copied from the ROM. `.gitignore` excludes `*.sfc`, `*.smc`, `*.srm`, `*.sst`, `*.thumb`, `roms/` and `out/`. Before opening a PR, with the engine built:

  ```
  .\alttp-recomp.exe recomp scan path\to\alttp_usa.sfc <folder with the exported commit>
  ```

  It must finish without error (export the commit with `git archive HEAD | tar -x -C <folder>`; scanning `.` always fails because it finds the ROM you keep in `roms\`).
- **Original code.** The C you add is clean-room. Public documentation about the game (community memory maps) may point you to an address, but the address is checked by hand against the real ROM.
- **Jump tables** are checked by hand before they go into `games/alttp_usa.toml`.
- **Improvements must not change the difficulty**: they only save steps, and are off by default (the only exception, `dialog_skip`, is on by default).

## What you can contribute

- **Game improvements:** `before` / `after` / `replace` / `guard` hooks in `games/alttp_usa.toml` with their C in `games/alttp_usa/`. They work over the original ROM and, if they could get in the way, have an option (`game_opt("key", default)`, passed with `--game-opt key=value`). State kept in C `static` variables must be recoverable from WRAM, because save states do not include it.
- **Addresses and tables** that are missing (`alttp-recomp.exe recomp discover <rom> --game games\alttp_usa.toml --unresolved` lists indirect jumps without a table).
- **Translations into other languages.** Like the Spanish one: text written for this project (`lang/xx.txt` and `lang/xx_menu.txt`, UTF-8, no BOM needed), screen lines of at most **168 pixels** (the sum of the widths in the ROM's font table, not the number of letters), checked with `python scripts/check_text.py roms/alttp_usa.sfc` (or `--sin-rom` for what does not need the ROM). Special characters are drawn on the fly from the game's own font, so only the USA ROM is needed. **We do not accept** importers that extract text or fonts from a ROM of another region, even if the extracted files are not uploaded. Open an issue first to agree on the approach (the engine's **F1** menu is separate and goes in `snes-recomp`).
- **Documentation** of how a part of the game works and of the addresses the hooks use. Write down what you find in [`docs/HALLAZGOS.md`](docs/HALLAZGOS.md).
- **Playthrough reports:** where you got stuck or the game stopped (`UNSUPPORTED …`), and on which version. A saved state from just before is very useful but derives from the ROM: **never attach it to a public issue**; say in the issue that you have one and we will arrange another way.

## Testing

```
powershell -File scripts\check.ps1          # Windows (needs your ROM, about 3 minutes)
scripts/check.sh                             # Linux
```

They generate the C with the engine, compile it and play scripted games. If you add a hook, extend the checks with the WRAM byte that changes (see how it is done for `$1CD9`) and add any new `.c` file to the list in **both** `check.ps1` and `check.sh` (CI checks it). To see an effect by hand: `alttp-recomp.exe roms\alttp_usa.sfc -- --game-opt name=value`.

## Commits and pull requests

- **Commit messages in English**, imperative, with the what and the why on the first line.
- Documentation is in Spanish, and also in English where an English version already exists (README, FAQ, changelog, this file).
- In the PR, say which ROM address you touch, how you checked it and with which ROM (without attaching anything from it).
- Questions that are not bugs ("which ROM do I need?", "it does not start") fit better in Discussions, once they are enabled, or in the [FAQ](docs/FAQ.md).
