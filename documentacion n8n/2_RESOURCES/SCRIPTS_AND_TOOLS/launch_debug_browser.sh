#!/bin/bash
# 🕵️ Lanzador de Brave en Modo Anti-Gravedad (Debug Remoto)
# Crea un perfil temporal para no chocar con tu sesión principal
# y habilita el puerto 9222 para que el Agente pueda ver y controlar.

echo "🚀 Lanzando Brave en puerto 9222 (Perfil Temporal)..."
echo "⚠️  Nota: Esto abrirá una instancia limpia de Brave/Chrome."

# Intenta detectar el binario (brave, brave-browser, google-chrome)
BROWSER=""
if command -v brave &> /dev/null; then
    BROWSER="brave"
elif command -v brave-browser &> /dev/null; then
    BROWSER="brave-browser"
elif command -v google-chrome &> /dev/null; then
    BROWSER="google-chrome"
elif command -v chromium &> /dev/null; then
    BROWSER="chromium"
fi

if [ -z "$BROWSER" ]; then
    echo "❌ No encontré Brave ni Chrome. ¿Estás seguro de que están en el PATH?"
    exit 1
fi

# Lanza el navegador
$BROWSER \
  --user-data-dir=/tmp/antigravity_browser_debug \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check \
  "http://localhost:5678" &

echo "✅ Navegador lanzado. El Agente MCP ahora puede conectarse."
