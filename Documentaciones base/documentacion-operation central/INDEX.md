# 🧠 PROJECT BRAIN INDEX

> Welcome, I am Antigravity. This is the central orchestration point for the **npmx Rebuild project**.

## Overview
This project aims to reconstruct the `npmx.dev` experience:
- **Speed**: Instant npm package search and navigation.
- **Aesthetics**: Premium UI with glassmorphism, gradients, and dark mode.
- **Persistence**: User sessions via Supabase.

## 🧭 Navigation
- [Core Persona](./0_CORE_PERSONA/INDEX.md)
    - [Vega Identity](./0_CORE_PERSONA/VEGA_IDENTITY.md)
    - [Core Pillars](./0_CORE_PERSONA/VEGA_CORE_PILLARS.md)
- [Protocols](./1_PROTOCOLS/INDEX.md)
    - [Auth Protocol](./1_PROTOCOLS/AUTH_PROTOCOL.md)
    - [Board Protocol](./1_PROTOCOLS/BOARD_PROTOCOL.md)
    - [Design System](./1_PROTOCOLS/DESIGN_SYSTEM.md)
    - [Temporal Tracing](./1_PROTOCOLS/TEMPORAL_TRACING.md)
    - [MCP Protocol](./1_PROTOCOLS/MCP_PROTOCOL.md)
- [Resources](./2_RESOURCES/INDEX.md)
- [Work Logs](./3_WORK_LOGS_AND_HISTORY/INDEX.md)

## 🚀 Active Goals
1. Rebuild `client` directory with Vite + React. [DONE]
2. Integrate Supabase Auth with custom `username@local` mapping. [DONE]
3. Implement Scrum Board with `@hello-pangea/dnd` and premium UI. [DONE]
4. Transition from Socket.io to Supabase Realtime logic. [DONE]
5. Fix PostgREST relationship detection via Foreign Key constraints. [DONE]
6. Implement Advanced Task Drawer (Polymorphic Side Panel) with Collaborator Search. [DONE]
7. Synchronize Knowledge Histogram for Temporal Tracing. [DONE]
8. Implement Obsidian Tags Protocol with Case-Insensitive Search & Premium UI. [DONE]
9. Refined Scrum Board UI: Removed Redundant 'Deploy Column'. [DONE]
10. Enhanced Execution Archive: Temporal Tracing for Tasks & Subtasks + Synergy UI. [DONE]
11. Finalization UX: GPU-Accelerated 'Black Hole' Animation + Context-Aware Creation. [DONE]
12. Operational Analytics: Real-time Global & Personal counters in Header. [DONE]
13. Animation Polish: Flicker-free 'Black Hole' sequence using AnimatePresence. [DONE]
14. Visual Blueprint: Implemented Excalidraw for task-based sketching and architecture. [DONE]
15. Analysis Environment: Global metrics and priority distribution dashboards. [DONE]
16. Excalidraw UI Hardening: Resolved rendering bugs and CSS injection for premium dark mode. [DONE]
17. Testing Infrastructure: Implemented unit tests for visual diff logic and established test protocols using Node.js built-in runner. [DONE]
17. Intelligence Integration: Implemented MCP Server for AI Agent interoperability. [DONE]
17. Secure Key Derivation: Transitioned Vault Protocol to password-based derivation for zero-knowledge integrity. [DONE]
17. Code Health: Removed unused imports in TaskDrawer.tsx for better maintainability. [DONE]
17. 🔒 Security Hardening: Implemented input validation for legacy login endpoint. [DONE]

17. Operational Recovery: Robust auto-save for Visual Blueprint and header cleanup. [DONE]
### ⚓ Infrastructure Rules
- **Docker-First Policy**: Every major implementation or change MUST be followed by rebuilding the container environment using the command: `docker-compose -f scrum-master-stack.yml up -d --build`.
- Refer to [Deployment Protocol](./1_PROTOCOLS/DEPLOYMENT.md) for full orchestration details.
