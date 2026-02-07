#!/usr/bin/env python3
"""
🔧 Hot Patch n8n Workflow - Modifica workflows en vivo sin F5

Este script modifica el workflow de Gemini directamente en la base de datos
de n8n y fuerza un reload usando la API interna.

Uso:
    python3 hot_patch_workflow.py
"""

import sqlite3
import json
import sys
import requests
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
N8N_API = "http://localhost:5678"
WORKFLOW_NAME = "Yes"

def get_workflow_from_db():
    """Obtiene el workflow desde SQLite"""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    # Buscar workflow por nombre
    cursor.execute("""
        SELECT id, nodes, connections, staticData, settings, name
        FROM workflow_entity 
        WHERE name = ?
    """, (WORKFLOW_NAME,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print(f"❌ No se encontró el workflow '{WORKFLOW_NAME}'")
        sys.exit(1)
    
    workflow_id, nodes, connections, static_data, settings, name = result
    
    return {
        'id': workflow_id,
        'nodes': json.loads(nodes) if nodes else [],
        'connections': json.loads(connections) if connections else {},
        'staticData': json.loads(static_data) if static_data else None,
        'settings': json.loads(settings) if settings else {},
        'name': name
    }

def patch_aggregator_node(workflow):
    """Modifica el nodo Aggregator para incluir datos estructurados"""
    nodes = workflow['nodes']
    
    # Buscar el nodo Aggregator
    aggregator_node = None
    for node in nodes:
        if node['name'] == 'Aggregator':
            aggregator_node = node
            break
    
    if not aggregator_node:
        print("❌ No se encontró el nodo 'Aggregator'")
        return False
    
    # Código mejorado
    new_code = """let result = "Success";
let structured_data = null;

if (items.length > 0) {
  if (items[0].json.id && items[0].json.name) {
     // Drive Search result - save both text AND structured data
     result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
     structured_data = items.map(i => ({ 
       id: i.json.id, 
       name: i.json.name, 
       mimeType: i.json.mimeType || 'unknown'
     }));
  } else if (items[0].json.stdout) {
     result = items[0].json.stdout;
  } else if (items[0].binary) {
     result = "Binary processed";
  }
}

// Aggregate for History WITH structured data
const prev = $('Clean Actor').last().json;
return [{ json: { 
  action_taken: prev.accion, 
  tool_result: result,
  tool_result_data: structured_data,
  planner_instruction: prev.instruction, 
  user_goal: prev.user_goal, 
  history: prev.history, 
  counter: prev.counter
} }];"""
    
    aggregator_node['parameters']['jsCode'] = new_code
    print("✅ Nodo 'Aggregator' modificado")
    return True

def patch_update_state_node(workflow):
    """Modifica el nodo Update State para incluir result_data en el history"""
    nodes = workflow['nodes']
    
    # Buscar el nodo Update State
    update_state_node = None
    for node in nodes:
        if node['name'] == 'Update State':
            update_state_node = node
            break
    
    if not update_state_node:
        print("❌ No se encontró el nodo 'Update State'")
        return False
    
    # Código mejorado
    new_code = """const item = $input.item.json;
const newHistory = item.history || [];

newHistory.push({
  plan: item.planner_instruction,
  action: item.action_taken,
  result: item.tool_result,
  result_data: item.tool_result_data  // ← NUEVO: datos estructurados
});

const newCounter = (item.counter || 0) + 1;

// Loop limit 15 - exit loop if reached
if (newCounter >= 15) {
    console.log('⚠️ Límite de 15 iteraciones alcanzado. Forzando salida.');
}

return [{ json: { 
  user_goal: item.user_goal, 
  history: newHistory, 
  counter: newCounter 
} }];"""
    
    update_state_node['parameters']['jsCode'] = new_code
    print("✅ Nodo 'Update State' modificado")
    return True

def patch_planner_prep_node(workflow):
    """Modifica Planner Prep para incluir datos estructurados en el prompt"""
    nodes = workflow['nodes']
    
    planner_prep_node = None
    for node in nodes:
        if node['name'] == 'Planner Prep':
            planner_prep_node = node
            break
    
    if not planner_prep_node:
        print("❌ No se encontró el nodo 'Planner Prep'")
        return False
    
    # Código mejorado
    new_code = """return $input.all().map(item => {
  const goal = item.json.user_goal;
  const history = item.json.history || [];
  const counter = item.json.counter || 0;

  // Format history for the Planner WITH structured data
  let historyText = "No se ha ejecutado ninguna acción aún.";
  if (history.length > 0) {
    historyText = history.map((h, i) => {
      let details = `PASO ${i+1}:
- El Planner decidió: ${h.plan}
- El Actor ejecutó: ${h.action}
- Resultado: ${h.result}`;
      
      // Si hay datos estructurados, agrégalos
      if (h.result_data && Array.isArray(h.result_data)) {
        details += `\\n- DATOS DISPONIBLES (usa estos IDs exactos):\\n${JSON.stringify(h.result_data, null, 2)}`;
      }
      
      return details;
    }).join("\\n\\n");
  }

  const prompt = `ERES EL CEREBRO ESTRATÉGICO de un sistema de ejecución.

OBJETIVO PRINCIPAL DEL USUARIO:
"${goal}"

HISTORIAL DE EJECUCIÓN (${history.length} acciones completadas):
${historyText}

IMPORTANTE: NO TIENES HERRAMIENTAS DISPONIBLES. Debes devolver JSON con una instrucción para que otro agente ejecute.

HERRAMIENTAS DISPONIBLES (para el Actor, no para ti):
1. buscar_en_drive(query: string) - Buscar archivos en Google Drive
2. descargar_de_drive(fileId: string, filename: string) - Descargar archivo
3. subir_a_drive(filename: string) - Subir archivo
4. ejecutar_comando(command: string) - Ejecutar comando bash

REGLAS DE ORO:
1. SI el historial está VACÍO → Planifica el primer paso lógico.
2. SI el objetivo NO está completo → Planifica el siguiente paso.
3. CUANDO uses IDs de archivos, USA EXACTAMENTE los IDs de "DATOS DISPONIBLES".
4. SOLO marca is_done:true SI el objetivo está 100% cumplido.
5. DEVUELVE SOLO JSON, SIN MARKDOWN.

EJEMPLO:
Usuario: "Descarga mis archivos takeout de Drive"
Historial: vacío
TU RESPUESTA (JSON PURO):
{
  "thought": "Debo buscar archivos con 'takeout' en Drive primero.",
  "next_instruction": "Buscar en Google Drive archivos que contengan 'takeout' en el nombre",
  "is_done": false,
  "final_response": ""
}

AHORA TU TURNO. SALIDA JSON:`;

  return { json: { prompt, history, user_goal: goal, counter } };
});"""
    
    planner_prep_node['parameters']['jsCode'] = new_code
    print("✅ Nodo 'Planner Prep' modificado")
    return True

def save_workflow_to_db(workflow):
    """Guarda el workflow modificado en SQLite"""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE workflow_entity 
        SET nodes = ?, 
            connections = ?,
            updatedAt = datetime('now')
        WHERE id = ?
    """, (
        json.dumps(workflow['nodes']),
        json.dumps(workflow['connections']),
        workflow['id']
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ Workflow guardado en DB (ID: {workflow['id']})")

def patch_tool_router_node(workflow):
    """Reconstruye el nodo Tool Router para corregir lógica de enrutamiento"""
    nodes = workflow['nodes']
    
    router_node = None
    for node in nodes:
        if node['name'] == 'Tool Router':
            router_node = node
            break
            
    if not router_node:
        print("❌ No se encontró el nodo 'Tool Router'")
        return False
        
    router_node['parameters']['rules'] = {
        "values": [
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "buscar_en_drive"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "descargar_de_drive"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "subir_a_drive"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "ejecutar_comando"}],
                    "combinator": "and"
                }
            }
        ]
    }
    print("✅ Nodo 'Tool Router' reconstruido")
    return True

def patch_drive_search_node(workflow):
    """Corrige la configuración del nodo Drive Search"""
    nodes = workflow['nodes']
    
    search_node = None
    for node in nodes:
        if node['name'] == 'Drive Search':
            search_node = node
            break
            
    if not search_node:
        print("❌ No se encontró el nodo 'Drive Search'")
        return False
    
    # Corregir resource de "fileFolder" a "file" y operation a "search"
    if 'parameters' in search_node:
        search_node['parameters']['resource'] = 'file'
        search_node['parameters']['operation'] = 'search'  # ✅ CORRECTO: search, no list
        
        # Asegurar que el filtro esté bien configurado
        if 'filter' not in search_node['parameters']:
            search_node['parameters']['filter'] = {}
        
        search_node['parameters']['filter']['q'] = "={{ $json.datos.query }}"
        
    print("✅ Nodo 'Drive Search' corregido (resource: file, operation: search)")
    return True

def patch_inject_webhook(workflow):
    """Inyecta un Webhook de prueba conectado a 'Read History'"""
    nodes = workflow['nodes']
    connections = workflow['connections']
    
    # Check if webhook exists
    for node in nodes:
        if node['name'] == 'Webhook_Testing':
            print("⚠️ Webhook 'Webhook_Testing' ya existe")
            return False
            
    webhook_node = {
        "parameters": {
            "httpMethod": "POST",
            "path": "test_agent_v1",
            "options": {}
        },
        "name": "Webhook_Testing",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [400, 300],
        "webhookId": "test-agent-v1-id"
    }
    
    nodes.append(webhook_node)
    
    # Connect to "Read History"
    if "Webhook_Testing" not in connections:
        connections["Webhook_Testing"] = {"main": [[{"node": "Read History", "type": "main", "index": 0}]]}
        
    print("✅ Webhook 'Webhook_Testing' inyectado (Path: /webhook/test_agent_v1)")
    return True

def main():
    print("🔧 Hot Patch n8n Workflow - Iniciando...\n")
    
    # 1. Obtener workflow de la DB
    print(f"📖 Leyendo workflow '{WORKFLOW_NAME}' de SQLite...")
    workflow = get_workflow_from_db()
    print(f"   → Encontrado: ID {workflow['id']} con {len(workflow['nodes'])} nodos\n")
    
    # 2. Aplicar patches
    print("🔨 Aplicando modificaciones...")
    patch_aggregator_node(workflow)
    patch_update_state_node(workflow)
    patch_planner_prep_node(workflow)
    patch_tool_router_node(workflow)
    patch_drive_search_node(workflow)
    patch_inject_webhook(workflow)
    print()

    
    # 3. Guardar en DB
    print("💾 Guardando cambios...")
    save_workflow_to_db(workflow)
    print()
    
    print("✨ ¡Listo! Ahora haz F5 en n8n para ver los cambios.")
    print("   Test with: curl -X POST -H 'Content-Type: application/json' -d '{\"user_goal\": \"hello\"}' http://localhost:5678/webhook/test_agent_v1")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
