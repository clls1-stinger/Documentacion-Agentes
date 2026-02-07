# 🔧 Fix para el Nodo Aggregator

## Problema Actual
El `Aggregator` solo guarda texto genérico como:
```
"[FILE] takeout-20240115.zip (abc123xyz)"
```

Pero el **Gemini Planner** no puede extraer el ID correctamente de este texto.

## Solución: Agregar Datos Estructurados

Modifica el código del nodo `Aggregator`:

```javascript
let result = "Success";
let structured_data = null;

if (items.length > 0) {
  if (items[0].json.id && items[0].json.name) {
     // Es resultado de Drive Search - guardar BOTH texto Y objeto
     result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
     structured_data = items.map(i => ({ id: i.json.id, name: i.json.name, mimeType: i.json.mimeType }));
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
  tool_result_data: structured_data,  // ← NUEVO: datos estructurados
  planner_instruction: prev.instruction, 
  user_goal: prev.user_goal, 
  history: prev.history, 
  counter: prev.counter
} }];
```

Luego, en **`Planner Prep`**, incluye estos datos en el prompt:

```javascript
if (history.length > 0) {
  historyText = history.map((h, i) => {
    let details = `PASO ${i+1}:
- El Planner decidió: ${h.plan}
- El Actor ejecutó: ${h.action}
- Resultado: ${h.result}`;
    
    // Si hay datos estructurados, agrégalos
    if (h.result_data && Array.isArray(h.result_data)) {
      details += `\n- DATOS DISPONIBLES:\n${JSON.stringify(h.result_data, null, 2)}`;
    }
    
    return details;
  }).join("\n\n");
}
```

## Por Qué Esto Funciona

Ahora el Planner ve:
```
PASO 1:
- El Planner decidió: Buscar archivos takeout
- El Actor ejecutó: buscar_en_drive  
- Resultado: [FILE] takeout-20240115.zip (1abc...), [FILE] takeout-20240120.zip (2def...)
- DATOS DISPONIBLES:
[
  { "id": "1abc...", "name": "takeout-20240115.zip", "mimeType": "application/zip" },
  { "id": "2def...", "name": "takeout-20240120.zip", "mimeType": "application/zip" }
]
```

Y puede decirle al Actor:
```
"Descargar el archivo con ID '1abc...' y guardarlo como 'takeout-20240115.zip'"
```

## Implementación en n8n

1. Abre el workflow en n8n
2. Edita el nodo `Aggregator`
3. Reemplaza el código JavaScript con la versión mejorada
4. Edita el nodo `Update State` para incluir `result_data`:

```javascript
newHistory.push({
  plan: item.planner_instruction,
  action: item.action_taken,
  result: item.tool_result,
  result_data: item.tool_result_data  // ← IMPORTANTE
});
```

5. Guarda y prueba de nuevo
