# Plan: demostrar que el juego se pasa (2026-11-24)

Cierra el §6 de [HALLAZGOS.md](HALLAZGOS.md): salas `0x01B`, `0x043` y `0x097`, recorrido natural contra BizHawk y partida completa.

## Lo que ya hay y lo que falta

- `headless` acepta `--press BOTON@A-B` (fotogramas), `--poke`, `--state-save/--state-load`, `--watch` y `--dump`. No hay grabación ni reproducción de entradas, ni muestreo periódico de la WRAM.
- El front (`play.c`) tiene `--state-script`, `--hash-wram` y F5/F7, pero tampoco graba entradas.
- Una ruta larga como lista de `--press` no cabe en la línea de órdenes: hace falta leerla de un fichero.
- BizHawk y Mesen2 están desinstalados. Receta de BizHawk en HALLAZGOS §5.4.

## Estado (2026-11-24)

- Fases 1 y 2 hechas: `scripts/route.py`, `scripts/compare_samples.py`, `--sample` (headless), `--record` y `--log-wram` (frontal). El script de BizHawk se ejecutó (HALLAZGOS §5.4).
- Fase 3: `scripts/probe_entradas.py` dio la mazmorra de cada entrada (HALLAZGOS §5.6); las salas 0x01B, 0x043 y 0x097 se cargan al forzarlas (HALLAZGOS §5.7), pero falta alcanzarlas jugando. Hay que jugar la partida: se puede grabar con `--record`.
- La grabación de entradas ya existe en el frontal: la partida completa se juega a mano y se graba.

## Fases

1. **Herramienta de ruta (aquí, `scripts/`)**: `route.txt` (una línea `fotograma botón-botón duración`) → `scripts/route.py` lo expande a `--press` y a un `.lua` de BizHawk con las mismas pulsaciones (`joypad.set` por fotograma). Una sola fuente para los dos.
2. **Muestreo de WRAM (hecho en nuestro lado, 2026-11-24)**: `headless --sample FICHERO:CADA:DIR[:LEN],...` (en `snes-recomp`, sin commitear) y `scripts/compare_samples.py` (primera diferencia por dirección, `--desfase`, `--ignorar`). Falta ejecutar el `.lua` en BizHawk. Idea original: sin cambiar el motor, `--dump` al final de tramos cortos (la ruta se parte en bloques de ~600 fotogramas con `--state-save`/`--state-load` encadenados) y el `.lua` vuelca las mismas direcciones cada N fotogramas. Comparar: `$10` (módulo), `$11` (submódulo), `$A0` (sala), `$22/$20` (X/Y de Link), `$7EF36C` (vida), `$7EF340..` (objetos). Si resulta incómodo, añadir al motor `--sample ADDR,LEN@CADA` (va en `snes-recomp`, es general).
3. **Primer hito: las tres salas.** Ruta hasta cada una desde una entrada conocida (la partida de `check.ps1` llega al módulo 7 en el fotograma 5300). Comprobar `$A0` y que `$AE/$AF` tomen 0x1C-0x1F; contar entradas a `01:CA17` con el ejecutable instrumentado. Hace falta saber qué mazmorra es cada sala: leer la cabecera `04:F502` y el nombre de la mazmorra en `$040C` al estar dentro.
4. **Segundo hito: recorrido natural contra BizHawk** de esa ruta, WRAM cada 60 fotogramas; informar de la primera divergencia (no se espera igualdad total: el audio y los ciclos no son idénticos, así que se compara un conjunto fijo de direcciones).
5. **Tercer hito: partida completa.** Guion largo por tramos, cada uno con su estado guardado al final (`saves/` ignorado por git) para reanudar sin repetir. Criterio de éxito: llegar a los créditos (módulo `$10` = 0x19) sin `UNSUPPORTED` ni parada. Es la parte más cara en tiempo; se hace por tramos y se anota cada uno en HALLAZGOS.

## Decisiones que necesito del usuario

- ¿Se instala BizHawk de nuevo (se desinstaló a petición del usuario) o se compara solo contra nuestro runtime?
- La partida completa: ¿jugarla a mano con el front y grabar las entradas (hay que añadir la grabación al motor) o escribir la ruta pulsación a pulsación? Recomendación: grabación en el front, es mucho más barata que escribirla a ciegas.

## Reglas

- Nada derivado de la ROM al repositorio: rutas (`route.txt`) sí, capturas, volcados y estados no.
- Los hallazgos van a HALLAZGOS.md; el motor se toca en `snes-recomp` y se commitea aparte.
