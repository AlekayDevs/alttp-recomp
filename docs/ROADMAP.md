# Hoja de ruta

Qué falta por hacer, al 2026-11-26. Lo que ya está hecho está en el [README](../README.md) y en [HALLAZGOS.md](HALLAZGOS.md). El diario de trabajo anterior (pruebas, releases 0.1 a 0.13, mediciones de rendimiento) era el `plan.md` de la raíz; está ahora en [HALLAZGOS.md §7](HALLAZGOS.md#7-diario-de-trabajo-detallado-antes-planmd).

Reparto (ver `CLAUDE.md`): lo general va al motor ([snes-recomp](https://github.com/ArgoxDevs/snes-recomp)); aquí solo lo específico de ALttP.

## 1. Demostrar que el juego se pasa

Nadie ha jugado una partida completa con la recompilación. Las 296 salas de mazmorra cargan al forzarlas (HALLAZGOS §5.7), pero eso se salta las puertas y el código normal de entrada.

- Jugar una partida entera con `--record`, por tramos y con un estado guardado al final de cada uno, hasta los créditos (`$10 = 0x19`) sin `UNSUPPORTED`. Plan en [PLAN_PARTIDA.md](PLAN_PARTIDA.md).
- Llegar jugando a las salas `0x01B`, `0x043` y `0x097` y comprobar que `01:CA17` hace lo de la consola (hoy lo cubre un `[[assume]]` del perfil).
- `08:A8E3` (entrada `0x24` de la tabla de `08:837F`): no se sabe si el juego la usa.
- Comparar un recorrido natural contra BizHawk con `route.py` y `compare_samples.py`.
- Hasta entonces, las versiones se publican como pre-lanzamiento o «beta pública».

## 2. Pruebas de los arreglos del original

Ver la sección «How well the fixes are tested» del README. Falta reproducir jugando, sin preparar estados: los ocho arreglos `guard` (`fix_door_submodule`, `fix_stair_tags`, `fix_skullwoods_door`, `fix_mushroom_warp`, `fix_double_absorb`, `fix_hidden_hookshot`, `fix_camera_twice`, `fix_bunny_walk`), `fix_portal_chime` en el Palacio de Hielo y `fix_death_count` con «guardar y salir». El barrido de las entradas `0`–`0x84` con `guards_win_fuzz.py` se paró a medias (87 de 266 partidas): repetirlo entero, y que el script imprima resultados parciales.

No hechos a propósito: la superbomba (los tres cambios de `zelda3` dependen unos de otros), la capa de invisibilidad (cambia el juego) y el espejo al Mundo Oscuro (salta la progresión).

## 3. Lanzamiento y paquetes

- ~~Una release con los tres paquetes y el arreglo de `01:CA17`~~: hecho, la 0.16 (2026-11-27) es la «Latest».
- Paquetes desde CI: Windows y Linux ya salen de CI (2026-11-27; el motor de Windows es el commiteado, el de Linux está fijado a `ENGINE_VERSION`). Falta el APK desde CI y la copia de la clave del APK fuera del equipo.
- Motor con versión y etiqueta en cada zip, sin construir con el árbol sucio (`snes-recomp`): hecho en código el 2026-11-27 (`--version`, `ENGINE_VERSION`, `release.ps1` estricto); falta fusionar la rama del motor, probar `release.ps1` y ponerle una etiqueta (antes, cerrar los cambios `hirom-mapping` de `..\snes-recomp`).
- Firmar las releases (minisign o *attestations*) y el `.exe` (SignPath).
- Notas de versión y descripción del repositorio bilingües; `CHANGELOG.md`; preguntas frecuentes.

## 4. Paridad del lanzador y opciones

- Aviso de actualización: probada en Windows la instalación real de la 0.15 a la 0.16 (2026-11-27, sin ratón: `saves\` intacta). Probada también pulsando los botones de la ventana (mismo día). Falta probar en Linux.
- Mejoras de calidad de vida en el menú F1: hecho en código (2026-11-27; motor con 64 opciones, desplazamiento y `desc`; 32 `[[option]]` aquí). Subido, con la ayuda en el menú táctil y las etiquetas en español; falta probarlo en un Android real.
- Probar en un Windows limpio (sin Visual Studio ni gcc, con y sin red), en un Android de gama media y con mando Bluetooth.

## 5. Traducción

- Mapa: no se encontró texto de zonas que traducir; mirarlo en el juego real, al aire libre.
- Revisión en pantalla de `es.txt` y de los nombres de objeto de `es_menu.txt`.
- Más idiomas (alemán, issue #1) y otras ROM (EU, JP, alemana): mismo perfil con otras direcciones.

## 6. Rendimiento y extras (motor)

- Rendimiento con ventana y audio en el equipo modesto (Celeron) tras los últimos cambios de la PPU y del audio; anotar a oído tirones y crujidos. `wide 96` en la intro aún pasa del presupuesto de 16,6 ms.
- Precisión de tiempos (HDMA, ondas del Mundo Oscuro), herramientas de depuración, audio MSU-1, 60 fps con interpolación, modo 7 en alta resolución, shader de CRT, logros y netplay (estos dos exigen determinismo estricto).
