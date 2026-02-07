# 🔍 Sesión de Debugging - 2026-02-02

## Objetivo
Resolver errores 404 y TypeErrors en el workflow "Herramienta Definitiva ahora si que si" del agente Gemini.

---

## 🐛 Errores Detectados

### Error #1: Phantom Routing (Ejecución 340)
**Síntoma**: El nodo `Tool Router` (Switch) enrutó `accion: "ejecutar_comando"` hacia la salida 1 (Drive Download) en lugar de la salida 3 (Execute Command).

**Evidencia**:
```json
{
  "input": {"accion": "ejecutar_comando", "datos": {"command": "mkdir -p antigravity_brain"}},
  "runData": {"previousNodeOutput": 1}  // ❌ Debería ser 3
}
```

**Causa**: Posible corrupción en la definición del nodo Switch o condiciones de carrera en la evaluación de expresiones JEXL.

**Solución Aplicada**:
- Reconstrucción completa del nodo `Tool Router` mediante hot patch
- Redefinición explícita de las 4 reglas con estructura canónica

---

### Error #2: TypeError en Drive Search (Ejecución 342)
**Síntoma**: `TypeError: Cannot read properties of undefined (reading 'execute')`

**Stack Trace**:
```
at Object.router (/home/emky/n8n/node_modules/n8n-nodes-base/nodes/Google/Drive/v2/actions/router.ts:33:66)
```

**Causa**: Configuración incorrecta del nodo `Drive Search`:
```json
{
  "resource": "fileFolder",  // ❌ Incorrecto
  "operation": "list"
}
```

La combinación `fileFolder + list` es para listar carpetas, NO para buscar archivos. El router interno del nodo Google Drive v2 no tiene handler para esta combinación, devolviendo `undefined`.

**Solución Aplicada**:
```json
{
  "resource": "file",  // ✅ Correcto
  "operation": "list",
  "filter": {"q": "={{ $json.datos.query }}"}
}
```

---

### Error #3: Phantom Routing Persistente (Ejecución 343)
**Síntoma**: A pesar de las correcciones, el Tool Router sigue enrutando `ejecutar_comando` hacia Drive Search (salida 0).

**Evidencia**:
```json
{
  "accion": "ejecutar_comando",
  "datos": {"command": "..."}
}
// Pero se ejecutó Drive Search en lugar de Execute Command
```

**Análisis**:
- ✅ Reglas del Switch están correctas en la DB
- ✅ Conexiones están correctas (salida 3 → Execute Command)
- ❌ El runtime sigue enrutando incorrectamente

**Hipótesis**:
1. **Cache de n8n**: El workflow en memoria no se actualizó después del hot patch
2. **Modo del Switch**: Puede estar en modo "expression" en lugar de "rules"
3. **Orden de evaluación**: Las reglas se evalúan en orden y la primera que coincide gana

**Próximos Pasos**:
1. Verificar el modo del Switch (`mode` parameter)
2. Forzar recarga completa del workflow (no solo restart de PM2)
3. Considerar recrear el nodo Switch desde la UI en lugar de hot patch

---

## 📝 Lecciones Aprendidas

### 1. Datos Estructurados en Historial
- **Problema**: El Gemini Planner no recibía IDs de archivos explícitos
- **Solución**: Modificar `Aggregator` y `Update State` para incluir `result_data` con estructura JSON

### 2. Saneamiento de Expresiones
- **Problema**: Espacios extra en expresiones (`{{ $json.datos.fileId  }}`)
- **Solución**: `.trim()` exhaustivo en el nodo `Clean Actor`

### 3. Configuración de Resource en Google Drive
- **Regla**: Siempre verificar que `resource + operation` sea válida
- **Ejemplo**: `file + list` para buscar archivos, `fileFolder + list` para listar carpetas

### 4. Hot Patching vs UI Editing
- **Aprendizaje**: Los hot patches pueden no reflejarse inmediatamente en el runtime
- **Recomendación**: Después de un hot patch, verificar en la UI que los cambios se aplicaron

### 5. Debugging Forense con SQLite
- **Herramientas**:
  - `pm2 logs n8n-master --lines 1000 --nostream`
  - `sqlite3 /home/emky/.n8n/database.sqlite`
  - `jq` para navegar execution_data

---

## 🔧 Herramientas Desarrolladas

### hot_patch_workflow.py
Script Python para modificar workflows directamente en SQLite:
- `patch_aggregator_node()`: Agrega `result_data` al historial
- `patch_update_state_node()`: Incluye datos estructurados en el estado
- `patch_planner_prep_node()`: Pasa `result_data` al Planner
- `patch_tool_router_node()`: Reconstruye reglas del Switch
- `patch_drive_search_node()`: Corrige `resource: "file"`

**Uso**:
```bash
python3 /home/emky/n8n/hot_patch_workflow.py
pm2 restart n8n-master
```

---

## 🎯 Estado Actual

**Correcciones Aplicadas**:
- ✅ Datos estructurados en historial
- ✅ Tool Router reconstruido
- ✅ Drive Search corregido (`resource: file`)
- ✅ Documentación actualizada

**Problemas Pendientes**:
- ❌ Phantom routing persiste en ejecución 343
- ⚠️ Necesita verificación manual en UI

**Próxima Acción**:
Abrir la UI de n8n, verificar visualmente el nodo `Tool Router`, y si es necesario, recrearlo manualmente.

---

**FIRMADO**: Vega LifeOS Kernel  
**FECHA**: 2026-02-02  
**DURACIÓN**: ~2 horas de debugging forense
