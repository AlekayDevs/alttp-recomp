#!/usr/bin/env python3
"""Revisa la traduccion (games/alttp_usa/lang/es.txt y es_menu.txt) sin ejecutar el juego.

  python3 scripts/check_text.py [roms/alttp_usa.sfc]        # sale con 1 si hay algun fallo

es.txt: mide cada linea de pantalla con la tabla de anchos de la ROM (0E:CADF) y avisa de las que pasan de 168 pixeles
(el motor del juego corta lo que pasa de ahi); avisa de caracteres que text.c no sabe escribir, de comandos mal cerrados y de
signos de apertura (¿ ¡) que no casan con los de cierre dentro de un mensaje.
es_menu.txt: comprueba que cada texto solo lleva A-Z, espacio y ? y que no pasa del maximo de letras que dice su comentario.

La ROM solo se lee en memoria para sacar las anchuras: no se escribe nada de ella.
"""
import re
import struct
import sys
import zlib
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
LANG = ROOT / "games" / "alttp_usa" / "lang"
MAX_PX = 168
CRC = 0x777AAC2F
WIDTHS = 0x0ECADF      # ancho de cada codigo, hasta el $62
CMD_LEN = 0x0ED36B     # longitud de cada comando ($67-$7E)
SPACE = 0x59
PUNCT = {"!": 0x3E, "?": 0x3F, ".": 0x41, ",": 0x42, "'": 0x51}
BREAKS = {0x73, 0x74, 0x75, 0x76, 0x7E, 0x7F}   # fin de linea de pantalla, espera o fin del mensaje
# letras con acento: (codigo propio, ancho propio o None = el de la letra base)
ACCENT = {"á": (0x5A, "a"), "é": (0x5F, "e"), "í": (0x60, 4), "ó": (0x61, "o"), "ú": (0x62, "u"),
          "ñ": (0x47, "n"), "¿": (0x48, "?"), "¡": (0x49, "!")}
PLAIN = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N", "Ü": "U", "ü": "u"}


def lorom(bank, addr):
    return bank * 0x8000 + (addr - 0x8000)


def read_rom(path):
    data = Path(path).read_bytes()
    if len(data) % 1024 == 512:        # cabecera de copiador
        data = data[512:]
    if zlib.crc32(data) & 0xFFFFFFFF != CRC:
        sys.exit(f"{path}: no es la ROM USA de A Link to the Past (CRC32 777AAC2F)")
    return data


def code_of(ch):
    if "A" <= ch <= "Z":
        return ord(ch) - 65
    if "a" <= ch <= "z":
        return 0x1A + ord(ch) - 97
    if "0" <= ch <= "9":
        return 0x34 + ord(ch) - 48
    if ch == " ":
        return SPACE
    return PUNCT.get(ch)


def width_of(ch, w):
    """Ancho en pixeles de un caracter del texto (None si text.c no lo sabe escribir)."""
    if ch in PLAIN:
        ch = PLAIN[ch]
    if ch in ACCENT:
        own, base = ACCENT[ch]
        return base if isinstance(base, int) else w[code_of(base)]
    c = code_of(ch)
    return None if c is None else w[c]


def measure(text, w, cmd_len):
    """Divide un mensaje en lineas de pantalla y devuelve [(pixeles, texto)] y los fallos de lectura."""
    lines, errors = [], []
    cur, px, i, n = [], 0, 0, len(text)
    text = text.replace("\r", "").replace("\n", "")
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "{":
            j = text.find("}", i)
            if j < 0 or (j - i - 1) % 2 or j == i + 1 or not re.fullmatch(r"[0-9A-Fa-f]+", text[i + 1:j]):
                errors.append("llave mal cerrada o con digitos que no son hexadecimales")
                break
            bytes_ = bytes.fromhex(text[i + 1:j])
            k = 0
            while k < len(bytes_):
                b = bytes_[k]
                if b < 0x67:               # un codigo de la fuente ({43}, {5B}...)
                    px += w[b] if b < len(w) else 0
                    cur.append("{%02X}" % b)
                    k += 1
                else:                      # un comando con sus parametros
                    ln = cmd_len[b] if 0x67 <= b < 0x7F and cmd_len[b] else 1
                    if b in BREAKS:
                        lines.append((px, "".join(cur)))
                        cur, px = [], 0
                    k += ln
            i = j + 1
            continue
        wd = width_of(ch, w)
        if wd is None:
            errors.append(f"caracter que el juego no puede escribir: {ch!r}")
        else:
            px += wd
        cur.append(ch)
        i += 1
    if cur:
        lines.append((px, "".join(cur)))
    return lines, errors


def parse_messages(path):
    """{numero: (linea donde empieza, texto)}"""
    msgs, num, start, buf = {}, None, 0, []
    for ln, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if raw.startswith("#"):
            continue
        m = re.fullmatch(r"@(\d+)", raw.strip())
        if m:
            if num is not None:
                msgs[num] = (start, "".join(buf))
            num, start, buf = int(m.group(1)), ln, []
        elif num is not None:
            buf.append(raw)
    if num is not None:
        msgs[num] = (start, "".join(buf))
    return msgs


def check_es(rom):
    w = list(rom[lorom(0x0E, 0xCADF & 0xFFFF):][:0x63])
    cmd_len = list(rom[lorom(0x0E, 0xD36B):][:0x80])   # se indexa por el propio byte del comando, como en text.c
    path = LANG / "es.txt"
    msgs = parse_messages(path)
    bad, worst = [], []
    for num, (ln, text) in sorted(msgs.items()):
        lines, errors = measure(text, w, cmd_len)
        for e in errors:
            bad.append(f"es.txt:{ln} @{num:03d}: {e}")
        for px, t in lines:
            worst.append((px, num, ln))
            if px > MAX_PX:
                bad.append(f"es.txt:{ln} @{num:03d}: {px} px (maximo {MAX_PX}): {t[:60]}")
        plain = re.sub(r"\{[0-9A-Fa-f]+\}", "", text)
        for open_c, close_c, name in (("¿", "?", "?"), ("¡", "!", "!")):
            if plain.count(open_c) != plain.count(close_c):
                bad.append(f"es.txt:{ln} @{num:03d}: {plain.count(open_c)} '{open_c}' y {plain.count(close_c)} '{close_c}'")
    worst.sort(reverse=True)
    print(f"es.txt: {len(msgs)} mensajes, {sum(1 for _ in worst)} lineas; la mas ancha {worst[0][0]} px (@{worst[0][1]:03d}, linea {worst[0][2]})")
    return bad


def check_menu():
    bad, n = [], 0
    limit, path = None, LANG / "es_menu.txt"
    for ln, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"#.*hasta (\d+) letras", raw)
        if m:
            limit = int(m.group(1))
            continue
        if raw.startswith("#") or "=" not in raw:
            continue
        key, val = (s.strip() for s in raw.split("=", 1))
        n += 1
        # los nombres de objeto llevan dos filas separadas por | y pueden llevar guion; el limite del comentario es por fila
        if not re.fullmatch(r"[A-Z ?|-]*", val):
            bad.append(f"es_menu.txt:{ln} {key}: solo A-Z, espacio, ? (y | y - en los objetos) ({val!r})")
        if limit is not None:
            for row in val.split("|"):
                if len(row) > limit:
                    bad.append(f"es_menu.txt:{ln} {key}: {len(row)} letras en {row!r}, el comentario dice {limit}")
        limit = None
    print(f"es_menu.txt: {n} textos")
    return bad


def main():
    rom_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "roms" / "alttp_usa.sfc"
    if not rom_path.exists():
        print(f"check_text: no hay ROM en {rom_path}; se omite")
        return 0
    bad = check_es(read_rom(rom_path)) + check_menu()
    for b in bad:
        print("  FALLO", b)
    print("OK" if not bad else f"{len(bad)} fallos")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
