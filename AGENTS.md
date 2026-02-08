# 🤖 VEGA OS KERNEL: AGENT INTERFACE

> **⚠️ CRITICAL DIRECTIVE**: If you are an autonomous agent (AI) reading this, you **MUST** read this file first. It is the Boot Loader for your cognitive process.

## 1. 🛑 STOP AND ORIENT
Before executing any code or writing any plan, you must ingest the "Agency" context.

*   **Step 1**: Read [AGENCY/README.md](AGENCY/README.md).
*   **Step 2**: Consult [AGENCY/3_LEXICON/VEGA_GLOSSARY.md](AGENCY/3_LEXICON/VEGA_GLOSSARY.md) to understand the "Lingua Franca".
*   **Step 3**: Check [AGENCY/1_PRESENT/GLOBAL_STATE.md](AGENCY/1_PRESENT/GLOBAL_STATE.md) for the current status quo.

## 2. 📜 THE LAW OF INFALLIBILITY
Your primary mission is to reduce ambiguity to zero.
*   **Do not guess**: Use the `Panopticon` principle (Total Visibility).
*   **Do not repeat errors**: Use the `Einstein Loop` protocol.
*   **Do not act blindly**: Use the `Chronos` principle (Historical Awareness).

## 3. 📝 DOCUMENTATION PROTOCOLS
All documentation you create **MUST** follow the standardized templates in `AGENCY/4_TEMPLATES/`.
*   **Session Logs**: Use `SESSION_LOG.md`.
*   **Decisions**: Use `DECISION_RECORD.md`.
*   **State Updates**: Update `GLOBAL_STATE.md` at the end of your session.

## 4. 🧭 NAVIGATION
*   **Past (Arche)**: `AGENCY/0_ARCHE/` - Where we came from.
*   **Present (Status Quo)**: `AGENCY/1_PRESENT/` - Where we are.
*   **Future (Telos)**: `AGENCY/2_FUTURE/` - Where we are going.

---
*Vega OS Kernel - v2.0 "Agency"*
**Supabase:** Pre-configured in environment (`PUBLIC_SUPABASE_URL`:https://helwbjlsdajtjebfsxlf.supabase.co, `PUBLIC_SUPABASE_ANON_KEY`:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbHdiamxzZGFqdGplYmZzeGxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAyMzk1MjEsImV4cCI6MjA4NTgxNTUyMX0.zc9HoOMH74oGfjnXzNFwnIJXck63e6wDdhVAOK4l8ts,`service_role`:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbHdiamxzZGFqdGplYmZzeGxmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDIzOTUyMSwiZXhwIjoyMDg1ODE1NTIxfQ.CZCnbGTdqJ-17_45eYt2XvOK59NREPyF0XO6jDoqIco).
*   **Service Role:** `SUPABASE_SERVICE_ROLE_KEY` (use for admin actions, bypass RLS).
*   **Render:** `RENDER_API_KEY` (use for triggering deploys or checking status).
*   **Google/Jules:** Managed via external MCP or environment injection. Credentials for Google APIs (if needed) should be accessed via `process.env.GOOGLE_APPLICATION_CREDENTIALS` or similar standard patterns, never hardcoded.
