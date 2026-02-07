# 📚 VEGA GLOSSARY (Lingua Franca)

> **Directive**: All agents must use these terms with absolute precision. Ambiguity is the enemy of execution.

## I. CORE ENTITIES

### 🧠 Cerebro (The Brain)
*   **Definition**: The cognitive center responsible for high-level strategy, planning, and decision-making.
*   **Role**: Analyzes context, consults memory, and issues directives to the Actor.
*   **Model**: Typically a high-reasoning model (e.g., Gemini 1.5 Pro, GPT-4).
*   **Output**: Structured plans (JSON), not direct actions.

### 🎭 Actor (The Executioner)
*   **Definition**: The tactical unit responsible for executing specific, atomic actions.
*   **Role**: Receives directives from Cerebro and interacts with the physical world (APIs, filesystem, CLI).
*   **Model**: Typically a fast, cost-effective model (e.g., Gemini 2.5 Flash).
*   **Output**: Concrete tool calls (Bash, API requests).

### 👁️ Panopticon (Total Visibility)
*   **Definition**: The state of complete observability where no system component is opaque.
*   **Principle**: "Do not guess. Look."
*   **Artifacts**: Screenshots, verbose logs, database queries, state dumps.

### 🤝 The Human Handover (Intervention Protocol)
*   **Definition**: The explicit request for human assistance when an agent encounters a limitation outside its capabilities.
*   **Protocol**: STOP -> ASK -> WALKTHROUGH.
*   **Requirement**: Must provide a simplified, step-by-step guide for the human to resolve the blocker.

## II. TEMPORAL CONCEPTS (CHRONOS)

### 📜 Arche (The Origin)
*   **Definition**: The immutable history and foundational context of the project.
*   **Includes**: Core protocols, initial requirements, and the "why" of the project's existence.

### 📍 Status Quo (The Present)
*   **Definition**: The exact, verifiable state of the system at the current moment (`t=now`).
*   **Includes**: Active tasks, known bugs, current git branch, and running processes.

### 🚀 Telos (The Destination)
*   **Definition**: The strategic goal or "end state" the system is moving towards.
*   **Includes**: Roadmap, backlog, and visionary concepts.

## III. OPERATIONAL PROTOCOLS

### 🔁 Einstein's Loop
*   **Definition**: A detected cycle of repetitive failure (doing the same thing > 2 times).
*   **Protocol**: IMMEDIATE STOP. Re-evaluate assumptions. Zoom out.

### 🧠 Meta-Cognition
*   **Definition**: The act of documenting the *reasoning* behind a decision, not just the decision itself.
*   **Artifact**: `DECISION_RECORD.md`.

## IV. DATA STRUCTURES

### 🧬 Histogram
*   **Definition**: The narrative arc of the project, mapping the trajectory from Arche -> Status Quo -> Telos.
*   **Purpose**: Allows any agent to instantly understand the vector of progress.
