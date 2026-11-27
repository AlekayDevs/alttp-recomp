# Changelog / Registro de cambios

English first, then Spanish. Versions are published on the [releases page](https://github.com/ArgoxDevs/alttp-recomp/releases); this file is the summary. The version in force is in the `VERSION` file.

---

## English

### Unreleased
- (nothing yet)

### 0.17
- Packaging: the Windows package is built by a CI workflow (`windows-package.yml`) from the committed engine, and the Linux workflow pins the engine to the commit in `ENGINE_VERSION`.
- Supply chain: the Windows and Linux packages built by CI carry a signed build-provenance attestation (`gh attestation verify <file> -R ArgoxDevs/alttp-recomp`); see the FAQ. The 0.14 and 0.15 release notes are now bilingual.
- Docs: the Linux package keeps saves in `~/.local/share/alttp-recomp/saves` (the FAQ and README said otherwise).
- ROM errors: a refused ROM now says what the file is (size, removed header, internal title, odd size) and the usual causes; a `.zip`/`.7z`/`.rar` is named as an archive. Android accepts `.smc` ROMs with a copier header (it refused them before).
- Updater (Windows): unpacks with the system `tar`, so a Git Bash `tar` first in PATH no longer breaks it.

### 0.16 (2026-11-27)
- Engine traceability: `alttp-recomp.exe --version` prints the engine version and commit, the launcher shows it next to the game version (Windows, Linux and Android), and the engine package carries an `ENGINE_VERSION` file (copied here by `update-engine.ps1`). The engine's `release.ps1` refuses to build from a tree with uncommitted changes.
- Android: the game's C compiles on the device again (the on-device TinyCC lacked `time.h`, `fputc` and `strcspn`), and the Android/Linux builds no longer break on a duplicated `gl_layer` (engine). The touch menu's Controller page now shows the pad picture with the selected button lit; tapping a button of the picture waits for the controller button, and the change confirmation names the buttons that answer it (A yes, B no). Tested on a tablet with an Xbox Series X controller over Bluetooth.
- Fix: switching `language` from `es` back to `en` in the middle of a game now restores the game's own `$47`–`$49` glyphs (they kept showing `ñ ¿ ¡` until the next menu).
- Translation files may start with a UTF-8 BOM (Windows Notepad adds one); it is skipped when loading.
- `scripts/check_text.py --sin-rom` checks what does not need the ROM (encoding, format, allowed characters, menu limits) and runs in CI.
- The version now comes from a single `VERSION` file read by `release.ps1`, `release.sh` and the Linux package workflow.
- Release binaries no longer contain paths from the build machine (engine).
- A button label longer than 16 letters is cut instead of leaving another button's icon; the translation file is checked once per second at most, not at every text box; the Spanish prompt «QUE DATOS QUIERES?» now ends in `?`.
- Packaging: `release.ps1` takes `games\` from the commit (`git archive HEAD`), not the working tree; new `THIRD-PARTY.txt` (SDL2, TinyCC, engine crates) in both packages.
- Documentation: FAQ, honest per-fix test levels in the README, roadmap, banner fixed.
- **All 32 improvements and fixes are now in the Game tab of the F1 menu** (and in Game options on Android), each with a one-line explanation (in Spanish with `language=es`), saved in `config.ini`. Needs the engine with room for 64 options and a scrolling menu.

### 0.15 (pre-release, Windows only)
- **Fix for a game halt:** `01:CA17`, the routine of certain room tags (used in rooms `0x01B`, `0x043` and `0x097`), was not translated and the game stopped when it reached it. It is translated now; the generator leaves 0 untranslated functions out of 4,178. Checked against BizHawk in the five cases tested.
- `08:A8E3` no longer stops the game (the original does not use it).

### 0.14 (pre-release, Windows only)
- A single executable, `alttp-recomp.exe`, with the game's icon and name (`snes-port.exe` and `snes-recomp.exe` are gone; generator commands are `alttp-recomp.exe recomp <command>`).
- Launcher with the Zelda look (green stone, golden frame, Triforce), like Android and Linux.
- Windows launcher: language button (EN/ES) that remembers the choice, Licenses, visible version, "Check now" and the new-version prompt.

### 0.13
- Language switch on the fly: the pause menu, item names, actions and the LIFE label go back to English without restarting.
- Android: updating from the app was tested.

### 0.12
- **Android: a different app.** The identifier changed to `io.github.alekaydevs.alttprecomp`: it installs next to the old one and starts without saves.
- The pre-publish scan no longer stops at a standard color table that ships inside `SDL2.dll`.

### 0.11
- Maintenance: project moved to the new account; three translation lines fixed (one cut off, one too wide, one missing `¡`) plus an automatic width and sign check.
- `SECURITY.md` and issue templates.

### 0.10 and 0.9
- 0.10: more complete Spanish translation (pause-menu item names with drawings, frame labels, a full review of the messages).
- 0.9: a menu of its own for phones (touch sections, controller remapping, app settings).

### 0.8 and earlier
- 0.8: engine update and Spanish item names in the pause menu. **New Android signing key: uninstall the previous app first.**
- 0.2 to 0.7: Android updates from the app, launcher look and language button, touch D-pad by angular sectors, touch-responsive menu, Linux package built in CI (glibc 2.34), downloads page.
- 0.1: first release (Android, Linux, Windows).

---

## Español

### Sin publicar
- (nada todavía)

### 0.17
- Empaquetado: el paquete de Windows sale de un workflow de CI (`windows-package.yml`) con el motor commiteado, y el de Linux fija el motor al commit de `ENGINE_VERSION`.
- Cadena de suministro: los paquetes de Windows y Linux construidos por CI llevan una *attestation* firmada de procedencia (`gh attestation verify <archivo> -R ArgoxDevs/alttp-recomp`); mira la FAQ. Las notas de la 0.14 y la 0.15 son ya bilingües.
- Documentación: el paquete de Linux guarda las partidas en `~/.local/share/alttp-recomp/saves` (la FAQ y el README decían otra ruta).
- Errores de ROM: una ROM rechazada dice qué es el archivo (tamaño, cabecera quitada, título interno, tamaño raro) y las causas habituales; un `.zip`/`.7z`/`.rar` se nombra como comprimido. Android acepta las `.smc` con cabecera (antes las rechazaba).
- Actualizador (Windows): descomprime con el `tar` del sistema; un `tar` de Git Bash primero en el PATH ya no lo rompe.

### 0.16 (2026-11-27)
- Trazabilidad del motor: `alttp-recomp.exe --version` dice la versión y el commit del motor, el lanzador los enseña junto a la versión del juego (Windows, Linux y Android) y el paquete del motor lleva un fichero `ENGINE_VERSION` (que copia `update-engine.ps1`). El `release.ps1` del motor se niega a construir con cambios sin commit.
- Android: el C del juego vuelve a compilar en el dispositivo (al TinyCC del dispositivo le faltaban `time.h`, `fputc` y `strcspn`) y las compilaciones de Android y Linux ya no se rompen por una `gl_layer` duplicada (motor). La página «Mando» del menú táctil muestra el dibujo del mando con el botón elegido iluminado; tocar un botón del dibujo espera el botón del mando, y la confirmación del cambio dice qué botones responden (A sí, B no). Probado en una tablet con un mando Xbox Series X por Bluetooth.
- Arreglo: al volver de `language=es` a `en` en plena partida se restauran los glifos `$47`–`$49` del juego (seguían mostrando `ñ ¿ ¡` hasta el siguiente menú).
- Los ficheros de traducción pueden empezar con BOM de UTF-8 (el Bloc de notas de Windows lo añade); se salta al cargar.
- `scripts/check_text.py --sin-rom` comprueba lo que no necesita la ROM (codificación, formato, caracteres permitidos, límites del menú) y se ejecuta en CI.
- La versión sale de un único fichero `VERSION` que leen `release.ps1`, `release.sh` y el workflow del paquete de Linux.
- Los binarios de las releases ya no llevan rutas de la máquina que los construyó (motor).
- Una etiqueta de botón de más de 16 letras se recorta en vez de dejar el icono de otro botón; el fichero de traducción se mira una vez por segundo como mucho, no en cada cuadro de texto; el aviso «QUE DATOS QUIERES?» ya acaba en `?`.
- Empaquetado: `release.ps1` toma `games\` del commit (`git archive HEAD`) y no del árbol de trabajo; `THIRD-PARTY.txt` nuevo (SDL2, TinyCC, crates del motor) en los dos paquetes.
- Documentación: preguntas frecuentes, nivel de prueba de cada arreglo en el README, hoja de ruta, banner corregido.
- **Las 32 mejoras y arreglos están ya en la pestaña Juego del menú F1** (y en Opciones del juego en Android), cada una con una línea que la explica (en español con `language=es`), guardadas en `config.ini`. Necesita el motor con sitio para 64 opciones y el menú con desplazamiento.

### 0.15 (pre-lanzamiento, solo Windows)
- **Arreglo de una parada del juego:** `01:CA17`, la rutina de ciertas etiquetas de sala (salas `0x01B`, `0x043` y `0x097`), no se traducía y el juego se detenía al llegar a ella. Ya se traduce; el generador deja 0 funciones sin traducir de 4 178. Comprobado contra BizHawk en los cinco casos probados.
- `08:A8E3` ya no detiene el juego (el original no la usa).

### 0.14 (pre-lanzamiento, solo Windows)
- Un solo ejecutable, `alttp-recomp.exe`, con el icono y el nombre del juego (ya no van `snes-port.exe` ni `snes-recomp.exe`; las órdenes del generador son `alttp-recomp.exe recomp <orden>`).
- Lanzador con el aspecto de Zelda (piedra verde, marco dorado, Trifuerza), como Android y Linux.
- Lanzador de Windows: botón de idioma (EN/ES) con recuerdo, Licencias, versión visible, «Buscar ahora» y aviso de versión nueva.

### 0.13
- Idioma en caliente: el menú de pausa, los nombres de objeto, las acciones y el rótulo VIDA vuelven al inglés sin reiniciar.
- Android: probada la actualización desde la app.

### 0.12
- **Android: otra app.** El identificador pasa a `io.github.alekaydevs.alttprecomp`: se instala junto a la antigua y empieza sin partidas.
- El escaneo previo a publicar ya no se para con una tabla de colores estándar que lleva `SDL2.dll`.

### 0.11
- Mantenimiento: el proyecto pasa a la cuenta nueva; tres líneas de la traducción corregidas (una cortada, una demasiado ancha y un `¡` que faltaba) y una comprobación automática de anchos y signos.
- `SECURITY.md` y plantillas de issues.

### 0.10 y 0.9
- 0.10: traducción al español más completa (nombres de objeto con dibujo del menú de pausa, rótulos del marco, revisión completa de los mensajes).
- 0.9: menú propio para el móvil (secciones táctiles, reasignación del mando, ajustes de la app).

### 0.8 y anteriores
- 0.8: motor actualizado y nombres de objeto en español en el menú de pausa. **Clave de firma nueva en Android: desinstala antes la app anterior.**
- 0.2 a 0.7: actualizaciones desde la app de Android, aspecto del lanzador y botón de idioma, cruceta táctil por sectores angulares, menú táctil, paquete de Linux construido en CI (glibc 2.34), página de descargas.
- 0.1: primera release (Android, Linux, Windows).
