# 🏥 PROTOCOLO DE SANITIZACIÓN Y RECUPERACIÓN DE n8n (VEGA)

Este protocolo está diseñado para cuando n8n se comporta de manera errática, lanza errores inexplicables de tipos de datos (`json property is not object`), o parece saturado ("tilteado") por exceso de información.

---

## 🛑 FASE 1: Diagnóstico Rápido (First Aid)

### 1. Verificación de Logs
Antes de reiniciar nada, verifica qué está pasando.

```bash
# Ver los últimos 200 logs en tiempo real
tail -n 200 -f /home/emky/n8n/n8nEventLog.log

# O si usas PM2 (más común para ver errores de arranque)
pm2 logs n8n --lines 100
```

### 2. Verificar Estado del Servicio
```bash
pm2 status n8n
# O
systemctl status n8n
```

---

## 🧹 FASE 2: Sanitización y Limpieza (The Purge)

Si n8n está lento o con errores de memoria, sigue estos pasos para limpiarlo.

### 1. Detener n8n
```bash
pm2 stop n8n-master
```

### 2. Limpieza de Logs Antiguos (Rotación Manual)
Si los logs son gigantescos (>1GB), muévelos o bórralos.
```bash
cd /home/emky/n8n
# Mover log actual a backup comprimido (simulado)
mv n8nEventLog.log "n8nEventLog_$(date +%F).bak"
# O truncarlo a 0 si no te importa la historia
truncate -s 0 n8nEventLog.log
```

### 3. Vacuum de la Base de Datos (Opcional pero Recomendado)
Esto compacta la base de datos SQLite y la hace más rápida. **n8n DEBE estar detenido.**
```bash
sqlite3 ~/.n8n/database.sqlite "VACUUM;"
```

---

## 🩺 FASE 3: Corrección Quirúrgica (Hot Patching)

Si el problema es un error específico de un nodo (como el Loop infinito o el error de objeto JSON), aplica los parches conocidos.

### 1. Parche de Estructura Estricta (Fix JSON Object Error)
Ejecuta esto si ves "A 'json' property isn't an object".
```bash
python3 /home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/patch_v20_strict_structure.py
```

### 2. Parche del Loop Infinito (Fix Aggregator)
Ejecuta esto si el agente se queda buscando en Drive eternamente.
```bash
python3 /home/emky/n8n/hot_patch_workflow.py
```

---

## ⚡ FASE 4: Reinicio y Verificación

### 1. Iniciar n8n
```bash
pm2 restart n8n-master
# O start si estaba parado
pm2 start n8n-master
```

### 2. Verificar Salud
Espera 30 segundos y verifica que no haya crash loops.
```bash
pm2 logs n8n-master --lines 50
```

### 3. Prueba de Humo (Smoke Test)
Abre la interfaz web de n8n y ejecuta el workflow manualmente con una entrada simple.

---

## 📝 Lista de Chequeo Rápida (Cheat Sheet)

- [ ] ¿Logs muestran error de memoria o "Event Loop Delay"? -> **Reinicia.**
- [ ] ¿Error "json property is not object"? -> **Aplica `patch_v20` + F5.**
- [ ] ¿Base de datos > 1GB? -> **Stop -> Vacuum -> Start.**
- [ ] ¿Agente en loop? -> **Detener ejecución desde UI -> Aplicar `hot_patch`.**

---
**Última actualización**: 2026-02-03
**Autor**: Vega
