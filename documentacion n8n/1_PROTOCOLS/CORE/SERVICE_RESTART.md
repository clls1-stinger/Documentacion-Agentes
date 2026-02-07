# 🔄 N8N SERVICE RESTART PROTOCOL
> **Protocol ID**: N8N-SRP-001
> **Context**: Service Management & Recovery

## 🚨 CRITICAL INSTRUCTION
**NEVER** use `./start-n8n.sh` or `node ...` to restart the service manually. This causes port conflicts and orphans the process from the process manager.

## ✅ THE CORRECT METHOD
The n8n service is managed by **PM2**. To restart it safely:

```bash
pm2 restart n8n-master
```

## 🛠️ TROUBLESHOOTING (Ghost Processes)
If `pm2 restart` hangs or the UI remains unresponsive:

1.  **Check Status**:
    ```bash
    pm2 list
    ```

2.  **Force Kill (If hung)**:
    Find the process occupying port 5678 and kill it manually. PM2 will automatically resurrect it.
    ```bash
    fuser -k 5678/tcp
    # OR
    killall -9 node
    ```

## 📝 LOG VERIFICATION
After restart, always verify the service is up:
```bash
tail -f /home/emky/n8n/n8n-debug.log
```
