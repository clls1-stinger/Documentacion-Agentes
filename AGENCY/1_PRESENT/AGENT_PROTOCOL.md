# 🤖 Vega OS Agent Protocol

> **System Prompt for AI Collaborators**

Welcome to the Vega OS Kernel. This repository adheres to strict operational protocols. As an AI Agent (like Jules, Vega Core, or Code Architect), you are required to follow these guidelines to ensure system integrity and coherence.

## 1. Core Directives

*   **Read the Manual First:** Before executing any task, you MUST consult `documentacion/INDEX.md` and the relevant sub-protocols (e.g., `BOARD_PROTOCOL.md`, `AUTH_PROTOCOL.md`). Your actions must align with the established architectural patterns.
*   **Identify Your Role:** Check the `task_ai_collaborators` table (or the UI context) to see which agent persona you are fulfilling. Adopt the appropriate tone and focus.
*   **Follow the Spec:** Execute the task description *exactly*. If a description is ambiguous, ask for clarification (if interactive) or make a conservative, best-effort decision based on existing patterns.

## 2. Proactive Task Registration

*   **Zero Invisible Work:** If you identify a necessary improvement, bug fix, or refactor that is NOT currently tracked:
    1.  **Create a New Task:** Add a card to the **Backlog** or **To Do** column.
    2.  **Self-Assign:** Add yourself (or the appropriate AI persona) to the `task_ai_collaborators`.
    3.  **Document Intent:** Clearly describe the *Why* and *What* in the task description.
    4.  **Execute:** Proceed with the work only after the task is registered.

## 3. Navigation & Context (The Map)

Agents must associate Tasks with Repositories using **Tags**. Use this map to understand where your work is located.

| Tag | Repository / Context | Description |
| :--- | :--- | :--- |
| `operation-center` | `this-repo` | The Scrum Board, Database Schema, and Core Logic. |
| `frontend` | `src/` | Astro/React Frontend Components. |
| `backend` | `supabase/functions/` | Supabase Edge Functions & SQL. |
| `documentation` | `documentacion/` | Protocols, Knowledge Base, and Forensics. |
| `infrastructure` | `render.yaml` | Deployment Configuration (Render). |
| `legacy` | `legacy/` | Old Express backend (reference only). |

## 4. Task Retrieval Protocol

To find your work:
1.  **Identify Identity:** Know your `agent_id` (e.g., via `ai_agents` table).
2.  **Fetch Assigned Tasks:** Query `tasks` JOIN `task_ai_collaborators` WHERE `agent_id = your_id`.
3.  **Filter by Context:** Check `tags` on the task to ensure you are working in the correct repository/directory.
4.  **Review Status:** Only work on tasks in `col-todo` or `col-inprogress`. Do not touch `col-done` unless explicitly verifying.

## 5. Credentials & Access

*   **Supabase:** Pre-configured in environment.
*   **Service Role:** `SUPABASE_SERVICE_ROLE_KEY` (use for admin actions, bypass RLS).
*   **Render:** `RENDER_API_KEY` (use for triggering deploys or checking status).
*   **Google/Jules:** Managed via external MCP or environment injection. Credentials for Google APIs (if needed) should be accessed via `process.env.GOOGLE_APPLICATION_CREDENTIALS` or similar standard patterns, never hardcoded.

## 6. Task Execution Workflow

1.  **Ingest Context:** Read the `description`, `subtasks`, and any linked `task_attachments`.
2.  **Execute:** Perform the required code changes, documentation updates, or analysis.
3.  **Verify:** Ensure your changes pass any existing checks (lint, build - noting environment limitations).
4.  **Log:** If you have write access to `task_editions`, log your actions. Otherwise, leave a detailed comment explaining what you did.
5.  **Complete:**
    *   Mark all `subtasks` as done (if applicable).
    *   Move the task to the **Done** column (`col-done`) if the entire scope is complete.

## 7. Operational Boundaries & The "Walkthrough" Protocol

*   **Do Not Hallucinate Features:** Only implement what is requested.
*   **Respect Environment Limits:** Be aware that `node_modules` might be missing or network access restricted. Adjust your strategy accordingly (e.g., verify code logic statically).
*   **Security First:** Never commit credentials. Rotate keys if exposed.
*   **🚨 FUNDAMENTAL PILLAR: The Human Handover:**
    *   If you encounter a task or requirement that is **outside your capabilities** (e.g., requires physical access, specific auth tokens not available, or complex decision-making beyond your scope):
    *   **STOP**. Do not guess.
    *   **REQUEST INTERVENTION**: Explicitly ask the human user for help.
    *   **CREATE A WALKTHROUGH**: Provide a **simplified, step-by-step list** of actions the human needs to perform to unblock you. This list must be crystal clear, assuming no prior context.
    *   *Example*: "I cannot access the production database directly. Please run this SQL script in the Supabase Dashboard and paste the result here."

---
*Vega OS Kernel - Machine Intelligence Division*
