# 📉 N8N Version Downgrade Log

**Date**: 2026-02-04
**Action**: Downgrade n8n from `^2.6.3` (Unknown/Bleeding) to `1.75.2` (Stable).
**Reason**: User reported critical failure in 'Execute Command' node. Suspected version mismatch or breaking change in 'latest'.

## Steps Taken
1. Modified `package.json` to pin version `1.75.2`.
2. Initiated `npm install` to apply changes.

## Next Steps (User Action)
If the system does not auto-restart, please run:
```bash
pm2 restart n8n
```
Or if using the start script:
```bash
./start-n8n.sh
```

**Note**: Ensure `fixed_restore.json` is imported to fix the node configuration itself.
