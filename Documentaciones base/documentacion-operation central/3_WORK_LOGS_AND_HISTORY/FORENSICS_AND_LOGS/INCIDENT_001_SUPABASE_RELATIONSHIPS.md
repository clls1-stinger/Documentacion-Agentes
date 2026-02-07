# 🚨 INCIDENT REPORT: SUPABASE RELATIONSHIP DETECTION (001)

## Status
**RESOLVED**

## Description
The frontend failed to load tasks highlighting a `400 Bad Request` in the console. The query attempted to join `tasks` with `profiles` but PostgREST could not detect the relationship despite the columns existing.

## Forensics & Analysis
- **Tool used**: `curl` with `service_role` key to bypass RLS and inspect the REST API directly.
- **Discovery**: `PGRST200: Could not find a relationship between 'tasks' and 'profiles'`.
- **Root Cause**: The Foreign Key constraint was either missing or not correctly indexed in the PostgREST schema cache after the initial migration.

## remediation
1. **Explicit Constraints**: Re-applied `FOREIGN KEY` constraints on `tasks(user_id)` and `task_collaborators(user_id)` pointing to `profiles(id)`.
2. **Schema Reload**: Triggered a manual schema reload via `NOTIFY pgrst, 'reload schema'`.
3. **Query Patch**: Updated the frontend to include explicit relationship hints (`!tasks_user_id_fkey`) to avoid ambiguity.

## Prevention
- Always ensure FKs are explicitly named and provided as hints in complex join queries.
- Monitor PostgREST schema cache status during migrations.

---
*Vega OS Kernel - Security & Stability Module*
