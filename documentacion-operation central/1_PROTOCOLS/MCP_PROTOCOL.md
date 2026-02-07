# 🔌 Model Context Protocol (MCP)

> Integration for AI Agents to interact with the Vega Ecosystem.

## Overview
The `operation-center` MCP Server exposes core operational capabilities to AI agents, allowing them to act as autonomous Scrum Masters, developers, or analysts within the system.

## Tech Stack
- **Runtime**: Node.js (TypeScript)
- **Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Transport**: Stdio
- **Database Access**: Supabase Client (Service Role)

## Capabilities (Skills)

### 📋 Board Management
Allows agents to manipulate the Scrum Board state.
- `get_board_state`: Retrieve columns and tasks.
- `create_task`: Inject new protocols (tasks) into the Backlog.
- `update_task`: Modify task attributes, move between columns.
- `complete_task`: Finalize a protocol (move to Done).

### 🧠 Knowledge Access
Allows agents to consult the project's documentation ("Project Brain").
- `list_documentation`: Explore the documentation hierarchy.
- `read_documentation`: Read specific protocol files or logs.

## Setup & Usage
The server is located in `vega-mcp-server/`.
To run:
1. `cd vega-mcp-server`
2. `npm install`
3. `npm run build`
4. `npm start` (or configure your MCP Client to run this command)

## Security
- Uses `SUPABASE_SERVICE_ROLE_KEY` for administrative access.
- Confined to `documentacion/` directory for file access.

---
*Vega OS Kernel - Intelligence Interface*
