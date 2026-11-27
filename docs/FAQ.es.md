# Preguntas frecuentes y problemas comunes

[English](FAQ.md) · Volver al [README](../README.es.md).

## ¿Qué ROM necesito?

La versión **USA** de *The Legend of Zelda: A Link to the Past*, CRC32 **`777AAC2F`**. También vale una ROM con cabecera de copiadora de 512 bytes (`.smc`): la cabecera se ignora. Las versiones europea, japonesa y alemana, las traducciones y los hacks tienen otro CRC32 y se rechazan; otras regiones están en la [hoja de ruta](ROADMAP.md).

Para comprobar la tuya (el CRC32 del fichero sin cabecera, si la tiene):

```
python -c "import sys,zlib;d=open(sys.argv[1],'rb').read();d=d[512:] if len(d)%1024==512 else d;print('%08X'%zlib.crc32(d))" alttp_usa.sfc
```

La ROM nunca se incluye, se sube ni se envía a ningún sitio.

## Windows dice «Windows protegió su PC» (SmartScreen) o mi antivirus lo bloquea

`alttp-recomp.exe` no está firmado y, la primera vez que abres el juego, genera y compila código C en tu equipo, algo de lo que algunos antivirus desconfían. No se descarga ni se envía nada: todo ocurre en local, y el código está en este repositorio y en [snes-recomp](https://github.com/ArgoxDevs/snes-recomp).

1. Comprueba que la descarga es la publicada: en PowerShell, `Get-FileHash .\alttp-recomp-X.Y-win64.zip` debe coincidir con la línea de ese fichero en el `SHA256SUMS` de la release.
2. SmartScreen: pulsa **Más información** y después **Ejecutar de todas formas**.
3. Si tu antivirus lo pone en cuarentena, restáuralo y añade a sus exclusiones la carpeta donde descomprimiste el juego.

## Android: «Bloqueada por Play Protect» o «aplicación no instalada»

El APK se reparte fuera de Play Store, así que Android pregunta antes de instalarlo. Permite instalar desde tu navegador o gestor de ficheros cuando lo pida y, en el aviso de Play Protect, elige **Más detalles** y después **Instalar de todos modos**. Necesita Android 10 o posterior en un móvil ARM de 64 bits (arm64); el paquete de Linux es solo para PC x86_64.

Desde la versión 0.12 la app de Android tiene otro identificador: se instala **junto a** la antigua y empieza sin partidas; mira las notas de esa release.

## ¿Dónde están mis partidas?

- **Windows:** la carpeta `saves\` junto a `alttp-recomp.exe` (o `%APPDATA%\snes-port\saves` si en esa no se puede escribir).
- **Linux:** `saves/` junto al programa, o `~/.local/share/snes-port/saves` (`$XDG_DATA_HOME/snes-port/saves`) si ahí no se puede escribir. El lanzador guarda sus ajustes (idioma, última ROM) en `~/.local/share/alttp-recomp`.
- **Android:** dentro de la carpeta propia de la app.

`.srm` es la partida del juego, `.sst` un estado guardado y `.thumb` la miniatura de un estado.

## ¿Puedo usar una partida de otro emulador?

No está probado. Haz copia de tus ficheros, copia el `.srm` del emulador sobre el `.srm` del juego (mismo nombre que la ROM) y pruébalo. Si lo haces, cuéntanos en un issue si funcionó.

## ¿Mis estados guardados sobreviven a una actualización?

Las partidas del propio juego (`.srm`) siempre. Los estados (`.sst`) guardan un número de formato y el CRC32 de la ROM; si una versión futura cambia el formato, los estados antiguos no cargarán (no se pierde nada: sigue desde tu partida normal). Si te importa un estado, guarda desde el menú del juego antes de actualizar.

## ¿Qué equipo necesito?

Cualquier PC reciente lo mueve con holgura. Medido: un i5-13420H mantiene 60 fps con el TinyCC del paquete con unos 8 ms libres por fotograma; un equipo con la mitad de potencia va justo, y la opción de pantalla ancha (`wide`) cuesta más. Sin ventana, un Celeron N4000 (unos 1,1 GHz de base) necesita unos 12 ms por fotograma con gcc, por debajo de los 16,6 ms disponibles. En Windows no hace falta instalar compilador: TinyCC viene en el paquete.

## La primera vez tarda

La primera vez el lanzador genera y compila el juego desde tu ROM (unos 3 minutos con gcc, menos con el TinyCC del paquete en un PC rápido). Se guarda en caché por el CRC32 de la ROM; los siguientes arranques son instantáneos. `alttp-recomp.exe clean roms\alttp_usa.sfc` borra la caché si un cambio no se nota.

## El juego se paró con `UNSUPPORTED …`

Es un fallo. La 0.13 y anteriores se paran al entrar en las salas `0x01B`, `0x043` y `0x097` (una función del juego no se traducía); el arreglo está en la 0.15. Si lo ves en una versión más nueva, [abre un issue](https://github.com/ArgoxDevs/alttp-recomp/issues/new/choose) con la versión, el mensaje exacto y dónde estabas. Nunca adjuntes la ROM, partidas ni capturas con gráficos del juego.

## ¿Cómo activo las mejoras de calidad de vida?

Con `--game-opt nombre=valor` en la línea de órdenes (mira el README). La pestaña **Game** del menú F1 solo ofrece `language` por ahora, así que en Android y al abrir desde el lanzador todavía no se pueden activar las demás.

## ¿Cómo añado un idioma?

Mira [TRADUCCION.md](TRADUCCION.md): un fichero `lang/<xx>.txt` con líneas de 168 píxeles como máximo, comprobado con `scripts/check_text.py`.
