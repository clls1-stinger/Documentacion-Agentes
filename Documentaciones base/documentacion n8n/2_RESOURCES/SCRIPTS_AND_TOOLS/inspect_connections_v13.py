import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT nodes, connections FROM workflow_entity WHERE id="Urf7HpECFvfQooAv"')
row = cursor.fetchone()
nodes = json.loads(row[0])
conns = json.loads(row[1])

def find_node_name(node_name):
    for n in nodes:
        if n['name'] == node_name:
            return n
    return None

critical_nodes = ['Parse Planner', 'Route Decision', 'Actor Prep', 'Final Response']

print("--- DIAGNÓSTICO DE CONEXIONES ---")

for name in critical_nodes:
    print(f"\n📍 NODE: {name}")
    node = find_node_name(name)
    if not node:
        print("   ❌ NO EXISTE")
        continue

    # Ver salidas (Outputs)
    node_out = conns.get(name, {})
    if not node_out:
        print("   ⚠️ SIN SALIDAS DEFINIDAS")
    else:
        for output_type, outputs in node_out.items():
            print(f"   out ({output_type}):")
            for i, output_list in enumerate(outputs):
                print(f"     [{i}] -> {json.dumps(output_list)}")

print("\n--- BÚSQUEDA INVERSA (ENTRADAS) ---")
# Ver quién entra a Route Decision
print("¿Quién conecta a 'Route Decision'?")
found = False
for src, outputs in conns.items():
    if 'main' in outputs:
        for idx, links in enumerate(outputs['main']):
            for link in links:
                if link['node'] == 'Route Decision':
                    print(f"   ✅ {src} [puerto {idx}] --> Route Decision [input {link.get('index', 0)}]")
                    found = True
if not found:
    print("   ❌ NADIE CONECTA A ROUTE DECISION (ISLAND MODE)")
