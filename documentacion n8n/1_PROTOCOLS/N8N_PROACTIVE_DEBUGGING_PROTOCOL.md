# 🔍 Protocolo de Depuración Proactiva (N8N_PROACTIVE_DEBUGGING_PROTOCOL)

Este protocolo define cómo los Agentes/LLMs deben actuar con **autonomía** para diagnosticar errores en n8n sin intervención humana constante.

---

## 🏗️ 1. Fuente de Verdad (Real-time Logs)
Los logs en vivo de `pm2` son la única ventana confiable a la ejecución real. No confíes en archivos estáticos antiguos o estados guardados que puedan estar desfasados.

### Comando de Diagnóstico Principal:
Ejecuta esto SIEMPRE que necesites investigar un fallo reciente:

```bash
pm2 logs n8n-master --lines 1000 --nostream
```

---

## 🧠 2. Análisis Proactivo (Traceback)
No mires solo el error final; analiza la cadena de causalidad.

1.  **STOP & READ**: No asumas el error. Lee los logs **hacia atrás**.
2.  **IDENTIFICAR NODO INICIAL**: Busca el evento `Running node "NombreDelNodo" started` justo antes del error.
3.  **VERIFICAR PREDECESOR**: Identifica qué nodo se ejecutó *antes* de ese. ¿Terminó correctamente (`finished`)?
4.  **SECUENCIA COMPLETA**: Al tener 1000 líneas, puedes ver la secuencia completa. Úsala para deducir en qué punto del flujo se corrompieron los datos (ej: un nodo anterior no pasó el `fileId` esperado).
5.  **DIAGNÓSTICO AUTÓNOMO**: Diagnostica el problema basándote en esta cadena de eventos antes de proponer cambios o pedir ayuda.

---

## 📚 3. Referencias de Soporte
*   [Optimización de Nodos Custom](./N8N_CUSTOM_NODE_OPTIMIZATION.md): Reglas para modificar el código del nodo Gemini CLI.
*   [Gestión Avanzada de Estados](./ADVANCED_WORKFLOW_STATE_MANAGEMENT.md): Manejo de bucles complejos y depuración forense.
*   [Recuperación de Desastres](./N8N_DISASTER_RECOVERY_AND_REPAIR.md): Restauración de workflows y limpieza.

---
**Esencia**: "No preguntes qué falló, descubre dónde se rompió el flujo."
