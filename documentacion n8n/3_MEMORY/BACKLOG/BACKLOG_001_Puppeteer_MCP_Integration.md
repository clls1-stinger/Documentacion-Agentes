---
id: BACKLOG_001
title: "Integración de Puppeteer MCP en n8n Workflow"
status: "🟡 In Progress"
priority: "⚡ High"
created: "2026-02-03"
updated: "2026-02-03 T05:20Z"
assignee: "Vega"
tags:
  - feature
  - enhancement
  - n8n
  - mcp
  - puppeteer
  - automation
related_files:
  - /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py
  - /home/emky/n8n/documentacion/PROXYS_AND_PROTOCOLS/PUPPETEER_MCP_INTEGRATION.md
  - ~/.n8n/database.sqlite (Workflow: Urf7HpECFvfQooAv)
---

# 🌐 Integración de Puppeteer MCP en n8n Workflow

## 🎯 Objetivo (¿QUÉ quiere el usuario?)
El usuario (**Emky**) quiere que su agente de n8n tenga la capacidad de controlar un navegador web usando Puppeteer, exactamente como lo hace Vega para el sistema de autotest. Esto permitirá al agente navegar por la web, interactuar con elementos (clicks, inputs), tomar screenshots, extraer datos dinámicos, y automatizar tareas de UI.

## 🤔 Motivación (¿POR QUÉ lo necesita?)
### Contexto Histórico
Durante la sesión de debugging del workflow "Yes", Vega implementó un sistema de **autotest** usando el servidor MCP de Puppeteer para validar los cambios del workflow de forma autónoma. Emky vio esto en acción y se dio cuenta del poder que tendría si su propio agente de n8n pudiera hacer lo mismo.

### Casos de Uso Específicos
1. **Web Scraping Dinámico**: Obtener datos de sitios que usan JavaScript pesado (ej: SPAs, dashboards).
2. **Automatización de Formularios**: Completar formularios web, hacer login automático.
3. **Testing Visual**: Capturar screenshots de aplicaciones para validación.
4. **Interacción con APIs visuales**: Usar servicios web que no tienen API pública.

### Problema que Resuelve
Sin Puppeteer, el agente solo puede:
- Hacer requests HTTP básicos (estáticos)
- Leer archivos locales
- Ejecutar comandos de terminal

Con Puppeteer, el agente se convierte en un "humano virtual" que puede interactuar con CUALQUIER interfaz web.

## 📖 Historia del Usuario
Como **Emky**, quiero que mi agente de n8n pueda **navegar por sitios web y extraer información dinámica** para que pueda **automatizar tareas que requieren interacción visual con navegadores** sin tener que hacerlo manualmente.

## ✅ Criterios de Aceptación
- [ ] El agente puede recibir un comando como `navegar_web(url="https://google.com")` en el Planner.
- [ ] El Tool Router reconoce `navegar_web` y lo enruta correctamente.
- [ ] Se ejecuta un script que interactúa con el servidor MCP de Puppeteer.
- [ ] El agente recibe de vuelta información útil (screenshot path, texto extraído, confirmación de navegación).
- [ ] Los logs muestran claramente qué acciones de navegador se están ejecutando.
- [ ] El sistema es seguro (no expone credenciales, usa sandbox si es necesario).

## 🏗️ Diseño Técnico

### Arquitectura
```
┌─────────────────┐
│ Gemini Planner  │
│  (Decide usar)  │
│  navegar_web()  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Tool Router    │
│  (Detecta cmd)  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Execute Command │
│  python3 bridge │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ MCP Bridge      │
│  (Python)       │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Puppeteer MCP   │
│  Server (stdio) │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Chrome/Chromium│
│  (Headless)     │
└─────────────────┘
```

### Componentes Involucrados
- **Workflow**: `Urf7HpECFvfQooAv` (nombre: "Yes")
  - Nodo: `Planner Prep` (actualizar prompt con nueva herramienta)
  - Nodo: `Tool Router` (agregar caso para `navegar_web`)
  - Nodo: `Execute Command` (reutilizar el existente)
- **Scripts**:
  - `[[SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py]]` (ya creado, pendiente de configuración)
- **Servidor MCP**:
  - `@anthropic/mcp-server-puppeteer` (pendiente de instalación)

### Dependencias
- **Externas**:
  - Node.js (ya instalado)
  - Chrome/Chromium (verificar si está instalado)
  - Servidor MCP de Puppeteer (instalar con npm)
- **Internas**:
  - Cliente MCP en Python (investigar si existe o usar requests si el servidor expone HTTP)

## 🔗 Archivos Relacionados
- [[SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py]] - Script bridge (creado)
- [[PROXYS_AND_PROTOCOLS/PUPPETEER_MCP_INTEGRATION.md]] - Documentación técnica
- [[PROXYS_AND_PROTOCOLS/VEGA_SELF_TEST_PROTOCOL.md]] - Ejemplo de uso de Puppeteer
- [[FORENSICS_AND_LOGS/DEBUGGING_SESSION_2026_02_03_ROUTING.md]] - Contexto de cómo llegamos aquí

## 📝 Implementación

### Paso 1: Verificar Dependencias del Sistema
- [ ] Verificar que Chrome/Chromium esté instalado
  ```bash
  which google-chrome || which chromium
  ```
- [ ] Verificar Node.js y npm
  ```bash
  node --version && npm --version
  ```

### Paso 2: Instalar Servidor MCP de Puppeteer
- [ ] Instalar el paquete globalmente
  ```bash
  npm install -g @anthropic/mcp-server-puppeteer
  ```
- [ ] Verificar que el servidor se puede iniciar
  ```bash
  mcp-server-puppeteer --help
  ```

### Paso 3: Configurar el Bridge
- [ ] Modificar `[[SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py]]` para conectarse al servidor MCP
  - Investigar si el servidor usa stdio o HTTP
  - Implementar la función `call_mcp()` con la conexión real
- [ ] Probar el bridge manualmente
  ```bash
  python3 puppeteer_mcp_bridge.py navigate "https://google.com"
  ```

### Paso 4: Actualizar Workflow de n8n
- [ ] Modificar `Planner Prep`:
  - Añadir en el prompt: `6. navegar_web(url): Abre URL en navegador y retorna screenshot.`
  - Archivo: Usar script de patching
- [ ] Modificar `Tool Router`:
  - Añadir caso: `if (instruction.includes('navegar_web')) => Execute Command`
  - Archivo: Crear `[[SCRIPTS_AND_TOOLS/patch_add_puppeteer_tool.py]]`
- [ ] Probar con F5 en n8n

### Paso 5: Testing de Integración
- [ ] Enviar mensaje al agente: "Abre google.com y dime qué ves"
- [ ] Verificar que el Tool Router detecta `navegar_web`
- [ ] Verificar que el bridge se ejecuta sin errores
- [ ] Verificar que el agente recibe la respuesta del navegador

### Paso 6: Documentación
- [ ] Actualizar `[[KNOWLEDGE_BASE/N8N_MAJESTIC_AGENT_DOCUMENTATION.md]]` con la nueva herramienta
- [ ] Añadir ejemplo de uso en `[[PROXYS_AND_PROTOCOLS/PUPPETEER_MCP_INTEGRATION.md]]`

## 🧪 Testing
- [ ] **Test 1**: Navegación básica
  - Input: "navega a https://example.com"
  - Expected: Screenshot guardado y path retornado
- [ ] **Test 2**: Extracción de texto
  - Input: "ve a google.com y dime el título de la página"
  - Expected: Agente responde "Google"
- [ ] **Test 3**: Click en elemento
  - Input: "abre github.com y haz click en 'Sign in'"
  - Expected: Navegación al formulario de login

## 📊 Progreso
- [x] Investigación de MCP completada
- [x] Documentación técnica creada
- [x] Bridge básico creado (sin conexión real)
- [ ] Servidor MCP instalado
- [ ] Bridge configurado y funcional
- [ ] Workflow actualizado
- [ ] Tests pasando
- [ ] Integración completa en producción

## 🐛 Blockers / Problemas Conocidos
- **Blocker 1**: No sabemos si el servidor MCP de Puppeeter usa stdio o HTTP
  - **Workaround**: Investigar en la documentación oficial o probar ambos
- **Blocker 2**: Posible falta de Chrome/Chromium en el sistema
  - **Workaround**: Instalar con `sudo pacman -S chromium` (Arch Linux)

## 📚 Referencias
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Anthropic MCP Servers](https://www.anthropic.com/news/model-context-protocol)
- [Puppeteer Documentation](https://pptr.dev/)

## 💬 Notas del Desarrollo
**2026-02-03 T05:20Z - Vega**: Feature documentada completamente. Bridge creado pero pendiente de configuración. Usuario (Emky) muy entusiasmado con esta capacidad. Prioridad alta debido al impacto en automatización.

**2026-02-03 T05:30Z - Vega**: Pendiente: Instalar servidor MCP y probar conexión stdio vs HTTP.

---
**Última actualización**: 2026-02-03 T05:30Z  
**Estado actual**: Bridge creado, pendiente de instalación del servidor MCP y configuración de la conexión real.
