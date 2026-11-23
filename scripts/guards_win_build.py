# Windows (MSVC): construye guard.exe con contadores en cada guard (sin inyectar nada). Uso: python scripts/guards_win_build.py
import re, subprocess, sys, tomllib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
work = ROOT / "out" / "guards-win"
gen = work / "rom"; gen.mkdir(parents=True, exist_ok=True)
subprocess.run([str(ROOT/"snes-recomp.exe"), "codegen", str(ROOT/"roms/alttp_usa.sfc"), "--all", "-o", str(gen),
                "--game", "games/alttp_usa.toml"], cwd=ROOT, check=True, capture_output=True)
prof = tomllib.loads((ROOT/"games/alttp_usa.toml").read_text(encoding="utf-8"))
names = sorted({h["call"] for h in prof["hook"] if h["kind"] == "guard"})
q = gen/"game"/"quality.c"; body = q.read_text(encoding="utf-8")
w = ['\n#include <stdio.h>\n#include <stdlib.h>\n', f'static unsigned hits[{len(names)}][2];\n', 'static void report_guards(void) {\n']
for i, n in enumerate(names): w.append(f'printf("GUARD {n} %u %u\\n", hits[{i}][0], hits[{i}][1]);\n')
w.append('}\nstatic int registered_guards;\n')
for i, n in enumerate(names):
    body, c = re.subn(r'\bint ' + n + r'\(Cpu \*c\)', f'static int original_{n}(Cpu *c)', body)
    assert c == 1, n
    w.append(f'int {n}(Cpu *c) {{\nif (!registered_guards) {{ atexit(report_guards); registered_guards = 1; }}\n'
             f'int r = original_{n}(c); hits[{i}][!!r]++; return r;\n}}\n')
q.write_text(body + ''.join(w), encoding="utf-8")
vc = subprocess.check_output([r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe","-latest","-products","*","-property","installationPath"], text=True).strip() + r"\VC\Auxiliary\Build\vcvars64.bat"
(work/"b.bat").write_text(f'call "{vc}" >nul 2>&1\ncl /nologo /MP /O2 /TC /std:c11 /DSNES_RT_TICK /I"{gen}" "{gen}\*.c" "{gen}\game\*.c" /Fe:"{work}/guard.exe" /Fo:"{gen}\\\\" > "{work}/build.log" 2>&1\n')
(gen/"x").mkdir(exist_ok=True)
r = subprocess.run(["cmd","/c",str(work/"b.bat")]); print("cl rc", r.returncode)
