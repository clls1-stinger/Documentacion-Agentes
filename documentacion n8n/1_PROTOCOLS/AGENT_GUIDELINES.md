# Protocolo de Organización para Agentes IA (Vega)

Para mantener la cordura y el orden en este entorno LifeOS, todo agente que opere aquí DEBE seguir estas reglas estrictas de ubicación de archivos. **Queda terminantemente prohibido ensuciar el path raíz de n8n.**

## 📂 Directorios de Destino

### 1. Workflows (Dumps de Producción)
Cualquier export de workflow para parcheo o backup debe ir aquí:
- **Path:** `/home/emky/Codigo/workflows/workflows_vega/`
- **Uso:** Archivos `.json` de workflows activos o backups de versiones específicas.

### 2. Forenses y Logs de Sesión
Scripts temporales, volcados de datos de ejecución y archivos de depuración:
- **Path:** `/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/`
- **Uso:** Scripts `.py`, `.js` de parcheo puntual, logs temporales, volcados SQLite.

### 3. Herramientas y Recursos Permanentes
Herramientas que serán reutilizadas por otros agentes o por el sistema:
- **Path:** `/home/emky/n8n/documentacion/2_RESOURCES/SCRIPTS_AND_TOOLS/`
- **Uso:** Scripts de mantenimiento, utilidades del sistema, prompts maestros.

### 4. Base de Conocimiento (Lecciones Aprendidas)
Documentación sobre fallos, soluciones complejas y "Aha!" moments:
- **Path:** `/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/KNOWLEDGE_BASE/`
- **Uso:** Archivos `.md` que expliquen lógica técnica o protocolos.

## 📜 Regla de Nombramiento
- **Scripts:** `[accion]_[contexto]_[version].py` (ej. `patch_aggregator_v1.py`).
- **Dumps:** `raw_[entidad]_[id].json` (ej. `raw_exec_486.json`).
- **Documentos:** `[TIPO]_[DESCRIPCION].md` (ej. `LEARNINGS_SQL_PATCHING.md`).

## 🧠 Protocolo de Búsqueda Semántica (RAG)
Antes de realizar una búsqueda exhaustiva con `grep` o `find`, el agente **DEBE**:
1.  Consultar la DB Vectorial usando la skill `search_rag.py`.
2.  Si la información es insuficiente, proceder con el `INDEX.md`.
3.  **Indexación:** Cada vez que se cree un documento de aprendizaje crítico (ej. en `3_WORK_LOGS_AND_HISTORY`), el agente debe sugerir al usuario ejecutar el workflow `Vega_Knowledge_Base_Indexer` para mantener la base vectorial actualizada.

## ⚠️ Archivos de Sistema Críticos
Existen archivos en la raíz que **NUNCA** deben ser movidos, modificados o borrados por un agente sin permiso explícito del usuario:
- **`config`**: Contiene la `encryptionKey`. Sin ella, n8n no puede usar ninguna credencial.
- **`database.sqlite`**: La base de datos viva del sistema.
- **`ecosystem.config.js`**: Configuración de PM2 para el runtime.

## ⚠️ Acciones Prohibidas
- **NO** crear archivos en `/home/emky/n8n/` (solo folders de sistema permitidos).
- **NO** tocar archivos marcados como **CRÍTICOS** en el `SYSTEM_MAP.md`.
- **NO** dejar archivos de test en la raíz después de la verificación.

---
*Este protocolo es parte esencial del núcleo Vega. Ignorarlo se considera mala praxis operativa.*
