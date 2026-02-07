# 🗺️ Mapa del Sistema de Archivos Local

Este documento define la "verdad" sobre las rutas del sistema para el Agente Vega ("Vega").

## 📍 Puntos de Montaje Críticos
El sistema tiene acceso a los siguientes directorios clave. El agente debe usar estas rutas base para cualquier operación de lectura/escritura local.

| Variable | Ruta Absoluta | Descripción |
| :--- | :--- | :--- |
| `MOUNT_POINT` | `/run/media/emky/MEGATRON` | Raíz del disco externo principal. |
| `OBSIDIAN_ROOT` | `/run/media/emky/MEGATRON/Google Drive/Habitos Obsidian` | Base de conocimientos (Obsidian Vault). |
| `DAILY_NOTES_DIR` | `/run/media/emky/MEGATRON/Google Drive/Habitos Obsidian/Hábitos/Notas Diarias` | Notas diarias y journal. |
| `PROJECTS_DIR` | `/run/media/emky/MEGATRON/Google Drive/Habitos Obsidian/CODE` | Código fuente y proyectos activos. |
| `WORKFLOWS_DIR` | `/home/emky/Codigo/workflows/workflows_vega` | Workflows JSON de n8n. |
| `BRAIN_DIR` | `/home/emky/.gemini/antigravity/brain` | Memoria, artefactos y logs del agente. |
| `DOCS_ROOT` | `/home/emky/n8n/documentacion` | Raíz de toda la documentación y guías. |
| `CONFIG_FILE` | `/home/emky/n8n/config` | **CRÍTICO:** Contiene la `encryptionKey`. **BORRARLO INHABILITA TODAS LAS CREDENCIALES.** |
| `TOOLS_HISTORY` | `/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/TOOLS_HISTORY` | Historial cronológico de scripts LLM. |
| `PM2_PROCESS_NAME` | `n8n-master` | Nombre del proceso n8n en PM2 (NO USAR 'n8n'). |

## ⚠️ Advertencia de Alucinación
Si el Agente intenta acceder a rutas genéricas como `/home/user/Documents` o `./`, **DETENER** y redirigir a una de las rutas arriba mencionadas.

### 📝 Guías de Escritura
Todo agente **DEBE** consultar `[AGENT_GUIDELINES.md](./AGENT_GUIDELINES.md)` antes de crear nuevos archivos para evitar desordenar la raíz.

## 🔄 Daemon de Montaje
(Pendiente de investigación: Script de automontaje en `/etc` o `systemd`)
