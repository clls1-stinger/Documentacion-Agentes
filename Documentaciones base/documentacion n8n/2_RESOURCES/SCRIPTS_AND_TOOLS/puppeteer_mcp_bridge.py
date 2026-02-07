#!/usr/bin/env python3
"""
🌐 PUPPETEER MCP BRIDGE FOR N8N
Este script actúa como puente entre n8n y el servidor Puppeteer MCP,
utilizando la librería mcp-client para la comunicación.

USO:
    /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/.venv_mcp/bin/python \
        /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py \
        navigate "https://example.com"

    /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/.venv_mcp/bin/python \
        /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py \
        screenshot "https://example.com" "screenshot_name"

    /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/.venv_mcp/bin/python \
        /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py \
        click "selector"

    /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/.venv_mcp/bin/python \
        /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py \
        fill "selector" "text"

    /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/.venv_mcp/bin/python \
        /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py \
        get_text "selector"
"""

import sys
import json
import subprocess
from mcp_client import Client # Import the MCP client library

def call_mcp(tool_name, args):
    """
    Llama al servidor MCP de Puppeteer usando el cliente MCP.
    Asume que el servidor `chrome-devtools-mcp` está ejecutándose y
    conectado a la instancia de Brave en debug mode.
    """
    try:
        # Conectar al servidor MCP 'puppeteer'.
        # Por defecto, mcp-client buscará el servidor a través de stdin/stdout
        # o un socket local si se ha configurado así el servidor.
        client = Client("puppeteer")
        
        # Realizar la llamada a la herramienta específica en el servidor MCP
        response = client.call(tool_name, args)
        
        # El objeto response de mcp_client tiene un atributo 'result'
        # que contiene la respuesta del servidor.
        return {"success": True, "result": response.result}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": tool_name,
            "args": args,
            "message": "Error al comunicar con el servidor MCP. Asegúrate de que 'chrome-devtools-mcp' esté ejecutándose."
        }

def navigate(url):
    return call_mcp("navigate", {"url": url})

def screenshot(url, name):
    # La API de MCP para screenshot probablemente solo necesite el nombre,
    # el URL se manejaría con una navegación previa.
    # Necesitamos consultar la API real del servidor chrome-devtools-mcp.
    # Por ahora, pasamos ambos.
    return call_mcp("screenshot", {"url": url, "name": name})

def click(selector):
    return call_mcp("click", {"selector": selector})

def fill(selector, text):
    return call_mcp("fill", {"selector": selector, "value": text})

def get_text(selector):
    return call_mcp("get_text", {"selector": selector})

if __name__ == "__main__":
    # Asegurarse de que estamos usando el python del venv
    # Se añade esto al inicio del script para asegurar que el path es el correcto.
    # Sin embargo, el script debería ser ejecutado con el intérprete del venv.
    # Por ejemplo: /path/to/venv/bin/python script.py

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Comando no especificado",
            "usage": "python3 puppeteer_mcp_bridge.py <command> [args...]"
        }, indent=2))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "navigate":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "URL requerida"}, indent=2))
            sys.exit(1)
        result = navigate(sys.argv[2])
    
    elif command == "screenshot":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "URL y nombre requeridos"}, indent=2))
            sys.exit(1)
        result = screenshot(sys.argv[2], sys.argv[3])
    
    elif command == "click":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Selector requerido"}, indent=2))
            sys.exit(1)
        result = click(sys.argv[2])
    
    elif command == "fill":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Selector y texto requeridos"}, indent=2))
            sys.exit(1)
        result = fill(sys.argv[2], sys.argv[3])
    
    elif command == "get_text":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Selector requerido"}, indent=2))
            sys.exit(1)
        result = get_text(sys.argv[2])
    
    else:
        result = {"error": f"Comando desconocido: {command}"}
    
    print(json.dumps(result, indent=2))