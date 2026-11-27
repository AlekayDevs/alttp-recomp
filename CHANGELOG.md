# Changelog / Registro de cambios

English first, then Spanish. Versions are published on the [releases page](https://github.com/ArgoxDevs/alttp-recomp/releases); this file is the summary. The version in force is in the `VERSION` file.

---

## English

### Unreleased
- Fix: switching `language` from `es` back to `en` in the middle of a game now restores the game's own `$47`–`$49` glyphs (they kept showing `ñ ¿ ¡` until the next menu).
- Translation files may start with a UTF-8 BOM (Windows Notepad adds one); it is skipped when loading.
- `scripts/check_text.py --sin-rom` checks what does not need the ROM (encoding, format, allowed characters, menu limits) and runs in CI.
- The version now comes from a single `VERSION` file read by `release.ps1`, `release.sh` and the Linux package workflow.
- Release binaries no longer contain paths from the build machine (engine).
- A button label longer than 16 letters is cut instead of leaving another button's icon; the translation file is checked once per second at most, not at every text box; the Spanish prompt «QUE DATOS QUIERES?» now ends in `?`.
- Packaging: `release.ps1` takes `games\` from the commit (`git archive HEAD`), not the working tree; new `THIRD-PARTY.txt` (SDL2, TinyCC, engine crates) in both packages.
- Documentation: FAQ, honest per-fix test levels in the README, roadmap, banner fixed.
- **All 32 improvements and fixes are now in the Game tab of the F1 menu** (and in Game options on Android), each with a one-line explanation on the desktop, saved in `config.ini`. Needs the engine with room for 64 options and a scrolling menu.

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
- Arreglo: al volver de `language=es` a `en` en plena partida se restauran los glifos `$47`–`$49` del juego (seguían mostrando `ñ ¿ ¡` hasta el siguiente menú).
- Los ficheros de traducción pueden empezar con BOM de UTF-8 (el Bloc de notas de Windows lo añade); se salta al cargar.
- `scripts/check_text.py --sin-rom` comprueba lo que no necesita la ROM (codificación, formato, caracteres permitidos, límites del menú) y se ejecuta en CI.
- La versión sale de un único fichero `VERSION` que leen `release.ps1`, `release.sh` y el workflow del paquete de Linux.
- Los binarios de las releases ya no llevan rutas de la máquina que los construyó (motor).
- Una etiqueta de botón de más de 16 letras se recorta en vez de dejar el icono de otro botón; el fichero de traducción se mira una vez por segundo como mucho, no en cada cuadro de texto; el aviso «QUE DATOS QUIERES?» ya acaba en `?`.
- Empaquetado: `release.ps1` toma `games\` del commit (`git archive HEAD`) y no del árbol de trabajo; `THIRD-PARTY.txt` nuevo (SDL2, TinyCC, crates del motor) en los dos paquetes.
- Documentación: preguntas frecuentes, nivel de prueba de cada arreglo en el README, hoja de ruta, banner corregido.
- **Las 32 mejoras y arreglos están ya en la pestaña Juego del menú F1** (y en Opciones del juego en Android), cada una con una línea que la explica en el escritorio, guardadas en `config.ini`. Necesita el motor con sitio para 64 opciones y el menú con desplazamiento.

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
