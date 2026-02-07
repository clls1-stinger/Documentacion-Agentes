# 🧠 Advanced Workflow Architecture & Forensic Debugging
> **Author**: Vega
> **Context**: Post-Mortem Analysis of Execution #334 (The "Takeout" Failure)
> **Relates to**: Gemini CLI Node / n8n Agent Overlord

This document codifies the "Deep Lessons" learned while debugging complex autonomous agents in n8n.

---

## 1. The Survival of Metadata (Data Persistence)
In n8n, a workflow's state is not "global" by default. If you are running a loop (e.g., Planner -> Actor -> Aggregator -> Bucle), data must be explicitly passed through every node.

### The Problem
If a Custom Node (like Gemini CLI) only returns the `result: "model_output"`, all previous inputs like `user_goal` or `history` are **destroyed** for the next iteration.

### The Solution (Node Level)
The `execute` method in the custom node must perform a shallow merge of the input data:
```typescript
const inputData = items[itemIndex].json;
returnData.push({ json: { ...inputData, ...result }, pairedItem: itemIndex });
```
This ensures the "Context" survives the journey through the brain node.

---

## 2. The Planner-Actor-Aggregator Pattern
When building agents without native tool-calling inside n8n nodes, we use this tripartite logic:

1.  **Planner (Strategist)**: Decide *what* to do (high-level instruction).
2.  **Actor (Executor)**: Small model that converts the instruction into **valid JSON for n8n switches**.
3.  **Aggregator (Memory)**: Node that captures the result (like a list of IDs) and packs it back into the `history` array.

**VITAL**: The Aggregator must save **Structured Data** (JSON), not just text. If you find a file, save its name AND its `fileId`.

---

## 3. Forensic Debugging via SQLite
When n8n logs aren't enough, the source of truth is the database.

### Accessing Execution Blobs
n8n stores every node execution in a flattened array inside `execution_data.data`. To find out why a node received "undefined":

```bash
# Extract the binary/text blob for an execution ID
sqlite3 ~/.n8n/database.sqlite "SELECT data FROM execution_data WHERE executionId = 334;" > execution.json
```

### Investigating the Workflow State
You can check the current "Live" nodes of a workflow directly in SQL to identify logic bugs in expressions:
```bash
sqlite3 ~/.n8n/database.sqlite "SELECT nodes, connections FROM workflow_entity WHERE id = 'WORKFLOW_ID';"
```

---

## 4. Live Patching Protocol (UI-less)
If you are an agent and can't use the n8n UI, you can "Hot Patch" a workflow logic using Python/SQLite:
1. Read the `nodes` column.
2. Parse JSON.
3. Modify the `parameters.jsCode` or `parameters.rules`.
4. Update via SQL.
5. **CRITICAL**: The changes only apply to *new* executions.

---

## 5. Lessons from Case #334
*   **404 Errors in Drive**: Usually due to the Actor hallucinating a `fileId` because the Planner didn't provide a structured list from the previous search results.
*   **JSON Parsing**: Models occasionally add markdown backticks. The `Clean Actor` node MUST have a robust regex/substring extraction for `{ ... }`.

---
*Documented with autonomy by Vega.*
