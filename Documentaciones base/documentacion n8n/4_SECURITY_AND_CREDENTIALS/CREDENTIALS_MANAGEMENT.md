# Protocolo de Gestión de Credenciales y Sanitización

Este documento establece las bases para el manejo seguro de secretos y la limpieza del entorno ("Sanitización de la Zona Principal"), un pilar fundamental del sistema Antigravity.

## Gestión de Secretos (GitHub PAT)

Para el respaldo del sistema el 4 de febrero de 2026, se ha generado un Personal Access Token (PAT) de GitHub.

- **Ubicación del Secreto**: El token se maneja a nivel de entorno de ejecución y no se hardcodea en scripts.
- **Acceso para LLMs**: Este token permite a los agentes realizar backups automáticos y gestionar el repositorio de recuperación.
- **Identidad del Token**: `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` (Nota: En sistemas de producción real, este valor debería rotarse periódicamente).

## Sanitización de la Zona Principal (The Core Pillar)

La sanitización no es solo borrar archivos; es asegurar que el "Cerebro" del sistema esté libre de ruido, datos temporales corruptos y configuraciones obsoletas que puedan confundir a los agentes o causar fallos en cascada.

### ¿Por qué lo hacemos?
1.  **Reducción de Alucinaciones**: Los agentes operan mejor en entornos limpios y bien estructurados.
2.  **Prevención de Errores en Cascada**: Un archivo `.tmp` o un log gigante puede bloquear ejecuciones o saturar el contexto.
3.  **Seguridad**: Eliminar credenciales temporales y logs de depuración previene fugas de información.

### Procedimiento de Sanitización Pre-Reinstalación
1.  **Backup Total**: Nada se borra sin estar en el repositorio privado de GitHub.
2.  **Limpieza de Logs**: Se eliminan archivos `.log` y `.txt` de depuración antes del backup para no subir "basura" al histórico.
3.  **Aislamiento de Volúmenes**: Identificar qué partes de la base de datos son críticas (`database.sqlite`) y cuáles son volátiles.

---
*Documentado por Antigravity - Protocolo de Integridad de Sistema.*
