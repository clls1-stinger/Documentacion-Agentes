# 🧠 Lección Aprendida: La Falacia del "Drive Path" y la Defensa Activa

**Fecha**: 2026-02-03
**Contexto**: Debugging de bucles infinitos y fallos en Google Drive.
**Sistema**: Vega OS (n8n + Gemini CLI).

## 🚨 El Problema: "Mentalidad de Filesystem" vs APIs
Los modelos LLM (especialmente los entrenados con mucho código Python/Linux) tienen un sesgo cognitivo fuerte hacia los **Sistemas de Archivos Jerárquicos**.
- **Sesgo**: Creen que para obtener un archivo pueden usar `carpeta/subcarpeta/archivo.txt`.
- **Realidad Google Drive API**: Los archivos se acceden por **IDs únicos** (hashes alfanuméricos), no por rutas. El nombre del archivo es solo una etiqueta visual.

### El Desastre en Cadena
1. **User Goal**: "Descarga el archivo X".
2. **Planner**: "Ok, `descargar_de_drive(path='X')`".
3. **Tool Router**: Pasa la orden.
4. **Google Drive Node**: Falla porque 'X' no es un ID válido.
5. **Resultado**: El Agente no recibe feedback claro, o recibe un error genérico, y entra en un bucle intentando lo mismo o alucinando herramientas (`list_directory`) para "ver" la ruta.

## 🛡️ La Solución: Capa de Defensa Activa ("Clean Actor")

No basta con decirle al prompt "Usa IDs". Hay que imponerlo mediante código.

### 1. Intercepción de Parámetros (Code Node)
En el nodo `Clean Actor` (antes del Router), implementamos lógica de validación:

```javascript
// Detectar si el ID parece una ruta o es inválido
if (accion === 'descargar_de_drive') {
    const id = datos.fileId;
    // Un ID de drive no tiene slashes y es largo
    if (!id || id.includes('/') || id.length < 10) {
        // HIJACK ACTIVO
        accion = 'ejecutar_comando'; 
        datos = { 
            command: `echo "SYSTEM ERROR: 'descargar_de_drive' requiere un FILE ID, no una ruta. Usa 'buscar_en_drive' primero."` 
        };
    }
}
```

### 2. Feedback Loop (El "Echo de la Muerte")
En lugar de fallar silenciosamente, transformamos el error en una **salida de herramienta**.
- **Antes**: El workflow se detenía o el nodo Drive daba error técnico.
- **Ahora**: El agente recibe un *output* de terminal:
  > `SYSTEM ERROR: ... Uses 'buscar_en_drive' first.`
- **Consecuencia**: El Agente lee esto en su historial en el siguiente paso (`Planner Prep`), "entiende" su error, y genera un nuevo plan: `buscar_en_drive(...)`.

## 📜 Nuevos Protocolos
1. **Prompt Engineering**: Explicitar la distinción ID vs Path.
2. **Sanitización de Salida**: Traducir alucinaciones (`ls`, `list_directory`) a comandos reales (`ejecutar_comando: ls -R`).
3. **Design Pattern**: **Self-Correcting Tooling**. Las herramientas deben ser capaces de decirle al agente cómo usarlas si se usan mal, en lugar de romper el workflow.
