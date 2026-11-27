#!/usr/bin/env bash
# Arma out/release/alttp-recomp-<version>-linux-x86_64.tar.gz con el lanzador de Linux del motor (../snes-recomp/linux/build.sh):
# un ejecutable `alttp-recomp` con libtcc y SDL2 dentro. El usuario descomprime, abre `alttp-recomp`, elige su ROM y juega; no
# necesita compilador ni SDL2.
# No lleva ROMs, partidas, estados ni C generado: si algo así acaba en la carpeta, falla y no crea el paquete.
#   scripts/release.sh [version] [carpeta con snes-port y snes-recomp]
set -euo pipefail
cd "$(dirname "$0")/.."
# La versión sale del fichero VERSION de la raíz (la misma que lee release.ps1); si se pasa otra, falla.
ver="$(head -n1 VERSION | tr -d '[:space:]')"
[[ "$ver" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]] || { echo "VERSION no tiene una versión válida: '$ver'"; exit 1; }
[ -z "${1:-}" ] || [ "$1" = "$ver" ] || { echo "la versión $1 no coincide con VERSION ($ver): cambia el fichero VERSION"; exit 1; }
tags=$(git tag --points-at HEAD 2>/dev/null | grep -E '^v[0-9]' || true)
if [ -n "$tags" ] && ! grep -qx "v$ver" <<<"$tags"; then echo "HEAD está etiquetado $(echo $tags) pero VERSION es $ver"; exit 1; fi
[ -n "$tags" ] || echo "aviso: HEAD no tiene la etiqueta v$ver todavía" >&2
motor="${SNES_ENGINE_REPO:-../snes-recomp}"
[ -x "$motor/linux/build.sh" ] || { echo "falta $motor/linux/build.sh (el motor, rama con el lanzador de Linux)"; exit 1; }
name="alttp-recomp-$ver-linux-x86_64"
stage="out/release/$name"
"$motor/linux/build.sh" "$PWD/games/alttp_usa.toml" alttp-recomp
rm -rf "$stage"; mkdir -p "$stage"
cp -r "$motor/out/linux/alttp-recomp/." "$stage/"
cp README.md README.es.md LICENSE LICENSE-engine README-engine.md THIRD-PARTY.txt "$stage/"
printf 'repo=ArgoxDevs/alttp-recomp\nversion=%s\n' "$ver" > "$stage/update.info" # lo lee el aviso de versión nueva del lanzador
bad=$(find "$stage" -type f \( -iname '*.sfc' -o -iname '*.smc' -o -iname '*.srm' -o -iname '*.sst' -o -iname '*.thumb' -o -name 'rom_*.c' -o -name snes_entry.c -o -name snes_funcs.h \) -print)
[ -z "$bad" ] || { echo "El paquete lleva ficheros que no deben ir:"; echo "$bad"; rm -rf "$stage"; exit 1; }
tar -C out/release -czf "out/release/$name.tar.gz" "$name"
echo "out/release/$name.tar.gz"
