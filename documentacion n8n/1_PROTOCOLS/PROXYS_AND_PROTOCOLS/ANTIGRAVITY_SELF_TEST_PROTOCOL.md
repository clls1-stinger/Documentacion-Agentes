# 🧪 PROTOCOLO DE AUTO-TESTING (VEGA)

Este protocolo permite que Vega valide sus propios cambios sin intervención humana.

## 🛠️ Herramientas
- **Puppeteer MCP**: Para interactuar con la interfaz de n8n.
- **SQL Scripts**: Para verificar el estado de la ejecución en la DB.
- **History.json**: Para validar la respuesta final entregada al usuario.

## 🔄 El Ciclo de Validación
1. **Trigger**: Enviar un mensaje de chat simulado vía Puppeteer o API.
2. **Watch**: Monorear el nodo `Is Done Switch` en la base de datos.
3. **Verify**: Comprobar si se ejecutaron las herramientas esperadas (Drive Search, etc.).
4. **Iterate**: Si el ruteo falla, aplicar un parche correctivo y repetir.

## 📝 Caso de Prueba: Google Takeout
Input: "baja mis archivos takeout"
Resultado esperado:
- El `Gemini Planner` debe devolver `is_done: false`.
- El `Tool Router` debe activar el nodo `Drive Search`.
- El flujo NO debe terminar con "(Agent finished without text response)".

---
*Documento generado por Vega para la posteridad.*
