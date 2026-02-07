# 🛰️ SESIÓN DE DEBUGGING: BUCLE DE BÚSQUEDA / ACCIÓN DESCONOCIDA (2026-02-03)

## 📋 Contexto
El usuario reportó que el workflow "se va por el mismo camino de search todo el rato" (bucle de búsqueda) o falla repetidamente.
Evidencia: `last_exec_raw.json` mostró que el agente Gemini instruyó: `list_directory(dir_path='google_takeout_data/')`.
Alucinación: El Prompt explícitamente prohíbe inventar `list_directory`, pero el modelo lo hizo de todos modos.

## 🕵️ Investigación Forense
1. **El Problema**: El `Tool Router` (Switch) no tenía una regla para `list_directory`.
2. **El Síntoma**: 
   - El nodo `Clean Actor` recibía `list_directory` y, al no estar en su mapa, lo pasaba tal cual.
   - El `Tool Router` no coincidía con ninguna regla (ni `ejecutar_comando` ni `buscar_en_drive`).
   - El flujo se detenía silenciosamente o, si el usuario reintentaba, parecía "atrapado" (o el usuario interpretaba el silencio como "sigue buscando").
3. **Loop Potencial**: Si el agente no recibe feedback de error ("No existe esa herramienta"), asume que no pasó nada y vuelve a intentarlo, o prueba "search" como fallback mental.

## 💉 Solución: Parche v32 (Self-Correcting Actor)
He modificado el nodo `Clean Actor` (`c39b8f9d-9816-484a-bb4a-8b61255de101`) con lógica defensiva:

1. **Mapping Explícito**: `list_directory` y `ls` ahora se transforman automáticamente a `ejecutar_comando` con el comando `ls -R <path>`.
2. **Sistema de Error Feedback**: Si la acción final no coincide con ninguna herramienta válida (`buscar_en_drive`, `ejecutar_comando`, etc.), el nodo **reescribe** la acción a `ejecutar_comando` y el comando a `echo "SYSTEM ERROR: Action <name> unknown..."`.
   - **Beneficio**: Esto asegura que el error llegue al Agente en el siguiente paso (vía History), permitiéndole corregirse (e.g., "Ah, debo usar ejecutar_comando").

## 🚀 Estado
- **Workflow**: `workflow_yes_patched_v32.json` generado en `FORENSICS_AND_LOGS`.
- **Implementación**: Importar este JSON en n8n para aplicar el fix.

---
**ANALISTA**: Vega LifeOS Kernel
