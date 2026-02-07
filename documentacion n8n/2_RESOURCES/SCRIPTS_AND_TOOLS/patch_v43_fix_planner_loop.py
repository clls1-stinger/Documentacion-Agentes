import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

NEW_PLANNER_JS = r"""const inputItems = $input.all();
return inputItems.map(item => {
    const json = item.json;
    const history = json.history || [];
    const chatHistory = json.chat_history || [];
    const goal = json.user_goal || "No goal defined";
    const counter = json.counter || 0;

    let historyText = history.length > 0 ? JSON.stringify(history, null, 2) : "No actions yet.";

    const prompt = `Actua como un Agente Autónomo experto en Sistemas y Google Drive.

=== OBJETIVO ACTUAL ===
${goal}

=== HISTORIAL DE ACCIONES (MEMORIA OPERATIVA) ===
${historyText}

=== PROTOCOLO DE RESPUESTA (ESTRICTO) ===
1. **NO ALUCINES IDs**: No inventes IDs de archivos. Si no lo ves en el historial, búscalo.
2. **NO USES PATHS EN DESCARGAS**: descargar_de_drive('mis datos', ...) -> ERROR. descargar_de_drive('1A2b...', ...) -> BIEN.
3. **LOGICA**: 
   - ¿Necesito un archivo? -> buscar_en_drive.
   - ¿Tengo el ID? -> descargar_de_drive.
   - ¿Tengo el archivo local? -> ejecutar_comando.
4. **NO HABLES MUCHO**: Accion directa.
5. **EMPTY RESULTS**: Si en el Historial ves "tool_result": "No results found", ¡DETENTE! No vuelvas a buscar lo mismo. Tu respuesta final debe ser informar al usuario que no encontraste nada.

=== FORMATO JSON ===
{
  "thought": "Tengo el ID del archivo X en el historial, ahora lo descargo...",
  "next_instruction": "Nombre_Funcion(args...)",
  "is_done": false,
  "final_response": null
}`;
    return { json: { prompt, history: history, chat_history: chatHistory, user_goal: goal, counter } };
});
"""

def fix_planner_prompt_loop():
    print(f"🔧 Applying Patch v43 - Planner Anti-Loop Prompt for {WORKFLOW_ID}...")
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    if not result:
        print("❌ Workflow not found")
        return
    
    nodes = json.loads(result[0])
    
    for node in nodes:
        if node['name'] == "Planner Prep":
            print(f"  📦 Modifying node: {node['name']}")
            node['parameters']['jsCode'] = NEW_PLANNER_JS
            print(f"    ✅ Updated JS Prompt with Anti-Loop instructions")

    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v43 - Anti-Loop Prompt)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Patch v43 applied. Planner now knows to stop if results are empty.")

if __name__ == "__main__":
    fix_planner_prompt_loop()
