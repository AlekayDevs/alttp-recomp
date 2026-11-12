# Desarrollo

Volver al [README](../README.md). Aquí está lo que necesita quien quiere compilar, probar o empaquetar el proyecto; para jugar basta con las [releases](https://github.com/AlekayDevs/alttp-recomp/releases).

## Qué contiene

- `games/alttp_usa.toml`: identifica la ROM (CRC32 `777AAC2F`) y da al recompilador las entradas de código, las tablas de saltos (comprobadas a mano contra la ROM real) y los ganchos. Solo lleva direcciones, nombres y tamaños de tabla; ningún byte del juego.
- `games/alttp_usa/dialog.c`: C original que se compila junto al código generado. Acelera los mensajes.
- `games/alttp_usa/widefill.c`: con la pantalla ancha (`wide` en `config.ini` o `--opt wide=N`), tapa en negro las columnas extra donde no hay mapa cargado: pasado el borde del área en el exterior, y en las salas y cuevas, siempre.
- `games/alttp_usa/text.c`: vuelca los mensajes del juego a un fichero de texto y, con la opción `language`, los sustituye por los de `lang/es.txt`.
- `games/alttp_usa/menutext.c`: lo mismo para el texto fijo de la selección de partida y del registro de nombre, con `lang/es_menu.txt`.
- `scripts/check.ps1` y `scripts/check.sh`: prueban que lo anterior funciona (necesitan tu ROM). `scripts/test_refund.c` y `scripts/test_hooks.c` comprueban la lógica de algunos arreglos sin partida: se compilan aparte con el C de `games/alttp_usa/quality.c`.
- `scripts/release.ps1`: arma el paquete para repartir.

## Construir y ejecutar desde el código

### En Windows

```
snes-port.exe                                  # doble clic: el lanzador (eliges la ROM y juegas)
snes-port.exe roms\alttp_usa.sfc               # construye si hace falta y abre el juego
snes-port.exe roms\alttp_usa.sfc --no-launch   # solo construye
snes-port.exe clean roms\alttp_usa.sfc         # borra la caché de la ROM (si un cambio no se nota)
snes-port.exe roms\alttp_usa.sfc -- --game-opt dialog_skip=0   # opciones del juego
```

Este repositorio lleva el motor ya hecho en la raíz (`snes-port.exe`, `snes-recomp.exe`, `sdl2\`, `toolchain\` con TinyCC; licencia y README del motor como `LICENSE-engine` y `README-engine.md`), así que no hace falta clonar `snes-recomp` para jugar: **doble clic en `snes-port.exe`** abre la ventana del lanzador (reconoce el juego por `games\`), eliges tu ROM y juegas; con una ROM como argumento lo hace sin ventana. Para actualizar el motor: en `snes-recomp`, `powershell -File scripts\release.ps1`; aquí, `powershell -File scripts\update-engine.ps1`, y se sube como cualquier cambio.

### En Linux

**Desde el código:** los binarios de la raíz son de Windows; en Linux se compila el motor y se usa con el perfil de este repositorio:

```
sudo apt install build-essential pkg-config libsdl2-dev python3-pil   # compilador de C, SDL2 y Pillow (solo para check.sh)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh        # Rust, si no lo tienes
git clone https://github.com/AlekayDevs/snes-recomp ../snes-recomp
(cd ../snes-recomp && cargo build --release)
../snes-recomp/target/release/snes-port roms/alttp_usa.sfc --game games/alttp_usa.toml
```

La primera vez construye el juego con gcc (unos 3 minutos) y lo guarda en `~/.cache/snes-port`; las siguientes arranca al instante. Opciones del juego tras `--`, como en Windows. Las partidas y los estados van a `saves/` junto a `snes-port` (o a `~/.local/share/snes-port/saves` si ahí no se puede escribir). Hace falta un motor que sepa construir en Linux (con el arreglo del nombre del ejecutable y la detección de SDL2 del sistema).

**El lanzador del paquete de Linux** (`alttp-recomp`, del motor: `../snes-recomp/linux/launcher.c`) habla inglés o español. El idioma inicial es el que haya guardado el botón del globo (arriba a la derecha, o la tecla **L**) en `~/.local/share/alttp-recomp/lang.txt` o, si no hay nada, el del entorno (`LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, `LANG`: español si empieza por `es`). En Windows el lanzador sigue el idioma del sistema y en Android todavía no hay selector. Para sacar capturas sin pantalla (así salen las de `docs/img/launcher*.png`): `SNES_PORT_SHOT=ruta.ppm SDL_VIDEODRIVER=dummy ./alttp-recomp [rom]` vuelca el último fotograma del lanzador, y el aviso de versión nueva se simula con un `update.info` junto al ejecutable, `check=1` en `update.txt` de la carpeta de datos y un servidor local en `SNES_PORT_UPDATE_API`. Con vídeo `dummy` el juego no arranca (solo el lanzador).

**Paquete de Linux para repartir:** construirlo en local con `scripts/release.sh` da un ejecutable que pide la glibc de la máquina (2.39 en Ubuntu 24.04). Para repartir, `gh workflow run linux-package.yml -f version=X.Y` lo construye en Ubuntu 22.04 (`.github/workflows/linux-package.yml`) y deja el `.tar.gz` y `SHA256SUMS` como artefacto de la ejecución (`gh run download`); el paquete pide glibc 2.34. No publica ninguna release.

### Con el motor

```
git clone https://github.com/AlekayDevs/snes-recomp
git clone https://github.com/AlekayDevs/alttp-recomp
cd snes-recomp
cargo run --release --bin snes-port -- ..\mi-carpeta\alttp_usa.sfc --game ..\alttp-recomp\games\alttp_usa.toml
```

Opciones del juego tras `--`, por ejemplo `-- --game-opt dialog_skip=0`.

## Comprobar y empaquetar

```
powershell -File scripts\check.ps1 -Rom ruta\a\alttp_usa.sfc      # genera, compila y ejecuta; ~3 min
cd ..\snes-recomp ; powershell -File scripts\release.ps1 ; cd ..\alttp-recomp
powershell -File scripts\release.ps1
```

En Linux, `scripts/check.sh [roms/alttp_usa.sfc] [ruta/a/snes-recomp]` hace lo mismo con gcc o clang (necesita Python 3 con Pillow y busca el motor en `../snes-recomp/target/release/`). `check.ps1` y `check.sh` se omiten con un aviso si falta la ROM, el motor o el compilador. `release.ps1` y `update-engine.ps1` son solo de Windows. `release.ps1` falla si el paquete llevara ROMs, partidas guardadas, estados guardados (`.sst`) o C generado.

Para comprobar por separado la integración de los ganchos `guard` en Linux:

```sh
python3 scripts/check_guards.py
# Rutas alternativas: --rom ruta/alttp_usa.sfc --engine ruta/snes-recomp
```

Requiere Python 3.11+ y gcc (o `CC=clang`), además del motor y la ROM. Genera y compila el juego en una carpeta nueva `out/guards-*`, sin borrar resultados anteriores. Instrumenta una copia de `quality.c` para contar llamadas reales desde el código recompilado y retornos de cada gancho. Compara WRAM, VRAM, CGRAM y OAM del recorrido de control con las ocho opciones apagadas y encendidas, y fuerza el estado de conejo temporal con `--poke` para comprobar que se alcanza su gancho. No sustituye una reproducción natural de ese bug ni valida ganchos cuyos contadores quedan a cero. Los registros y `summary.json` son resultados locales, no material para publicar.

`--headless out/guards-…/headless` permite repetir escenarios con un ejecutable instrumentado anterior; úsalo solo si no han cambiado el perfil, el C propio, la ROM ni el motor. `--verify-results out/guards-…` vuelve a comprobar los registros y volcados de una ejecución existente. El escenario del conejo escribe tanto `$5D = $1C` como el temporizador de 16 bits `$03F5 = $0100`: con el temporizador a cero, `07:8365` revierte la transformación antes de llegar a la animación.

Con un ejecutable instrumentado actualizado, `--only-sprites` prueba un corazón y un hada, `--only-hidden` compara la marca de un objeto escondido con la opción activada y desactivada, y `--only-mushroom` prueba la seta con el submódulo normal y con `$11 = 1`. El hada se coloca ocho píxeles por debajo de Link y se mantiene cerca unos fotogramas porque su colisión usa `$0F70 = 9`; el script comprueba la absorción con `fix_double_absorb=1` y su retorno con la opción apagada. En la ejecución completa, `GUARD_INJECT` prepara una sola vez el estado en la llamada de los ganchos de cámara, escaleras, Skull Woods y puertas para probar sus saltos y retornos; en puertas también se prepara `$6C = 1` para llegar a la rutina. Esto no equivale a provocar esos bugs en una partida real. Además, `door_walks` guarda un estado en el fotograma 5300, entra en mazmorras con `$010E` (entradas 2, 3, 7 y 8) y el módulo 6, camina por ellas y exige que el guard de la puerta se alcance sin inyección y que, con las opciones `fix_*` encendidas y apagadas, WRAM, VRAM, CGRAM y OAM queden idénticas.

## Limitaciones conocidas

- Los estados guardados no incluyen el fotograma en curso (se redibuja) ni variables estáticas del C propio; por ahora se guardan en un único punto del bucle principal (`[resume]` en `00:8034`). Cada uno lleva una miniatura (`.sN.thumb`) para el selector de ranuras, que no se publica.
- De las 4 178 funciones de la ROM, 2 (`01:CA17`, `08:A8E3`) se quedan como *stub* y no se ejecutan en el juego. Causa (registro del generador): un bloque se alcanza con anchos de registro distintos (`01:CA19` con M=16 X=16 y M=8 X=16; `08:A878` con M=16 X=8 y M=8 X=8); el generador las deja como *stub* con el motivo «register widths in conflict».
- La interpolación del DSP usa un núcleo en forma de campana, cercano a la gaussiana del hardware pero no su tabla exacta; la PPU no emula el entrelazado; los comportamientos que dependen de ciclos exactos no se reproducen.
