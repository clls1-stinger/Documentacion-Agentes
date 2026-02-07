# 👁️ BACKLOG 008: The Watcher (Metacognition & Auto-Repair)

> "Quis custodiet ipsos custodes?" - The Watcher does.

## Objective
Implement a secondary, high-level supervisory agent ("The Watcher") that runs parallel to the main workflow. It observes the execution trace, detects anomalies (loops, errors, hallucinations), and triggers a self-repair mechanism *without* halting the main production flow.

## Components

### 1. The Observer (Metacognitionist) 🧠
- **Role**: Passive monitor of the `n8nEventLog.log` or a dedicated redis stream.
- **Logic**: It does not "do" tasks. It "watches" tasks.
- **Triggers**:
    - "Why did the agent try `ls` 5 times in a row?"
    - "The output JSON is malformed again."
    - "Execution time > 60s for a simple task."

### 2. The Auto-Repairer (The Mechanic) 🔧
- **Role**: Active interventionist.
- **Capabilities**:
    - **Hot Patching**: Can modify the SQLite database or Python scripts on the fly.
    - **State Injection**: Can inject a "System Prompt" into the ongoing chat history (e.g., "SYSTEM: You are stuck. Stop using `ls`. Use `find`.") to guide the main agent back on track.
    - **Node Reset**: Can restart a specific crashed node.

## Workflow Integration
- **Non-Blocking**: The repair process must happen alongside the main thread.
- **Resume Capability**: "para que cuando termine de reparar... sigamos por exactamente el camino donde se quedo".
    - This implies a **State Preservation** mechanism where the Main Agent pauses (or loops harmlessly) until the Watcher acknowledges the fix, then resumes from the last valid state.

## Implementation Phases
1. [ ] **Log Tap**: Build a reliable stream of events from n8n to the Watcher.
2. [ ] **Anomaly Detection**: Simple heuristic rules (3x repetition = Fail).
3. [ ] **Intervention API**: A mechanism to inject messages into the running context.

## Priority
**Visionary / High Complexity**
Requested by User on 2026-02-03.
