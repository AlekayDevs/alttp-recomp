# Hallazgos y técnicas

Registro de lo que se descubre al probar el juego, escrito para que sirva también a los otros ports (`dkc2-recomp`,
`minishcap-recomp`, `gba-recomp`...). Cada entrada dice qué pasó, cómo se comprobó y qué se aprendió. Lo específico de
ALttP (direcciones, salas) va marcado; lo general (método, trampas) sirve a cualquier juego. Volver al [README](../README.md).

## 1. Un stub no es «código que no se usa»: si se alcanza, el juego se detiene (2026-11-24)

**Qué pasó.** El generador deja como *stub* las funciones que no puede traducir; `docs/DESARROLLO.md` decía que «no se
ejecutan en el juego». Era falso: un stub llama a `rt_unsupported`, que imprime `UNSUPPORTED <dirección>` y para el
programa (código de salida 9). En ALttP eran dos, `01:CA17` y `08:A8E3`, ambas por el motivo «register widths in
conflict» (un bloque al que se llega con anchos de A/X distintos).

**Lo que había de verdad.** `01:CA17` es la rutina de las etiquetas de sala `0x1C` a `0x1F` (tabla `01:C27D`, índice `$AE`
para la etiqueta 1 y `$AF` para la 2). Tres salas la usaban: `0x01B`, `0x043` y `0x097`. Forzar la etiqueta en una mazmorra
cargada (`--poke 000AE=1C@N`) detenía el juego; ninguna prueba anterior había llegado a esas salas.

**Cómo se arregló** (solo en el perfil, `games/alttp_usa.toml`, con `[[assume]]`):

| Dirección | Fuerza | Por qué |
|---|---|---|
| `01:CA17` | M=16 X=16 | La llaman `01:C8D4` y `01:C98B` tras `REP #$20`; el código usa `AND #$00FF`, que con M=8 sería `AND #$FF` y un `BRK`. El camino de 8 bits es el del despachador por la tabla para las etiquetas `0x1E`/`0x1F`, que ninguna sala usa. |
| `01:C310` y `01:C31B` | M=8 X=8 | Tras cada `JSR (tabla,X)` del despachador sigue `LDA #$01`, que solo tiene sentido con M=8. `CA17` vuelve con M=16 (acaba en `REP #$20`), pero solo se la llama por `C8D4`/`C98B`, que ya vuelven con M=8. Sin esto, arreglar `CA17` hacía caer 26 funciones más. |
| `08:A878` | M=16 X=8 | `08:A8E3` es la entrada `0x24` de la tabla de 67 manejadores de `08:837F`, dos bytes antes de la `0x15` (`08:A8E5`). Con el acarreo puesto sigue a `A8E5`; con el acarreo limpio salta a `A876`, que continúa con `ADC #$000C` (M=16). |

Resultado: **0 stubs de 4 178 funciones** (antes 2). `check.ps1` y `check.sh` fallan ahora si el generador deja alguno.

**Comprobación.** Forzar las etiquetas `0x1C` a `0x1F` ya no detiene el juego. Regresión: las 133 entradas de mazmorra con el ejecutable nuevo y con el anterior dan la misma WRAM final, byte a byte (0 de 133 distintas, 0 paradas), y `check.ps1` termina en `OK`. Lo que **no** demuestra: que `01:CA17` haga lo que hace la consola (no hay emulador de referencia aquí).

**Lecciones generales.**

- Un conflicto de anchos casi siempre es el generador viendo **dos caminos con anchos distintos, de los que solo uno
  existe en la consola**. Mira cómo se decodifica la instrucción siguiente con cada ancho: si con uno de ellos aparece un
  `BRK` o una instrucción absurda, ese camino no se ejecuta en el hardware real.
- Arreglar un stub puede **destapar** conflictos en cadena (aquí 2 stubs pasaron a 28 y 663 conflictos). Mira siempre el
  recuento de stubs tras cada cambio y la causa raíz del primero de la lista, no la lista entera.
- Las **dos mitades de la comprobación** son estática (¿quién la llama?) y dinámica (¿se llega de verdad?). Hacen falta las dos.

## 2. Método: ¿se alcanza este stub?

1. Lista de stubs: `codegen --all` los imprime en stderr con su causa; `discover --widths` lista los conflictos.
2. Quién llama (**estático**). En la ROM busca `JSR`/`JSL`/`JMP`/`JML` con ese destino (`20/22/4C/5C` + dirección) y los
   punteros de 16 bits de tablas. Con `snes-recomp disasm <rom> <dirección> [n] [--m16] [--x16]` y `graph <rom> <dirección>`
   se ve qué es cada llamador. Cuidado: ver [trampas](#3-trampas).
3. Qué tabla y qué índice. Si el destino está en una tabla del perfil (`[[table]]`), calcula su índice y busca en los datos
   del juego qué objetos lo usan. En ALttP: la etiqueta → salas (cabeceras de sala `04:F502`, 296 punteros de 16 bits; la
   etiqueta 1 es el byte 5 de la cabecera y la 2 el byte 6; la dirección sale de la rutina `01:B5E6`, que escribe `$AE`/`$AF`).
4. Prueba **dinámica**. Parte de un estado guardado en el fotograma 5300 (Link controlable en su casa), entra por cada
   entrada de mazmorra con `--poke 0010E=<n>@5310 --poke 00010=06@5310 --poke 00011=00@5310 --poke 000B0=00@5310` y
   mira el código de salida y `UNSUPPORTED` en la salida. Las 133 entradas (0 a 0x84) tardan unos 15 min con 4 procesos.
   Para llegar a una situación concreta sin jugarla, fuerza la variable (`--poke 000AE=1C@6200`).
5. Un **control** sin el cambio tiene que pasar, y un **barrido de regresión** con y sin la corrección debe dar la
   misma WRAM (`--dump` escribe `wram.bin`).

## 3. Trampas

- **El `switch` con todas las funciones del banco no es evidencia.** Cuando el generador no resuelve un salto indirecto,
  emite un `switch` con *todas* las funciones del banco (`f_01_C2FD`, `f_08_833C`...); que un stub salga ahí no prueba nada.
- **Un par de bytes que coincide con una dirección no es un puntero.** `08:A8E3` aparecía como palabra en `08:A96B`, pero
  era el operando de un `LDA $A8E3,X`. Comprueba si el sitio es una tabla o código.
- **Una búsqueda de «tabla que cumple X» sin restricciones fuertes da falsos positivos.** Una búsqueda de la tabla de
  cabeceras «con etiquetas < 0x40» encontró una tabla de relleno `FFFF` (leía el banco siguiente y daba 296/296). Valida
  con una restricción del propio juego (aquí, el `count = 64` de la tabla de etiquetas) y mira que los valores tengan
  sentido (rangos, mínimo y máximo), no solo que el recuento sea alto.
- **No fíes direcciones de memoria.** Dos tablas «conocidas» (`04:F1E2`, `02:C577`) eran incorrectas. Saca la dirección
  del código que la usa (`disasm`).

## 4. Entorno (Windows)

- **Git Bash convierte las rutas que empiezan por `/`** (`/sdcard/...` pasa a `C:/Program Files/Git/sdcard/...`): con `adb`
  usa `MSYS_NO_PATHCONV=1`.
- **`git archive | tar -x` en PowerShell rompe el binario** (el pipe de PowerShell recodifica): usa Bash para exportar y
  escanear. Un escaneo sobre una carpeta vacía termina bien y no comprueba nada: cuenta los ficheros exportados.
- `alttp-recomp.exe` es un programa de ventanas: `Start-Process -Wait -PassThru -NoNewWindow` y rutas de Windows.
- `adb`: antes de tocar la pantalla, comprueba `dumpsys window | grep mCurrentFocus`. Un toque a ciegas abrió una
  notificación ajena.

## 5. Pendiente

- Llegar **jugando** a las salas `0x01B`, `0x043` y `0x097` (¿en qué mazmorras están? ¿se pueden saltar?) y comprobar que
  el comportamiento de `01:CA17` es el de la consola; hoy solo se sabe que ya no detiene el juego.
- Una partida completa (la prueba que falta para decir que el juego se pasa de principio a fin).
- Comparar con un emulador de referencia (ver `plan.md`, punto 9 de la lista de pruebas).
