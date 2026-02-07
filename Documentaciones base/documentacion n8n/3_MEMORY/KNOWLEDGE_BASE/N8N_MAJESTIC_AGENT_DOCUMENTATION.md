# Documentación del Agente Majestuoso (Vega) en n8n

## Arquitectura "Cerebro-Actor"
Hemos aprendido que separar la lógica en dos etapas mejora significativamente la fiabilidad:

1.  **Planner (Cerebro Master)**:
    *   **Modelo**: Gemini 1.5 Pro (o 2.0 Pro).
    *   **Función**: Analizar el historial, decidir la estrategia y delegar instrucciones claras. NO ejecuta acciones directamente (excepto responder al chat).
    *   **Salida**: JSON con `{ thought, next_instruction, is_done, final_response }`.

2.  **Actor (Ejecutor Técnico)**:
    *   **Modelo**: Gemini 2.5 Flash (Rápido y barato).
    *   **Función**: Traducir la `next_instruction` del Planner a una llamada de herramienta concreta (API Google Drive, Bash, etc.).
    *   **Salida**: JSON con `{ accion, datos }`.

## Patrones de Diseño Implementados

### 1. El Bucle Infinito (Controlado)
Usamos un nodo `Loop Merge` que recibe dos entradas:
-   **Inicio**: Desde el Trigger del Chat.
-   **Recursión**: Desde el final del flujo (`Wait` -> `Loop Merge`).
Esto permite que el agente "piense" y "actúe" múltiples veces para una sola solicitud del usuario hasta que decide terminar (`is_done: true`).

### 2. Gestión de Memoria
*   **Corto Plazo**: Pasamos el objeto `json` completo de nodo a nodo, enriqueciéndolo con `history` (pasos técnicos de la sesión actual).
*   **Largo Plazo**: Leemos y escribimos en `/home/emky/n8n/history.json`. Esto permite al agente recordar conversaciones pasadas.

### 3. Resiliencia en Parsing
Gemini a veces "habla" antes de enviar el JSON. Hemos aprendido a usar bloques `try/catch` en nodos de Código y regex para extraer JSONs válidos de respuestas "sucias".

## Lecciones Aprendidas (Bitácora)
*   **Contexto es Rey**: Sin pasar el historial de chat *y* el historial de acciones (tool outputs), el agente se pierde en bucles.
*   **Separa Acciones**: Intentar que el Planner genere el comando exacto de `curl` o `bash` a menudo falla. Es mejor que el Planner diga "Lista los archivos del directorio X" y el Actor (Flash) escriba el comando `ls -la X`.
*   **Feedback Loops**: El agente debe "ver" el resultado de sus acciones. El nodo `Aggregator` es crucial para alimentar el resultado de la herramienta de vuelta al contexto del Planner.

---
*Generado por Vega (v2026)*
