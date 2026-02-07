# Backup n8n - Pre-Reinstalación

Este documento detalla el estado del sistema n8n antes de la desinstalación y reinstalación planificada para el 4 de febrero de 2026.

## Componentes Clave Respaldados

- **Nodos Personalizados (`custom-nodes/` y `nodes/`)**: Contienen la lógica específica de conectores y extensiones creadas para el sistema Antigravity.
- **Base de Datos (`database.sqlite`)**: Contiene todos los flujos (workflows), ejecuciones, y configuraciones de nodos.
- **Documentación (`documentacion/`)**: Todos los protocolos operacionales y mapas del sistema.
- **Configuraciones Externas**: `Dockerfile`, `docker-compose.yml`, `ecosystem.config.js` (PM2), y scripts de parcheo.

## Estado del Sistema Actual
- **Versión n8n intentada**: v1.75.2
- **Problema de origen**: Errores 500 y crash en login tras intentos de actualización/downgrade de base de datos.
- **Objetivo**: Limpiar el entorno completamente y restaurar desde este backup en una instalación fresca.

## Repositorio de Respaldo (GitHub)
- **Privacidad**: Privado
- **Contenido**: Proyecto completo `/home/emky/n8n`
- **Nota**: Se excluye `node_modules` por tamaño y redundancia.

---
*Este documento debe ser revisado después de la reinstalación para asegurar que todos los volúmenes y rutas coincidan.*
