#!/usr/bin/env python3
"""
⭐ VEGA v14: CONNECTION REINFORCEMENT
Asegura que TODO esté conectado, incluyendo el Loop Merge.
"""
import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    conns = json.loads(cursor.fetchone()[0])
    
    print("🔧 REFORZANDO CONEXIONES...")
    
    # 1. Parse Planner -> Route Decision
    conns['Parse Planner'] = {'main': [[{'node': 'Route Decision', 'type': 'main', 'index': 0}]]}
    print("✅ Parse Planner -> Route Decision")
    
    # 2. Route Decision -> Actor Prep (0) / Final Response (1)
    conns['Route Decision'] = {
        'main': [
            [{'node': 'Actor Prep', 'type': 'main', 'index': 0}],    # Output 0: FALSE (Continue)
            [{'node': 'Final Response', 'type': 'main', 'index': 0}] # Output 1: TRUE (Done)
        ]
    }
    print("✅ Route Decision -> Actor Prep / Final Response")
    
    # 3. VERIFICAR EL LOOP: Update State -> Loop Merge (ESTO ES CRÍTICO PARA AGENTES)
    # Buscamos quién cierra el ciclo. Usualmente es el último nodo después de las herramientas,
    # que debería volver al Loop Merge o Planner Prep.
    # En tu workflow parece ser 'Update State'.
    
    if 'Update State' in conns:
        # Asegurar que Update State vuelve a Loop Merge
        conns['Update State'] = {'main': [[{'node': 'Loop Merge', 'type': 'main', 'index': 1}]]}
        print("✅ Update State -> Loop Merge (Cerrando el ciclo)")
    else:
        print("⚠️ Update State no encontrado en conexiones.")

    # 4. Loop Merge -> Planner Prep
    if 'Loop Merge' in conns:
        conns['Loop Merge'] = {'main': [[{'node': 'Planner Prep', 'type': 'main', 'index': 0}]]}
        print("✅ Loop Merge -> Planner Prep")

    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET connections = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(conns), WORKFLOW_ID)
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch()
    print("\n✅ Conexiones reforzadas. Ciclo cerrado. HAZ F5.")
