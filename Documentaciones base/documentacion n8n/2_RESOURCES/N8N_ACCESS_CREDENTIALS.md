# 🔐 Credenciales de Acceso Local n8n

Estas credenciales permiten al Agente (Vega/Vega) autenticarse de forma autónoma en la instancia local de n8n para realizar tareas de mantenimiento, visual debugging (Puppeteer) y hot-patching.

## 👤 Login n8n (Localhost)

- **URL**: `http://localhost:5678`
- **Usuario/Email**: `howtosnapside@gmail.com`
- **Contraseña**: `Gaming9-Wifi6-Waking4-Getting4-Stream0`

> **Nota de Seguridad**: Este archivo es estrictamente para uso interno del Agente en el entorno local del usuario. No compartir ni subir a repositorios públicos.

## 🤖 Uso con Puppeteer
Cuando se requiera intervención visual:
1. Usar `launch_debug_browser.sh` para abrir navegador.
2. Conectar MCP Puppeteer al puerto 9222.
3. Usar estas credenciales para el bypass del login screen.
