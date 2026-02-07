# Protocolo de Recuperación de Desastres y Reparación Estructural de Workflows

Este documento detalla los procedimientos avanzados para recuperar workflows de n8n corruptos, vacíos o con errores estructurales ("nodos fantasma"), utilizando manipulación directa de la base de datos SQLite.

**Fecha de creación:** 2026-02-02
**Contexto:** Recuperación del workflow "Yes" (Herramienta Definitiva) tras una corrupción de datos.

---

## 1. Síntomas de Corrupción
*   **Workflow Fantasma:** Nodos visibles en la UI pero desconectados o duplicados (dos flujos paralelos donde debería haber uno).
*   **Estado Vacío:** La base de datos reporta 0 nodos, pero la UI muestra un cache antiguo (o viceversa).
*   **Chat Output Roto:** El chat devuelve `[No response]` aunque la ejecución parezca exitosa.

## 2. Herramientas de Diagnóstico (Scripts Python)
Ubicación: `/home/emky/n8n/`

| Script | Función |
| :--- | :--- |
| `list_workflows.py` | Lista workflows recientes y su estado en DB. Útil para verificar si realmente existen. |
| `dump_execution.py` | Extrae metadatos crudos de una ejecución específica (`execution_data`). |
| `restore_and_fix_workflow.py` | Restaura un workflow completo desde un snapshot de ejecución pasada. |
| `clean_workflow.py` | Algoritmo BFS para eliminar nodos huérfanos/desconectados. |

---

## 3. Procedimiento de Recuperación (Time Travel)

Si un workflow se borra o corrompe, podemos "viajar en el tiempo" usando el historial de ejecuciones (`execution_entity` / `execution_data`).

### Paso 3.1: Encontrar una ejecución sana
Ejecutar query SQL para ver las últimas ejecuciones exitosas:
```sql
sqlite3 ~/.n8n/database.sqlite "SELECT id, startedAt FROM execution_entity WHERE workflowId = 'TU_ID' AND finished = 1 ORDER BY id DESC LIMIT 5;"
```

### Paso 3.2: Extraer Snapshot (Workflow Data)
La tabla `execution_data` contiene una copia COMPLETA del workflow (`workflowData`) tal como existía en el momento de esa ejecución.
```python
cursor.execute("SELECT workflowData FROM execution_data WHERE executionId = ?", (EXECUTION_ID,))
# workflowData contiene 'nodes' y 'connections' originales
```

### Paso 3.3: Restauración Quirúrgica
No basta con restaurar el JSON. Es vital limpiar inconsistencias.
1.  **Cargar Snapshot:** Parsear el JSON recuperado.
2.  **Sobrescribir Workflow Actual:** Hacer un `UPDATE` en `workflow_entity` usando los nodos/conexiones viejos.

---

## 4. Procedimiento de Limpieza de Grafo (Fix "Nodos Fantasma")

Si la UI muestra nodos desconectados o duplicados que no se pueden borrar:

### Algoritmo BFS (Breadth-First Search)
El script `clean_workflow.py` implementa esta lógica:
1.  **Identificar Raíz:** Buscar el nodo Trigger (ej. `ChatTrigger`).
2.  **Recorrer Conexiones:** Seguir todas las líneas de conexión desde el Trigger hacia abajo.
3.  **Marcar Nodos Válidos:** Guardar en un `set` todos los IDs alcanzables.
4.  **Purgar:** Eliminar cualquier nodo que NO esté en el `set` de válidos.

Esto elimina automáticamente cualquier "basura" flotante en la DB que corrompa la UI.

---

## 5. Fix Específico: n8n Chat `[No response]`
El nodo **Output to Chat** (o el Chat interface nativo) es estricto con la salida.

**Error Común:**
El nodo final devuelve `{ "response": "Hola mundo" }`.
La UI de Chat espera `{ "text": "Hola mundo" }`.

**Solución (Patch Automático):**
Al restaurar o reparar, inyectamos una regla en el nodo "Output to Chat":
```javascript
// En el script de restauración:
assignments.append({
    "id": "auto_text_fix",
    "name": "text", 
    "value": "={{ $json.response }}", // Mapeo forzado
    "type": "string"
})
```

---

## 6. Comandos Vitales
Siempre reiniciar n8n después de tocar la DB manualmente para limpiar cachés:
```bash
pm2 restart n8n-master
```

Nunca editar la DB mientras hay escrituras masivas concurrentes (riesgo bajo en SQLite con WAL, pero existente).
