#!/usr/bin/env python3
"""
⭐ VEGA - Autonomous Test Script v9 (Linear Approach)
- Abandons conditional login logic.
- Assumes a logged-out state and performs the login sequence linearly.
"""

import asyncio
from pyppeteer import launch
import sys

# --- CONFIGURATION ---
N8N_URL = "http://localhost:5678/"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

# Credentials from N8N_ACCESS_CREDENTIALS.md
EMAIL = "howtosnapside@gmail.com"
PASSWORD = "Gaming9-Wifi6-Waking4-Getting4-Stream0"

TEST_MESSAGE = "Navega a https://www.google.com y dime si la página carga correctamente."

async def main():
    browser = None
    try:
        print("▶️ [V9] Lanzando navegador...")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1366, 'height': 768})
        print("✅ [V9] Navegador lanzado.")
        
        # --- LINEAR LOGIN ---
        print(f"▶️ [V9] Navegando a n8n: {N8N_URL}")
        await page.goto(N8N_URL, {'waitUntil': 'networkidle2', 'timeout': 30000})
        
        print("... [V9] Esperando formulario de login...")
        await page.waitForSelector('#email', {'timeout': 15000})
        
        print("... [V9] Rellenando credenciales...")
        await page.type('#email', EMAIL, {'delay': 50})
        await page.type('#password', PASSWORD, {'delay': 50})
        
        print("... [V9] Enviando formulario...")
        await asyncio.gather(
            page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 30000}),
            page.click('button[type="submit"]')
        )
        print("✅ [V9] Inicio de sesión completado.")

        # --- NAVIGATE TO CHAT ---
        chat_url = f"{N8N_URL}workflow/{WORKFLOW_ID}"
        print(f"▶️ [V9] Navegando al workflow: {chat_url}")
        await page.goto(chat_url, {'waitUntil': 'networkidle2', 'timeout': 30000})

        chat_button_selector = 'div.chat-tab-button' # Using a potentially more stable selector
        print(f"... [V9] Esperando por el botón de chat: {chat_button_selector}")
        await page.waitForSelector(chat_button_selector, {'timeout': 30000})
        await page.click(chat_button_selector)
        print("... [V9] Clic en el botón de Chat.")

        chat_input_selector = 'textarea'
        print(f"... [V9] Esperando por el input del chat: {chat_input_selector}")
        await page.waitForSelector(chat_input_selector, {'timeout': 10000})
        await page.type(chat_input_selector, TEST_MESSAGE)
        
        send_button_selector = 'button[aria-label="Send message"]'
        print(f"... [V9] Esperando por el botón de envío: {send_button_selector}")
        await page.waitForSelector(send_button_selector)
        await page.click(send_button_selector)

        print("✅ [V9] Mensaje de prueba enviado de forma autónoma.")
        print("ℹ️ Ahora procederé a revisar los logs para el resultado del diagnóstico.")

    except Exception as e:
        print(f"❌ ERROR: Falló el script de autotest.", file=sys.stderr)
        print(f"   Detalle: {e}", file=sys.stderr)
        if 'page' in locals() and page:
            try:
                await page.screenshot({'path': '/home/emky/error_screenshot.png'})
                print("📸 Se ha guardado una captura de pantalla del error en /home/emky/error_screenshot.png")
            except Exception as e_ss:
                print(f"   No se pudo tomar captura de pantalla: {e_ss}", file=sys.stderr)
        
    finally:
        if browser:
            print("▶️ Cerrando el navegador.")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
