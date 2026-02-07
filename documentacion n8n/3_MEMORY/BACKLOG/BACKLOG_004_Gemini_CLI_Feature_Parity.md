---
id: BACKLOG_004
title: "Custom Gemini CLI Node Feature Parity"
status: "🟡 In Progress"
priority: "📌 Medium"
created: "2026-02-03"
updated: "2026-02-03 T05:45Z"
assignee: "Pending"
tags:
  - enhancement
  - gemini-cli
  - custom-node
  - n8n
related_files:
  - /home/emky/n8n/custom-nodes/n8n-nodes-gemini-cli-local/nodes/GeminiCLI/GeminiCLI.node.ts
  - /home/emky/n8n/custom-nodes/n8n-nodes-gemini-cli-local/package.json
---

# ⚙️ Custom Gemini CLI Node Feature Parity

## 🎯 Objetivo (¿QUÉ quiere el usuario?)
Asegurar que el **custom node de Gemini CLI** tenga paridad de features con la CLI oficial de Google, específicamente:
- Response Schema (implementado recientemente)
- Temperature control
- Max tokens
- Top-K / Top-P sampling
- Timeout settings
- Checkpointing
- Sandbox mode

## 🤔 Motivación (¿POR QUÉ es importante?)
### Contexto
El custom node fue desarrollado para tener control total sobre Gemini desde n8n. Sin embargo, durante el desarrollo ha habido varias iteraciones para agregar features que la CLI oficial ya tiene.

### Beneficio
Con paridad completa, el usuario tiene:
- **Control total** sobre el comportamiento del modelo
- **Optimización de costos** (max tokens, timeout)
- **Mejor calidad** (temperature, sampling)
- **Debugging** (checkpointing para ver sesiones)

## 📖 Historia del Usuario
Como **Emky**, quiero que mi **custom node de Gemini tenga todas las opciones de la CLI oficial** para poder **ajustar finamente el comportamiento del modelo** sin tener que modificar código.

## ✅ Criterios de Aceptación
- [ ] Todas las features de la CLI oficial están disponibles en el node
- [ ] Cada feature tiene una descripción clara en la UI de n8n
- [ ] Las features tienen valores por defecto sensatos
- [ ] La documentación interna del node está actualizada
- [ ] El icono del node se ve correctamente (Galaxy Brain 🧠)

## 🏗️ Diseño Técnico

### Features Implementadas ✅
- [x] Response Schema (JSON mode)
- [x] Temperature
- [x] Max Tokens
- [x] Top-K / Top-P
- [x] Timeout
- [x] Checkpointing
- [x] Sandbox mode
- [x] Galaxy Brain icon

### Features Pendientes ❓
- [ ] Context Caching (TTL, cache ID)
- [ ] Deep Thinking (thinking budget)
- [ ] Safety Settings customization
- [ ] Tool filtering (exclude specific tools)

## 🔗 Archivos Relacionados
- [[custom-nodes/n8n-nodes-gemini-cli-local/nodes/GeminiCLI/GeminiCLI.node.ts]]

## 📝 Implementación

### Paso 1: Verificar Features Actuales
- [ ] Listar todas las opciones del node
- [ ] Comparar con `gemini chat --help`
- [ ] Identificar gaps

### Paso 2: Implementar Context Caching
- [ ] Añadir parámetro `contextCacheTTL`
- [ ] Añadir parámetro `contextCacheID`
- [ ] Pasar flags a la CLI

### Paso 3: Implementar Deep Thinking
- [ ] Añadir parámetro `thinkingBudget`
- [ ] Documentar cuándo usarlo (tareas complejas)

### Paso 4: Safety Settings
- [ ] Añadir dropdown para cada categoría
- [ ] Valores: BLOCK_NONE, BLOCK_LOW, BLOCK_MEDIUM, BLOCK_HIGH

### Paso 5: Tool Filtering
- [ ] Añadir parámetro `excludeTools` (array)
- [ ] Permitir excluir tools específicos

## 📊 Progreso
- [x] Features básicas implementadas
- [ ] Context caching
- [ ] Deep thinking
- [ ] Safety settings
- [ ] Tool filtering
- [ ] Documentación completa

## 💬 Notas del Desarrollo
**2026-02-02 T22:00Z**: Se implementó Response Schema y Galaxy Brain icon. El node funciona bien para el caso de uso actual (agente de n8n).

**Prioridad**: Media porque el node YA funciona para el caso de uso principal. Estas features adicionales son optimizaciones futuras.

---
**Última actualización**: 2026-02-03 T05:45Z  
**Estado actual**: Features core funcionando. Context caching y deep thinking son las siguiente prioridades.
