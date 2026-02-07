import gkeepapi
import sys
import json

# CONFIGURACIÓN
USERNAME = 'tu_correo@gmail.com'
PASSWORD = 'tu_app_password_de_16_letras' # No es tu clave normal

keep = gkeepapi.Keep()
try:
    keep.login(USERNAME, PASSWORD)
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)

def search_notes(query):
    notes = keep.find(query=query)
    # Devolvemos ID, Título y Texto para que el agente decida qué leer
    return [{"id": n.id, "title": n.title, "text": n.text} for n in notes]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        results = search_notes(query)
        print(json.dumps(results))
