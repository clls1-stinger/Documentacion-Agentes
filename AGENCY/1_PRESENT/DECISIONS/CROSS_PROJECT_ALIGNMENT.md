# 🌐 CROSS-PROJECT ALIGNMENT STRATEGY (ONE BRAIN, MANY BODIES)

> **Purpose**: Ensure that every project (Visor, n8n, etc.) remains compliant with the "Master Template" while allowing for local specializations.

## 1. 🛠️ THE INFRASTRUCTURE: GIT SUBMODULES
To allow all agents to see the template, we use **Git Submodules** pointing to your central repository: `/home/emky/Codigo/Documentacion/Documentacion-Agentes/`.

*   **Implementation**: Each project will have a folder (e.g., `AGENCY_TEMPLATE`) linked to the master repo.
*   **The Jewel**: If you update a rule in the Master Template, a simple `git submodule update` in any project will notify the local agent of the new rules.

## 2. 🛡️ THE COMPLIANCE PROTOCOL (BOOTLOADER)
Every agent, upon "booting" (reading `AGENTS.md`), must perform a **Consistency Check**:

1.  **Read Global Rules**: Access the `AGENCY_TEMPLATE` folder.
2.  **Verify Local Context**: Compare local `AGENCY/1_PRESENT/` with the Template's requirements.
3.  **Identify Gaps**: Flag any missing documentation or violated pillars (e.g., "The 70/30 Rule" applied to a new SSD).

## 3. 🧠 AGENT INSTRUCTION (SYSTEM PROMPT)
Add this directive to the "Rules of Engagement":
> "Always verify if the current repository's `AGENCY` structure is aligned with the `AGENCY_TEMPLATE`. If inconsistencies are found, prioritize fixing the documentation to reflect the Master Pillars before proceeding with execution."

## 4. 🚀 THE VISION: CENTRALIZED KNOWLEDGE
By linking all projects to the same source, you create a **Meta-Agency**. An agent working on your n8n workflows will have the same "moral compass" and technical constraints as the agent working on your Visor media stack.

---
*Vega OS Kernel - Alignment Decisions*
