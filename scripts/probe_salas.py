#!/usr/bin/env python3
"""Fuerza cada sala de mazmorra (0 a 0x127) y mira si el juego sigue: HALLAZGOS §5.7.

    probe_salas.py ROM EJECUTABLE_HEADLESS [DIR_TRABAJO]

El ejecutable debe saber `--state-save` y `--sample` (headless del motor actual). Parte de la ruta de control
(docs/rutas/control_casa.txt), entra por la entrada 2 (sala del trono del Castillo) y guarda el estado en el fotograma 5400 (módulo 7).
Por sala lo carga, escribe `$A0` = sala y `$11` = 7 (el módulo 7 carga la sala con sus rutinas de cambio de sala) (en el fotograma siguiente al del estado: los pokes del propio fotograma guardado no se aplican al cargarlo) y deja correr
300 fotogramas. Escribe salas.txt: `sala módulo $AE $AF $041A parada`. Una sala va mal si no acaba en módulo 7, si el motor se
detiene por otra cosa que no sea llegar al último fotograma o si sale `UNSUPPORTED`. Es un cambio de sala forzado: no sustituye a jugarlas.
Nada de esto se sube (deriva de la ROM).
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRAMES = 5700
FORCE = 5400


def run(cmd, cwd=None):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=900, cwd=cwd)


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    rom, exe = str(Path(argv[1]).resolve()), str(Path(argv[2]).resolve())
    work = Path(argv[3] if len(argv) > 3 else "out/probe_salas").resolve()
    work.mkdir(parents=True, exist_ok=True)
    route = HERE.parent / "docs" / "rutas" / "control_casa.txt"
    args = subprocess.run([sys.executable, str(HERE / "route.py"), str(route), "args"], text=True,
                          capture_output=True, check=True).stdout.split()  # split() quita también los \r de Windows
    args[args.index("--frames") + 1] = "5301"
    entrada = ["--poke", "0010E=02@5310", "--poke", "0010F=00@5310", "--poke", "00010=06@5310",
               "--poke", "00011=00@5310", "--poke", "000B0=00@5310"]
    base = work / "base.sst"
    p = run([exe, rom, "--frame-blocks", "20000"] + args + entrada + ["--frames", "5401", "--state-save", f"{base}@{FORCE}"])
    if p.returncode or not base.exists():
        sys.stderr.write(p.stdout[-400:] + p.stderr[-400:])
        return 1

    def one(sala):
        out = work / f"s{sala:03X}.txt"
        cmd = [exe, rom, "--frame-blocks", "20000", "--frames", str(FRAMES), "--state-load", f"{base}@{FORCE}",
               "--poke", f"000A0={sala & 255:02X}{sala >> 8:02X}@{FORCE + 1}", "--poke", f"00011=07@{FORCE + 1}",
               "--sample", f"{out.name}:{FRAMES}:A0:2,10:1,AE:2,41A:1"]  # nombre relativo: el ':' de una letra de unidad rompe --sample
        p = run(cmd, cwd=work)
        stop = next((l for l in p.stdout.splitlines() if l.startswith("stop:")), "stop: ?")
        bad = "UNSUPPORTED" in p.stdout or "UNSUPPORTED" in p.stderr
        try:
            v = dict(w.split("=") for w in out.read_text().split()[1:])
            modulo, ae, af, t = int(v["00010"], 16), int(v["000AE"][:2], 16), int(v["000AE"][2:], 16), int(v["0041A"], 16)
            a0 = int(v["000A0"][2:] + v["000A0"][:2], 16)
        except Exception:
            modulo = ae = af = t = a0 = -1
        ok = p.returncode == 0 and stop == "stop: frames reached" and not bad and modulo == 7 and a0 == sala
        return sala, modulo, ae, af, t, ("ok" if ok else f"MAL ({stop}{', UNSUPPORTED' if bad else ''}, rc={p.returncode})")

    with ThreadPoolExecutor(max_workers=2) as pool:  # con 6 el equipo se quedó sin memoria
        rows = list(pool.map(one, range(0x128)))
    with open(work / "salas.txt", "w") as f:
        for r in rows:
            f.write("%03X %02X %02X %02X %02X %s\n" % r)
    malas = [r for r in rows if r[5] != "ok"]
    print(f"{len(rows)} salas, {len(malas)} con problemas ({work / 'salas.txt'})")
    for r in malas:
        print("  %03X módulo=%02X %s" % (r[0], r[1], r[5]))
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
