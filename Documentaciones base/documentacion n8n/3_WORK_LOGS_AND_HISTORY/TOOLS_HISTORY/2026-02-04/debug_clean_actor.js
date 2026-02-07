
const items = [{
  json: {
    response: '```json\n{\n  "ejecuciones": [\n    { "herramienta": "descargar_de_drive", "parametros": { "fileId": "12345", "filename": "test.txt" } }\n  ]\n}\n```',
    instruction: "Download test file",
    user_goal: "Download test file"
  }
}];

// Simulate Clean Actor logic
const item = items[0].json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try {
  const jsonMatch = raw.match(/```json\\s*([\\s\\S]*?)\\s*```/) || raw.match(/\\{.*\\}/s);
  if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
  parsed = JSON.parse(raw);
} catch (e) {
  parsed = { error: "Parse Error", raw: raw };
}

const map = {
  'search_drive': 'buscar_en_drive',
  'buscar_en_drive': 'buscar_en_drive',
  'download_file': 'descargar_de_drive',
  'descargar_de_drive': 'descargar_de_drive',
  'upload_file': 'subir_a_drive',
  'subir_a_drive': 'subir_a_drive',
  'run_command': 'ejecutar_comando',
  'run_shell_command': 'ejecutar_comando',
  'ejecutar_comando': 'ejecutar_comando',
  'execute_command': 'ejecutar_comando',
  'read_file': 'leer_archivo',
  'leer_archivo': 'leer_archivo',
  'navegar_web': 'navegar_web',
  'browse': 'navegar_web'
};

let actions = [];
if (parsed.ejecuciones && Array.isArray(parsed.ejecuciones)) {
  actions = parsed.ejecuciones;
} else if (parsed.actions && Array.isArray(parsed.actions)) {
  actions = parsed.actions;
} else if (parsed.herramienta || parsed.accion || parsed.action) {
  actions = [parsed];
}

const result = actions.map(a => {
  let tool = (a.herramienta || a.accion || a.action || "").toLowerCase();
  let params = a.parametros || a.datos || a.parameters || {};
  tool = map[tool] || tool;

  return {
    json: {
      accion: tool,
      datos: params
    }
  };
});

console.log(JSON.stringify(result, null, 2));
