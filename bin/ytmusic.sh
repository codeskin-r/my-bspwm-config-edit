#!/bin/bash

# -------- Configuración --------
MUSIC_DIR="$HOME/Music"
QUALITY="0"   # 0 = mejor calidad VBR

# -------- Validación --------
if [ -z "$1" ]; then
    echo "Uso: ytmusic <url_playlist>"
    exit 1
fi

URL="$1"

echo "Descargando playlist..."
yt-dlp \
-x \
--audio-format mp3 \
--audio-quality $QUALITY \
--embed-metadata \
--embed-thumbnail \
--add-metadata \
--parse-metadata "%(playlist_index)s:%(track_number)s" \
-o "$MUSIC_DIR/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s" \
"$URL"

echo "Actualizando base de datos MPD..."
mpc update

echo "Listo."
