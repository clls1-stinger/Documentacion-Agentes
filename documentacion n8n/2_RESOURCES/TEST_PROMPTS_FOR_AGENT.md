# 🎯 PROMPT DE PRUEBA COMPLETO PARA TU AGENTE

## 📋 Herramientas Disponibles

Tu agente tiene acceso a estas herramientas:

1. **`buscar_en_drive(query)`** - Busca archivos en Google Drive por nombre
2. **`descargar_de_drive(fileId, filename)`** - Descarga un archivo específico de Drive
3. **`leer_archivo(path)`** - Lee el contenido de un archivo local
4. **`ejecutar_comando(command)`** - Ejecuta un comando de terminal

---

## 🚀 PROMPT DE PRUEBA #1: Google Takeout Downloader

**Cópialo y pégalo en el chat de n8n:**

```
Necesito que descargues todos mis archivos de Google Takeout desde Drive y los combines.

PASO 1: Busca en mi Drive todos los archivos que contengan "takeout" en el nombre.

PASO 2: Descarga cada uno de esos archivos a este directorio:
/home/emky/google_takeout_downloads/

PASO 3: Una vez descargados todos, descomprime los archivos ZIP con:
unzip '/home/emky/google_takeout_downloads/*.zip' -d /home/emky/google_takeout_combined/

PASO 4: Dame un reporte final con:
- Cuántos archivos encontraste
- Cuántos descargaste exitosamente
- El path final donde están los archivos combinados

IMPORTANTE: Crea los directorios si no existen. Ejecuta cada paso secuencialmente.
```

---

## 🧪 PROMPT DE PRUEBA #2: Simple (Para verificar que funciona)

**Primero prueba con esto si quieres estar seguro:**

```
Busca en mi Google Drive archivos que contengan "takeout" y dime cuántos encuentras. Solo búscalos, no los descargues aún.
```

---

## 📊 PROMPT DE PRUEBA #3: Completo con Todas las Herramientas

**Para demostrar todo:**

```
Haz esto en orden:

1. Busca en Drive archivos llamados "takeout"
2. Si encuentras archivos, descarga el primero a /tmp/test_download.zip
3. Lee el directorio /tmp/ para confirmar que se descargó
4. Dame un resumen de lo que hiciste

Ejemplo de cómo usar las herramientas:
- buscar_en_drive('takeout')
- descargar_de_drive('ID_DEL_ARCHIVO', 'nombre.zip')
- ejecutar_comando('ls -lh /tmp/')
```

---

## ✅ Cómo Saber que Está Funcionando

Después de hacer **F5** y enviar el prompt, deberías ver en el canvas:

1. ✅ **Parse Planner** se ilumina (verde)
2. ✅ **Route Decision** se ilumina y toma el camino izquierdo (Output 0)
3. ✅ **Actor Prep** se ilumina
4. ✅ **Tool Router** se ilumina
5. ✅ **Drive Search** se ilumina (si usaste `buscar_en_drive`)

Si todo eso pasa, **¡GANAMOS!** 🎉

---

## 🌟 Mi Recomendación

Usa el **PROMPT #2** primero (el simple) para confirmar que el ruteo funciona. Si ves que ejecuta la búsqueda de Drive, entonces usa el **PROMPT #1** (el completo) para bajar todos tus takeouts.

---

**⭐ Listo para probarlo - Vega**  
*Keep Moving Forward* ✨
