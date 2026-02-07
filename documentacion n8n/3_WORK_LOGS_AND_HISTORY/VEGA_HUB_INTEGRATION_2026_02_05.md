# 🛰️ VEGA-HUB INTEGRATION (2026-02-05)

## 🎯 Objetivo
Centralizar la configuración de MCP y el System Prompt dinámico para que todos los flujos de n8n compartan la misma "inteligencia de campo".

## 🛠️ Cambios Realizados

### 1. Puppeteer MCP Server (`mcp_config.json`)
Se ha migrado la configuración de Puppeteer para utilizar un navegador ya abierto (Browser Persistence).
- **Ruta**: `/home/emky/vega-hub/mcp_config.json`
- **Cambio**: Añadido `--browser-url http://127.0.0.1:9222` para conectarse a una instancia de Brave con el puerto de depuración remoto abierto.

### 2. GeminiCLI Node Loader (`GeminiCLI.node.ts`)
El nodo personalizado de Gemini CLI ahora busca un archivo de sistema externo antes de procesar el prompt de la UI.
- **Ruta**: `/home/emky/n8n/custom-nodes/n8n-nodes-gemini-cli-local/nodes/GeminiCLI/GeminiCLI.node.ts`
- **Lógica**: 
    1. Busca `system.md` en `/home/emky/vega-hub/`.
    2. Si existe, lo carga y lo concatena al `systemPrompt` definido en el nodo de n8n.
    3. Esto permite actualizar la "personalidad" o reglas globales de Vega editando un solo archivo Markdown sin tocar n8n.

### 3. Compilación y Corrección del Nodo `GeminiCLI`
Se ha realizado una compilación exitosa del nodo para asegurar que los cambios de carga de archivos y lógica de MCP estén activos.
- **Acción**: Ejecución de `npm run build` en el directorio del nodo.
- **Correcciones Críticas**:
    - **TypeScript 5.3.3**: Se forzó la instalación de TS 5.3.3 para resolver conflictos con tipos de `zod` y `langchain` en las dependencias.
    - **Sintaxis**: Se corrigió una variable `finalInput` no declarada y se ajustó el uso de `NodeConnectionType` para compatibilidad con la versión actual de `n8n-workflow`.

## ✅ Verificación
- El archivo `system.md` en `/home/emky/vega-hub/` es ahora la fuente de verdad para el `finalSystemPrompt`.
- Puppeteer ahora puede interactuar con ventanas existentes de Chrome/Brave si se inician con `--remote-debugging-port=9222`.
- El servidor n8n (`n8n-master`) ha sido reiniciado mediante PM2 para cargar el nuevo binario del nodo.
