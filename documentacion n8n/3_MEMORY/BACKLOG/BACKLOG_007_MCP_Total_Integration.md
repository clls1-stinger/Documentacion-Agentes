# 🔌 BACKLOG 007: MCP Total Integration

> "Universal Connectivity for the Agent"

## Objective
Fully integrate the **Model Context Protocol (MCP)** into the n8n agent, allowing it to dynamically connect to any standard MCP Server (Filesystem, Git, GitHub, Postgres, Slack, etc.) without requiring custom node code for each integration.

## Context
Currently, we have ad-hoc integrations (Puppeteer script, custom Python scripts). The goal is to standardize tool access via MCP.
User Request: "agregar a backlog que quiero agregar los mcp al agente".

## Implementation Strategy

### 1. MCP Client Node (The Interface)
- Create or Install a generic **n8n MCP Client Node**.
    - **Input**: Server Config (Command/Env) + Tool Name + Arguments.
    - **Output**: JSON Result.
- *Alternative*: Use the python-mcp-sdk wrapped in an `Execute Command` node as a bridge.

### 2. Configuration Management (`mcp_config.json`)
- Maintain a central registry of available MCP servers in `/home/emky/.gemini/antigravity/mcp_config.json`.
- The Agent should be able to read this config to know what tools are available.

### 3. Dynamic Tool Discovery
- **Planner Phase**: The planner needs to know which tools are available.
- **Action**: Implement a "List Tools" step where the Agent queries the MCP Client for `extensions/list_tools` and injects them into the Planner's context.

## Priority
**High** - Enabler for massive capability expansion.
Requested by User on 2026-02-03.
