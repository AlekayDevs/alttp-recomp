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

- **`play.exe` sin `--game-dir` no traduce los mensajes.** La carpeta del juego es por defecto la de la ROM (`roms/`), y la traduccion se lee de `<carpeta del juego>/lang/es.txt`: el motor avisa por consola («cannot find ...: the messages stay in English») y los mensajes salen en ingles aunque el menu diga `es`. Con `alttp-recomp.exe` no pasa (encuentra `games/alttp_usa`); con un ejecutable lanzado a mano, `--game-dir games/alttp_usa`.
- **Automatizar clics en la ventana del juego desde un script es peligroso:** si la ventana no esta delante, el clic cae en otra aplicacion. Las coordenadas de `GetClientRect` tampoco coinciden con la pantalla si el programa no declara DPI. Para el menu: `--menu-keys F1,tap@X:Y` y `--menu-shot` (sin ventana) en vez de simular el raton.
- **TinyCC no compila el frontal con las cabeceras de SDL2 del repositorio sin `-DDECLSPEC= -DSDLCALL=`** (lo que hace `snes-port`), y `headless.c` usa `timespec_get`, que TinyCC no tiene: para una prueba rapida del frontal, `cl` con vcvars; para el sin-video con TinyCC, sustituir `timespec_get`.

- **Resuelto (2026-11-24): una pieza roja con una «n» en la caja del menú de Select (mensaje `@390`, «Continuar partida / Guardar y salir»).** La vio una vez el jugador (2026-11-24, tras salvar a Zelda, ya en el exterior, con `language=es`): una pestaña roja de un mosaico de texto abajo a la derecha de la caja. No sale siempre. El estado guardado justo después (ranura 1) no la tiene, y el mensaje `@390` lleva en `es.txt` los mismos códigos que el inglés, sin color: no viene de la traduccion. Se sospecha un resto de otro mensaje o de un mosaico del cuadro sin borrar. Para reproducirlo hace falta un estado (F5) tomado mientras se ve. Con `--state-script load@N` y `--game-opt language=en` el HUD cambia pero un mensaje ya abierto conserva su idioma.
  - **2026-11-24, segundo caso, con estado guardado (ranura 2).** Solo se abrió el menú de Select una vez. Del estado (formato `snes_state.inc`: cabecera 12 bytes, `Cpu` 24, WRAM 128 KiB, SRAM 32 KiB, `wram_port` 4, `hw` 64 KiB, `fixed_col` 3, VRAM 64 KiB, luego CGRAM y OAM) se descartó: no es un sprite (el OAM no tiene nada en x≈230, y≈124); el mosaico de la caja (BG3, filas 10-15, columnas 6-26, mosaicos `$39xx`) está limpio y la celda bajo la pieza (fila 15, columna 23, mosaico `$1FA`) está vacía en VRAM; BG2 es liso (`3C15`) bajo la caja. La pieza no se explica con esos datos: falta cargar el estado y verla renderizada (`--state-script load@N` se rechaza en la intro; hace falta una ruta de pulsaciones que pase del título antes).
  - **Causa y arreglo.** El menú de Select es el módulo `$10 = 0E` (subrutina `$11 = 0B`), el mismo que el menú de pausa (`$11 = 01`), y deja en la WRAM los búferes del mapa de la pausa. `alttp_pause_labels` (`hud.c`) solo miraba `$10 = 0E` y que el búfer tuviera la palabra de cada rótulo, así que en el Select se creía en la pausa y escribía las letras de «ACCION» y «EQUIPO» en mosaicos de repuesto (`$1F8` a `$1FA`) que son celdas del texto de la caja: la «n» roja era el último mosaico de «ACCION» en la celda fila 15, columna 23 de BG3. Arreglo: exigir también `$11 = 01`. Se vio con el estado de la ranura 2 cargado (`--state-script load@2000`, que sí funciona a los 2000 fotogramas, pasada la intro), sin ocultar sprites (siguió) y ocultando BG3 con `$1C = 12` (desapareció); el mosaico estaba vacío en la VRAM de final de ejecución porque el gancho lo escribe cada fotograma antes de que el juego lo vuelva a subir. Comprobado: Select sin la pieza y pausa con los cuatro rótulos en español.
  - **Lección:** un estado guardado cargado con `--state-script` en una ejecución sin ventana reproduce la pantalla exacta; `--poke 1C=NN@F` (una orden por fotograma) apaga capas de la pantalla principal para saber de qué capa viene algo. `--log-wram` toma la ruta de salida relativa a la carpeta de la caché (no admite `C:` por los dos puntos).

## 5. Revisión de lo que seguía sin demostrarse (2026-11-24)

**5.1 ¿`01:CA17` hace lo que dice su código? Sí, en lo observable.** Prueba de caja blanca con un ejecutable instrumentado (contador de
entradas en la función): se fuerza la etiqueta `0x1C` en una mazmorra cargada y se prepara `$0540..$055F`. Sin disparo (0 bits, 3 bits, o 4 bits
en los bytes bajos, que no cuentan) no cambia nada; con 4 palabras con el bit 15 puesto, o con `$0642 != 0`, queda `$041A=1`, `$02E4=1`, `$0FC1=1`,
`$0403=0x10`, y la función no se vuelve a llamar (la otra rama de `01:C8D4`). **No observable:** `$012D = 7` (petición de efecto de sonido que el audio
consume en el mismo fotograma) y que el resultado sea el de la consola; solo se comprueba contra el código.

**5.2 Llegar a las salas `0x01B`, `0x043`, `0x097`: no se ha conseguido.** Escribir `$A0` mientras carga una mazmorra deja la sala pedida y el módulo 7, pero
las etiquetas siguen en `(00,00)`: el cargador ya había leído la cabecera de la sala de la entrada. Las 133 entradas no caen en ellas, así que hay que ir
por puertas o escaleras. Ideas: reproducir una ruta con pulsaciones desde una entrada conocida, o escribir las variables del cambio de sala de una puerta
(sala destino y submódulo) en vez de `$A0`.

**5.3 `08:A8E3` = ancilla de tipo `0x25`, que el juego no usa.** El despachador (`08:836E`: `PLA; DEC A; ASL A; TAY; LDA $837F,Y`) indexa la tabla con *tipo − 1*; la
entrada 36 es el tipo `0x25` y la 21 (`08:A8E5`) el `0x16`. Crear un ancilla de esos tipos (`--poke 00C4A=25`) ejecuta cada manejador sin parar el juego.
Si el juego lo crea, no se sabe: la búsqueda de `LDA #tipo; STA $0C4A,X` es inútil (ni la bomba, `0x07`, aparece: los ancillas se crean por otras rutas).
Argumento a favor de que **no se use** en el juego original: el despachador deja el acarreo limpio (`ASL A` sobre `0x24`), así que el `BCC` de `08:A8E3` salta a
`08:A876` (`ASL $18`, `ADC #$0C` y, con M=8, un `BRK`); en la consola eso rompería el juego. Es una **inferencia**, no una prueba (depende de que el
despachador corra con M=8).

**Comprobado en BizHawk (referencia):** crear el ancilla `0x25` (`$0C4A=0x25`, mazmorra cargada) **cuelga el juego**: el contador de fotogramas `$1A` se
queda fijo (`EC`) durante 200 fotogramas, mientras que con el `0x16` avanza con normalidad. Es decir, `08:A8E3` rompe el juego en la consola, por lo que el
juego original no la usa; la inferencia de arriba (acarreo limpio, `BRK` con M=8) queda confirmada. Nuestra versión no se cuelga con el `0x25`, una
divergencia sin consecuencias porque ese tipo no se crea nunca.

**5.4 Comparación con un emulador de referencia: hecha para `01:CA17` (2026-11-24).** BizHawk 2.11.1 (núcleo Snes9x) con las mismas pulsaciones desde el
arranque y los mismos pokes que la prueba de caja blanca (5.1) da **los mismos valores en los cinco casos**: sin disparo (0 bits, 3 bits, 4 bits en bytes
bajos) todo a 0; con 4 bits altos o con `$0642=1`, `$041A=1`, `$02E4=1`, `$0FC1=1`, `$0403=0x10`. Es la primera prueba contra algo que no es nuestro C.
`$012D` sale 0 en ambos (el audio lo consume). Limitación: solo cubre lo que se fuerza, no el recorrido natural hasta la sala.

Recetas de herramienta (para los otros ports):
- **Mesen2 2.1.1:** el modo `--testRunner` con scripts Lua se quedó colgado en todas mis pruebas con `io`; no lo usé.
- **BizHawk:** `EmuHawk.exe <rom> --luaconsole --lua=<script.lua>` (la ROM primero). Sin `--luaconsole` el script no se carga. En Lua usa `/` en las rutas:
  una barra invertida seguida de `U` es un escape inválido y el script muere sin avisar (el error solo sale en la ventana «Lua Console»; se lee con UI Automation).
  `client.speedmode(6400)` acelera; `memory.readbyte(a, "WRAM")` / `memory.writebyte`; `joypad.set({["P1 A"]=true})` por fotograma; `client.exit()` al acabar.
- Los fotogramas de ambos no están alineados al ciclo, pero con pulsaciones por fotograma el juego llega al mismo punto (módulo 7 en el fotograma 5300).
- Al escribir scripts desde la shell, los heredocs se comen las barras invertidas y `\$`: escribe el fichero con una herramienta de ficheros.

**5.5 Partida completa: sin hacer.** Es lo único que demuestra «se puede pasar»; todo lo anterior solo descarta bloqueos concretos.

**5.6 Mazmorra de cada entrada (2026-11-24, `scripts/probe_entradas.py`).** Las 133 entradas (0 a 0x84) cargadas desde el estado de la casa (fotograma 5300) con `$010E`, `$10=6`: 15 mazmorras distintas en `$040C` (00 Alcantarillas, 02 Castillo, 04 Este, 06 Desierto, 08 Torre de Agahnim, 0A Pantano, 0C Palacio Oscuro, 0E Mire, 10 Skull Woods, 12 Hielo, 14 Hera, 16 Thieves, 18 Turtle Rock, 1A Ganon); las demas (`FF`) son casas y cuevas. Sala de entrada de cada una: Castillo 060-062, Este 0C9, Desierto 083-085 y 063, Pantano 028, Palacio Oscuro 04A, Mire 098, Hielo 00E, Hera 077, Thieves 0DB, Turtle Rock 023/024/0D5/0D6, Ganon 00C. Ninguna entrada cae en 0x01B, 0x043 ni 0x097. **Suposicion sin comprobar** (por la numeracion de salas y el vecino de entrada): 0x043 seria del Desierto, 0x097 del Mire y 0x01B del Palacio Oscuro; se confirma pasando por ellas con `--log-wram` de `$A0`.

**5.7 Las tres salas con su cabecera real (2026-11-26; forzado, no jugado).** Desde el estado de la sala del trono del Castillo (entrada 2, módulo 7 estable en el fotograma 5400) se escribe `$A0` = sala y `$11` = 2, 6 o 7 (`--poke 000A0=..@5400 --poke 00011=..@5400`): el módulo 7 carga la sala `$A0` con sus rutinas (las de un cambio de sala) y no con la de la entrada. Resultado a los 6300 fotogramas, sin `UNSUPPORTED` y con `$10`=7 estable, `$041A`=0 (así que `01:CA17` se llama):

| sala | `$AE` (etiqueta 1) | `$AF` (etiqueta 2) |
|---|---|---|
| 0x01B | 0x03 | 0x1C |
| 0x043 | 0x00 | 0x1D |
| 0x097 | 0x1C | 0x00 |

Coincide con las cabeceras de `04:F502` (§5, 0x01B tag2, 0x043 tag2, 0x097 tag1). Con `$11` = 1, 3, 4, 5 u 8 no carga la sala (`$A0` no cambia o el juego se va a otro sitio). Trampas: (1) escribir `$A0` en el fotograma de la entrada, o justo después, **no** recarga nada (la carga de la entrada ocurre entera en un fotograma; las capturas con y sin poke son idénticas): hay que escribirlo ya en módulo 7. (2) `--watch` del headless mira registros de la PPU, no la WRAM; para seguir una variable de la WRAM, `--sample FICHERO:CADA:DIR:LEN` con `CADA`=1. (3) Los pokes se aplican al terminar el fotograma indicado. (4) La captura de justo después muestra dos salas a medio desplazar: es el cambio de sala forzado, no un fallo. (5) `route.py ... args` en Windows deja `\r`: quítalo (`tr -d '\r'`) antes de pasar los argumentos. (6) El `headless` de `out\` de `check.ps1` es el del motor de la raíz, que no lleva `--state-save`/`--sample`; se regenera con `snes-recomp.exe codegen` y `cl` a otra carpeta (`out\rom2`).

**Las 296 salas (2026-11-26, `scripts/probe_salas.py`).** Misma técnica con las salas 0 a 0x127, 300 fotogramas cada una: **295 acaban en módulo 7 con `$A0` = la sala forzada, sin `UNSUPPORTED` ni parada del motor**. Las tres de `01:CA17` incluidas. La excepción es la **0x089**, que acaba en la **0x0A9** (piso inferior) con `$AE`=0x17: Link queda en las coordenadas de la sala del trono y, sin tocar nada, el propio juego lo mueve de sala. No es un fallo del port: muestreando cada fotograma (`--sample f.txt:1:A0:2,10:2,AE:2,20:4,A4:1,5D:1,A2:2`), Link aparece en la 0x089 en Y=0x03C0, X=0x04F8 (las del trono), a los ~120 fotogramas `$5D`=1 (cae por un agujero), el submódulo vuelve a 0 y a los ~175 la sala pasa a 0x0A9 con `$A2`=0x089 (sala anterior). Es la caída normal a la planta de abajo. Trampas del script: los pokes del fotograma del estado guardado no se aplican al cargarlo (hay que poner `@5401` para un estado del 5400); con 6 procesos a la vez el equipo se quedó sin memoria, van 2.

Sigue sin ser jugado: un cambio de sala forzado salta las puertas y no ejecuta el código de entrada a la sala por la vía normal.

## 6. Pendiente

- Llegar **jugando** (o con una ruta de pulsaciones) a las salas `0x01B`, `0x043` y `0x097` (con la cabecera real ya cargan y corren: §5.7).
- Comparar el recorrido natural (no forzado) contra BizHawk: misma ruta de pulsaciones y WRAM cada N fotogramas.
- Una partida completa.
