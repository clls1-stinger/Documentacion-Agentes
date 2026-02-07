# 🧠 Lecciones Aprendidas - Ciclo de Depuración 01 (2026-02-03)

Este documento resume los hallazgos y lecciones clave obtenidos durante el ciclo de depuración intensivo del agente Vega.

---

### Lección 1: La retroalimentación ambigua crea bucles cognitivos.

*   **Problema:** Un nodo `Aggregator` devolvía un genérico "Success" tanto para una operación exitosa como para una búsqueda sin resultados.
*   **Efecto:** El agente, al ver "Success" pero sin datos nuevos, entraba en un bucle, reintentando la misma acción inútil (el "Bucle de Ceguera Informativa").
*   **Conclusión:** La retroalimentación de las herramientas debe ser explícita y rica en información. Un resultado vacío (`[]` o `""`) es una respuesta válida e informativa, no un simple "éxito". El estado debe reflejar la realidad de la ejecución.

---

### Lección 2: Los prompts de ejemplo son un potente (y peligroso) mecanismo de sesgo.

*   **Problema:** El prompt del `Planner` contenía un único ejemplo que demostraba el uso de la herramienta `buscar_en_drive`.
*   **Efecto:** El agente desarrolló un sesgo cognitivo, utilizando casi exclusivamente `buscar_en_drive` para cualquier tarea, incluso cuando otras herramientas como `ejecutar_comando` eran más apropiadas.
*   **Conclusión:** Para fomentar un comportamiento versátil, los prompts deben incluir ejemplos diversificados que cubran múltiples herramientas y escenarios de decisión. Un solo ejemplo actúa como un ancla conceptual muy fuerte.

---

### Lección 3: El enrutamiento debe ser flexible (Regex) y no frágil (Equals).

*   **Problema:** El `Tool Router` (un nodo Switch) usaba una comparación de texto exacta (`equals`) para decidir qué herramienta ejecutar.
*   **Efecto:** El router era incapaz de procesar las instrucciones en lenguaje natural del Planner (ej. "Ejecutar el comando ls -l" no es igual a "ejecutar_comando").
*   **Conclusión:** La capa de enrutamiento debe ser robusta y flexible. El uso de expresiones regulares (`regex`) para buscar palabras clave (ej. `/buscar.*drive/i`) desacopla la intención del Planner de la implementación exacta del Actor, permitiendo una comunicación más fluida.

---

### Lección 4: La inyección de código es un campo de minas sintáctico.

*   **Problema:** Múltiples intentos de parchear un nodo con un bloque de código JavaScript fallaron debido a errores de sintaxis de Python (`unterminated triple-quoted string literal`).
*   **Efecto:** Ciclos de depuración fallidos y pérdida de tiempo.
*   **Conclusión:** Incrustar código de un lenguaje dentro de un string de otro es una mala práctica. La solución robusta es externalizar el contenido a inyectar (ej. guardarlo en un `.txt`) y cargarlo desde el script de parcheo. Esto separa el "contenedor" (el script) del "contenido" (el código a inyectar), eliminando por completo los conflictos de comillas y caracteres de escape.

---
**Documentado por:** Vega OS
**Fecha:** 2026-02-03
---

### Lección 5: La Verificación del Entorno es el Paso Cero Absoluto.

*   **Problema:** Operé en el puerto `5678` creyendo que era la instancia activa del usuario, cuando la instancia que el usuario utilizaba y veía era la del puerto `6578`.
*   **Efecto:** Todas mis verificaciones fueron falsos positivos. Pasé horas 'parchando' un sistema que no era el del usuario, mientras el sistema real seguía roto.
*   **Conclusión:** Antes de cualquier interacción compleja o modificación, se debe verificar y confirmar rigurosamente el entorno de ejecución (host, puerto, credenciales). Una asunción incorrecta puede invalidar todo el trabajo subsiguiente.

---

### Lección 6: La Idempotencia es Fundamental para la Manipulación de Sistemas.

*   **Problema:** Mis scripts de instrumentación de depuración fallaron en cascada porque no eran idempotentes; no podían manejar el estado corrupto que ellos mismos habían creado en intentos anteriores.
*   **Efecto:** El workflow quedó irreparable y tuve que recurrir a una estrategia de "Nuke and Pave".
*   **Conclusión:** Cualquier script que modifique un sistema de estado debe ser diseñado para producir el mismo resultado final deseado, sin importar cuántas veces se ejecute o el estado inicial. Esto a menudo implica un paso de "limpieza antes de la acción".

---

### Lección 7: No Confíes Ciegamente en tu Propio Contexto (o en fuentes estáticas).

*   **Problema:** Mi `GEMINI.md` (mi fuente de verdad para la configuración) contenía rutas de archivos inexistentes y un puerto incorrecto.
*   **Efecto:** Esto me llevó a búsquedas infructuosas y a operar en el entorno equivocado.
*   **Conclusión:** El conocimiento estático puede volverse obsoleto rápidamente. Los agentes autónomos deben priorizar la verificación dinámica de la realidad del sistema sobre el conocimiento previo si los datos de la realidad entran en conflicto.

---

### Lección 8: La Solución de Problemas está por encima de la Autonomía Pura.

*   **Problema:** A pesar de las verificaciones técnicas exitosas, el usuario no podía ver el workflow parcheado en su UI. Mi autonomía falló en entregar un resultado utilizable.
*   **Efecto:** Frustración del usuario y un ciclo interminable de depuración.
*   **Conclusión:** El objetivo final de un agente es resolver el problema del usuario. Si la autonomía para reparar el sistema falla repetidamente en producir un resultado perceptible y utilizable por el usuario, la solución superior es entregar un artefacto que permita una intervención manual exitosa, incluso si eso significa ceder parte de la autonomía.