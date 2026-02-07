# 🕰️ PROTOCOLO DE TRAZADO TEMPORAL (TIME TRAVEL)

> "No solo guardamos código, guardamos *por qué* lo escribimos."

Este protocolo define cómo los agentes de IA (Antigravity y sucesores) deben utilizar el sistema de persistencia temporal para mantener el contexto a largo plazo.

---

## 1. Arquitectura del Sistema

El sistema se compone de dos capas de memoria sincronizadas:

### A. Memoria de Ejecución (Context Database)
Archivo: `/home/emky/n8n/context_db/context.sqlite`
Motor: SQLite

Almacena el "Pensamiento" y metadatos de cada acción importante.

**Tabla: `execution_log`**
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | UUID | Identificador único del evento. |
| `timestamp` | ISO8601 | Cuándo ocurrió. |
| `agent_id` | String | Nombre/ID del agente (ej. "Antigravity"). |
| `task_name` | String | Nombre de la tarea (ej. "Fixing DB"). |
| `thought_process` | Text | Explicación del razonamiento ("The Why"). |
| `tools_used` | JSON | Lista de herramientas ejecutadas. |
| **`git_commit_hash`** | String | Enlace al estado exacto del código. |

### B. Memoria de Código (Git Snapshots)
Repositorio: `/home/emky/n8n/.git`

Cada "Snapshot" genera un commit automático en Git que captura el estado exacto de todos los archivos en `/home/emky/n8n`.

---

## 2. Cómo Usar el Sistema

### Generar un Snapshot (Guardar Contexto)
Cada vez que completes una tarea significativa o llegues a un hito estable:

```bash
python3 /home/emky/n8n/context_db/snapshot.py \
  --agent "TuNombre" \
  --task "Nombre de la Tarea" \
  --thought "Explico qué hice y por qué lo hice..." \
  --tools '["tool_1", "tool_2"]'
```

*Esto creará un commit en Git y una entrada en SQLite vinculados.*

### Consultar el Pasado (Recuperar Contexto)
Cuando inicies una nueva sesión y necesites entender qué pasó antes:

```bash
python3 /home/emky/n8n/context_db/query_context.py --limit 5
```

Filtros disponibles: `--agent`, `--task`.

---

## 3. Mantenimiento
- **Backup**: El archivo `context.sqlite` es crítico. Debe respaldarse junto con el volumen de n8n.
- **Git**: El repositorio en `/home/emky/n8n` es para control de versiones automático. No realizar commits manuales desordenados si es posible; usar `snapshot.py` para mantener la trazabilidad.

---
**ESTADO**: ACTIVO
**CREADO**: 2026-02-04
