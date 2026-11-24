#!/usr/bin/env python3
"""Una ruta de pulsaciones, una sola fuente para nuestro runtime y para BizHawk.

Formato de ruta (texto, UTF-8; '#' empieza un comentario):
    @frames 5400                 fotogramas totales (por defecto: el final de la última pulsación + 60)
    @sample 60 0010:2 00A0:1     cada 60 fotogramas vuelca esas direcciones de WRAM (hex, offset en $7E0000:longitud)
    A-B BOTONES                  pulsa BOTONES desde el fotograma A hasta el B (incluidos)
    A+N BOTONES                  igual, durante N fotogramas
BOTONES: B Y SELECT START UP DOWN LEFT RIGHT A X L R, unidos con '+' (p. ej. UP+A).

Uso:
    route.py ruta.txt args            # los --press y --frames para headless (uno por línea)
    route.py ruta.txt lua SALIDA.txt  # script de BizHawk; el volcado de @sample va a SALIDA.txt
    route.py ruta.txt check           # solo valida y resume
Las rutas se pueden subir (son entradas del jugador); los volcados y los estados, no.
"""
import re
import sys

BUTTONS = ["B", "Y", "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT", "A", "X", "L", "R"]
BIZ = {"B": "B", "Y": "Y", "SELECT": "Select", "START": "Start", "UP": "Up", "DOWN": "Down",
       "LEFT": "Left", "RIGHT": "Right", "A": "A", "X": "X", "L": "L", "R": "R"}


class RouteError(Exception):
    pass


def parse(text):
    frames = None
    samples = []          # (cada, [(dirección, longitud)])
    presses = []          # (inicio, fin, [botones])
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        w = line.split()
        try:
            if w[0] == "@frames":
                frames = int(w[1])
            elif w[0] == "@sample":
                every = int(w[1])
                if every < 1 or len(w) < 3:
                    raise ValueError
                spans = []
                for s in w[2:]:
                    a, _, l = s.partition(":")
                    addr, length = int(a, 16), int(l or "1")
                    if not 0 <= addr < 0x20000 or length < 1 or addr + length > 0x20000:
                        raise ValueError
                    spans.append((addr, length))
                samples.append((every, spans))
            else:
                m = re.fullmatch(r"(\d+)([-+])(\d+)", w[0])
                if not m or len(w) != 2:
                    raise ValueError
                a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
                end = b if op == "-" else a + b - 1
                if end < a:
                    raise ValueError
                btns = w[1].split("+")
                if any(x not in BUTTONS for x in btns):
                    raise ValueError
                presses.append((a, end, btns))
        except (ValueError, IndexError):
            raise RouteError(f"línea {n}: no entiendo «{raw.strip()}»")
    last = max((p[1] for p in presses), default=0)
    if frames is None:
        frames = last + 60
    elif frames <= last:
        raise RouteError(f"@frames {frames} termina antes de la última pulsación ({last})")
    return frames, samples, presses


def to_args(frames, presses):
    out = ["--frames", str(frames)]
    for a, b, btns in presses:
        out += ["--press", f"{'+'.join(btns)}@{a}-{b}"]
    return out


def to_lua(frames, samples, presses, out_path):
    L = []
    L.append("-- Generado por scripts/route.py; no editar a mano.")
    L.append(f'local out = io.open("{out_path.replace(chr(92), "/")}", "w")')
    L.append("local presses = {")
    for a, b, btns in presses:
        names = ", ".join(f'"P1 {BIZ[x]}"' for x in btns)
        L.append(f"  {{{a}, {b}, {{{names}}}}},")
    L.append("}")
    L.append("local samples = {")
    for every, spans in samples:
        s = ", ".join(f"{{{a}, {l}}}" for a, l in spans)
        L.append(f"  {{{every}, {{{s}}}}},")
    L.append("}")
    L.append(f"local total = {frames}")
    L.append("""client.speedmode(6400)
for f = 0, total do
  local pad = {}
  for _, p in ipairs(presses) do
    if f >= p[1] and f <= p[2] then for _, n in ipairs(p[3]) do pad[n] = true end end
  end
  joypad.set(pad)
  for _, s in ipairs(samples) do
    if f > 0 and f % s[1] == 0 then
      local parts = {}
      for _, sp in ipairs(s[2]) do
        local hex = {}
        for i = 0, sp[2] - 1 do hex[#hex + 1] = string.format("%02X", memory.readbyte(sp[1] + i, "WRAM")) end
        parts[#parts + 1] = string.format("%05X=%s", sp[1], table.concat(hex))
      end
      out:write(f, " ", table.concat(parts, " "), "\n")
    end
  end
  emu.frameadvance()
end
out:close()
client.exit()""")
    return "\n".join(L) + "\n"


def main(argv):
    sys.stderr.reconfigure(encoding="utf-8")
    if len(argv) < 3 or argv[2] not in ("args", "lua", "check") or (argv[2] == "lua") != (len(argv) == 4):
        sys.stderr.write(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            frames, samples, presses = parse(f.read())
    except (OSError, RouteError) as e:
        sys.stderr.write(f"error: {e}\n")
        return 2
    if argv[2] == "args":
        print("\n".join(to_args(frames, presses)))
    elif argv[2] == "lua":
        sys.stdout.write(to_lua(frames, samples, presses, argv[3]))
    else:
        print(f"{len(presses)} pulsaciones, {frames} fotogramas, {len(samples)} muestreos")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
