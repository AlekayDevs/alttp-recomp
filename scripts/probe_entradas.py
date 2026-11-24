#!/usr/bin/env python3
"""Para cada entrada de mazmorra (0 a 0x84): ¿en qué sala cae y cuál es la mazmorra ($A0, $040C)?

    probe_entradas.py ROM EJECUTABLE_HEADLESS [DIR_TRABAJO]

El ejecutable debe saber `--sample` (headless del motor). Parte de la ruta de control (docs/rutas/control_casa.txt)
hasta el fotograma 5300, guarda ese estado y, por entrada, lo carga, pone la entrada como check_guards.py y deja correr
~400 fotogramas. Escribe entradas.txt: `entrada sala mazmorra módulo piso`. Nada de esto se sube (deriva de la ROM).
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd, cwd=None):
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=600, cwd=cwd)
    if p.returncode:
        raise RuntimeError(f"{cmd[0]} terminó con {p.returncode}: {p.stdout[-300:]}")
    return p


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    rom, exe = str(Path(argv[1]).resolve()), str(Path(argv[2]).resolve())
    work = Path(argv[3] if len(argv) > 3 else "out/probe").resolve()
    work.mkdir(parents=True, exist_ok=True)
    route = HERE.parent / "docs" / "rutas" / "control_casa.txt"
    args = subprocess.run([sys.executable, str(HERE / "route.py"), str(route), "args"], text=True,
                          capture_output=True, check=True).stdout.split()
    i = args.index("--frames")
    args[i + 1] = "5301"
    state = work / "base.sst"
    run([exe, rom, "--frame-blocks", "20000"] + args + ["--state-save", f"{state}@5300"])

    def one(n):
        out = work / f"e{n:02X}.txt"
        cmd = [exe, rom, "--frame-blocks", "20000", "--frames", "5750", "--state-load", f"{state}@5300",
               "--poke", f"0010E={n:02X}@5310", "--poke", "0010F=00@5310", "--poke", "00010=06@5310",
               "--poke", "00011=00@5310", "--poke", "000B0=00@5310",
               "--sample", f"{out.name}:5750:A0:2,40C:1,10:1,A4:1"]  # relativo: el ':' de una letra de unidad rompe --sample
        run(cmd, cwd=work)
        w = out.read_text().split()[1:]
        v = {a.split("=")[0]: a.split("=")[1] for a in w}
        sala = int(v["000A0"][2:] + v["000A0"][:2], 16)
        return n, sala, int(v["0040C"], 16), int(v["00010"], 16), int(v["000A4"], 16)

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(one, range(0x85)))
    with open(work / "entradas.txt", "w") as f:
        for r in rows:
            f.write("%02X %03X %02X %02X %02X\n" % r)
    print(f"{len(rows)} entradas en {work / 'entradas.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
