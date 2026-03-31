#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: $0 URL_DE_PLAYLIST"
    exit 1
fi

URL="$1"
DEST="$HOME/Music"

mkdir -p "$DEST"

yt-dlp -x \
--audio-format mp3 \
--embed-metadata \
--embed-thumbnail \
--add-metadata \
--yes-playlist \
-o "$DEST/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s" \
"$URL"

echo "Descarga completada."
