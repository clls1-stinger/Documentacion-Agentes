# Protocolos de Escalación y Acceso (Vega)

Este documento instruye a futuros agentes y LLMs sobre cómo proceder cuando encuentran limitaciones técnicas o de permisos en el sistema.

## 1. Herramientas Faltantes (Ej: `gh`, `pacman`)
Si el sistema requiere una herramienta (como GitHub CLI) que no está instalada:
- **NO** intentes forzar instalaciones experimentales.
- **IDENTIFICA** el gestor de paquetes del host (en este caso, `pacman` en CachyOS/Arch).
- **SOLICITA** al usuario (`Emky`) la instalación proporcionando el comando exacto (Ej: `sudo pacman -S github-cli`).
- **EXPLICA** el porqué de la necesidad para mantener la transparencia.

## 2. Permisos Restringidos (`sudo`)
Antigravity opera en modo YOLO para comandos estándar, pero las acciones críticas del sistema (como modificar servicios de n8n o instalar paquetes) requieren intervención del usuario.
- Si un comando falla por `permission denied`, documenta el error y pide al usuario que lo ejecute con `sudo` o proporcione acceso.

## 3. Uso de Credenciales Compartidas
Para tareas de mantenimiento (como backups de emergencia):
- Las credenciales deben buscarse en `documentacion/4_SECURITY_AND_CREDENTIALS/`.
- El PAT de GitHub actual (`ghp_...`) está destinado a la persistencia del sistema. Si expira, debe pedirse una rotación.

## 4. El Deber de Documentar (Enseñar a Otros)
Cada vez que el usuario otorgue un acceso o instale una herramienta:
- Actualiza el `MANIFEST.md` y este protocolo.
- Enseña al siguiente agente cómo se resolvió el bloqueo. La inteligencia del sistema crece con cada intervención documentada.

---
*Vega OS Kernel - Protocol de Resiliencia.*
