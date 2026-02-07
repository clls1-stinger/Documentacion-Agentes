// VEGA v23: Paranoid Aggregator
let result = "Success";
let structured_data = null;
const items = $input.all();

try {
    if (items.length > 0) {
      if (items[0].json && items[0].json.id && items[0].json.name) {
         // Drive Search result
         result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
         structured_data = items.map(i => ({
           id: i.json.id,
           name: i.json.name,
           mimeType: i.json.mimeType || 'unknown'
         }));
      } else if (items[0].json && items[0].json.stdout) {
         result = items[0].json.stdout;
      } else if (items[0].binary) {
         result = "Binary processed";
      } else if (items[0].json && items[0].json.error) {
         result = "Error: " + items[0].json.error;
      }
    }
} catch (e) {
    result = "Error processing tool output: " + e.message;
}

// Access Previous State Defensively
let prev = {};
try {
    const cleanActor = $('Clean Actor').last();
    prev = (cleanActor && cleanActor.json) ? cleanActor.json : {};
} catch(e) {
    // Fallback if Clean Actor is unreachable (e.g. first run or weird loop)
    prev = {
        user_goal: "UNKNOWN (State Lost)",
        history: [],
        counter: 0,
        chat_history: []
    };
}

// Ensure critical fields exist
prev.history = Array.isArray(prev.history) ? prev.history : [];
prev.chat_history = Array.isArray(prev.chat_history) ? prev.chat_history : [];

return [{ json: {
  action_taken: prev.accion || "Unknown Action",
  tool_result: result,
  tool_result_data: structured_data,
  planner_instruction: prev.instruction || "No instruction",
  user_goal: prev.user_goal,
  history: prev.history,
  counter: prev.counter || 0,
  chat_history: prev.chat_history
} }];
