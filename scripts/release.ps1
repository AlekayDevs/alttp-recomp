# Arma out\release\alttp-recomp-<version>-win64.zip: un solo ejecutable, alttp-recomp.exe (el lanzador del motor con el nombre
# del juego), más SDL2, TinyCC, README, licencia y games\ de este repositorio. El usuario descomprime, abre alttp-recomp.exe,
# elige su ROM y juega. snes-recomp.exe es el mismo programa con otro nombre (la línea de comandos del generador): no va.
# No lleva ROMs, partidas guardadas ni C generado: si algo así acaba en la carpeta, el script falla y no crea el zip.
#
#   powershell -File scripts\release.ps1 [-Engine <zip o carpeta de snes-port del motor>] [-Version 0.1.0] [-NoTcc]
#
# Sin -Engine usa el motor de la raíz de este repositorio (alttp-recomp.exe, sdl2\, toolchain\; ver scripts\update-engine.ps1).
#
# El paquete debe llevar el compilador del motor (toolchain\tcc\tcc.exe) para que quien solo quiere jugar no tenga que
# instalar ni descargar nada; si el zip del motor no lo trae, el script falla (salvo con -NoTcc).
# El zip del motor sale de `powershell -File scripts\release.ps1` en el repositorio snes-recomp.
param(
    [string]$Engine = "",
    [string]$Version = "0.1.0",
    [switch]$NoTcc
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$name = "alttp-recomp-$Version-win64"
$stage = Join-Path $root "out\release\$name"
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force $stage | Out-Null

# el motor: un zip (se descomprime) o la carpeta ya armada
if ($Engine -eq "") {
    foreach ($f in "alttp-recomp.exe", "sdl2", "toolchain", "README-engine.md", "LICENSE-engine") {
        if (Test-Path $f) { Copy-Item $f $stage -Recurse }
    }
} elseif ((Get-Item $Engine).PSIsContainer) {
    Copy-Item "$Engine\*" $stage -Recurse
} else {
    $tmp = Join-Path $root "out\release\engine-tmp"
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    Expand-Archive -Path $Engine -DestinationPath $tmp
    $inner = Get-ChildItem $tmp -Directory | Select-Object -First 1
    $src = if ($inner -and (Test-Path "$($inner.FullName)\snes-port.exe")) { $inner.FullName } else { $tmp }
    Copy-Item "$src\*" $stage -Recurse
    Remove-Item -Recurse -Force $tmp
}
# el nombre del juego (lo reconoce el programa: cualquiera que no sea snes-recomp es el lanzador) y sin la copia del generador
if (Test-Path "$stage\snes-port.exe") { Move-Item "$stage\snes-port.exe" "$stage\alttp-recomp.exe" -Force }
Remove-Item "$stage\snes-recomp.exe" -ErrorAction SilentlyContinue
if (-not (Test-Path "$stage\alttp-recomp.exe")) { Remove-Item -Recurse -Force $stage; throw "el motor no trae el ejecutable" }

# el icono del juego en lugar del del motor (recursos RT_ICON 1.. y RT_GROUP_ICON 1, como los escribe build.rs del motor)
if (Test-Path "scripts\alttp-recomp.ico") {
    Add-Type @"
using System; using System.Runtime.InteropServices;
public static class ResUpd {
    [DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)] public static extern IntPtr BeginUpdateResource(string f, bool del);
    [DllImport("kernel32.dll", SetLastError=true)] public static extern bool UpdateResource(IntPtr h, IntPtr type, IntPtr name, ushort lang, byte[] data, uint cb);
    [DllImport("kernel32.dll", SetLastError=true)] public static extern bool EndUpdateResource(IntPtr h, bool discard);
}
"@
    $ico = [System.IO.File]::ReadAllBytes((Resolve-Path "scripts\alttp-recomp.ico"))
    $count = [BitConverter]::ToUInt16($ico, 4)
    $h = [ResUpd]::BeginUpdateResource("$stage\alttp-recomp.exe", $false)
    if ($h -eq [IntPtr]::Zero) { Remove-Item -Recurse -Force $stage; throw "no puedo abrir alttp-recomp.exe para ponerle el icono" }
    $group = New-Object System.Collections.Generic.List[byte]
    $group.AddRange([byte[]](0, 0, 1, 0)); $group.AddRange([BitConverter]::GetBytes([uint16]$count))
    $ok = $true
    for ($i = 0; $i -lt $count; $i++) {
        $e = 6 + 16 * $i
        $size = [BitConverter]::ToUInt32($ico, $e + 8); $offset = [BitConverter]::ToUInt32($ico, $e + 12)
        $img = New-Object byte[] $size; [Array]::Copy($ico, $offset, $img, 0, $size)
        $ok = $ok -and [ResUpd]::UpdateResource($h, [IntPtr]3, [IntPtr]($i + 1), 0x0409, $img, $size)
        $group.AddRange([byte[]]$ico[$e..($e + 11)]); $group.AddRange([BitConverter]::GetBytes([uint16]($i + 1)))
    }
    $g = $group.ToArray()
    $ok = $ok -and [ResUpd]::UpdateResource($h, [IntPtr]14, [IntPtr]1, 0x0409, $g, $g.Length)
    [void][ResUpd]::EndUpdateResource($h, (-not $ok))
    if (-not $ok) { Remove-Item -Recurse -Force $stage; throw "no se pudo poner el icono del juego en alttp-recomp.exe" }
}

# quien solo quiere jugar no tiene compilador: el paquete lleva el del motor
if (-not $NoTcc -and -not (Test-Path "$stage\toolchain\tcc\tcc.exe")) {
    Remove-Item -Recurse -Force $stage
    throw "el motor no trae toolchain\tcc\tcc.exe: usa un zip del motor con TinyCC (release.ps1 del motor, sin -NoTcc) o pasa -NoTcc para armar un paquete que pide descargarlo"
}

# el juego: su README sustituye al del motor, y su licencia va junto a la del motor
if (Test-Path "$stage\README.md") { Move-Item "$stage\README.md" "$stage\README-engine.md" -Force }
if (Test-Path "$stage\LICENSE") { Move-Item "$stage\LICENSE" "$stage\LICENSE-engine" -Force }
Copy-Item README.md, README.es.md, LICENSE $stage
Copy-Item games $stage -Recurse
# lo lee el aviso de version nueva del lanzador (src/update.rs del motor): repo y version instalada
Set-Content -Path "$stage\update.info" -Value "repo=AlekayDevs/alttp-recomp`nversion=$Version`nname=ALttP Recomp`ntagline=The Legend of Zelda: A Link to the Past" -Encoding ASCII

# la guarda: nada de ROMs, partidas guardadas ni C generado
$bad = Get-ChildItem $stage -Recurse -File | Where-Object {
    $_.Extension -in ".sfc", ".smc", ".srm", ".sst", ".thumb", ".fig", ".swc" -or
    $_.Name -like "rom_*.c" -or $_.Name -in "snes_entry.c", "snes_funcs.h", "snes_headless.c", "snes_play.c"
}
if ($bad) {
    $bad | ForEach-Object { Write-Error "prohibido en el paquete: $($_.FullName)" -ErrorAction Continue }
    Remove-Item -Recurse -Force $stage
    throw "el paquete llevaria ficheros de ROM o C generado: no se crea el zip"
}

$zip = Join-Path $root "out\release\$name.zip"
if (Test-Path $zip) { Remove-Item -Force $zip }
Compress-Archive -Path $stage -DestinationPath $zip
Write-Host "creado $zip ($([math]::Round((Get-Item $zip).Length / 1MB, 1)) MiB)"
