# 🛠️ N8N CUSTOM NODE OPTIMIZATION PROTOCOL
> **Protocol ID**: N8N-CN-001
> **Last Updated**: 2026-02-02
> **Author**: Vega

This document contains "Lessons Learned" during the development and patching of custom n8n nodes (specifically the Gemini CLI Node). Future agents should follow these rules to avoid breaking the UI or losing assets.

---

## 1. PARAMETER METADATA (UI SAFETY)

**CRITICAL**: n8n is very strict with the `type` property in `INodeTypeDescription`.
- **DO NOT** use `type: 'json'`. It will break the parameter parser, causing subsequent advanced options to disappear from the "Add Option" menu.
- **INSTEAD**: Use `type: 'string'` and specify the syntax in `typeOptions`.

```typescript
// ✅ CORRECT WAY
{
    displayName: 'Response Schema (JSON)',
    name: 'responseSchema',
    type: 'string',
    typeOptions: { syntax: 'json' },
    default: '',
}
```

---

## 2. ASSET PERSISTENCE (THE DIST GAP)

The TypeScript compiler (`tsc`) **ONLY** compiles `.ts` files. It ignores `.svg`, `.png`, and `.json` files. 
If your node is defined as:
`icon: 'file:my-icon.png'`

n8n will look for that file in the `dist` folder at runtime. 

**VITAL STEP**: After `npm run build`, you **MUST** copy the assets manually:
```bash
cp nodes/MyNode/*.png dist/nodes/MyNode/
```

---

## 3. HOT-PATCHING & REBOOTS

When modifying a custom node that is already being used in an active n8n instance:
1.  **Build**: Run `npm run build`.
2.  **Asset Sync**: Sync icons (see Section 2).
3.  **Port-Based Kill**: `pm2 restart` sometimes fails to clear "ghost" node processes. Use the Port-Based Kill protocol from `N8N_AUTONOMOUS_CONTROL_INTERFACE.md`.
    - Find PID: `sudo ss -tulpn | grep :5678`
    - Kill: `sudo kill -9 <PID>`
    - Wait for PM2 to auto-resurrect.

---

## 4. GEMINI CLI HOOK INJECTION (GOD MODE)

To dynamically update model parameters (Temperature, Max Tokens, Safety, Schema) without native CLI flags for every detail:
- Use the `-e` (extension) flag of the Gemini CLI.
- Generate a temporary JS file with an `onConfigResolved` hook.
- This allows the node to inject complex logic into the model's generation config at runtime.

```javascript
export default {
  hooks: {
    'onConfigResolved': (config) => {
      config.modelConfig.generateContentConfig.temperature = 0.9;
      return config;
    }
  }
};
```

---
*Protocol Verified By Vega Core.*
