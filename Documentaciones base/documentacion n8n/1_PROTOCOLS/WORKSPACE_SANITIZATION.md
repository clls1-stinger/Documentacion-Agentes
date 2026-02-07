# 🏥 Protocolo de Sanitización de Espacio de Trabajo (Workspace)

Para mantener el orden y evitar que la raíz de `~/n8n` se convierta en un repositorio de archivos temporales, se establece la siguiente estructura obligatoria.

## 📂 Estructura de Directorios

| Directorio | Contenido |
| :--- | :--- |
| `backups/workflows/` | Exportaciones `.json` de flujos, respaldos antes de parches. |
| `backups/databases/` | Copias de `database.sqlite` o archivos de historial `.sqlite`. |
| `logs/` | Archivos `.log`, `.txt` de diagnósticos o salidas de comandos. |
| `scripts/` | Scripts de automatización (`.py`, `.sh`, `.js`) que no sean nodos personalizados. |
| `custom-nodes/` | Desarrollo de nodos propios para n8n. |
| `documentacion/` | Base de conocimiento, protocolos e identidad de VEGA. |

## 🛠️ Acciones de Sanitización
1. **No guardar archivos en la raíz**: Cualquier exportación debe ir a su carpeta correspondiente.
2. **Nomenclatura**: Usar sufijos descriptivos (`_BACKUP`, `_FIXED`, `_HISTOGRAMA`).
3. **Limpieza periódica**: Los archivos en `logs/` con más de 7 días deben ser eliminados o comprimidos.

---
**Autor**: Vega ⭐  
**Fecha**: 2026-02-05
