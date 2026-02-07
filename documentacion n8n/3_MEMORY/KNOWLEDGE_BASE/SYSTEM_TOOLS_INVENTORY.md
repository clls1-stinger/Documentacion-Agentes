# 📖 Inventario de Herramientas del Sistema (Vega/Vega)

**Autor:** Vega (Vega OS Kernel)
**Fecha:** 2026-02-03
**Propósito:** Documentar todas las capacidades y herramientas disponibles para el agente, tanto a nivel de workflow de n8n como a nivel de infraestructura MCP.

---

## 1. Herramientas del Agente n8n (Workflow "Yes")

Estas son las capacidades que el **Planner** (Cerebro Estratégico) puede invocar. El **Actor** (Ejecutor Técnico) las traduce a comandos que el `Tool Router` del workflow ejecuta.

| Herramienta | Descripción de Uso | Nodo n8n Invocado |
| :--- | :--- | :--- |
| `buscar_en_drive(query)` | Busca archivos en Google Drive que coincidan con un término de búsqueda. Devuelve una lista de archivos con sus IDs. | `Drive Search` |
| `descargar_de_drive(fileId, filename)` | Descarga un archivo específico de Google Drive al directorio local de descargas (`/home/emky/n8n/descargas/`). | `Drive Download` |
| `subir_a_drive(filename)` | Sube un archivo desde el directorio local al raíz de Google Drive. | `Drive Upload` |
| `ejecutar_comando(command)` | Ejecuta un comando de terminal `bash` en el sistema anfitrión. Es la herramienta principal para interactuar con archivos locales (listar, mover, descomprimir, etc.). | `Execute Command` |
| `leer_archivo(path)` | Lee el contenido de un archivo de texto en el sistema local y lo devuelve como string. | `Read Disk` |
| `navegar_web(url)` | **(Recién integrada)** Utiliza el servidor MCP de Puppeteer para abrir una URL en una instancia de navegador controlada. Permite la automatización y el scraping web. | `Execute Command (Puppeteer)` |

---

## 2. Servidores MCP (Model Context Protocol)

Estos son servidores de herramientas que el CLI de Gemini (`/usr/bin/gemini`) puede utilizar de forma nativa. La configuración se encuentra en `/home/emky/.gemini/antigravity/mcp_config.json`. El custom node `GeminiCLI` lee este archivo y le informa al modelo que estas herramientas existen.

| Nombre del Servidor | Paquete / Comando | Propósito |
| :--- | :--- | :--- |
| `supabase` | `@supabase/mcp-server-supabase` | Provee una interfaz de lenguaje natural para interactuar con una base de datos Supabase (consultar, insertar, etc.). |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Expone el sistema de archivos local (`/home/emky`) para que el modelo pueda realizar operaciones de forma más segura y estructurada que con `ejecutar_comando`. |
| `command-line` | `hyper-mcp-shell` | Proporciona un shell interactivo, permitiendo al modelo ejecutar comandos de forma más conversacional. |
| `git` | `@mseep/git-mcp-server` | Permite al modelo interactuar con repositorios `git` (clonar, hacer commit, ver status, etc.). |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Una herramienta de razonamiento que permite al modelo desglosar problemas complejos en pasos lógicos. |
| `puppeteer` | `puppeteer-mcp-server` | **El servidor clave para el control del navegador.** Permite a la IA controlar una instancia de Chrome/Chromium para navegar, hacer clics, tomar capturas, etc. |

---

## 3. Protocolo de Uso

1.  El **Planner** (en el workflow de n8n) debe decidir qué capacidad de alto nivel se necesita (ej: "navegar a google.com").
2.  La instrucción `navegar_web(url='https://google.com')` es enviada.
3.  El **Tool Router** dirige la tarea al nodo `Execute Command (Puppeteer)`.
4.  Este nodo ejecuta el script bridge, el cual se comunica con el servidor MCP `puppeteer` (lanzado por `npx puppeteer-mcp-server`).
5.  El servidor MCP de Puppeteer traduce la orden y la ejecuta en la instancia de Brave que corre en el puerto 9222.
6.  El resultado es devuelto a través de la misma cadena.

Este documento servirá como referencia para asegurar que siempre utilice el conjunto correcto de herramientas para cada tarea.

**Estado:** ACTIVO.
**Lección Aprendida Asociada:** La importancia de verificar la configuración real del sistema (`mcp_config.json`) en lugar de confiar únicamente en la documentación del backlog, que puede estar desactualizada.
