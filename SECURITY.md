# Security policy / Política de seguridad

## Reporting a vulnerability / Cómo avisar

Please **do not open a public issue** for a security problem. Use GitHub's private reporting instead:
**Security → Report a vulnerability** in this repository
(<https://github.com/AlekayDevs/alttp-recomp/security/advisories/new>).

No abras un issue público para un problema de seguridad: usa el aviso privado de GitHub (enlace de arriba).

Useful details: version (`v0.x`), system, what you did, what happened, and whether it needs a crafted ROM, save file or network position.

## What counts / Qué cuenta

- The launcher's **update mechanism** (version check, download, SHA-256 verification, replacing files) on Windows, Linux and Android.
- A **save, save state or ROM file** that makes the program run code it should not.
- A published **release asset** that does not match `SHA256SUMS`.
- Anything that sends your ROM, saves or personal data off your device. The only network connection the project makes is the optional version check.

## Verifying a download / Verificar una descarga

Each release ships a `SHA256SUMS` file. Compare it with your download:

```
# Linux / macOS
sha256sum -c --ignore-missing SHA256SUMS
# Windows (PowerShell)
Get-FileHash .\alttp-recomp-<version>-win64.zip -Algorithm SHA256
```

Releases are not code-signed yet, so Windows SmartScreen and some antivirus programs may warn about an unsigned program that compiles code at startup. Everything happens on your machine.

## Supported versions / Versiones con soporte

Only the [latest release](https://github.com/AlekayDevs/alttp-recomp/releases/latest).

## Out of scope / Fuera de alcance

Bugs in the recompiler, PPU, sound or runtime belong in [`snes-recomp`](https://github.com/AlekayDevs/snes-recomp); security problems there go through that repository's private reporting.
