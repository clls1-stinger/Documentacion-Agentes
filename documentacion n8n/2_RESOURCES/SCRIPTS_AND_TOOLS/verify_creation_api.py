#!/usr/bin/env python3
"""
✅ Verify n8n Workflow Creation via API

Este script utiliza la API de n8n para listar los workflows y verificar
que el nuevo workflow parcheado ha sido creado e insertado correctamente.
"""

import requests
import json
import sys
from pathlib import Path

# --- Configuración ---
N8N_API_URL = "http://localhost:5678/api/v1/workflows"
N8N_API_KEY = "n8n_api_85508494b4e6a15470d133695b9e4ab21198fff0821d325d9b190c3e76861585b84d63474a642e8f" # Proporcionada por el usuario
TARGET_WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def main():
    print(f"✅ Verificando la creación del workflow '{TARGET_WORKFLOW_NAME}' vía API...")
    
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY
    }

    try:
        response = requests.get(N8N_API_URL, headers=headers)
        response.raise_for_status() # Lanza un error para códigos de estado HTTP incorrectos
        
        workflows = response.json()
        
        found = False
        print("\n--- Workflows encontrados en n8n: ---")
        for wf in workflows['data']:
            print(f"- ID: {wf.get('id')} | Nombre: {wf.get('name')} | Activo: {wf.get('active')}")
            if wf.get('name') == TARGET_WORKFLOW_NAME:
                found = True
        print("------------------------------------")

        if found:
            print(f"\n✅ ¡ÉXITO! El workflow '{TARGET_WORKFLOW_NAME}' ha sido encontrado en n8n.")
        else:
            print(f"\n❌ FALLO: El workflow '{TARGET_WORKFLOW_NAME}' NO fue encontrado en n8n.")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error de conexión a la API de n8n: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"\n❌ Error al decodificar la respuesta JSON de la API. Respuesta: {response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
