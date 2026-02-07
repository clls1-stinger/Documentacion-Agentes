# Knowledge Entry: Excalidraw Stability & Serialized State
**ID:** KNOWLEDGE_003_EXCALIDRAW_PERSISTENCE
**Category:** Frontend Architecture / Third-Party Integration

## Problem: The "Collaborators" Crash
When integrating Excalidraw into a persistent environment like Supabase/PostgreSQL, the `appState.collaborators` object (a JavaScript `Map`) causes issues. 
- **Symptom**: `TypeError: collaborators.forEach is not a function`.
- **Root Cause**: JSON serialization destroys the `Map` prototype, turning it into a plain object `{}` (or empty) that doesn't share the same interface as Excalidraw's internal expectation.

## Solution: Clear & Sanitize
Always initialize and save the `appState` with a clean `collaborators: new Map()`. Do not try to persist session-based UI state in the permanent database unless explicitly building a real-time multiplayer backend.

## Knowledge: Interaction-Aware Auto-Save
Standard debouncing (e.g., saving 2 seconds after the last change) is dangerous in Excalidraw because a "change" event fires continuously during a drag operation. 
- **Pattern**: Check `appState.isResizing || appState.isRotating || appState.draggingElement || appState.editingElement`. If ANY of these are true, the user is mid-action. Postpone the sync.
- **Visual Feedback**: A breathing animation during sync provides a "living system" feel that matches premium expectations.

---
*Verified by Antigravity Operation Kernel*
