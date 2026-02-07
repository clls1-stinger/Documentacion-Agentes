---
id: BACKLOG_003
title: "Fix Boolean Routing with Router/Switch (v30 Fallback Mode)"
status: "🟢 Done"
priority: "🔥 Critical"
created: "2026-02-03"
updated: "2026-02-03 T11:30Z"
assignee: "Vega + Emky"
tags:
  - bug
  - critical
  - n8n
  - switch-node
  - type-coercion
  - router
related_files:
  - /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/patch_v30_switch_router.py
  - ~/.n8n/database.sqlite (Workflow: Yes)
  - /home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v30.json
---

# 🐛 Fix Boolean Routing with Router/Switch (v30 Fallback Mode)

## 🎯 Objetivo (¿QUÉ quiere el usuario?)
Eliminar el nodo `IF` inestable y reemplazarlo por un `Switch` (Router) con lógica de `Fallback` para garantizar que el flujo nunca se detenga por errores de evaluación de tipos.

## 🤔 Motivación (¿POR QUÉ es crítico?)
Tras múltiples intentos con el nodo `IF` (v1-v7), se descubrió que n8n presenta inconsistencias al evaluar booleanos que provienen de diferentes fuentes (Python/JS). El usuario sugirió usar un "Router" (Switch) con una salida por defecto (fallback) para asegurar que el sistema intente ejecutar herramientas si no está 100% seguro de que la tarea terminó.

## ✅ Criterios de Aceptación
- [x] El nodo `Route Decision` es de tipo `n8n-nodes-base.switch` (v3.2).
- [x] Regla 0: `is_done_string === "TRUE"` -> Puerto 0 (Final Response).
- [x] Regla 1: `is_done_string === "FALSE"` -> Puerto 1 (Actor Prep).
- [x] Fallback: Redirigir al Puerto 1 (Actor Prep) por seguridad.
- [x] Reinicio de PM2 confirmado.

## 🏗️ Diseño Técnico
Se cambió la arquitectura de decisión de una lógica binaria (`IF`) a una lógica de enrutamiento estricto (`Switch`). 

1. **Entrada**: `planner_output.is_done_string` (Generado por `Parse Planner`).
2. **Lógica**:
   - Match `"TRUE"` -> Output 0.
   - Match `"FALSE"` -> Output 1.
   - No Match / Error -> Output 1 (Fallback).

## 📝 Implementación
- [x] Dump de workflow `Yes`.
- [x] Script `patch_v30_switch_router.py` creado.
- [x] Cambio de tipo de nodo y parámetros aplicados.
- [x] Push a SQLite y reinicio de n8n.

## 🧪 Testing
- [x] Verificado en dump de workflow que las reglas están correctamente aplicadas.
- [ ] **Siguiente**: Usuario debe refrescar UI y probar.

## 📊 Progreso
- [x] Reemplazo de IF por Switch (v30).
- [x] Configuración de Fallback a Output 1.
- [x] Aplicación de parche en DB.
- [x] Reinicio de sistema.

**CONCLUIDO**: El sistema ahora usa un Router robusto con salvatrastos (fallback).

---
**Última actualización**: 2026-02-03 T11:30Z  
**Estado actual**: Parche v30 aplicado. Sistema listo para validación final. 🚀
