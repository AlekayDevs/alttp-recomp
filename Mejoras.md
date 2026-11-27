# Mejoras y correcciones antes del lanzamiento a la comunidad

Revisión del 2026-11-26 sobre `main` (`1603872`). Cada punto dice **qué** pasa, **dónde** se ve y **qué** hacer. Prioridad:
🔴 bloquea el lanzamiento · 🟠 importante, debería ir en el lanzamiento · 🟡 conviene · ⚪ menor.

Lo que es del motor (`snes-recomp`) va marcado **[motor]**: se arregla allí y aquí solo se actualiza el binario o la documentación.

> **Progreso (2026-11-27):** ✅ hecho 20 · 🔶 parcial 10 · ⬜ pendiente 3 · ➖ sin cambios 1 (de 34 puntos numerados). Cada punto lleva su estado justo debajo del título. Lo que sigue por hacer, en orden de trabajo, está en [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## 0. Qué se ha contrastado y cómo

Para que cada punto se pueda volver a comprobar. Primera revisión y segunda revisión (las dos del 2026-11-26).

| Comprobación | Cómo | Resultado |
|---|---|---|
| Releases publicadas | `gh release list`, `gh release view v0.15` | `v0.13` es «Latest» (Win, Linux, APK); `v0.14` y `v0.15` son pre-releases **solo con el zip de Windows** y `SHA256SUMS`; notas de la 0.15 solo en español |
| Etiquetas locales | `git tag` | solo `v0.1`–`v0.11`; faltan `v0.12`–`v0.15` |
| CI | `gh run list` | CI y Pages en verde en el último push (`1603872`) |
| Issues | `gh issue list`, `gh issue view 1` | un issue abierto (#1, alemán), respondido solo en español |
| Metadatos del repositorio | `gh repo view --json …` | descripción en español, Discussions **desactivado**, 4 temas |
| Traducción | `python scripts/check_text.py roms/alttp_usa.sfc` | `OK`: 382 mensajes, 2305 líneas, la más ancha 168 px (`@393`); `es_menu.txt` 56 textos |
| Ganchos del perfil frente al C | lista de `call` de los `[[hook]]` de `alttp_usa.toml` comparada con las funciones `alttp_*` de `games/alttp_usa/*.c` | todos los ganchos tienen su función; las 6 funciones sin gancho (`alttp_hud_poll`, `alttp_intro_skip`, `alttp_pause_labels*`, `alttp_text_menus`, `alttp_window_icon`) se llaman desde otros ganchos: correcto |
| Opciones del perfil | `grep '\[\[option\]\]'` en el perfil; en el motor, `runtime/play.c` (`gopts_load`, menú) y `MAX_GAME_OPT`/`MAX_OPTIONS` | **solo se declara `language`**; el motor solo enseña y guarda las opciones declaradas, con un máximo de **16** (ver 1.4) |
| Estado `static` del C frente a los estados guardados | lectura de `quality.c`, `text.c`, `menutext.c`, `hud.c` | se cumple la regla del `CLAUDE.md` (ver 4.3) |
| Rutas personales en lo que se sube | `git grep` de `alexm`, `C:\Users`, `jks`, `_backup_git`; `grep -a` dentro de `alttp-recomp.exe` | `plan.md` (línea 57) y el `.exe` (rutas de `.cargo` y de `Proyectos\snes-recomp…out`) |
| Contenido del zip de Windows | lectura de `scripts/release.ps1`; `ls sdl2/lib/x64` | copia `games\` y `sdl2\` enteros desde el árbol de trabajo; `SDL2.pdb` 6,6 MB |
| Versión por defecto de los scripts | `release.ps1` (`-Version "0.1.0"`), `linux-package.yml` (`default: "0.2"`) | confirmado |
| Estado del motor hermano | `git status`, `git tag`, `ls out/release` en `..\snes-recomp` | 10 ficheros modificados sin commit (+496 líneas, cambio `hirom-mapping`), **ninguna etiqueta**, el zip del motor siempre se llama `snes-port-0.1.0-win64.zip` (ver 2.9) |
| Carpeta de partidas en Linux | README frente a `DESARROLLO.md` y `CLAUDE.md` | rutas distintas (ver 3.1) |
| Banner del README | vista de `docs/img/banner.png` | el subtítulo sale **cortado** por el borde inferior (ver 3.7) |
| Página de descargas | lectura de `docs/index.html` | usa `releases/latest` (por eso reparte la 0.13); ver 6 |
| Plantillas de issue | `.github/ISSUE_TEMPLATE/*.yml` | bilingües y piden versión, sistema y CRC32: bien |
| Licencias de terceros | `toolchain/AVISO-TINYCC.txt`, `sdl2/COPYING.txt` | presentes |

No se ha ejecutado `check.ps1` ni `check.sh`, ni se ha jugado: todo lo anterior es lectura de código, de documentación y de GitHub.

---

## 1. Bloqueantes 🔴

### ✅ 1.1 Linux y Android siguen con la parada de `01:CA17`
- **Estado (2026-11-27): ✅ publicada la v0.16 como «Latest» con zip de Windows, `.tar.gz` de Linux (workflow en Ubuntu 22.04), APK (misma firma que la 0.13) y `SHA256SUMS`; notas EN/ES. Sin probar: instalar los tres paquetes desde la release en máquinas limpias y el aviso de actualización de la 0.13 a la 0.16.**
- La versión estable (`v0.13`, «Latest» en GitHub) es la única que hay para Linux y Android, y **detiene el juego** (`UNSUPPORTED`) al entrar en las salas `0x01B`, `0x043` y `0x097` (HALLAZGOS §1 y §5.7). El arreglo solo está en las pre-releases `v0.14`/`v0.15`, que son **solo de Windows**.
- La página de descargas y el aviso de actualización usan `releases/latest`, así que hoy reparten la 0.13 a todo el mundo, Windows incluido.
- **Hacer:** una release (0.16 o 1.0) con los **tres** paquetes (zip de Windows, `.tar.gz` de Linux desde `linux-package.yml` y APK) que lleve el perfil con los `[[assume]]`, y marcarla como «Latest». Es lo más urgente: un jugador que avance unas cuantas mazmorras se queda bloqueado.

### ⬜ 1.2 Nadie ha terminado el juego
- **Estado (2026-11-26): Sin hacer; el README ya dice «Beta».**
- README, `plan.md` y HALLAZGOS §5.5/§6 lo dicen: no hay ninguna partida completa. Las 296 salas cargan al forzarlas (§5.7), pero un cambio de sala forzado se salta las puertas y el código normal de entrada a la sala.
- **Hacer** (al menos una de estas, mejor las dos):
  1. Jugar una partida completa con el frontal y `--record` (ya existe), por tramos y con un estado guardado al final de cada uno. Criterio: llegar a los créditos (`$10 = 0x19`) sin `UNSUPPORTED`. Anotar cada tramo en HALLAZGOS.
  2. Si se lanza antes, llamarlo claramente **«beta pública»** (no 1.0), pedir partidas completas en las notas y tener una plantilla de issue para «me quedé bloqueado en…» que pida el estado `.sst` de justo antes (el `.sst` es de quien juega y deriva de la ROM: pedirlo por privado, nunca adjunto en el issue público).

### 🔶 1.3 Las versiones no salen de un solo sitio
- **Estado (2026-11-26): Hecho: fichero `VERSION` (0.16) leído por `release.ps1`, `release.sh` y el workflow, sin valores por defecto, con comprobación de la etiqueta. Falta solo la norma de no reemplazar paquetes ya publicados (es una costumbre, no código).**
- `scripts/release.ps1` tiene `-Version` con valor por defecto **`0.1.0`**. Si alguien olvida el parámetro, el zip lleva `update.info` con `version=0.1.0` y el lanzador de Windows ofrece «actualizar» todos los días.
- Linux la toma de un input del workflow, que también tiene un valor por defecto viejo (`default: "0.2"`), y Android de `versionCode` en el motor. Ya hubo un APK roto que se reemplazó dentro de la misma versión (0.8) y no avisó a nadie.
- **Hacer:** un fichero `VERSION` en la raíz que lean `release.ps1`, `release.sh` y el workflow; quitar los valores por defecto (que falle sin versión); y que `release.ps1` compare la versión con la etiqueta de git de `HEAD`. Nunca reemplazar un paquete dentro de una release publicada: sacar una versión nueva.

### 🔶 1.4 Las mejoras de calidad de vida no se pueden activar sin la línea de órdenes
- **Estado (2026-11-27): 🔶 hecho en código, falta publicarlo.** Motor (rama `game-options-scroll` de `snes-recomp`): hasta 64 opciones, campo `desc` (línea de ayuda), la pestaña Game del escritorio se desplaza (rueda incluida). Aquí: 32 `[[option]]` (`Off`/`On`, etiqueta ≤ 90 px, `desc` ≤ 212 px), paso de CI que exige un `[[option]]` por cada `game_opt` del C, README/FAQ/CHANGELOG al día. Probado: captura del menú, `config.ini` guarda `game.fix_kiki_bomb = On`, `check.ps1` en `OK` con el motor nuevo. Motor subido y `alttp-recomp.exe` actualizado. Probado en una tablet Android real (SM-X510, 2026-11-27): las 33 filas salen y se desplazan, la línea de ayuda aparece bajo la lista, las etiquetas van en español con `language=es` y un valor cambiado (Objetos L/R = Sí) sigue ahí tras cerrar y abrir la app. También hecho: la línea de ayuda en el menú táctil y las etiquetas en español (`label_es`/`desc_es`). Aviso de actualización probado en la misma tablet (2026-11-27, con red real): con la 0.13 instalada, «Buscar actualizaciones ahora» dice «Estás al día (versión 0.13)»; con una 0.12, sale «Versión nueva: v0.13 (tienes 0.12)» con Omitir esta versión / Ahora no / Descargar e instalar, y este último pide el permiso de «instalar aplicaciones» (Abrir ajustes / Ahora no). No se llegó a instalar el APK descargado. Mando Xbox Series X por Bluetooth probado en la misma tablet (2026-11-27): el usuario jugó con él; en la captura posterior Link está dentro de la casa tras la intro y la selección de partida, la superposición táctil se ocultó y el marcador sale en español («VIDA»). El menú con el botón ☰ no quedó confirmado en captura. Descubierto en la tablet: el TinyCC del dispositivo usa cabeceras mínimas (`spikes/tcc_include`) y no tenía `time.h`, `fputc` ni `strcspn`, así que el C del juego no compilaba en Android; añadidos en el motor (`20f0e7e`). El punto 4 (prueba en `check.ps1`) no se hizo: `check.ps1` solo usa el runtime sin ventana.
- El README dice: «turn them on in the **Game** tab of the **F1** menu or with `--game-opt`». No es así: el perfil solo declara **un** `[[option]]`, `language` (`games/alttp_usa.toml`, línea 890). El motor solo enseña en el menú y solo guarda en `config.ini` (`game.<clave>`) las opciones declaradas (`runtime/play.c`, `gopts_load`/`gopts_store`). Las otras 32 (`item_switch_lr`, `skip_intro`, `rupees_9999`, `fix_*`…) solo se leen con `--game-opt`.
- Consecuencia: quien abre el juego con doble clic en el lanzador (Windows, Linux) y **todo Android** no puede encender ninguna. Ya se vio en la tablet: «"Game options" solo tiene "Language"» (`plan.md`, v0.12). Son la mitad de lo que anuncia el README.
- Además el motor admite **como mucho 16** opciones declaradas (`MAX_GAME_OPT 16` en `runtime/snes_core.inc`, `MAX_OPTIONS = 16` en `src/config.rs`), y ALttP tiene 32 activables más `language`.
- **Hacer:**
  1. **[motor]** subir el límite (o hacerlo dinámico) y que la pestaña Game admita muchas filas: desplazamiento, o grupos/secciones («Calidad de vida», «Arreglos del original»), también en el menú táctil de Android.
  2. Aquí: un `[[option]]` por mejora, con `names = ["off", "on"]` (o `["on", "off"]` donde el valor por defecto es 1: `dialog_skip`, `low_hp_beep`), una etiqueta corta en inglés y, si el motor lo admite, en español.
  3. Comprobar que `game_opt()` devuelve el **índice** del nombre (así lo hace `gopt_eff[i]`): con `names = ["off","on"]`, `off` = 0 y `on` = 1, que es lo que espera el C. `wide` es del motor (pestaña Image) y no hace falta declararlo.
  4. Una prueba: `--menu-keys` + `--menu-shot` que entre en Game, encienda una mejora y compruebe que `config.ini` la guarda.
  - Mientras tanto, como mínimo, corregir el README para que no prometa el menú.

---

## 2. Importantes 🟠

### 🔶 2.1 Paridad entre plataformas (regla del propio `CLAUDE.md`)
- **Estado (2026-11-26): **Corrección:** el lanzador de Windows SÍ tiene botón de idioma (`ID_LANG`; 0.14); README y `DESARROLLO.md` ya corregidos. Falta probar la actualización de verdad en Windows y Linux.**
- El lanzador de Windows **no tiene botón de idioma** (sigue el idioma del sistema); Linux y Android sí. Lo reconoce la hoja de ruta del README. **[motor]** `src/launcher_win.rs`.
- **El aviso de actualización de Windows no se ha probado en una instalación real** (README, hoja de ruta; `plan.md` §7c y v0.13: «Pendiente: Buscar actualizaciones en Windows y Linux»). Linux tampoco aparece como probado de una versión a otra.
- **Hacer:** botón de idioma en Windows y una prueba de actualización de verdad en Windows y Linux (instalar la N-1, publicar la N, «Buscar ahora», instalar y comprobar que `saves\` sigue intacta) antes de anunciar el proyecto.

### 🔶 2.2 El paquete de Windows y el APK se hacen a mano en una sola máquina
- **Estado (2026-11-27): 🔶 `release.ps1` ya arma `games\` desde `git archive HEAD` (sin probar: no se ha ejecutado tras el cambio). Faltan paquetes desde CI, motor fijado y copia de la clave del APK.**
- Solo Linux sale de CI. El zip de Windows lo arma `release.ps1` en local **con los ficheros del árbol de trabajo** (`Copy-Item games … -Recurse`), no con una exportación del commit: cualquier fichero sin seguimiento que esté en `games\` entra en el zip (la guarda solo mira ROM, `.srm`, `.sst`, `.thumb` y C generado).
- El APK depende de la cadena de Android y de la clave que hay en este PC. Si se pierde la clave, no hay más actualizaciones sobre la app instalada (ya pasó una vez, en la 0.8).
- `linux-package.yml` clona `snes-recomp` en `HEAD` (`--depth 1`), sin fijar: el paquete de Linux puede llevar un motor distinto del que se probó con la etiqueta.
- **Hacer:**
  - `release.ps1`: armar el paquete desde `git archive HEAD` (como pide el escaneo) y no desde el árbol de trabajo.
  - Workflow de Windows (`windows-latest`) que construya el zip con el motor de una etiqueta concreta, y fijar en `linux-package.yml` el motor a una etiqueta o un commit.
  - Copia de seguridad de la clave del APK fuera de este equipo (y anotar dónde, **no** en el repositorio).

### ✅ 2.3 Rutas personales dentro de `alttp-recomp.exe` **[motor]**
- **Estado (2026-11-26): Motor `bac96e4`→`3307d72`: `--remap-path-prefix` en su `release.ps1` y atajo `out/sdl2` solo en desarrollo; los `.exe` reconstruidos no llevan «alexm» ni «Users». Falta copiarlo a este repositorio con `update-engine.ps1` (ver 2.9).**
- El binario que se sube y se reparte lleva rutas de esta máquina: `C:\Users\alexm\.cargo\registry\…` (rutas de *panic* de las dependencias) y `C:\Users\alexm\Documents\Proyectos\snes-recomp…out…`. La segunda parece una ruta de compilación (`CARGO_MANIFEST_DIR` o similar): **hay que comprobar que no se use en tiempo de ejecución** en el equipo del jugador.
- **Hacer:** compilar las releases del motor con `--remap-path-prefix` (o `trim-paths` en el perfil `release` de Cargo) y buscar el uso de esa ruta. Lo ideal es que el zip del motor salga de CI y no de este PC.

### ✅ 2.4 `plan.md` es un cuaderno interno publicado
- **Estado (2026-11-26): `plan.md` sustituido por `docs/ROADMAP.md`; el diario detallado está en `HALLAZGOS.md` §7; `PLAN_PARTIDA.md` al día; sin rutas personales.**
- Son 57 KB de notas de trabajo en la raíz del repositorio. Lleva rutas locales (`C:\Users\alexm\Android`, `C:\Users\alexm\keys\snes-port.jks`, `Proyectos\_backup_git*`), decisiones a medio tomar («Decisiones que necesito del usuario») y estados que ya no valen (habla de los *stubs* como pendientes, de la «0.14 pre-lanzamiento», de BizHawk «sin ejecutar», cuando HALLAZGOS §5.4 dice que sí se ejecutó).
- `docs/PLAN_PARTIDA.md` dice lo mismo: «El script de BizHawk no se ha ejecutado» y «las salas 0x01B, 0x043 y 0x097 siguen sin alcanzarse», en contra de HALLAZGOS §5.4 y §5.7.
- **Hacer:** quitar las rutas personales y la ubicación de la clave; pasar lo que sigue vivo a issues o a un `docs/ROADMAP.md` corto y actualizado, y archivar o borrar el resto. Al menos hay que poner al día `PLAN_PARTIDA.md`.

### ✅ 2.5 El README promete más de lo que está probado
- **Estado (2026-11-26): Sección «How well the fixes are tested» en los dos README, con cuatro niveles de prueba.**
- «Everything here is implemented and tested» (sección de mejoras). Según `plan.md`, los ocho arreglos `guard` (`fix_door_submodule`, `fix_stair_tags`, `fix_skullwoods_door`, `fix_mushroom_warp`, `fix_double_absorb`, `fix_hidden_hookshot`, `fix_camera_twice`, `fix_bunny_walk`) solo se han probado con estados preparados o con la condición inyectada, nunca con el fallo provocado jugando. `fix_magic_refund` y `fix_bunny_palette` solo se han probado con `test_refund.c`/`test_hooks.c`. `fix_portal_chime` no se ha probado en la pantalla del Palacio de Hielo, y `fix_death_count` no con «guardar y salir».
- **Hacer:** una columna «Prueba» en la tabla (partida con guion / lógica sola / estado preparado), o una nota bajo la tabla. La comunidad de ALttP conoce bien estos fallos y lo va a comprobar.

### 🔶 2.6 Notas de versión solo en español
- **Estado (2026-11-26): Hecho: `CHANGELOG.md` bilingüe, descripción del repositorio en inglés, notas EN/ES preparadas. Faltan las notas de la 0.15 en GitHub (siguen solo en español) y publicarlas con la release.**
- El README principal está en inglés, pero las notas de la 0.15 (y la descripción del repositorio en GitHub) están solo en español. La respuesta al issue #1 (alemán) también va solo en español.
- **Hacer:** notas de versión bilingües (EN primero), descripción del repositorio en inglés y un `CHANGELOG.md` (EN/ES) con lo que cambia en cada versión, enlazado desde las releases.

### ⬜ 2.7 Mensajes de error para las ROM que no valen **[motor]**
- **Estado (2026-11-26): Sin hacer. Dato: el motor ya acepta ROM con cabecera `.smc`; el FAQ lo explica.**
- Mucha gente tiene la ROM con cabecera de 512 bytes (`.smc`), la europea, la japonesa o una versión parcheada. El README solo dice «USA, CRC32 `777AAC2F`».
- **Hacer:** comprobar (o añadir) en el lanzador un mensaje claro para cada caso común: «tiene cabecera de copiadora: se quita sola», o «es la versión europea o japonesa: hace falta la USA», o «CRC distinto: ¿está parcheada?». Y si el motor no quita la cabecera solo, que lo haga. Ponerlo también en una sección de preguntas frecuentes (2.8).

### ✅ 2.8 Falta una sección de preguntas frecuentes y problemas comunes
- **Estado (2026-11-26): `docs/FAQ.md` y `docs/FAQ.es.md`, enlazados desde los README. Sin probar: partidas de otros emuladores.**
Para el día del anuncio, en el README (o en `docs/FAQ.md`):
- antivirus y SmartScreen con un `.exe` sin firmar que compila código (está como una línea; dar los pasos concretos);
- Play Protect bloqueó el APK la primera vez (`plan.md`, v0.12): decir qué hacer;
- qué ROM vale y cómo comprobar el CRC32;
- si el `.srm` es compatible con el de un emulador (importar una partida existente);
- los `.sst` dependen de la versión del motor: avisar de que un estado puede dejar de cargar tras actualizar;
- requisitos mínimos de CPU (con TinyCC un equipo de la mitad de potencia que un i5-13420H va justo, según `plan.md` §8b);
- dónde están las partidas en cada sistema (ver 3.1).

### 🔶 2.9 No se puede saber qué motor lleva cada paquete **[motor]**
- **Estado (2026-11-27): 🔶 hecho en código (commit `e751ae8` de la rama `game-options-scroll` del motor): `--version` (`snes-recomp`/`snes-port`), el commit en la línea de versión de los tres lanzadores, `ENGINE_VERSION` en el zip (que `update-engine.ps1` copia aquí) y `release.ps1` que falla con el árbol sucio y nombra el zip con la etiqueta o el commit. Probado: `--version` en una compilación de depuración (`0.1.0 (3b3dc26-dirty)`). Sin probar: `release.ps1` entero, el lanzador de Windows/Linux y el APK con la línea nueva. Falta fusionar la rama, subir y reconstruir `alttp-recomp.exe`. Las 10 modificaciones sin commit de `..\snes-recomp` (`hirom-mapping`) siguen ahí: hay que cerrarlas antes de etiquetar un motor.**
- `..\snes-recomp` tiene **10 ficheros modificados sin commit** (+496 líneas: `codegen.rs`, `config.rs`, `rom.rs`, `snes_core.inc`, `snes_rt.h`…, cambio `hirom-mapping`). No tiene **ninguna etiqueta**, y su `release.ps1` siempre produce `snes-port-0.1.0-win64.zip`.
- El `alttp-recomp.exe` de la raíz (fecha 2026-11-24 20:50) se pudo construir con cambios sin commit: nadie puede reconstruirlo igual, y si falla en el equipo de alguien no se sabe qué código lleva.
- **Hacer:** en el motor, versión y etiqueta en cada zip; que el zip no se construya con el árbol sucio (que `release.ps1` falle si `git status` no está limpio); y que el binario imprima su commit (`alttp-recomp.exe --version`, y en el lanzador junto a la versión del juego). Aquí, un `ENGINE_VERSION` (etiqueta y commit del motor) junto a `alttp-recomp.exe`, que escriba `update-engine.ps1`.

---

## 3. Documentación desactualizada o contradictoria 🟡

### 🔶 3.1 Carpeta de partidas en Linux
- **Estado (2026-11-26): README y FAQ corregidos según el código del motor; falta comprobarlo con el `.tar.gz` real.**
- README/README.es: `~/.local/share/alttp-recomp/saves`. `CLAUDE.md` y `DESARROLLO.md`: `saves/` junto a `snes-port`, o `~/.local/share/snes-port/saves`. Puede que las dos sean ciertas (paquete frente a motor compilado), pero el README no lo distingue. **Hacer:** comprobarlo con el paquete `.tar.gz` y decir las dos rutas.

### ✅ 3.2 `docs/TRADUCCION.md`
- **Estado (2026-11-26): Ahora dice 168 px.**
- Dice «con líneas de 32 letras como máximo». La regla real es **168 píxeles** con la tabla de anchos de la ROM (`CLAUDE.md`, `check_text.py`). Corregir: un traductor nuevo seguiría la regla equivocada.

### ✅ 3.3 `docs/DESARROLLO.md`
- **Estado (2026-11-26): Lista de ficheros al día; selector de idioma de Android/Windows corregido.**
- «en Android todavía no hay selector» de idioma: el README dice que la pantalla de inicio de Android tiene botón EN/ES.
- La lista «Qué contiene» no nombra `quality.c`, `hud.c` ni `icon.c` (ni `check_text.py`, `check_guards.py`, `probe_*.py`, `route.py`).
- **Hacer:** ponerlo al día. Y que la estructura salga de un solo sitio (`DESARROLLO.md`), con `CLAUDE.md`/`AGENTS.md` enlazando allí, para que no se desfasen.

### ✅ 3.4 Comentario de `games/alttp_usa/dialog.c`
- **Estado (2026-11-26): Comentario corregido.**
- La cabecera dice «the text appears three times faster»; el código (y el README) hacen un carácter por fotograma. ⚪

### 🔶 3.5 README: estado y versión
- **Texto preparado para cuando salga la release (2026-11-27):**
  - EN: «**Beta.** Releases 0.16 and later include the fix for the halt in rooms `0x01B`, `0x043` and `0x097` on Windows, Linux and Android (the generator leaves 0 untranslated functions out of 4,178). If you are on 0.13 or earlier, update.» (quitar lo de «Windows-only pre-releases»).
  - ES: «**Beta.** Las releases 0.16 y posteriores llevan el arreglo de la parada en las salas `0x01B`, `0x043` y `0x097` en Windows, Linux y Android (el generador deja 0 funciones sin traducir de 4 178). Si tienes la 0.13 o anterior, actualiza.»
- **Estado (2026-11-26): «Status» reescrito para decir lo que es cierto hoy (beta; la 0.13 se para en tres salas). Hay que volver a reescribirlo cuando salga la release.**
- La sección «Status» explica la 0.13 estable y las 0.14/0.15 pre-releases. En cuanto salga la release del punto 1.1 hay que reescribirla (en los dos README) y quitar lo de «Windows-only pre-releases».

### 🔶 3.6 Etiquetas locales
- **Estado (2026-11-26): Etiquetas `v0.12`–`v0.15` traídas y recolocadas en `main` (con la reescritura de historia). `git fetch --tags` antes de cada release.**
- El clon local solo tiene las etiquetas `v0.1`–`v0.11`; en GitHub existen `v0.12`–`v0.15`. `git fetch --tags` antes de la próxima release (si no, `git describe` y cualquier script que mire las etiquetas se equivocan).

### ✅ 3.7 El banner del README sale cortado
- **Estado (2026-11-26): Subtítulo cortado eliminado del banner.**
- En `docs/img/banner.png` (1280×270) el subtítulo de debajo de «ALttP Recomp» queda **cortado por el borde inferior**: solo se ven las puntas de las letras. Es la primera imagen que ve quien entra en el repositorio. **Hacer:** volver a generarlo con más alto (o el subtítulo más arriba) o quitar el subtítulo.

### ✅ 3.8 El README promete el menú F1 para las mejoras
- **Estado (2026-11-26): README sin la promesa; dice que se activan con `--game-opt`.**
- Ver 1.4. Mientras no estén declaradas, la frase «turn them on in the **Game** tab of the **F1** menu» (y la de `README.es.md`) es falsa.

---

## 4. Código del juego 🟡

### ✅ 4.1 `text.c`: al volver de `es` a `en` en plena partida, los glifos `$47`–`$49` siguen siendo `ñ ¿ ¡`
- **Estado (2026-11-26): Hecho en `text.c`. Falta añadir el caso a la prueba del cambio de idioma en caliente de `check.ps1`/`check.sh`.**
- `alttp_text_translate` solo llama a `use_letters()` cuando `language == es`. Con `language = en` en caliente y las letras puestas (`letters_state == 1`), la fuente sigue con `ñ ¿ ¡` en `$47`–`$49` hasta volver a un menú (`alttp_text_menus`, módulos < 6). Esos códigos son los signos de los mensajes 182 y 188 (la escritura hyliana): en inglés saldrían mal hasta pasar por la selección de partida.
- **Arreglo:** en `alttp_text_translate`, con `language != es`, `if (letters_state == 1) use_letters(0);`. Añadir el caso a la prueba del cambio de idioma en caliente de `check.ps1`/`check.sh`.

### ✅ 4.2 `text.c`: `label_codes` no deletrea etiquetas de más de 16 letras
- **Estado (2026-11-26): ✅ Hecho: `label_codes` recorta a 16 letras. Sin probar con un mando real.**
- Si `input_label` da un nombre de tecla largo (por ejemplo «Right Shift» con un prefijo, o el nombre de un botón de mando raro), `label_codes` devuelve 0 y el mensaje deja el icono original sin avisar. ⚪ Valorar abreviar o recortar en vez de abandonar.

### ➖ 4.3 Estado en variables `static` y estados guardados
- **Estado (2026-11-26): Sin cambios necesarios; mantener la regla.**
- Repasado: `sfx_on_entry`, `rup_*`, `deaths_before`, `somaria_in_*`, `moldorm_in_46`, `kiki_in_cc`, `absorb_in_shield` y `cancelling` viven solo de la entrada a la salida de una rutina, y `camera_applied` se borra en `07:81A0` antes de que se use. Cumplen la regla del `CLAUDE.md`. No hay nada que cambiar; solo **mantener la regla** en lo que se añada y anotarla en cada comentario nuevo (como ya hace `bird_cancel`).

### ✅ 4.4 `check.sh` y `check.ps1` deben ir a la par
- **Estado (2026-11-26): `ci.yml` comprueba también `check.sh`.**
- CI comprueba que cada `.c` esté en `check.ps1`, pero **no en `check.sh`** (`for f in dialog.c widefill.c …`, línea 43), aunque `CLAUDE.md` pide las dos. Añadir el mismo paso para `check.sh` en `ci.yml`.

### ✅ 4.5 Los ficheros de traducción no aceptan el BOM de UTF-8
- **Estado (2026-11-26): `text.c` y `menutext.c` saltan el BOM; `check_text.py` lo avisa.**
- `text.c` (`parse_file`) y `menutext.c` (`parse_file`) no saltan los bytes `EF BB BF` del principio. Hoy los dos ficheros empiezan por `#` sin BOM (comprobado con `od`), pero el Bloc de notas de Windows y otros editores lo añaden. Con BOM, en `es.txt` sale un aviso («text before the first @NNN») y se ignora; en `es_menu.txt`, si la primera línea fuera una clave, esa clave se perdería en silencio («no string called …»). Lo mismo valdrá para `de.txt` del issue #1.
- **Arreglo:** saltar el BOM al empezar a leer (tres líneas en cada `parse_file`) y que `check_text.py` lo avise.

### ✅ 4.6 Detalle de la traducción del menú
- **Estado (2026-11-26): ✅ `erase.which = QUE DATOS QUIERES?` (18 letras). Falta verlo en pantalla.**
- `erase.which = QUE DATOS QUIERES` acaba sin `?`, al contrario que `copy.which = CUAL?` y `copy.to_which = A CUAL?`. Caben 24 letras: `QUE DATOS QUIERES BORRAR?` (25) no entra, pero `QUE DATOS BORRAS?` o `QUE DATOS QUIERES?` sí. ⚪ Revisar las tres en pantalla.

### ✅ 4.7 Lectura del fichero de traducción en cada mensaje
- **Estado (2026-11-26): ✅ `text.c` mira el fichero una vez por segundo como mucho (`menutext.c` ya lo hacía cada 30 fotogramas).**
- `text.c` hacía un `stat()` del fichero de traducción en **cada** cuadro de texto y `menutext.c` cada 30 fotogramas, para poder editarlo con el juego en marcha. Es útil para traducir, pero en el móvil y con la carpeta del juego en un disco lento es trabajo innecesario. ⚪ Valorar hacerlo solo con una opción de desarrollo (`lang_reload=1`) o con un intervalo mayor; no corre prisa.

---

## 5. CI y empaquetado 🟡

### ✅ 5.1 La guarda de ficheros prohibidos de CI está incompleta
- **Estado (2026-11-26): Guarda de CI igualada con `.gitignore`.**
- `ci.yml` busca `\.(sfc|smc|srm|sst)$|^(roms|out)/`. Faltan `*.thumb` (miniaturas: gráficos del juego), `*.fig`, `*.swc` y los volcados `alttp_messages_*.txt` / `alttp_menu_*.txt`, que sí están en `.gitignore`. Igualar la lista con `.gitignore` y con la guarda de `release.ps1`.

### ✅ 5.2 Comprobar la traducción en CI sin ROM
- **Estado (2026-11-26): `check_text.py --sin-rom` y paso nuevo en CI.**
- `check_text.py` necesita la ROM para los anchos, pero una parte no: UTF-8 válido, solo los caracteres permitidos, `¿`/`¡` que casan, formato `@NNN` y `{hh}`, y los límites y el alfabeto de `es_menu.txt`. Separar esa parte (`--sin-rom`) y ejecutarla en CI: es lo que más van a tocar los colaboradores (issue #1).

### 🔶 5.3 Contenido del zip de Windows
- **Estado (2026-11-26): Hecho: sin `SDL2.pdb`, `SDL2main.lib` ni `SDL2test.lib` (zip de 4,9 a 2,7 MiB) y `README.txt` bilingüe en el zip. Se mantienen `SDL2.dll`, `SDL2.lib` y las cabeceras.**
- `sdl2\` entero va al paquete: `SDL2.pdb` (6,6 MB), `SDL2test.lib`, `SDL2main.lib` y todas las cabeceras. Comprobar qué necesita de verdad TinyCC para construir (probablemente `SDL2.dll`, `SDL2.lib` y algunas cabeceras) y quitar el resto: el `.pdb` solo pesa.
- El zip lleva `README.md` en Markdown. Para quien descomprime en Windows, un `LEEME.txt`/`README.txt` corto (qué abrir, qué ROM, dónde van las partidas) ayuda más.

### ⬜ 5.4 Firma de los paquetes
- **Estado (2026-11-26): Sin hacer (firma del `.exe` y de `SHA256SUMS`).**
- Ni el `.exe` está firmado (SmartScreen y antivirus) ni `SHA256SUMS` lleva firma: el actualizador se fía de lo que haya en la cuenta de GitHub. Ya está en `plan.md` §7c («firmar las releases (minisign)»). Opciones gratuitas para código abierto: SignPath Foundation para el `.exe`; minisign o las *artifact attestations* de GitHub para `SHA256SUMS`, con la clave pública dentro del lanzador. **[motor]** para la verificación.

### ✅ 5.5 Avisos de las acciones
- **Estado (2026-11-26): `actions/checkout` y `upload-artifact` a `@v7`; CI en verde.**
- `plan.md` anota los avisos de Node 20 en `actions/checkout@v4` y de la migración de `ubuntu-latest`. Subir las versiones de las acciones (`checkout`, `upload-artifact`) antes de que dejen de funcionar.

### ✅ 5.6 `.gitignore`
- **Estado (2026-11-26): `.claude/` en `.gitignore`.**
- Añadir `.claude/` (aparece sin seguimiento en `git status`) y los ficheros temporales de `out\` que generan los scripts fuera de `out\` si los hay (`engine.tmp/` ya está).

---

## 6. Comunidad y repositorio 🟡

- **Estado (2026-11-26): 🔶 parcial.** Hecho: Discussions activado y enlazado en el selector de issues, temas nuevos, etiquetas `translation`, `engine` y `needs-repro`, `CONTRIBUTING.md` (EN) y `CONTRIBUTING.es.md`, plantillas con `UNSUPPORTED`. Issue #1 respondido (en español, por el usuario). Hecho el 2026-11-27: aviso de requisitos por plataforma junto al botón de la página de descargas; `bug.yml` ya tiene el campo de opciones activas (texto libre: las casillas esperan al menú F1, 1.4) y pide el `UNSUPPORTED`. Pendiente: *milestone* de la 1.0, menú F1 del motor en inglés, ~~`THIRD-PARTY.txt` (7)~~ (hecho). 2026-11-27: `bug.yml` pide las líneas `game.` de `config.ini` en lugar de casillas (32 casillas serían demasiadas).

- **Issue #1 (alemán):** la respuesta está bien, pero solo en español; añadir un resumen en inglés. Es la primera aportación externa: conviene responder rápido y en el idioma de quien pregunta.
- **Discussions desactivado:** activarlo para preguntas («¿qué ROM?», «no arranca») y dejar los issues para fallos. Enlazarlo desde `ISSUE_TEMPLATE/config.yml`.
- **Plantilla de issue «me quedé bloqueado / el juego se paró»:** pedir versión, plataforma, sala o zona, el texto `UNSUPPORTED …` si sale, y si hay estado guardado de justo antes (por privado, ver 1.2).
- **`CONTRIBUTING.md`:** explicar en inglés cómo proponer un idioma nuevo (lo que se le contestó en el issue #1: `lang/<xx>.txt`, 168 px, `check_text.py`) y qué cosas son del motor y cuáles de aquí.
- **Etiquetas de GitHub** (`good first issue`, `translation`, `engine`, `needs-repro`) y un *milestone* para la 1.0.
- **Temas del repositorio:** añadir `recompilation`, `decompilation`, `snes-recomp`, `android`, `linux`, `windows`, `spanish-translation`.
- **Menú F1 en inglés solamente** **[motor]**: con `language=es` el juego sale en español pero el menú del motor no. Decirlo en el README o traducirlo.
- **Página de descargas** (`docs/index.html`): solo mira `releases/latest`, así que hoy ofrece la 0.13 (ver 1.1). En un móvil Android de 32 bits o un Linux ARM (Raspberry Pi) ofrece igual el APK arm64 o el `.tar.gz` x86_64, que no funcionan; conviene avisar («Android 10+ arm64», «Linux x86_64») junto al botón, como ya hace la tabla del README.
- **Plantilla de errores** (`bug.yml`): está bien. Añadir un campo «¿Qué opciones de calidad de vida tienes activas?» con casillas (cuando existan en el menú, 1.4), y pedir el texto de la consola o del lanzador si sale `UNSUPPORTED`.

---

## 7. Legal y marca ⚪

- El aviso legal es claro y la regla de no subir nada derivado se cumple (`check_text.py` pasa: 382 mensajes, el más ancho de 168 px; CI en verde).
- `docs/img/banner.png` (revisado): damero verde, marco dorado, una Trifuerza dibujada y el título en una tipografía de píxel propia; no se ven gráficos de la ROM. La Trifuerza es un símbolo de la marca: aceptable en un proyecto de fans, pero no darle más protagonismo.
- Antes de anunciar, **repasar a mano** que el resto de imágenes, las capturas del lanzador (`launcher*.png`), `android-controls.png` y los iconos de `games/alttp_usa/android/res/` sean **arte propio**, sin sprites, letras ni logotipos del juego. Las capturas del juego en sí no deben subirse (ya es regla).
- **Revisión de imágenes (2026-11-27):** vistas `android-controls.png`, `launcher.png`, `launcher-pick.png`, `launcher-update.png` y el icono `mipmap-xxxhdpi/ic_launcher.png`: damero verde, marco dorado, Trifuerza, botones y cristal dibujados a mano en píxel; ningún sprite, letra ni logotipo del juego. Sin abrir aún: las variantes `-es` del lanzador (mismo arte con texto en español) y el resto de densidades del icono (misma fuente, otra escala).
- El nombre del repositorio y del paquete llevan «alttp»/«Zelda»: es lo habitual en los ports (`zelda3`), pero no usar el logotipo oficial ni la tipografía de Nintendo en el banner ni en la página de descargas.
- TinyCC (LGPL 2.1) va con su aviso y el enlace al código fuente (`toolchain/AVISO-TINYCC.txt`); SDL2 con `COPYING.txt`. Bien. ~~Falta `THIRD-PARTY.txt`~~ Hecho el 2026-11-27: `THIRD-PARTY.txt` en la raíz y en los dos paquetes (SDL2, TinyCC, crates del motor con remisión a su `Cargo.lock`). Falta que el motor genere la lista exacta de crates **[motor]**.

---

## 8. Después del lanzamiento (no bloquea)

- Comparar un recorrido natural (no forzado) contra BizHawk con `route.py` + `compare_samples.py` (HALLAZGOS §6).
- Terminar el barrido de las entradas `0`–`0x84` con `guards_win_fuzz.py` (se paró a medias: 87 de 266 partidas) y que el script imprima resultados parciales.
- Probar en un Windows limpio (máquina virtual sin Visual Studio ni gcc, con y sin red) y en un móvil Android de gama media (`plan.md` §8b y §7b).
- Medir el rendimiento con ventana y audio en el Celeron tras los cambios del motor y anotar a oído tirones y crujidos (`plan.md` §7).
- Otras ROM (EU, JP) y más idiomas (alemán, issue #1).

---

## Orden recomendado

1. **1.1** release con los tres paquetes y el arreglo de `01:CA17` (+ **1.3** versión única, **2.9** motor con versión y **3.6** etiquetas).
2. **1.4** mejoras en el menú F1 (motor: más de 16 opciones; aquí: un `[[option]]` por mejora). Hasta entonces, corregir el README (**3.8**).
3. **2.3** y **2.4**: quitar rutas personales del binario y de `plan.md` antes de que el proyecto tenga más visitas.
4. **4.1**, **4.4**, **4.5**, **5.1**, **3.7**: arreglos pequeños y baratos.
5. **2.5**, **2.6**, **2.8**, **3.x**: documentación honesta y bilingüe.
6. **2.1** y **2.2**: paridad del lanzador de Windows y paquetes desde CI.
7. **1.2**: partida completa (o anunciar como beta pública).
