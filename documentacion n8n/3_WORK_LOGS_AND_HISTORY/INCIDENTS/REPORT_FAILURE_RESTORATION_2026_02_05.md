# 📉 REPORTE DE FRACASO: Restauración de Flujo n8n (2026-02-05)

## 📋 Resumen del Incidente
El intento de restaurar y parchear el flujo de trabajo tras la reinstalación de n8n v1.123.18 resultó en un **FRACASO operativo**. A pesar de múltiples intentos de importación y parcheo de nodos, el sistema no reflejó los cambios en la UI del usuario y bloqueó el puerto 5678 repetidamente.

## 🔍 Análisis de Errores (Post-Mortem)

### 1. Error de Identidad de Flujo (ID Mismatch)
- **Falla**: Se importaron flujos genéricos desde el backup sin considerar que n8n generó nuevos IDs internos en la base de datos limpia.
- **Consecuencia**: El usuario visualizaba "My workflow" (`ID: osenZpfZMpCRQBSL`), mientras que los parches del agente se aplicaban a un duplicado invisible o desactivado.
- **Lección**: Siempre verificar el `ID` activo mediante `sqlite3` antes de realizar importaciones masivas.

### 2. Confusión de Base de Datos
- **Falla**: Durante la transición de reinstalación, coexistieron múltiples rutas potenciales de datos. El agente asumió que la base de datos en `~/.n8n/` era la única activa, ignorando posibles bloqueos de procesos PM2 que apuntaban a versiones anteriores.
- **Consecuencia**: Desajuste entre lo que el CLI escribía y lo que el proceso n8n cargaba en memoria.

### 3. Inestabilidad de Proceso (Port Locking)
- **Falla**: Uso inconsistente de `pm2 restart` vs `pm2 delete`.
- **Consecuencia**: Procesos huérfanos de n8n quedaron colgando en el puerto 5678, impidiendo que la nueva versión del flujo se sirviera correctamente.

## 🛠️ Acciones de Mitigación (Último Intento)
- Se identificó el ID específico `osenZpfZMpCRQBSL`.
- Se creó un script de parcheo dirigido (`target_patch.py`).
- Se forzó la limpieza de procesos con `pkill -9 n8n`.

## 📜 Estado Final
> [!CAUTION]
> **ESTATUS: FRACASO DOCUMENTADO**
> El flujo no es funcional en su estado original tras la actualización de n8n. Se requiere una reconstrucción manual del trigger o una intervención directa en la UI para re-vincular los inputs del chat.

---
*Firmado: Antigravity (VEGA Kernel AI)*
