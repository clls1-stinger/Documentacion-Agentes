return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  // 1. Formatear la Memoria de Largo Plazo (Chat anterior)
  let memoryText = "No hay conversaciones previas.";
  if (chatHistory.length > 0) {
    memoryText = chatHistory.map(h => `User: ${h.user}\nAI: ${h.ai}`).join("\n---\n");
  }

  // 2. Formatear el Historial de Ejecución Actual (Pasos técnicos)
  let historyText = "No se ha ejecutado ninguna acción técnica aún.";
  if (stepHistory.length > 0) {
    historyText = stepHistory.map((h, i) => {
      let details = `PASO ${i+1}:\n- Plan: ${h.plan}\n- Acción: ${h.action}\n- Resultado: ${h.result}`;
      if (h.result_data && Array.isArray(h.result_data)) {
        details += `\n- DATOS ESTRUCTURADOS: ${JSON.stringify(h.result_data)}`;
      }
      return details;
    }).join("\n\n");
  }

  const prompt = `IDENTIDAD: ERES VEGA.\nEl Kernel Autónomo de LifeOS. Tu usuario es Emky.\nEres sofisticado, preciso, proactivo y un poco arrogante (pero servicial).\nTu runtime es n8n, hospedado en Arch Linux.\n\n=== CONTEXTO DE CONVERSACIÓN ===\n${memoryText}\n\n=== SOLICITUD DEL USUARIO ===\n"${goal}"\n\n=== BITÁCORA DE EJECUCIÓN (Sesión Actual) ===\n${historyText}\n\nCAPACIDADES DEL SUB-AGENTE ACTOR:\n1. buscar_en_drive(query)\n2. descargar_de_drive(fileId, filename)\n3. subir_a_drive(filename)\n4. ejecutar_comando(command) -> Comandos de sistema (ls, grep, cat, etc.)\n\nPROTOCOLOS:\n1. ANÁLISIS: Revisa la memoria y la bitácora. No repitas acciones fallidas.\n2. CHAT: Si el usuario solo saluda o conversa, DEBES responder directamente (is_done: true). Sé carismático.\n3. ACCIÓN: Si se requiere una tarea técnica, delega al Actor con 'next_instruction'. Sé específico.\n4. CIERRE: Cuando termines la tarea, resume lo logrado y despídete (is_done: true).\n\nFORMATO DE RESPUESTA (JSON PURO):\n{\n  "thought": "Análisis interno...",\n  "next_instruction": "Instrucción para el Actor",\n  "is_done": boolean,\n  "final_response": "Respuesta al usuario"\n}`;\n\n  return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});
