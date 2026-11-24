#!/usr/bin/env python3
"""Compara dos volcados de WRAM (`--sample` de headless y el .lua de scripts/route.py).

Cada línea: `FOTOGRAMA DIR=HEX DIR=HEX...`. Muestra, por dirección, el primer fotograma en que difieren
y cuántos de los comunes difieren; sale con 1 si alguno difiere.

    compare_samples.py nuestro.txt bizhawk.txt [--desfase N] [--ignorar DIR,DIR]

--desfase N: el fotograma f de BizHawk se compara con el f+N del nuestro (los dos arrancan con
alineaciones distintas; mira cuántos hacen falta con el módulo `$10` y ajústalo).
--ignorar: direcciones (hex) que no se comparan (p. ej. el contador `$1A` o lo que dependa del reloj).
"""
import sys


def load(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            w = line.split()
            if not w:
                continue
            try:
                rows[int(w[0])] = {int(a, 16): v for a, v in (x.split("=") for x in w[1:])}
            except ValueError:
                sys.exit(f"error: {path}:{n}: línea no válida")
    return rows


def main(argv):
    args, shift, ignore = [], 0, set()
    it = iter(argv[1:])
    for a in it:
        if a == "--desfase":
            shift = int(next(it, "x"))
        elif a == "--ignorar":
            ignore = {int(x, 16) for x in next(it, "").split(",") if x}
        else:
            args.append(a)
    if len(args) != 2:
        sys.stderr.write(__doc__)
        return 2
    ours, ref = load(args[0]), load(args[1])
    first, bad, total = {}, {}, 0
    for f in sorted(ref):
        o = ours.get(f + shift)
        if o is None:
            continue
        total += 1
        for addr, v in ref[f].items():
            if addr in ignore or addr not in o:
                continue
            if o[addr] != v:
                bad[addr] = bad.get(addr, 0) + 1
                first.setdefault(addr, (f, o[addr], v))
    print(f"{total} fotogramas comunes")
    for addr in sorted(first, key=lambda a: first[a][0]):
        f, o, r = first[addr]
        print(f"  {addr:05X}: primera diferencia en {f} (nuestro {o}, referencia {r}); {bad[addr]} de {total}")
    if not first:
        print("sin diferencias")
    return 1 if first else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
