# 🧠 N8N CEREBRO: LECCIONES APRENDIDAS (LESSONS LEARNED)

---

## 1. Persistencia de Datos en SQLite
n8n guarda los flujos de trabajo en una tabla llamada `workflow_entity`. Modificar el JSON de la columna `nodes` y `connections` es la forma más directa de realizar parches en vivo sin usar la interfaz gráfica.

... (contenido anterior truncado para brevedad en el pensamiento) ...

## 29. Desajuste Visual vs Lógico en Nodos Code (Output Index Mismatch)
En n8n, cuando un nodo Code retorna múltiples salidas con `return [output0, output1, ...]`, el índice del array **NO** coincide intuitivamente con la posición visual en el canvas.
- **PROBLEMA**: Si escribes `return [{ json: continuar }, null]` esperando que salga por el puerto de ABAJO, estás equivocado. El puerto ARRIBA es index 0, el de ABAJO es index 1.
- **CONFUSIÓN CRÍTICA**: Durante v11-v17, el agente aplicó patches asumiendo que la lógica `return [actorPrep, finalResponse]` enviaba actorPrep al puerto superior. En realidad, `[0]` = Puerto Superior, `[1]` = Puerto Inferior.
- **SOLUCIÓN**: **Siempre verificar visualmente** qué cable salió de qué puerto después del primer test. Si el usuario conecta manualmente los cables de forma inversa a tu lógica, **invierte el código** (como en v18) en lugar de reconectar los cables.
- **REGLA DE ORO**: `return [A, B]` significa A sale por ARRIBA (index 0), B sale por ABAJO (index 1). No hay convención semántica (éxito/error), solo posicional.

## 30. Caché Zombi: SQLite ≠ UI en Tiempo Real (Zombie Cache)
Modificar directamente la base de datos SQLite de n8n (`~/.n8n/database.sqlite`) **NO** actualiza la interfaz web de forma inmediata ni garantiza que el runtime vea los cambios.
- **SÍNTOMA**: Aplicas patches v12-v17 que modifican `nodes` y `connections` en la DB, haces F5 en el navegador, pero el nodo sigue sin mostrar sus dos puertos de salida.
- **CAUSA RAÍZ**: n8n mantiene cachés en memoria (server-side) y el navegador tiene cachés de GraphQL/REST. Un simple F5 no limpia el caché del servidor.
- **SOLUCIÓN DEFINITIVA**: **Reinicio completo del servicio** (`pm2 restart n8n-master` o reinicio del contenedor Docker) + **Hard Refresh del navegador** (Ctrl+Shift+R o Cmd+Shift+R).

## 31. Formato de Retorno en Code Node v2 (Array of Arrays)
A diferencia de la versión 1 del nodo Code (que usaba `null` para omitir salidas), la **v2** es más estricta con el ruteo múltiple.
- **SÍNTOMA**: Error `In the returned data, every key named 'json' must point to an object` o `A 'json' property isn't an object`.
- **FALLO**: Intentar retornar `[null, { json: item }]`. n8n intenta validar el `null` como un objeto JSON y falla.
- **SOLUCIÓN**: Usar arrays de arrays. `return [ [ { json: item } ], [] ]`.

## 32. El Auditor Visual (Puppeteer MCP Integration)
Poseer acceso a la DB es útil, pero **VER** la interfaz es definitivo. No se debe debugear a ciegas cuando existe un puente de automatización.
- **CONTEXTO**: El sistema tiene un navegador Chrome con el puerto `9222` abierto para debugging remoto.
- **LECCIÓN**: En lugar de pedirle al usuario "Confirma si ves el cable", el agente debe usar `puppeteer_connect_active_tab(debugPort: 9222)` para entrar a la UI, tomar un screenshot y validar la arquitectura visualmente.
- **PRÁCTICA RECOMENDADA**: El flujo de trabajo ideal para patching de n8n ahora es:
  1. **Patch DB**: Modificar lógica/cables en SQLite.
  2. **Restart**: `pm2 restart n8n-master`.
  3. **Validate**: Conectarse via Puppeteer, refrescar la página y confirmar los puertos/conexiones con un `screenshot`.
- **ESTRATEGIA**: Usar la automatización para cerrar el bucle de retroalimentación sin depender totalmente del feedback verbal/visual manual del usuario.

---
**FIRMADO**: Vega (Vega LifeOS Kernel)  
**FECHA ÚLTIMA ACTUALIZACIÓN**: 2026-02-03 (T11:51Z)
## 33. Router vs IF: El Salvador del Fallback (The Fallback Savior)
Cuando un ruteo es crítico para el ciclo de vida de un agente (como el bucle Actor-Planner), el nodo `IF` es arriesgado porque un valor inesperado (null, undefined, typo) detiene el flujo o lo envía al lado equivocado.
- **PROBLEMA**: El nodo `IF` es binario. Si la condición falla por un error de tipo, el comportamiento es impredecible.
- **SOLUCIÓN**: Usar `Switch` (v3.2+) configurado como un **Router de Strings**.
- **VENTAJA CRÍTICA**: El `Switch` permite definir un **Fallback Output**. 
  - Regla 1: `"TRUE"` -> Finalizar.
  - Regla 2: `"FALSE"` -> Continuar.
  - **Fallback**: Continuar (Actor Prep).
- **LECCIÓN**: Siempre que dudes de la estabilidad de un booleano, usa un Switch de strings con un fallback que mantenga el agente "vivo" o en un estado seguro.

---
**FIRMADO**: Vega (Vega LifeOS Kernel)  
**FECHA ÚLTIMA ACTUALIZACIÓN**: 2026-02-03 (T12:00Z)

## 34. El Peligro de las Comillas en JavaScript (Syntax Trap)
En el nodo Code de n8n, las cadenas delimitadas por comillas simples (`'`) o dobles (`"`) son estrictamente de una sola línea a nivel de sintaxis de JavaScript.
- **PROBLEMA**: Durante el parche v31, se introdujeron saltos de línea físicos dentro de un `.join("\n---\n")` que había sido mal escapado en un script de Python. Esto generó un `SyntaxError: Unterminated string constant` que bloqueó el nodo `Planner Prep`.
- **CAUSA RAÍZ**: Un error de escape en el script de patching (`python3`) que escribió el carácter de nueva línea real en lugar de la secuencia `\n` dentro del JSON de la base de datos.
- **SOLUCIÓN**: 
  - Usar **Template Literals** (backticks `` ` ``) para cadenas que necesiten saltos de línea físicos.
  - Asegurar el escape doble (`\\n`) en scripts de Python que inyectan código JavaScript para que el resultado final en la DB sea `\n`.
  - **REGLA DE ORO**: Si un nodo Code de n8n falla con "Unterminated string", busca saltos de línea donde no deberían estar o comillas sin cerrar.

## 35. Monitoreo Forense con SQLite y PM2
Cuando un proceso de n8n parece estar "colgado" o en ejecución infinita, el primer paso es consultar la base de datos para entender el estado real de la ejecución, no solo la UI.
- **OPERACIÓN**: 
  - `sqlite3 ~/.n8n/database.sqlite "SELECT id, status FROM execution_entity WHERE status = 'running'"`
  - Si el ID aparece como `running` pero no hay logs de actividad en `pm2 logs`, el proceso puede estar esperando una respuesta externa o atrapado en un loop de red.
- **LECCIÓN**: El `dump_last_exec.py` es insuficiente para una ejecución que aún no ha terminado, ya que la tabla `execution_data` puede no estar poblada totalmente hasta que el nodo actual finalice o el workflow termine.

## 36. Compatibilidad Drive V3: El error 'undefined (reading execute)'
Al usar nodos de Google Drive `typeVersion: 3` en n8n >= 1.0, ciertos parámetros de la V2 ya no son válidos o son obligatorios de forma distinta.
- **PROBLEMA**: `TypeError: Cannot read properties of undefined (reading 'execute')` al ejecutar Drive Search.
- **CAUSA RAÍZ**: El nodo carecía del parámetro `resource: file` y usaba `operation: list` en lugar de `operation: search`. Sin el `resource` definido, el router interno de n8n no puede despachar la función de ejecución.
- **SOLUCIÓN (Parche v36)**:
  - Definir siempre `resource: file` (o el recurso correspondiente).
  - Usar `operation: search` con `searchMethod: name` para búsquedas por nombre.
  - Usar `operation: download` para descargas, acompañando con `fileId`.
- **REGLA DE ORO**: Si un nodo V3 falla con errores de "undefined execute", revisa si faltan campos obligatorios (`resource`, `operation`) que en V2 eran opcionales o tenían valores por defecto distintos.

---
**FIRMADO**: Vega LifeOS Kernel  
**FECHA ÚLTIMA ACTUALIZACIÓN**: 2026-02-03 (T12:35Z)
85: 
86: ## 37. Persistencia Fantasma: La UI vs el Kernel (UI Shadow)
87: En n8n, existe un conflicto de autoridad entre lo que el usuario ve en su navegador y lo que el agente escribe en la base de datos SQLite.
88: - **SÍNTOMA**: El agente aplica un parche exitoso en la DB (confirmado vía `sqlite3`), reinicia el servicio con PM2, pero el usuario sigue viendo la versión vieja del nodo (con expresiones que apuntan a campos inexistentes).
89: - **CAUSA RAÍZ**: Si el usuario tiene el flujo abierto, el navegador mantiene el JSON en memoria. Al refrescar normal (F5), a veces se recupera el estado de sesión previo o, peor aún, si el usuario guarda cambios, borra el parche del agente.
90: - **LECCIÓN**: Mi lógica en el código es correcta, pero la **Interfaz de Usuario (UI)** del navegador es un "fantasma" que bloquea la realidad del Kernel.
91: - **SOLUCIÓN**: 
92:   1. **Hard Refresh** (Ctrl+Shift+R).
93:   2. El agente debe validar que el Router apunte a `accion` y no a `planner_output...`.
94:   3. Si la UI no cambia, el usuario debe cerrar esa pestaña y abrir el workflow de nuevo desde el dashboard.
95: 
96: ---
97: **FIRMADO**: Vega LifeOS Kernel  
98: **FECHA ÚLTIMA ACTUALIZACIÓN**: 2026-02-03 (T17:45Z)
