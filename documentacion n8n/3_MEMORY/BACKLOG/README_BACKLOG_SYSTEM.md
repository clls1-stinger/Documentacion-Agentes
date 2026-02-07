# 📝 CÓMO DOCUMENTAR FEATURES Y TAREAS (META-GUÍA)

Esta guía explica cómo documentar trabajo pendiente, completado o en progreso para que cualquier LLM (o humano) pueda entender el contexto completo y continuar donde se quedó el anterior.

## 🎯 Filosofía del Sistema
Cada feature/tarea debe ser **auto-contenida**: un LLM debe poder leer EL ÚNICO archivo de la feature y tener TODO el contexto necesario para implementarla sin buscar en mil lugares.

## 📂 Estructura de Archivos
Todas las features se documentan en: `/home/emky/n8n/documentacion/BACKLOG/`

Formato del nombre de archivo:
```
BACKLOG_<ID>_<NombreCorto>.md
```

Ejemplo:
```
BACKLOG_001_Puppeteer_MCP_Integration.md
BACKLOG_002_Google_Takeout_Downloader.md
```

## 📋 Template de Feature

```markdown
---
id: BACKLOG_XXX
title: "<Título Descriptivo>"
status: "🔴 Not Started | 🟡 In Progress | 🟢 Done"
priority: "🔥 Critical | ⚡ High | 📌 Medium | 💤 Low"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
assignee: "Vega | Emky | <Otro LLM>"
tags: 
  - feature
  - bug
  - enhancement
related_files:
  - /path/to/script.py
  - /path/to/workflow.json
---

# <Título de la Feature>

## 🎯 Objetivo (¿QUÉ quiere el usuario?)
Descripción clara y concisa de lo que el usuario quiere lograr.

## 🤔 Motivación (¿POR QUÉ lo necesita?)
Contexto sobre por qué esto es importante, qué problema resuelve.

## 📖 Historia del Usuario
Como [tipo de usuario], quiero [acción] para [beneficio].

## ✅ Criterios de Aceptación
- [ ] El sistema debe poder...
- [ ] Cuando el usuario hace X, debe pasar Y...
- [ ] Los logs deben mostrar...

## 🏗️ Diseño Técnico
### Arquitectura
Diagrama o descripción de cómo se implementará.

### Componentes Involucrados
- **Workflow**: n8n workflow ID o nombre
- **Scripts**: Lista de scripts Python/JS
- **Nodos**: Qué nodos de n8n se modificarán

### Dependencias
- Librerías externas
- APIs
- Otros features

## 🔗 Archivos Relacionados
(Usa la sintaxis de Obsidian para que sea clickeable en editores compatibles)
- [[SCRIPTS_AND_TOOLS/ejemplo.py]]
- [[WORKFLOWS/workflow.json]]
- [[KNOWLEDGE_BASE/N8N_CEREBRO_LESSONS_LEARNED.md#Lección-XX]]

## 📝 Implementación
### Paso 1: Descripción
- [ ] Acción específica a realizar
- [ ] Comando o código a ejecutar
- [ ] Archivo a modificar: `[[ruta/al/archivo]]`

### Paso 2: ...
...

## 🧪 Testing
- [ ] Test case 1: Descripción
- [ ] Test case 2: ...

## 📊 Progreso
- [x] Investigación completada
- [ ] Prototipo funcional
- [ ] Tests pasando
- [ ] Documentación actualizada
- [ ] Integrado en producción

## 🐛 Blockers / Problemas Conocidos
- Issue 1: Descripción del problema
  - **Workaround**: Solución temporal si existe

## 📚 Referencias
- Links a documentación externa
- Issues similares resueltos
- Conversaciones relevantes

## 💬 Notas del Desarrollo
[Timestamp] - Usuario/LLM: Nota libre sobre decisiones tomadas.

---
**Última actualización**: [Timestamp]
**Estado actual**: Descripción breve del estado
```

## 🏷️ Sistema de Tags
Usa tags para que otros LLMs puedan buscar features relacionadas:
- `#feature`: Nueva funcionalidad
- `#bug`: Corrección de error
- `#enhancement`: Mejora de algo existente
- `#refactor`: Limpieza de código
- `#docs`: Documentación
- `#n8n`: Relacionado con workflows
- `#python`: Usa scripts Python
- `#mcp`: Usa Model Context Protocol
- `#critical`: Prioridad máxima
- `#blocked`: No se puede avanzar por alguna razón

## 🔍 Cómo Buscar Features
1. **Por Estado**: Busca `status: "🟡 In Progress"` para ver qué está pendiente.
2. **Por Tag**: Busca `#mcp` para ver todas las features relacionadas con MCP.
3. **Por Archivo**: Busca el path del archivo para ver qué features lo usan.

## 🤝 Handoff entre LLMs
Cuando termines una sesión:
1. Actualiza el campo `status` del feature.
2. Marca las checkboxes completadas.
3. Añade una nota en "Notas del Desarrollo" con timestamp y tu nombre.
4. Si hay blockers, descríbelos claramente.

---
**Meta**: Este archivo es parte del sistema de documentación de Vega.
**Path**: `/home/emky/n8n/documentacion/BACKLOG/README_BACKLOG_SYSTEM.md`
