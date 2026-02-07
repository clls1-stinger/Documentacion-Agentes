---
id: BACKLOG_002
title: "Google Takeout Downloader & Combiner"
status: "🔴 Not Started"
priority: "🔥 Critical"
created: "2026-02-03"
updated: "2026-02-03 T05:35Z"
assignee: "Pending"
tags:
  - feature
  - user-request
  - google-drive
  - automation
  - file-management
related_files:
  - ~/.n8n/database.sqlite (Workflow: Urf7HpECFvfQooAv)
  - /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/patch_sync_v7.py
  - /home/emky/n8n/documentacion/FORENSICS_AND_LOGS/DEBUGGING_SESSION_2026_02_03_ROUTING.md
---

# 📦 Google Takeout Downloader & Combiner

## 🎯 Objetivo (¿QUÉ quiere el usuario?)
El usuario (**Emky**) quiere que el agente de n8n **descargue automáticamente sus archivos ZIP de Google Takeout desde Google Drive** y los **combine/una en un solo directorio** en su sistema local.

## 🤔 Motivación (¿POR QUÉ lo necesita?)
### Contexto Histórico
Google Takeout exporta datos de servicios de Google (Gmail, Photos, Drive, etc.) pero los divide en múltiples archivos ZIP (usualmente de 2GB cada uno). Estos archivos se suben automáticamente a Google Drive, pero el usuario tiene que:
1. Buscar manualmente cada archivo
2. Descargarlos uno por uno (tedioso con 10+ archivos)
3. Descomprimirlos y combinar el contenido

### Problema que Resuelve
Este proceso manual puede tomar **horas** y es propenso a errores (olvidar algún archivo, descargar duplicados, etc.). Automatizarlo ahorra tiempo y garantiza que todos los archivos se procesen correctamente.

### Valor para el Usuario
- **Tiempo ahorrado**: De 2-3 horas a 5 minutos
- **Reducción de errores**: Garantiza que todos los archivos se descarguen
- **Automatización completa**: Solo decir "baja mis takeout" y el agente hace todo

## 📖 Historia del Usuario
Como **Emky**, quiero que mi agente **busque, descargue y combine mis archivos de Google Takeout** para que pueda **tener todos mis datos de Google en un solo lugar local** sin trabajo manual.

## ✅ Criterios de Aceptación
- [ ] El agente puede buscar archivos que contengan "takeout" en el nombre en Google Drive
- [ ] El agente descarga TODOS los archivos encontrados (no solo el primero)
- [ ] Los archivos se guardan en un directorio local específico (ej: `~/google_takeout_data/`)
- [ ] El agente descomprime los ZIPs automáticamente
- [ ] Los contenidos descomprimidos se combinan en una estructura unificada
- [ ] El agente reporta al usuario cuántos archivos se descargaron y el tamaño total
- [ ] Si algo falla, el agente lo reporta claramente

## 🏗️ Diseño Técnico

### Flujo de Trabajo
```
1. Usuario: "baja mis archivos de takeout"
   ↓
2. Gemini Planner: is_done=false, next_instruction="buscar_en_drive('takeout')"
   ↓
3. Tool Router: Detecta "buscar_en_drive" → Google Drive Search
   ↓
4. Drive Search: Retorna lista de archivos [file1.zip, file2.zip, ...]
   ↓
5. Gemini Planner: Ve la lista, decide descargar cada uno
   ↓
6. Loop: Para cada archivo:
   - descargar_de_drive(fileId, filename)
   - Guardar en ~/google_takeout_data/
   ↓
7. Gemini Planner: Todos descargados, ahora descomprimir
   ↓
8. ejecutar_comando("unzip *.zip -d ./combined")
   ↓
9. Gemini Planner: is_done=true, final_response="Descargados X archivos, Y GB totales"
```

### Componentes Involucrados
- **Workflow**: `Urf7HpECFvfQooAv` (nombre: "Yes")
  - Nodo: `Gemini Planner` (ya funcional)
  - Nodo: `Tool Router` (ya tiene `buscar_en_drive` y `descargar_de_drive`)
  - Nodo: `Drive Search` (ya existe)
  - Nodo: `Drive Download` (ya existe)
  - Nodo: `Execute Command` (para `unzip`)

### Dependencias
- **Herramientas ya existentes**:
  - `buscar_en_drive(query)` ► Funcional
  - `descargar_de_drive(fileId, filename)` ► Funcional
  - `ejecutar_comando(command)` ► Funcional
- **Herramientas pendientes**: Ninguna (todo ya existe)
- **Blocker actual**: El ruteo del Switch está roto (en proceso de fix con v7)

## 🔗 Archivos Relacionados
- [[FORENSICS_AND_LOGS/DEBUGGING_SESSION_2026_02_03_ROUTING.md]] - Debugging del Switch
- [[KNOWLEDGE_BASE/N8N_CEREBRO_LESSONS_LEARNED.md#Lección-27]] - Boolean Type Coercion
- [[SCRIPTS_AND_TOOLS/patch_sync_v7.py]] - Parche que debe resolver el ruteo

## 📝 Implementación

### Paso 1: Validar que el Parche v7 Funciona
- [ ] Hacer F5 en n8n para cargar el parche v7
- [ ] Enviar mensaje: "TEST_V7: busca mis archivos de takeout"
- [ ] Verificar que el flujo va a `Actor Prep` (no a `Final Response`)
- [ ] Si falla, debugging adicional del Switch

### Paso 2: Probar Búsqueda de Takeout
- [ ] Enviar mensaje: "busca archivos de takeout en mi drive"
- [ ] Verificar que el agente ejecuta `buscar_en_drive('takeout')`
- [ ] Verificar que retorna una lista de archivos
- [ ] El agente debe reportar cuántos encontró

### Paso 3: Probar Descarga de un Archivo
- [ ] El agente debe decidir descargar el primer archivo
- [ ] Ejecutar `descargar_de_drive(fileId, 'takeout-001.zip')`
- [ ] Verificar que el archivo se guarda en el disco local
- [ ] Verificar que el agente reporta el progreso

### Paso 4: Implementar Loop de Descarga Multiple
- [ ] Si hay >1 archivo, el agente debe iterar
- [ ] Descargar todos los archivos secuencialmente
- [ ] (Posible mejora futura: descargas paralelas)

### Paso 5: Descomprimir y Combinar
- [ ] El agente debe ejecutar: `unzip '*.zip' -d ./combined/`
- [ ] Verificar que los archivos se descomprimen correctamente
- [ ] Manejar posibles errores de archivos corruptos

### Paso 6: Reporte Final
- [ ] El agente debe contar archivos descargados
- [ ] Calcular el tamaño total (ej: "5 archivos, 12GB")
- [ ] Dar respuesta final al usuario

## 🧪 Testing
- [ ] **Test 1**: Búsqueda básica
  - Input: "busca takeout en drive"
  - Expected: Lista de archivos encontrados
- [ ] **Test 2**: Descarga de 1 archivo
  - Input: "descarga el primer takeout"
  - Expected: Archivo guardado en `~/google_takeout_data/`
- [ ] **Test 3**: Descarga múltiple
  - Input: "baja todos los takeout"
  - Expected: Todos los archivos descargados
- [ ] **Test 4**: Descompresión
  - Input: "descomprime los takeout"
  - Expected: Archivos unzipeados en `./combined/`
- [ ] **Test 5**: Flujo completo
  - Input: "baja mis archivos de takeout y combínalos"
  - Expected: Todo el proceso automático, reporte final

## 📊 Progreso
- [x] Parche v7 validado
- [x] Parche v36 applied (Drive V3 Fix)
- [ ] Búsqueda de archivos testeada
- [ ] Descarga de 1 archivo testeada
- [x] Loop de descarga múltiple implementado
- [ ] Descompresión testeada
- [ ] Reporte final implementado
- [ ] Flujo end-to-end validado

## 🐛 Blockers / Problemas Conocidos
- **Blocker 1**: El Switch de ruteo estaba roto.
  - **Status**: Resuelto en v30-v32.
- **Blocker 2**: Error `TypeError: Cannot read properties of undefined (reading 'execute')` en Drive Search.
  - **Status**: 🟢 Resuelto (v39)
  - **Causa**: Configuración incorrecta en previos parches. n8n V2 requiere `resource: fileFolder` para búsqueda (no `file`).
  - **Solución**: `patch_v39_fix_v2_parameters.py` configuró correctamente el esquema V2 (`fileFolder` + `search` + `query`).
- **Issue Potencial**: Archivos muy grandes pueden tardar en descargar
  - **Solución futura**: Implementar progress reporting durante descarga

## 📚 Referencias
- [Google Takeout](https://takeout.google.com/)
- [n8n Google Drive Nodes](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googledrive/)

## 💬 Notas del Desarrollo
**2026-02-03 T05:35Z - Vega**: Esta es la feature que motivó toda la sesión de debugging. El usuario pidió esto desde el principio, pero el workflow se rompía antes de poder ejecutar las herramientas. Ahora que tenemos el parche v7, esta feature debería "simplemente funcionar" sin código adicional.

**Criticidad**: 🔥 Esta es LA feature que el usuario quiere. Todo lo demás (debugging, patches, autotest) fue para hacer esto posible.

---
**Última actualización**: 2026-02-03 T05:35Z  
**Estado actual**: Bloqueada por el bug del Switch. Parche v7 aplicado, pendiente de validación manual por el usuario.
