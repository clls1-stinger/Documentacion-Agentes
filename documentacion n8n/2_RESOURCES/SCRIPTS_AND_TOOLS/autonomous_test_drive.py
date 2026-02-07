#!/usr/bin/env python3
"""
⭐ VEGA - Autonomous Test Script (Drive V3 Connection Fix)
- Modified to test the Google Drive V3 Search fix.
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

TEST_MESSAGE = "Busca en mi Google Drive archivos que contengan takeout y dime cuántos encuentras."

async def main():
    browser = None
    try:
        print("▶️ [DRIVE_TEST] Lanzando navegador...")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1366, 'height': 768})
        print("✅ [DRIVE_TEST] Navegador lanzado.")
        
        # --- LINEAR LOGIN ---
        print(f"▶️ [DRIVE_TEST] Navegando a n8n: {N8N_URL}")
        await page.goto(N8N_URL, {'waitUntil': 'networkidle2', 'timeout': 30000})
        
        print("... [DRIVE_TEST] Esperando formulario de login...")
        await page.waitForSelector('#email', {'timeout': 15000})
        
        print("... [DRIVE_TEST] Rellenando credenciales...")
        await page.type('#email', EMAIL, {'delay': 50})
        await page.type('#password', PASSWORD, {'delay': 50})
        
        print("... [DRIVE_TEST] Enviando formulario...")
        await asyncio.gather(
            page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 30000}),
            page.click('button[type="submit"]')
        )
        print("✅ [DRIVE_TEST] Inicio de sesión completado.")

        # --- NAVIGATE TO WORKFLOW ---
        chat_url = f"{N8N_URL}workflow/{WORKFLOW_ID}"
        print(f"▶️ [DRIVE_TEST] Navegando al workflow: {chat_url}")
        await page.goto(chat_url, {'waitUntil': 'networkidle2', 'timeout': 30000})

        # --- FIND AND CLICK CHAT TAB ---
        # The selector might be dynamic, so we try multiple or wait for it
        print("... [DRIVE_TEST] Buscando tabla de Chat...")
        # Try to find the button that contains "Chat" text or specific class
        await page.waitForTimeout(5000) # Give it time to load the workflow fully
        
        # Click the chat icon in the sidebar/footer or wherever it is
        # Note: In n8n v1, chat is usually in the execution area or a separate tab
        # Based on previous script, 'div.chat-tab-button' might be it.
        chat_button_selector = '.chat-button' # Common n8n chat button
        try:
            await page.waitForSelector('.manual-chat-trigger-button', {'timeout': 10000})
            await page.click('.manual-chat-trigger-button')
            print("... [DRIVE_TEST] Clic en el botón de Chat Trigger.")
        except:
             print("... [DRIVE_TEST] Falló .manual-chat-trigger-button, probando .chat-button")
             await page.click('.chat-button')

        print("... [DRIVE_TEST] Esperando input del chat...")
        await page.waitForSelector('textarea', {'timeout': 10000})
        await page.type('textarea', TEST_MESSAGE)
        
        print("... [DRIVE_TEST] Enviando mensaje...")
        await page.keyboard.press('Enter') # Usually Enter sends it

        print("✅ [DRIVE_TEST] Mensaje enviado. Esperando 15 segundos para la ejecución...")
        await asyncio.sleep(15)
        
        print("📸 Tomando captura final para validación visual...")
        screenshot_path = '/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/drive_test_result.png'
        await page.screenshot({'path': screenshot_path, 'fullPage': True})
        print(f"✅ Captura guardada en {screenshot_path}")

    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        if 'page' in locals() and page:
            await page.screenshot({'path': '/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/drive_test_error.png'})
            print("📸 Error capturado en FORENSICS_AND_LOGS/drive_test_error.png")
        
    finally:
        if browser:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
