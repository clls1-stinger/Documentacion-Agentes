import json
import os

DUMP_PATH = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_dump.json"
PATCHED_PATH = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v31.json"

def patch_planner_prep():
    with open(DUMP_PATH, 'r') as f:
        data = json.load(f)
    
    nodes = data['nodes']
    found = False
    for node in nodes:
        if node['name'] == "Planner Prep":
            print(f"Patching node: {node['name']}")
            # Modificamos el JS para ser agresivo
            node['parameters']['jsCode'] = """return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  let memoryText = chatHistory.length > 0 ? chatHistory.map(h => `User: ${h.user}\nAI: ${h.ai}`).join(\"\n---\n\") : \"No hay historial.\";
  let historyText = stepHistory.length > 0 ? stepHistory.map((h, i) => `STEP ${i+1}: ${h.action} -> ${h.result}`).join(\"\n\") : \"Sin acciones previas.\";

  const prompt = `IDENTIDAD: VEGA OS.
Usuario: Emky.
Estado del Sistema: Operativo.

=== CAPACIDADES (HERRAMIENTAS) ===
1. buscar_en_drive(query): Busca archivos en Google Drive.
2. descargar_de_drive(fileId, filename): Descarga de Drive al sistema local.
3. subir_a_drive(filename): Sube un archivo local a Google Drive.
4. ejecutar_comando(command): Ejecuta comandos Linux (ls, grep, mkdir, unzip, etc.).
   - USA 'ls -R' PARA LISTAR DIRECTORIOS.
5. leer_archivo(path): Lee el contenido de un archivo de texto local.
6. navegar_web(url): Abre una URL en Brave (debug 9222).

=== OBJETIVO ACTUAL ===
${goal}

=== HISTORIAL DE ACCIONES (ESTO YA PASO) ===
${historyText}

=== PROTOCOLO DE RESPUESTA (ESTRICTO) ===
- No saludes. No digas 'Online'. No te presentes.
- Si el objetivo requiere pasos tecnicos, USA LAS HERRAMIENTAS INMEDIATAMENTE.
- No termines la tarea (is_done: true) hasta que el objetivo este CUMPLIDO.
- Si el objetivo es 'Busca archivos', la respuesta DEBE incluir 'next_instruction' con 'buscar_en_drive'.

=== FORMATO JSON ===
{
  \"thought\": \"Analisis de que herramienta necesito ahora...\",
  \"next_instruction\": \"Nombre_Funcion(args...)\",
  \"is_done\": false,
  \"final_response\": null
}`;
        return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""
            found = True
            break
    
    if not found:
        print("❌ Could not find Planner Prep node")
        return

    with open(PATCHED_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Patched workflow saved to {PATCHED_PATH}")

if __name__ == "__main__":
    patch_planner_prep()
