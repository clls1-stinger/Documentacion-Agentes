# Vega Core - Protocolo de Persistencia de Datos (v1.0)

## 1. Principio Fundamental: Preservación Absoluta
En el ecosistema Vega Core, **NINGÚN DATO SE ELIMINA FÍSICAMENTE** de la base de datos. La información es un activo acumulativo que alimenta la inteligencia del sistema y la trazabilidad histórica.

## 2. Mecanismo "Soft Delete"
Para mantener el orden visual y operativo sin destruir información, implementamos el patrón *Soft Delete*.

### Implementación Técnica
Todas las tablas críticas (`tasks`, `projects`, `snapshots`, `identities`) poseen una columna de control:

```sql
is_deleted BOOLEAN DEFAULT FALSE
```

### Reglas de Operación (CRUD)
*   **DELETE (API Level):** No ejecuta un `DELETE FROM`. Ejecuta un `UPDATE table SET is_deleted = TRUE WHERE id = ...`.
*   **READ (API Level):** Por defecto, todas las consultas filtran `WHERE is_deleted = FALSE` a menos que se solicite explícitamente el historial completo o la papelera.
*   **AUDIT:** Los datos marcados como `is_deleted = TRUE` permanecen accesibles para análisis forense, entrenamiento de modelos o restauración.

## 3. Arquitectura de Datos: Modularidad No Restrictiva
El sistema utiliza múltiples bases de datos lógicas (o esquemas) para separar contextos, pero mantiene una **interoperabilidad total**:

*   **Vega Core DB:** Metadatos, Tareas, Snapshots del Kernel.
*   *(Futuro)* **Vega Knowledge DB:** Vectores, Embeddings, Wikis.
*   *(Futuro)* **Vega User DB:** Preferencias, Perfiles extendidos.

Las APIs están autorizadas para realizar cruces de información (JOINS lógicos) entre estos dominios para generar contexto, siempre respetando el principio de no destrucción.
