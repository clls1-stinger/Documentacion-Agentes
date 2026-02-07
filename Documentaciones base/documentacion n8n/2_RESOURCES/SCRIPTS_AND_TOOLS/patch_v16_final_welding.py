#!/usr/bin/env python3
"""
⭐ VEGA v16: FINAL WELDING
Reparando las conexiones faltantes identificadas visualmente.
1. Route Decision -> Final Response
2. Wait -> Loop Merge
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    conns = json.loads(cursor.fetchone()[0])
    
    print("🔥 SOLDANDO CONEXIONES FALTANTES...")
    
    # 1. FIX Route Decision -> Final Response
    # Aseguramos que Route Decision tenga 2 salidas main
    # Output 0 -> Actor Prep
    # Output 1 -> Final Response
    
    if 'Route Decision' not in conns:
        conns['Route Decision'] = {'main': [[], []]}
    
    # Asegurar estructura de array de salidas
    if 'main' not in conns['Route Decision']:
        conns['Route Decision']['main'] = [[], []]
    
    # Si solo tiene 1 array, agregar el segundo
    if len(conns['Route Decision']['main']) < 2:
        conns['Route Decision']['main'].append([])
        
    # Salida 0 (Abajo): Actor Prep
    conns['Route Decision']['main'][0] = [
        { "node": "Actor Prep", "type": "main", "index": 0 }
    ]
    
    # Salida 1 (Arriba): Final Response
    conns['Route Decision']['main'][1] = [ # <--- ESTO ES LO QUE FALTABA
        { "node": "Final Response", "type": "main", "index": 0 }
    ]
    
    print("✅ Soldado: Route Decision [salida 1] -> Final Response")


    # 2. FIX Wait -> Loop Merge
    # El bucle debe cerrarse desde el nodo 'Wait' hacia el 'Loop Merge' (entrada 1)
    
    # Verificar si el nodo Wait existe en las conexiones (si tiene salidas)
    if 'Wait' not in conns:
        conns['Wait'] = {'main': [[]]}
        
    conns['Wait']['main'] = [
        [
            { "node": "Loop Merge", "type": "main", "index": 1 } # Input 1 es el Loop Input
        ]
    ]
    
    print("✅ Soldado: Wait -> Loop Merge [entrada 1]")
    
    # Limpiar conexiones viejas que podrían interferir (ej. Update State -> Loop Merge)
    # Queremos que vaya Update State -> Wait -> Loop Merge
    if 'Update State' in conns:
         # Redirigir Update State -> Wait
         conns['Update State']['main'] = [
             [{ "node": "Wait", "type": "main", "index": 0 }]
         ]
         print("✅ Corregido: Update State -> Wait")

    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET connections = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(conns), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v16: FINAL WELDING")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ Conexiones soldadas. HAZ F5.")
    print("   Ahora sí, verás los cables puestos.")
