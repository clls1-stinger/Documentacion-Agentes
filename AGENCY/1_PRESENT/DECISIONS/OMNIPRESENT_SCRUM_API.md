# 🌐 OMNIPRESENT SCRUM API (THE AGENTIC NERVOUS SYSTEM)

> **Purpose**: Allow all agents (local, n8n, Jules, etc.) to read and update the central Scrum Board (Operation Center) with granular detail.

## 1. 🏗️ ARCHITECTURE: N8N BRIDGE
Agents interact with the Board via **n8n** as an API Gateway.

*   **Endpoint**: `https://<n8n-instance>/webhook/scrum-api`
*   **Security**: `X-AGENCY-AUTH` header.

## 2. 🛡️ AGENT PROTOCOL (NEURAL SCRUM)
Every agent must follow this lifecycle for any assigned task:

### A. Identification & Assignment
1.  **Poll tasks**: `GET /tasks?status=Backlog&tag=<project_name>`
2.  **Verify Availability**: If the task has NO `collaborator`, proceed.
3.  **Self-Assign & Move**: 
    *   Update `collaborator` with the agent's ID.
    *   Update `status` to `In Progress`.
    *   **Action**: `PATCH /tasks/:id` with `{"collaborator": "ID", "status": "In Progress"}`.

### B. Planning (Subtasks)
1.  **Analyze Story**: Read `description` and `title`.
2.  **Generate Subtasks**: Break work into atomic sub-items.
3.  **Sync Subtasks**: Use `POST /tasks/:id/subtasks` to register the plan.

### C. Execution & Reporting
1.  **Incremental Updates**: As each subtask is finished, call `PATCH /subtasks/:id` with `status: done`.
2.  **Visibility**: This allows human engineers to see precisely how the agent is progressing in real-time.
3.  **Final Completion**: Once all subtasks are done, mark the main task as `Done`.

## 3. 🚀 DATA STRUCTURE (GOALS)
```json
{
  "id": "uuid",
  "title": "String",
  "description": "Markdown",
  "status": "Backlog | In Progress | Done",
  "collaborators": ["Agent-ID"],
  "subtasks": [
    {"id": "s1", "text": "Task 1", "done": true}
  ]
}
```

---
*Vega OS Kernel - v2.5 "Consolidated Agency"*
