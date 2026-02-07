# 🗄️ Vega OS Data Schema Reference

> **Simplified Database Map for AI Agents**

Use this reference to understand the core data structures when querying Supabase via MCP or SQL.

## 1. Tables

### `tasks` (The Work Units)
*   **id** (TEXT): Unique ID (e.g., 'task-123', UUID).
*   **content** (TEXT): Title of the task.
*   **description** (TEXT): Detailed requirements.
*   **column_id** (TEXT): Status ('col-backlog', 'col-todo', 'col-inprogress', 'col-verify', 'col-done').
*   **priority** (TEXT): 'urgent', 'high', 'medium', 'low'.
*   **tags** (TEXT[]): Array of tags (e.g., ['frontend', 'bug']).
*   **user_id** (UUID): Creator ID.

### `ai_agents` (The Personas)
*   **id** (UUID): Unique Agent ID.
*   **name** (TEXT): Display Name (e.g., 'Vega Core').
*   **role** (TEXT): Functional Role (e.g., 'System Architect').
*   **capabilities** (TEXT[]): List of skills.

### `task_ai_collaborators` (The Assignments)
*   **task_id** (TEXT): Foreign Key to `tasks.id`.
*   **agent_id** (UUID): Foreign Key to `ai_agents.id`.

### `task_editions` (The History)
*   **task_id** (TEXT): Linked Task.
*   **edit_type** (TEXT): Type of change (e.g., 'status_change', 'agent_assigned').
*   **old_value** (JSONB): Previous state.
*   **new_value** (JSONB): New state.

## 2. Common Queries

**Find My Tasks:**
```sql
SELECT t.* FROM tasks t
JOIN task_ai_collaborators tac ON t.id = tac.task_id
WHERE tac.agent_id = 'YOUR_AGENT_UUID'
AND t.column_id != 'col-done';
```

**Register a New Task:**
```sql
INSERT INTO tasks (content, description, column_id, tags)
VALUES ('New Feature', 'Description...', 'col-todo', ARRAY['backend']);
-- Then link yourself in task_ai_collaborators
```
