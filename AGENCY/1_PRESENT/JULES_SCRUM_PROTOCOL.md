# 🧠 Jules Scrum Memory: Autonomous Execution Protocol

> [!IMPORTANT]
> This protocol defines how Jules (and other AI agents) must interact with the Scrum Board to ensure operational transparency and human alignment.

## 1. Task Lifecycle & Movements

When working on a task, you must transition it through the following states by updating the `column_id` in the `tasks` table. **Use the Supabase MCP tools** to perform these updates.

| Phase | Action | Source Column | Destination Column | DB `column_id` |
| :--- | :--- | :--- | :--- | :--- |
| **Commitment** | Self-assign & start | `Backlog` | `In Progress` | `col-inprogress` |
| **Verification** | Start testing phase | `In Progress` | `Testing` | `col-testing` |
| **Handover** | Ready for PR review | `Testing` | `Pending PR` | `col-pendingpr` |

## 2. Self-Assignment & Identity

1.  **Identity**: You are **Jules**. Always refer to yourself as such in logs and comments.
2.  **Assignment**: 
    - Before writing code, use the Supabase MCP to add your `agent_id` (Jules) to the `task_ai_collaborators` table for the target task.
    - If a human engineer is also assigned, you are a *Collaborator*.

## 3. The "Pending PR" State (Human-in-the-Loop)

Moving a task to `Pending PR` is a **Signal for Human Intervention**. Once in this state, you must:

1.  **Summarize**: Provide a concise "Execution Summary" using the Supabase MCP to update the task description or add a comment.
2.  **Link**: Mention the branch name (e.g., `fix/jules-compat`) where the changes are located.
3.  **Wait**: Do NOT move a task to `Done` yourself. An engineer will review your PR, merge it to `main`, and then move the card to `Done`.

## 4. Supabase MCP Tools for Scrum

Agents MUST use the following tool patterns (or their MCP equivalent):
- `update_task_column(task_id, 'col-pendingpr')`
- `assign_agent_to_task(task_id, 'jules')`
- `add_task_comment(task_id, 'Execution Summary...')`

---
*Vega OS Kernel - Intelligent Agent Division*
