---
type: decision_record
author: [AGENT_ID]
date: 2024-05-23
context: Ensuring multi-project consistency across Visor, n8n, etc.
decision: Use Git Submodules pointing to a central 'Master Template' repository.
status: ACCEPTED
---

# 🧠 DECISION RECORD: CROSS-PROJECT ALIGNMENT STRATEGY (ONE BRAIN, MANY BODIES)

> **Meta-Cognition Principle**: Capture the *reasoning* so future agents understand the *intent*.

## 1. ❓ CONTEXT (THE PROBLEM)
*   **Situation**: Multiple projects (Visor, n8n, etc.) need to remain compliant with a "Master Template" while allowing for local specializations. Without a central mechanism, documentation and protocols drift apart.
*   **Constraints**: Needs to work across different repositories and possibly different machines.
*   **Assumption**: Agents can access the central repository path or URL.

## 2. 💡 OPTIONS CONSIDERED
*   **Option A**: **Git Submodules** (Chosen)
    *   **Pros**: Single source of truth. Updates propagate via `git submodule update`.
    *   **Cons**: slightly more complex git operations.
*   **Option B**: **Manual Copying**
    *   **Pros**: Simple, no dependency.
    *   **Cons**: High risk of drift, manual labor to update.

## 3. ✅ THE DECISION
*   **Chosen Option**: **Option A (Git Submodules)** pointing to `/home/emky/Codigo/Documentacion/Documentacion-Agentes/`.
*   **Rationale**: By linking all projects to the same source, we create a **Meta-Agency**. An agent working on n8n workflows will have the same "moral compass" and technical constraints as the agent working on the Visor media stack.
*   **Implementation Details**:
    *   **Structure**: Each project will have a folder (e.g., `AGENCY_TEMPLATE`) linked to the master repo.
    *   **Compliance Protocol**: Every agent, upon "booting", must compare local `AGENCY/1_PRESENT/` with the Template's requirements.
    *   **Agent Instruction**: "Always verify if the current repository's `AGENCY` structure is aligned with the `AGENCY_TEMPLATE`."

## 4. 🔮 PREDICTED CONSEQUENCES (FUTURE)
*   **Positive**: **Centralized Knowledge**. Updates in the Master Template flow to all bodies.
*   **Negative**: Agents must handle submodule initialization and updates correctly.

## 5. 🔄 REVIEW TRIGGER
*   **When to reconsider**: If the submodule approach becomes too cumbersome for simple agents or if we move to a monorepo structure.
