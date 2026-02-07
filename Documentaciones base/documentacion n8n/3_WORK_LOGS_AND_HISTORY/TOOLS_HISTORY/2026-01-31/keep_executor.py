import gkeepapi
import sys
import json

# CONFIGURACIÓN
USERNAME = 'tu_correo@gmail.com'
PASSWORD = 'tu_app_password'

keep = gkeepapi.Keep()
keep.login(USERNAME, PASSWORD)

# El agente enviará el código como el primer argumento
code_from_agent = sys.argv[1]

# Inyectamos el objeto 'keep' y 'gkeepapi' para que el agente los use
context = {
    'keep': keep,
    'gkeepapi': gkeepapi,
    'json': json,
    'result': None # Aquí guardaremos la salida
}

try:
    # Ejecutamos el código generado por la IA
    exec(code_from_agent, context)
    # Devolvemos lo que la IA haya guardado en 'result'
    print(json.dumps(context.get('result', "Ejecución exitosa sin retorno")))
except Exception as e:
    print(json.dumps({"error": str(e)}))
