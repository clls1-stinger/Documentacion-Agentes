---
type: decision_record
author: [AGENT_ID]
date: 2024-05-23
context: Enabling unified task management for all agents across the ecosystem.
decision: Use n8n as the central API Gateway for the Scrum Board.
status: ACCEPTED
---

# 🧠 DECISION RECORD: OMNIPRESENT SCRUM API (THE AGENTIC NERVOUS SYSTEM)

> **Meta-Cognition Principle**: Capture the *reasoning* so future agents understand the *intent*.

## 1. ❓ CONTEXT (THE PROBLEM)
*   **Situation**: We need a way for diverse agents (local scripts, n8n workflows, external LLMs) to interact with a central task board (Operation Center) with granular detail.
*   **Constraints**: Must be accessible via standard HTTP requests.
*   **Assumption**: n8n is running and accessible.

## 2. 💡 OPTIONS CONSIDERED
*   **Option A**: **n8n API Gateway** (Chosen)
    *   **Pros**: Decouples agents from the DB. Flexible logic in n8n.
    *   **Cons**: Dependency on n8n uptime.
*   **Option B**: **Direct Database Access**
    *   **Pros**: Faster?
    *   **Cons**: Security risk, requires DB driver in every agent environment.

## 3. ✅ THE DECISION
*   **Chosen Option**: **Option A (n8n Bridge)**.
*   **Rationale**: Acts as a "Neural Scrum" where agents poll for work and report status.
*   **Implementation Details**:
    *   **Endpoint**: `https://<n8n-instance>/webhook/scrum-api`
    *   **Security**: `X-AGENCY-AUTH` header.
    *   **Protocol**:
        1.  **Poll**: `GET /tasks?status=Backlog&tag=<project_name>`
        2.  **Self-Assign**: `PATCH /tasks/:id` with `{"collaborator": "ID", "status": "In Progress"}`
        3.  **Execute**: Break down into subtasks via `POST /tasks/:id/subtasks`.
        4.  **Report**: Update subtasks incrementally.

## 4. 🔮 PREDICTED CONSEQUENCES (FUTURE)
*   **Positive**: **Real-time Visibility**. Humans can see precisely how agents are progressing. Agents become autonomous workers.
*   **Negative**: Latency introduced by the webhook layer.

## 5. 🔄 REVIEW TRIGGER
*   **When to reconsider**: If n8n becomes a performance bottleneck or single point of failure.
