# 🚨 HIPÓTESIS ALTERNATIVA (Aplicando Regla de Einstein)

**FECHA**: 2026-02-03T01:03Z  
**CONTEXTO**: El error `[ERROR: A 'json' property isn't an object [item 0]]` persiste después de parchear 5 nodos diferentes (Route Decision v20, Parse Planner v22, Aggregator v23, Update Memory v23).

## HIPÓTESIS ACTUAL (DESCARTADA)
"El problema es el código JavaScript dentro de los nodos individuales que procesan mal el objeto `json`."

## NUEVA HIPÓTESIS (Escape del Bucle)

### Opción 1: Cache/Inval

idation de n8n
**Teoría**: n8n está cargando una versión cacheada del workflow desde memoria, ignorando las actualizaciones de la DB.
**Cómo probar**: 
- Detener n8n completamente (`pm2 stop n8n-master`)
- Limpiar cache si existe (`rm -rf ~/.n8n/.cache` o similar)
- Reiniciar (`pm2 start n8n-master`)

### Opción 2: El error NO viene de un nodo Code
**Teoría**: El mensaje de error es GENÉRICO de n8n cuando CUALQUIER nodo intenta procesar un ítem con `json` inválido, no necesariamente un nodo "Code".
**Cómo probar**:
- Buscar en TODOS los nodos (incluyendo nativos como If, Switch, Merge) si están usando expresiones que asumen `item.json` es un objeto.
- Ver logs RAW de ejecución (execution_data table) para identificar el nodo EXACTO que crashea.

### Opción 3: El Trigger o Init Context producen datos corruptos desde el origen
**Teoría**: El nodo "When chat message received" o "Init Context" está devolviendo un array en lugar de un objeto, y TODO el flujo downstream hereda ese problema.
**Cómo probar**:
- Agregar un nodo de debug inmediatamente después del trigger para hacer `console.log(JSON.stringify($input.all()))`.
- Hotpatch "Init Context" para forzar que SIEMPRE devuelva un objeto válido con validación estricta.

### Opción 4: Migración de n8n rompió compatibilidad
**Teoría**: La estructura de datos que n8n espera cambió entre versiones y nuestro workflow usa un formato antiguo.
**Cómo probar**:
- Verificar versión de n8n (`npm ls n8n` en el directorio de instalación).
- Buscar en changelogs de n8n si hubo breaking changes en la estructura de `item.json`.

## PLAN DE ACCIÓN (NUEVO)
1. ✅ Documentar esta hipótesis
2. [ ] Limpiar cache de n8n y reiniciar desde cero
3. [ ] Si persiste: Insertar nodo de logging CRUDO después del trigger
4. [ ] Si persiste: Recrear un workflow MÍNIMO (trigger → code → response) para aislar el problema
5. [ ] Si persiste: Contactar logs de n8n en `/var/log` o `pm2 logs n8n-master` para ver stack trace completo

**NO MÁS PARCHES DE NODOS HASTA PROBAR ESTO.**
