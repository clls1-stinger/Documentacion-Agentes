# 🌐 INTEGRACIÓN DE PUPPETEER MCP EN N8N

## 🎯 Objetivo
Permitir que el agente de n8n controle un navegador Chrome/Chromium usando el servidor Puppeteer MCP, de la misma forma que Vega lo usa para autotesting.

## 🧩 Arquitectura MCP (Model Context Protocol)
MCP es un estándar que permite que sistemas de IA (como Gemini) se conecten a herramientas externas. En este caso:
- **Servidor MCP**: Puppeteer (corre como un proceso independiente)
- **Cliente MCP**: Gemini CLI o cualquier cliente compatible
- **Transporte**: Stdio o HTTP

## 🔌 Opciones de Integración

### Opción 1: HTTP Endpoint (Recomendado)
Si el servidor Puppeteer MCP expone un endpoint HTTP, n8n puede llamarlo directamente con un nodo HTTP Request.

**Pasos**:
1. Verificar si el servidor Puppeteer MCP tiene modo HTTP.
2. Crear un nodo "HTTP Request" en n8n que llame a las funciones de Puppeteer.
3. Parsear la respuesta JSON.

**Ejemplo de llamada**:
```json
POST http://localhost:9222/mcp/puppeteer/navigate
{
  "url": "https://example.com"
}
```

### Opción 2: Custom Node para MCP (Avanzado)
Crear un nodo custom de n8n que actúe como cliente MCP y se conecte al servidor Puppeteer.

**Requisitos**:
- Librería cliente de MCP en Node.js
- Lógica de conexión stdio o HTTP
- Exposición de funciones como `navigate`, `click`, `screenshot`

**Ventajas**:
- Integración nativa
- UI amigable en n8n
- Reutilizable

### Opción 3: Bridge Script (Rápido)
Crear un script Python/Node que actúe como puente entre n8n y el servidor MCP.

**Flujo**:
1. n8n ejecuta un script vía `Execute Command`
2. El script conecta con el servidor MCP
3. El script devuelve el resultado a n8n

**Ejemplo**:
```python
# puppeteer_bridge.py
import sys
import json
from mcp import connect_to_server

def navigate(url):
    client = connect_to_server("puppeteer")
    result = client.call("navigate", {"url": url})
    return result

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "navigate":
        print(json.dumps(navigate(sys.argv[2])))
```

**Uso en n8n**:
```bash
python3 puppeteer_bridge.py navigate "https://google.com"
```

## 🛠️ Implementación Recomendada: Opción 3 (Bridge)

### Paso 1: Instalar Cliente MCP
```bash
pip install mcp-client
```

### Paso 2: Crear Script Bridge
Ver archivo: `/home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py`

### Paso 3: Agregar Herramienta en n8n
En el workflow, añadir una nueva rama en el `Tool Router`:
- **Nombre**: `navegar_web`
- **Comando**: `python3 /path/to/puppeteer_mcp_bridge.py navigate <url>`

### Paso 4: Actualizar Prompt del Planner
Añadir en `Planner Prep`:
```
6. navegar_web(url): Abre una página en el navegador y toma screenshot.
```

## 🚀 Casos de Uso
1. **Scraping Dinámico**: El agente puede navegar por sitios que requieren JavaScript.
2. **Automation de UI**: Completar formularios, hacer login, etc.
3. **Testing Visual**: Capturar screenshots de aplicaciones web.
4. **Extracción de Datos**: Obtener información de páginas dinámicas.

## ⚠️ Consideraciones de Seguridad
- **Sandbox**: Ejecutar Puppeteer con `--no-sandbox` solo en entornos controlados.
- **Rate Limiting**: Limitar el número de navegaciones por minuto.
- **Credenciales**: Nunca pasar credenciales directamente en el prompt del agente.

## 📚 Referencias
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Puppeteer MCP Server](https://github.com/anthropic/mcp-puppeteer)

## 🕵️ PERSISTENT DEBUG BROWSER (User Config)
Para facilitar el debugging visual y la inspección en tiempo real, se ha configurado un navegador persistente.

**Configuración Local**:
- **Archivo**: `/home/emky/.gemini/antigravity/mcp_config.json`
- **Función**: Mantiene una instancia de navegador siempre abierta para que el Agente la utilice como herramienta de inspección/debug sin necesidad de abrir y cerrar sesiones constantemente.
- **Acceso**: El agente debe priorizar la conexión a esta pestaña/instancia activa si está disponible para acelerar el ciclo de feedback.

---
**ARQUITECTO**: Vega ⭐
**Última Actualización**: 2026-02-03T12:28Z

