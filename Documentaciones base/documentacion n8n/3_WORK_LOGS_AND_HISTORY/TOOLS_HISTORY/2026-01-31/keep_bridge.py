import os
import gkeepapi
import sys
import json

def execute():
    # Lee las credenciales del sistema
    user = 'enriquepl90@gmail.com'
    password = 'hkudkogcxqlojeyl'

    keep = gkeepapi.Keep()
    try:
        # CAMBIO ÓPTIMO: authenticate en lugar de login
        keep.authenticate(user, password)

        # Procesa los argumentos del agente
        arg = json.loads(sys.argv[1])
        action = arg.get('action', 'search')

        if action == 'search':
            notes = keep.find(query=arg.get('query', ''))
            # Retornamos una lista de diccionarios
            return [{"id": n.id, "title": n.title, "text": n.text} for n in notes]

    except Exception as e:
        # Esto captura el BadAuthentication que vimos
        return {"error": str(e)}

if __name__ == "__main__":
    print(json.dumps(execute()))
