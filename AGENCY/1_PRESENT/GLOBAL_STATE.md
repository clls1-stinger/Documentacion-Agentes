# 🌍 GLOBAL STATE (The Status Quo)

> **Directive**: This file is the single source of truth for the *current* state of the project. It must be updated at the end of every significant session.

## 1. 📍 CURRENT CONTEXT (t=2026-02-18)
*   **Active Phase**: V2 Migration (Tauri + Preact)
*   **Current Focus**: Porting advanced features from the legacy Astro client to the new Preact-based native architecture.
*   **Last Update**: 2026-02-18 by Antigravity Kernel

## 2. 🚧 ACTIVE WORKSTREAMS
*   [x] **Infrastructure**: FastAPI bridge fixed (Service Role Key) and Docker stack synchronized. (`api/main.py` [L39], `docker-compose.yml` [L10])
*   [x] **Core Views**: Board [L335], Backlog [L375], Archive [L425], and Analysis [L455] views fully implemented in `src/components/ScrumBoard.tsx`.
*   [x] **Task Logic**: Subtasks [L72], Priority [L185], Emoji [L164], Tags [L210], and Due Date [L195] support added in `src/components/TaskDrawer.tsx`.
*   [x] **Advanced Ops**: Sorting [L170], Search [L163], and Bulk Actions (Ctrl+Click) [L130, L145] operational in `src/components/ScrumBoard.tsx`.
*   [x] **Agent Intelligence**: Implemented `skills.sh` pattern in `Documentacion/Documentacion-Agentes/skills/` for procedural knowledge.
*   [ ] **Tauri Integration**: Finalizing the native desktop build with sidecars.

## 3. 🛑 KNOWN BLOCKERS
*   **Feature Gap**: Reminder notifications and Private Task encryption still pending.

## 4. 🛠️ ENVIRONMENT HEALTH
*   **Build Status**: Preact client runs via Vite; API runs via Python.
*   **Database**: Supabase (Remote) managed via Service Role for total visibility.
*   **Dependencies**: Preact, Tauri, FastAPI, Supabase, Excalidraw.

## 5. 📉 RECENT INCIDENTS (Last 3)
*   **Astro Instability**: Legacy version deprecated.
*   **Auth Bridge Error**: Fixed Service Role Key mismatch in Docker.

## 6. ⏭️ IMMEDIATE NEXT ACTIONS
1.  Implement Reminder Notifications (System-level).
2.  Add "Private Task" encryption logic.
3.  Polish UI transitions and micro-interactions.
