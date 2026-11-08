#!/usr/bin/env python3
"""Integra los guard con la ROM real en Linux; todo lo generado queda en out/.

No sustituye partidas que reproduzcan cada bug. Instrumenta una copia del C
propio para contar llamadas desde el código recompilado, sin falsear retornos.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def verify(work):
    """Revisa los resultados guardados, sin regenerar ni recompilar el juego."""
    results = {}
    cases = ["off", "on", "bunny0", "bunny1"]
    cases += [p.name for p in sorted(work.glob("inject_*")) if p.is_dir()]
    for case in cases:
        log = (work / case / "stdout.txt").read_text()
        if "stop: frames reached\n" not in log or "frames: 5400\n" not in log:
            raise RuntimeError(f"{case}: la partida no completó los 5400 fotogramas")
        results[case] = {n: [int(a), int(b)] for n, a, b in
                         re.findall(r'^GUARD (\w+) (\d+) (\d+)$', log, re.M)}
    for file in ("wram.bin", "vram.bin", "cgram.bin", "oam.bin"):
        if (work / "off" / file).read_bytes() != (work / "on" / file).read_bytes():
            raise RuntimeError(f"Opciones encendidas alteran el recorrido de control: {file}")
    if any(v[1] for v in results["off"].values()):
        raise RuntimeError("Algún guard se activa con las opciones apagadas")
    if results["bunny0"]["alttp_bunny_walk_guard"][0] == 0:
        raise RuntimeError("El control del conejo no alcanzó su guard")
    if results["bunny0"]["alttp_bunny_walk_guard"][1] != 0:
        raise RuntimeError("El guard del conejo se activa con la opción apagada")
    if results["bunny1"]["alttp_bunny_walk_guard"][1] == 0:
        raise RuntimeError("El juego no alcanzó el guard del conejo temporal")
    if not all(sum(results["on"][n]) for n in
               ("alttp_camera_frame", "alttp_camera_guard",
                "alttp_skullwoods_guard", "alttp_stair_tags_guard")):
        raise RuntimeError("El recorrido no alcanzó los ganchos de control esperados")
    for name in ("alttp_stair_tags_guard", "alttp_skullwoods_guard", "alttp_camera_guard"):
        case = "inject_" + name
        if case in results and results[case][name][1] == 0:
            raise RuntimeError(f"{name}: no se ejecutó la rama de corrección")
    (work / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
    print("OK: recorrido de control idéntico y guard del conejo temporal alcanzado.", flush=True)
    print("Corazón, hada, escondido y seta se prueban con --poke; la puerta, además, con recorridos por mazmorras.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=ROOT / "roms/alttp_usa.sfc")
    parser.add_argument("--engine", type=Path,
                        default=ROOT.parent / "snes-recomp/target/release/snes-recomp")
    parser.add_argument("--verify-results", type=Path,
                        help="revisar una carpeta de resultados existente sin recompilar")
    parser.add_argument("--headless", type=Path,
                        help="usar un ejecutable instrumentado de una ejecución anterior")
    parser.add_argument("--only-sprites", action="store_true",
                        help="probar corazón y hada con --headless, sin repetir los recorridos de control")
    parser.add_argument("--only-hidden", action="store_true",
                        help="probar un objeto escondido con --headless")
    parser.add_argument("--only-mushroom", action="store_true",
                        help="probar una seta con --headless")
    args = parser.parse_args()
    if args.verify_results:
        verify(args.verify_results.resolve())
        return
    rom, engine = args.rom.resolve(), args.engine.resolve()
    # Una carpeta nueva por ejecución: no borra los resultados anteriores.
    (ROOT / "out").mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="guards-", dir=ROOT / "out"))
    print(f"Resultados: {work}", flush=True)
    profile = tomllib.loads((ROOT / "games/alttp_usa.toml").read_text())
    names = sorted({h["call"] for h in profile["hook"] if h["kind"] == "guard"})
    if args.headless:
        exe = args.headless.resolve()
    else:
        gen = work / "rom"
        with (work / "codegen.log").open("w") as log:
            subprocess.run([str(engine), "codegen", str(rom), "--all", "-o", str(gen),
                            "--game", "games/alttp_usa.toml"], cwd=ROOT,
                           stdout=log, stderr=log, check=True)
        quality = gen / "game/quality.c"
        body = quality.read_text()
        wrappers = ['\n#include <stdio.h>\n#include <stdlib.h>\n',
                    '#include <string.h>\n',
                    f'static unsigned hits[{len(names)}][2];\n',
                    'static void report_guards(void) {\n']
        for i, name in enumerate(names):
            wrappers.append(f'printf("GUARD {name} %u %u\\n", hits[{i}][0], hits[{i}][1]);\n')
        wrappers.append('}\nstatic int registered_guards;\n')
        for i, name in enumerate(names):
            body, count = re.subn(r'\bint ' + name + r'\(Cpu \*c\)',
                                 f'static int original_{name}(Cpu *c)', body)
            if count != 1:
                raise RuntimeError(f"No se encontró una única definición de {name}")
            inject = {
                "alttp_door_guard": ("0x11", "1"),
                "alttp_stair_tags_guard": ("0x11", "1"),
                "alttp_skullwoods_guard": ("0x10", "9"),
            }
            wrapper = (f'int {name}(Cpu *c) {{\n'
                       'if (!registered_guards) { atexit(report_guards); registered_guards = 1; }\n'
                       f'const char *inject = getenv("GUARD_INJECT");\n')
            if name in inject:
                addr, value = inject[name]
                wrapper += (f'if (inject && strcmp(inject, "{name}") == 0 && !hits[{i}][1]) {{\n'
                            f'uint8_t saved = wram_read8({addr}); wram_write8({addr}, {value});\n'
                            f'int r = original_{name}(c); wram_write8({addr}, saved);\n'
                            f'hits[{i}][!!r]++; return r;\n}}\n')
            elif name == "alttp_camera_guard":
                wrapper += (f'if (inject && strcmp(inject, "{name}") == 0 && !hits[{i}][1]) {{\n'
                            'uint8_t saved = camera_applied; camera_applied = 1;\n'
                            f'int r = original_{name}(c); camera_applied = saved;\n'
                            f'hits[{i}][!!r]++; return r;\n}}\n')
            wrapper += f'int r = original_{name}(c); hits[{i}][!!r]++; return r;\n}}\n'
            wrappers.append(wrapper)
        quality.write_text(body + ''.join(wrappers))
        exe = work / "headless"
        sources = sorted(gen.glob("*.c")) + sorted((gen / "game").glob("*.c"))
        print("Compilando el juego completo (puede tardar varios minutos)...", flush=True)
        with (work / "build.log").open("w") as log:
            subprocess.run([os.environ.get("CC", "gcc"), "-std=c11", "-O2", "-DSNES_RT_TICK",
                            "-I" + str(gen), *map(str, sources), "-o", str(exe), "-lm"],
                           stdout=log, stderr=log, check=True)
    inputs = ["START@1100-1110", "A@1300-1305", "A@1500-1504", "DOWN@1540-1542",
              "DOWN@1560-1562", "DOWN@1580-1582", "RIGHT@1600-1602", "RIGHT@1620-1622",
              "A@1640-1643", "A@2000-2004"]
    inputs += [f"A@{f}-{f+3}" for f in range(2100, 5200, 50)]
    base = [str(exe), str(rom), "--frames", "5400", "--frame-blocks", "20000"]
    for press in inputs:
        base += ["--press", press]
    options = ["fix_door_submodule", "fix_stair_tags", "fix_skullwoods_door",
               "fix_mushroom_warp", "fix_double_absorb", "fix_hidden_hookshot",
               "fix_camera_twice", "fix_bunny_walk"]
    results = {}

    def run(name, extra, inject=None):
        dest = work / name
        dest.mkdir()
        env = os.environ.copy()
        if inject:
            env["GUARD_INJECT"] = inject
        proc = subprocess.run(base + ["--dump", str(dest)] + extra,
                              text=True, capture_output=True, timeout=120, env=env)
        (dest / "stdout.txt").write_text(proc.stdout)
        (dest / "stderr.txt").write_text(proc.stderr)
        proc.check_returncode()
        if "stop: frames reached\n" not in proc.stdout or "frames: 5400\n" not in proc.stdout:
            raise RuntimeError(f"{name}: la partida no completó los 5400 fotogramas")
        counts = {n: [int(a), int(b)] for n, a, b in
                  re.findall(r'^GUARD (\w+) (\d+) (\d+)$', proc.stdout, re.M)}
        if set(counts) != set(names):
            raise RuntimeError(f"{name}: faltan contadores de integración")
        results[name] = counts
        (work / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
        print(name + ": " + json.dumps({n: v for n, v in counts.items() if sum(v)}), flush=True)
        return dest

    if args.only_sprites or args.only_hidden or args.only_mushroom:
        if not args.headless:
            parser.error("las pruebas de objetos requieren --headless")
        cases = ((("heart", "D8"), ("fairy", "E3")) if args.only_sprites else
                 (("hidden", "D8"),) if args.only_hidden else (("mushroom", "E7"),))
        for kind, sprite in cases:
            y = "64" if kind == "fairy" else "5C"
            extra = ["--poke", "0F36D=10@5250",
                       "--poke", "00DDF=09@5300", "--poke", f"00E2F={sprite}@5300",
                       "--poke", f"00D0F={y}@5300", "--poke", "00D1F=5B@5300",
                       "--poke", "00D2F=21@5300", "--poke", "00D3F=09@5300",
                       "--game-opt", "fix_double_absorb=1"]
            if kind == "fairy":
                # Su colisión usa $0F70=9: a la misma Y que Link no lo toca.
                for frame in range(5301, 5351):
                    extra += ["--poke", f"00D0F={y}@{frame}",
                              "--poke", f"00D1F=5B@{frame}"]
            if kind == "hidden":
                extra += ["--poke", "00E9F=01@5300", "--poke", "00DAF=07@5300",
                          "--game-opt", "fix_hidden_hookshot=1"]
            if kind == "mushroom":
                extra += ["--game-opt", "fix_mushroom_warp=1"]
            run(kind, extra)
            if kind == "heart" and results[kind]["alttp_heart_guard"][1] == 0:
                raise RuntimeError("El corazón no activó la rama de doble absorción")
            if kind == "hidden":
                if sum(results[kind]["alttp_hidden_hookshot_guard"]) == 0:
                    raise RuntimeError("El objeto escondido no alcanzó su gancho")
                if (work / kind / "wram.bin").read_bytes()[0x0DAF] != 0:
                    raise RuntimeError("El gancho no limpió la marca del objeto escondido")
                extra[-1] = "fix_hidden_hookshot=0"
                run("hidden_off", extra)
                if (work / "hidden_off" / "wram.bin").read_bytes()[0x0DAF] == 0:
                    raise RuntimeError("La marca se limpió también con la opción apagada")
            if kind == "fairy":
                if results[kind]["alttp_heart_guard"][1] == 0:
                    raise RuntimeError("El hada no activó la rama de doble absorción")
                off = extra.copy()
                off[off.index("fix_double_absorb=1")] = "fix_double_absorb=0"
                run("fairy_off", off)
                if results["fairy_off"]["alttp_heart_guard"][1] != 0:
                    raise RuntimeError("La rama del hada se activó con la opción apagada")
            if kind == "mushroom":
                if sum(results[kind]["alttp_mushroom_guard"]) == 0:
                    raise RuntimeError("La seta no llegó a su gancho")
                run("mushroom_sub1", [*extra, "--poke", "00011=01@5300"])
                if results["mushroom_sub1"]["alttp_mushroom_guard"][1] == 0:
                    raise RuntimeError("La seta no activó la rama del submódulo")
        return

    off = run("off", [])
    on = run("on", [a for opt in options for a in ("--game-opt", opt + "=1")])
    # Un recorrido normal sin activar condiciones de los bugs debe conservar el estado.
    for file in ("wram.bin", "vram.bin", "cgram.bin", "oam.bin"):
        if (off / file).read_bytes() != (on / file).read_bytes():
            raise RuntimeError(f"Opciones encendidas alteran el recorrido de control: {file}")
    # Estado temporal de conejo forzado mediante la interfaz real de pruebas.
    for opt in (0, 1):
        run(f"bunny{opt}", ["--poke", "0005D=1C@5300",
                              "--poke", "003F5=0001@5300",
                              "--press", "RIGHT@5301-5370",
                              "--game-opt", f"fix_bunny_walk={opt}"])
    for name, option, extra in (
        ("alttp_stair_tags_guard", "fix_stair_tags", []),
        ("alttp_skullwoods_guard", "fix_skullwoods_door", []),
        ("alttp_camera_guard", "fix_camera_twice", []),
        ("alttp_door_guard", "fix_door_submodule", ["--poke", "0006C=01@5300"]),
    ):
        case = "inject_" + name
        run(case, ["--game-opt", option + "=1", *extra], inject=name)
        if results[case][name][1] == 0:
            raise RuntimeError(f"{name}: no se ejecutó la rama de corrección")
    door_walks(exe, rom, base, work, results)
    verify(work)


# Recorridos naturales por mazmorras: entrada de mazmorra puesta con $010E y el módulo 6 (carga del subsuelo), y Link camina.
# Con las opciones encendidas y apagadas el estado final debe ser idéntico (no hay bug que corregir) y debe haberse
# pasado por el guard de la puerta.
DOOR_WALKS = {
    "castle": (2, "UP@5600-5900"),
    "east": (7, "UP@5600-5800 RIGHT@5800-5950 UP@5950-6100 LEFT@6100-6250"),
    "castle3": (3, "UP@5600-5750 LEFT@5750-5900 UP@5900-6050 RIGHT@6050-6250"),
    "castle8": (8, "UP@5600-5800 RIGHT@5800-5950 DOWN@5950-6100 LEFT@6100-6250"),
}


def door_walks(exe, rom, base, work, results):
    from concurrent.futures import ThreadPoolExecutor
    state = work / "base.sst"
    # La partida del recorrido de control hasta el fotograma 5300 (en la casa de Link), guardada como estado.
    subprocess.run(base + ["--state-save", f"{state}@5300"], text=True, capture_output=True,
                   timeout=300, check=True)
    options = ["fix_door_submodule", "fix_stair_tags", "fix_skullwoods_door", "fix_camera_twice"]

    def walk(job):
        name, (entrance, presses), opt = job
        dest = work / f"walk_{name}_{opt}"
        dest.mkdir()
        cmd = [str(exe), str(rom), "--frames", "6300", "--frame-blocks", "20000",
               "--state-load", f"{state}@5300",
               "--poke", f"0010E={entrance:02X}@5310", "--poke", "0010F=00@5310",
               "--poke", "00010=06@5310", "--poke", "00011=00@5310", "--poke", "000B0=00@5310"]
        for press in presses.split():
            cmd += ["--press", press]
        for o in options:
            cmd += ["--game-opt", f"{o}={opt}"]
        cmd += ["--dump", str(dest)]
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=300)
        (dest / "stdout.txt").write_text(proc.stdout)
        proc.check_returncode()
        counts = {n: [int(a), int(b)] for n, a, b in
                  re.findall(r'^GUARD (\w+) (\d+) (\d+)$', proc.stdout, re.M)}
        return name, opt, dest, counts

    jobs = [(n, w, o) for n, w in DOOR_WALKS.items() for o in (1, 0)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(walk, jobs))
    final = {(n, o): (d, c) for n, o, d, c in done}
    for name in DOOR_WALKS:
        (don, con), (doff, _) = final[(name, 1)], final[(name, 0)]
        for file in ("wram.bin", "vram.bin", "cgram.bin", "oam.bin"):
            if (don / file).read_bytes() != (doff / file).read_bytes():
                raise RuntimeError(f"walk_{name}: opciones encendidas alteran el recorrido ({file})")
        if sum(con["alttp_door_guard"]) == 0:
            raise RuntimeError(f"walk_{name}: no se alcanzó el guard de la puerta")
        results[f"walk_{name}"] = con
        print(f"walk_{name}: guard puerta {con['alttp_door_guard']}, estado idéntico con opciones", flush=True)


if __name__ == "__main__":
    main()
