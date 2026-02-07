# 🕒 TEMPORAL TRACING (Knowledge Histogram)

> "A project without a history is a project without a soul. Knowledge Histogram ensures we never forget the 'why'."

## Overview
Temporal Tracing is the technical implementation of the **Chronos Protocol**. It uses a local SQLite database and Git integration to create a traceable timeline of agent thoughts, actions, and system states.

## Components
1.  **`data/context.sqlite`**: The living memory of the system.
2.  **`bin/snapshot.py`**: The orchestration tool to capture snapshots.
3.  **Git Commits**: Every snapshot is linked to a specific git hash.

## Snapshot Structure
Each entry in the "Histogram" contains:
- **Timestamp**: Exact moment of the change.
- **Agent**: The identity of the agent (e.g., Antigravity).
- **Task**: The high-level goal being pursued.
- **Thought Process**: The logic and rationale behind the implementation.
- **Tools**: List of tools used to achieve the result.
- **Git Context**: Commit hash and list of modified files.

## Usage
Agents must generate a snapshot after every significant milestone:

```bash
python3 bin/snapshot.py \
  --agent "Antigravity" \
  --task "Feature Implementation" \
  --thought "Implementing glassmorphism on the board..." \
  --tools '["write_to_file", "run_command"]'
```

---
*Vega OS Kernel - Memory Module*
