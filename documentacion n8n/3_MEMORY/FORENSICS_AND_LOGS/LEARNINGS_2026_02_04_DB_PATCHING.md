# Protocolo de Emergencia: Parcheo Directo de DB n8n

**Fecha:** 2026-02-04
**Incidente:** Fallo en Aggregator y Nombres de Archivos
**Contexto:** El CLI de n8n (`n8n import`) no funcionó debido a incompatibilidad de versión de Node.js en el entorno (v25 vs v20).

## 1. Técnica: Direct SQLite Patching
Cuando el CLI no está disponible, la "Fuente de la Verdad" final es la base de datos SQLite. Podemos manipular el JSON del workflow directamente en la tabla `workflow_entity`.

**Ubicación DB:** `/home/emky/.n8n/database.sqlite`
**Tabla:** `workflow_entity`
**Columnas Clave:** `nodes` (JSON), `connections` (JSON), `versionId` (Incrementar para forzar actualización).

### Script de Parcheo (Plantilla)
```python
import sqlite3
import json

DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_ID = "TARGET_WORKFLOW_ID"

def patch_node(node_name, param_name, new_value):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    row = cursor.fetchone()
    nodes = json.loads(row['nodes'])
    
    for node in nodes:
        if node['name'] == node_name:
            node['parameters'][param_name] = new_value
            
    # Guardar
    cursor.execute("UPDATE workflow_entity SET nodes = ? WHERE id = ?", 
                   (json.dumps(nodes), WORKFLOW_ID))
    conn.commit()
    conn.close()
```

## 2. Patrones de Código Defensivo (Aggregator)
El nodo Aggregator es propenso a fallar si el nodo anterior (`Clean Actor`) no devuelve datos válidos o si el ciclo de ejecución se corrompe.

**Código Robusto:**
```javascript
let prev = {};
try {
    // Intentar obtener el último item del nodo anterior
    const cleanActor = $('Clean Actor').last();
    // Validar existencia ANTES de acceder a propiedades
    prev = (cleanActor && cleanActor.json) ? cleanActor.json : {};
} catch(e) {
    // Fallback seguro en caso de error catastrófico
    prev = { user_goal: "RECOVERY_MODE", history: [] };
}
```

## 3. Preservación de Nombres de Archivo
Para que n8n guarde un archivo con su nombre original (detectado por nodos previos como Google Drive), no se debe usar una ruta estática.

**Configuración Correcta (Save to Disk):**
- **File Selector:** `/path/to/folder/{{ $binary.data.fileName }}`
- **Nota:** `$binary.data` es el objeto binario estándar por defecto. Si el binario tiene otro nombre (ej. `imagen`), usar `{{ $binary.imagen.fileName }}`.

## 4. Gestión de Servicio (PM2)
Cualquier cambio directo en la DB requiere reiniciar el proceso para que n8n recargue la configuración en memoria.

```bash
pm2 restart n8n-master
```
