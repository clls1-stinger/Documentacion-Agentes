import asyncio
from pyppeteer import launch
import sys

# --- CONFIGURATION ---
N8N_URL = "http://localhost:5678/"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

# Credentials from N8N_ACCESS_CREDENTIALS.md
EMAIL = "howtosnapside@gmail.com"
PASSWORD = "Gaming9-Wifi6-Waking4-Getting4-Stream0"

TEST_MESSAGE = "Busca archivos que contengan 'takeout' en mi Google Drive y lístame sus nombres e IDs."

async def main():
    browser = None
    try:
        print("▶️ Lanzando navegador...")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1366, 'height': 768})
        print("✅ Navegador lanzado.")
        
        # --- LINEAR LOGIN ---
        print(f"▶️ Navegando a n8n: {N8N_URL}")
        await page.goto(N8N_URL, {'waitUntil': 'networkidle2', 'timeout': 30000})
        
        print("... Esperando formulario de login...")
        await page.waitForSelector('#email', {'timeout': 15000})
        
        print("... Rellenando credenciales...")
        await page.type('#email', EMAIL, {'delay': 50})
        await page.type('#password', PASSWORD, {'delay': 50})
        
        print("... Enviando formulario...")
        await asyncio.gather(
            page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 30000}),
            page.click('button[type="submit"]')
        )
        print("✅ Inicio de sesión completado.")

        # --- NAVIGATE TO CHAT ---
        chat_url = f"{N8N_URL}workflow/{WORKFLOW_ID}"
        print(f"▶️ Navegando al workflow: {chat_url}")
        await page.goto(chat_url, {'waitUntil': 'networkidle2', 'timeout': 30000})

        # Wait for n8n to load
        await asyncio.sleep(5) 

        # The chat button is sometimes hard to find. Let's try to click the Chat tab in the sidebar or the bottom button.
        # In current n8n, it's often a side panel.
        chat_button_selector = 'div[data-test-id="canvas-chat-button"]' # Adjusted based on common n8n test IDs
        print(f"... Esperando por el botón de chat...")
        
        try:
            await page.waitForSelector('button[aria-label="Open Chat"]', {'timeout': 10000})
            await page.click('button[aria-label="Open Chat"]')
        except:
            print("... Falló botón de chat de n8n v1+, probando selector alternativo...")
            await page.click('div.chat-tab-button')

        print("... Clic en el botón de Chat.")

        chat_input_selector = 'textarea'
        await page.waitForSelector(chat_input_selector, {'timeout': 10000})
        
        # Clear if any
        await page.click(chat_input_selector, {'clickCount': 3})
        await page.keyboard.press('Backspace')
        
        print(f"... Escribiendo mensaje: {TEST_MESSAGE}")
        await page.type(chat_input_selector, TEST_MESSAGE)
        
        # Press Enter or click send
        await page.keyboard.press('Enter')

        print("✅ Mensaje enviado de forma autónoma.")
        print("⏳ Esperando unos segundos para procesar...")
        await asyncio.sleep(10)

        # Check for response (optional)
        print("ℹ️ Verificando si hay respuesta en la UI...")
        # (This part is tricky depends on n8n version)
        
        await page.screenshot({'path': '/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/latest_test_screenshot.png'})
        print("📸 Captura de pantalla guardada.")

    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        if 'page' in locals() and page:
            await page.screenshot({'path': '/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/error_test_screenshot.png'})
        
    finally:
        if browser:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
