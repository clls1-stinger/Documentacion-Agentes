# 🦾 Vega OS Kernel: Protocolo de Documentación para Agentes (v2.1)

> "No documentas para guardar información, documentas para transferir inteligencia al siguiente 'yo'."

Este protocolo define cómo los LLMs deben operar, documentar y mantener la integridad del sistema Vega LifeOS. Adherirse a estos pilares garantiza la **Resiliencia de Contexto** y la **Eficiencia de Tokens**.

---

## 🧭 Pilares Operativos

### 1. El Pilar de la Sanitización (Higiene Digital)
Antes de actuar, limpia. Antes de terminar, purifica.
- **Identifica el ruido**: Borra archivos `.tmp`, logs redundantes o snapshots de depuración que ya no sirven.
- **Protege el núcleo**: **ESTÁ PROHIBIDO** crear archivos en el path raíz de n8n (`/home/emky/n8n/`). Solo se permiten directorios de sistema.
- **Propósito**: Un entorno libre de basura minimiza las alucinaciones y maximiza la precisión de los tokens.

### 2. Jerarquía y Divulgación Progresiva
No leas todo, no escribas todo. Navega con precisión.
- **Punto de Entrada**: Todo agente debe empezar por el `[INDEX.md](./documentacion/INDEX.md)`.
- **Navegación**: Usa el `[MANIFEST.md](./documentacion/MANIFEST.md)` antes de búsquedas globales con `find`.

### 3. Persistencia y Manipulación de Base de Datos (SQLite)
Vega opera sobre una arquitectura SQLite. La manipulación directa es el **"God Mode"** y debe usarse con precaución extrema.
- **Path de la DB**: `/home/emky/n8n/database.sqlite` (o `~/.n8n/database.sqlite` según la instalación).
- **Herramienta Maestra**: Usa el `[n8n_master_controller.py](./documentacion/2_RESOURCES/SCRIPTS_AND_TOOLS/n8n_master_controller.py)` para `dump`, `push` y `search` en lugar de SQL crudo.
- **Protocolo de Parcheo**: Antes de un `push` a la DB, el controlador genera un backup. Si algo falla, usa el `[N8N_DISASTER_RECOVERY_AND_REPAIR.md](./documentacion/1_PROTOCOLS/N8N_DISASTER_RECOVERY_AND_REPAIR.md)`.
- **Forense**: Para extraer datos de ejecuciones pasadas, consulta la tabla `execution_entity` (Ver `[SQLITE_QUERIES.md](./documentacion/2_RESOURCES/CHEAT_SHEETS/SQLITE_QUERIES.md)`).

### 4. Organización Estricta de Archivos
| Destino | Path (Absoluto) | Tipo de Contenido |
| :--- | :--- | :--- |
| **Workflows** | `/home/emky/n8n/workflows_antigravity/` | Exports `.json` de n8n. |
| **Forense/Logs** | `/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/` | Scripts de depuración, volcados de DB. |
| **Herramientas** | `/home/emky/n8n/documentacion/2_RESOURCES/SCRIPTS_AND_TOOLS/` | Scripts permanentes y utilidades. |
| **Conocimiento** | `/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/KNOWLEDGE_BASE/` | `.md` con lecciones aprendidas. |

### 5. Memoria, Escalación y Respaldo
- **Forensics**: Documenta incidentes críticos en `FORENSICS_AND_LOGS` (`INCIDENT_YYYY-MM-DD.md`).
- **Knowledge Base**: Documenta "Aha! moments" y soluciones complejas.
- **Escalación**: Si falta una herramienta, identifica el gestor (`pacman`) y pregunta al usuario. No instales nada sin permiso.

---

## ⚠️ Regla de Oro: Nombramiento de Archivos
- **Scripts:** `[accion]_[contexto]_[version].py` (ej. `patch_aggregator_v1.py`).
- **Dumps:** `raw_[entidad]_[id].json` (ej. `raw_exec_486.json`).
- **Documentos:** `[TIPO]_[DESCRIPCION].md` (ej. `LEARNINGS_SQL_PATCHING.md`).

---
*Vega OS Kernel - Protocolo de Integridad de Sistema (v2.1 - Persistence Update).*
