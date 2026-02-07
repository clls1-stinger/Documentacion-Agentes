#!/usr/bin/env python3
"""
⭐ VEGA v15: FIX ROUTER VISUALS
El Code Node funciona lógicamente, pero visualmente falta una salida.
Solución: Definir explícitamente 'outputs': ['main', 'main'] en el nodo.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    # Encontrar Route Decision
    node_idx = None
    target_node = None
    for idx, node in enumerate(nodes):
        if node['name'] == 'Route Decision':
            node_idx = idx
            target_node = node
            break
    
    if not target_node:
        print("❌ Route Decision node not found!")
        return
    
    print(f"🔍 Fixing Route Decision node at index {node_idx}...")
    
    # FIX VISUAL DE SALIDAS
    # Para Code Node v2, esto podría no ser estándar, pero para que el UI muestre cables,
    # a veces necesita ayuda. Si es v1, outputs=['main', 'main'].
    
    # Vamos a forzar el comportamiento de 2 salidas Main
    # Esto es estándar en n8n para nodos con múltiples salidas del mismo tipo
    target_node['type'] = 'n8n-nodes-base.code'
    target_node['typeVersion'] = 2
    
    # Esta propiedad es clave para la visualización de los puertos
    # Le dice al canvas: "Tengo 2 puertos de salida tipo main"
    # El puerto 0 (arriba) y el puerto 1 (abajo)
    # Nota: En n8n internamente, output index match con este array.
    if 'outputs' not in target_node:
         # Esto define 2 canales 'main'
         # Output 0 -> Main
         # Output 1 -> Main
         # Así n8n dibuja 2 bolitas.
         target_node['outputs'] = ['main', 'main']
         print("✅ Added 'outputs': ['main', 'main'] property")
    else:
        print(f"ℹ️ Node already has outputs: {target_node['outputs']}")
        target_node['outputs'] = ['main', 'main'] # Forzar
        
    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v15: FIXING ROUTER VISUALS")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ Visuals patched. HAZ F5.")
    print("   Ahora deberías ver las 2 salidas del Code Node.")
