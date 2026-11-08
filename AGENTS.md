# Instrucciones para trabajar en alttp-recomp

## Alcance y documentación

Este repositorio contiene el perfil y las mejoras propias de *The Legend of Zelda: A Link to the Past*, USA, CRC32 `777AAC2F`. El motor es `snes-recomp`, un proyecto separado cuyo código fuente está normalmente en `../snes-recomp`.

- Consulta `README.md` para el producto y las opciones del jugador, `docs/DESARROLLO.md` para desarrollo, `docs/TRADUCCION.md` para traducción y `plan.md` para avances y pendientes.
- Estas instrucciones proceden de `CLAUDE.md`. Mantén ambos documentos coherentes cuando cambien las reglas de trabajo.
- El plan mezcla notas históricas con avances posteriores: contrasta sus pendientes con el perfil, el C y las pruebas antes de implementar algo que ya exista. No presentes como probado lo que solo está previsto o tiene una prueba de lógica.
- Documentación y mensajes de commit en español.

## Separación entre juego y motor

- Aquí van las direcciones, tablas de saltos, ganchos, traducción y C específicos de ALttP.
- Los cambios generales del traductor, PPU, sonido, menú, lanzadores y runtime van en `snes-recomp`. Sigue allí sus instrucciones y su flujo OpenSpec; el plan indica comenzar los cambios del motor con `/opsx:propose`.
- Si una mejora necesita API nueva, impleméntala de forma general en el motor y consúmela aquí mediante `snes_rt.h`. No copies código fuente del motor a este repositorio.
- Cada repositorio se commitea por separado. Los binarios de Windows distribuidos en la raíz son distintos del motor compilado localmente en Linux.

## Código y datos

- `games/alttp_usa.toml`: perfil, entradas, tablas, opciones y `[[hook]]`. Solo direcciones, nombres y tamaños; ningún byte del juego.
- `games/alttp_usa/`: `dialog.c` (mensajes rápidos), `widefill.c` (pantalla ancha), `text.c`, `menutext.c` y `hud.c` (traducción), `quality.c` (mejoras y arreglos), `icon.c` (arte propio generado con `scripts/make_icon.py`).
- El C debe ser original, clean-room. Las direcciones y tablas se comprueban a mano contra la ROM USA; referencias externas son pistas, no prueba de que una dirección coincida.
- Usa la API de `snes_rt.h`, por ejemplo `wram_read8`, `wram_write8`, `game_opt`, `ppu_wide` y `ppu_wide_blank`. Las mejoras opcionales se declaran en el perfil y se consultan con `game_opt`.
- Añade cada C nuevo a las listas de **ambos** scripts, `scripts/check.sh` y `scripts/check.ps1`.
- El perfil usa ganchos `guard`: requieren un motor compatible. Según las notas actuales del plan, los ejecutables de Windows de la raíz necesitan actualizarse antes de construir ese perfil. Comprueba su compatibilidad cuando se sustituyan.

## Estados guardados

El punto `[resume]` es `00:8034`, espera del NMI del bucle principal, con `S = $01FF`. Solo se guarda dentro de la partida; la intro y el título cambian de pila. Cualquier estado persistente del C propio debe poder recuperarse desde WRAM: las variables estáticas no se restauran automáticamente.

Las partidas y estados del motor de desarrollo van a `saves/` junto al ejecutable o a la carpeta de datos del usuario si no se puede escribir ahí. El paquete Linux del juego tiene sus propias rutas, documentadas en el README. No confundas ambas instalaciones.

## Traducción

- `games/alttp_usa/lang/es.txt` y `es_menu.txt` son texto propio en UTF-8 y sí se versionan; nunca deben copiar el volcado original.
- En `es.txt`: A-Z, a-z, 0-9, espacio, `! ? . , '`, y `á é í ó ú ñ ¿ ¡`. Las mayúsculas acentuadas y `ü` se muestran sin marca.
- Cada línea admite como máximo **168 píxeles**, sumando anchuras de la fuente, no caracteres.
- Conserva los códigos `{5B}` A, `{5C}` B, `{5D}` X y `{5E}` Y: al cargar se sustituyen por las etiquetas reales del control con `input_label`.
- `es_menu.txt` admite solo A-Z, espacio y `?`.

## Construir y validar

En Linux, los `.exe` de la raíz no sirven como motor nativo. Con el motor hermano ya compilado:

```sh
../snes-recomp/target/release/snes-port roms/alttp_usa.sfc --game games/alttp_usa.toml --no-launch
scripts/check.sh
# ROM y motor alternativos:
scripts/check.sh ruta/alttp_usa.sfc ruta/snes-recomp
```

Para jugar, omite `--no-launch`. Las opciones propias se pasan tras `--`, por ejemplo `-- --game-opt dialog_skip=0`. Para compilar el motor se usa `cargo build --release` desde su repositorio; el desarrollo Linux requiere compilador C, SDL2 y, para las pruebas, Python 3 con Pillow.

En Windows:

```powershell
.\snes-port.exe roms\alttp_usa.sfc --no-launch
powershell -File scripts\check.ps1
```

- **`check.sh` borra y recrea `out/`**. Revisa si hay resultados de trabajo que deban conservarse antes de ejecutarlo.
- Ambos scripts pueden omitir las pruebas por falta de ROM, motor o compilador. Un código de salida 0 con «omitido» no significa que las pruebas hayan pasado.
- Para cambios de lógica, amplía las comprobaciones pertinentes en ambos sistemas. `scripts/check_eval.py` contiene las comprobaciones de datos de Linux; `scripts/test_hooks.c` y `scripts/test_refund.c` verifican lógica aislada de arreglos.
- Distingue pruebas de lógica, partidas automáticas y pruebas manuales de imagen o sonido al informar resultados. Ejecuta solo las pertinentes; una edición documental no requiere reconstruir el juego.
- CI (`.github/workflows/ci.yml`) valida sin ROM el TOML, ficheros prohibidos, la lista de C en `check.ps1` y la sintaxis del C contra la cabecera del motor con funciones generadas de relleno.
- Rendimiento: `scripts/bench.sh` y `scripts/bench_play.sh`. La medición con controlador `dummy` es una cota de CPU, no una prueba de ventana o audio reales.

## Material que nunca se publica

Nunca añadas ROMs, C generado, volcados, capturas con gráficos del juego, partidas ni estados o miniaturas a commits, PR, issues o paquetes. Esto incluye `roms/`, `out/`, `*.sfc`, `*.smc`, `*.srm`, `*.sst`, `*.thumb` y los volcados `alttp_messages_*.txt` y `alttp_menu_*.txt`. Que un archivo esté ignorado no basta para asegurar que un paquete esté limpio.

Antes de cada push, exporta el commit a una carpeta temporal vacía y ejecuta `scan` sobre esa exportación con la ROM local. Debe terminar sin error. No escanees `.`: encontraría la propia ROM ignorada. Ejemplo en Linux, después de crear el commit que se quiere comprobar:

```sh
scan_dir=$(mktemp -d /tmp/alttp-scan.XXXXXX)
git archive HEAD | tar -x -C "$scan_dir"
../snes-recomp/target/release/snes-recomp scan roms/alttp_usa.sfc "$scan_dir"
```

En Windows usa `snes-recomp.exe scan` sobre una exportación equivalente. Este control de `HEAD` no cubre cambios sin commitear.

## Empaquetado

- Windows: `scripts/release.ps1`; para sustituir el motor, `scripts/update-engine.ps1` recibe el paquete creado en el repositorio del motor. Un motor antiguo puede fallar al enlazar API nueva.
- Linux: `scripts/release.sh [version]`, que usa `../snes-recomp/linux/build.sh`; salida en `out/release/`.
- `scripts/sums.sh` genera `out/release/SHA256SUMS`, usado por las actualizaciones del lanzador.
- Respeta las comprobaciones de contenido de los scripts de release y verifica que no se incluya material derivado de la ROM.
