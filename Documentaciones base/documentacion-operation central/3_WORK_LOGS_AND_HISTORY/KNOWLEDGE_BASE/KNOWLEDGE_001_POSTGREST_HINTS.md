# 💡 KNOWLEDGE entry: POSTGREST RELATIONSHIP HINTS (001)

## Context
When using Supabase (PostgREST) to fetch related data across tables, the system automatically detects relationships based on Foreign Keys. However, in complex schemas or after schema changes, this detection can fail.

## Key Learning
- **Ambiguity**: If there are multiple foreign keys between two tables, you MUST provide a hint.
- **Syntax**: Use the `!constraint_name` syntax in the select string.
- **Example**:
  ```typescript
  .select(`*, owner:profiles!tasks_user_id_fkey(*)`)
  ```
- **Cache**: Sometimes PostgREST needs a manual reload to "see" new FKs:
  ```sql
  NOTIFY pgrst, 'reload schema';
  ```

## Why it matters
Without hints, Supabase returns a `400 Bad Request`, which can be hard to debug as it looks like a syntax error but is actually a schema resolution error.

---
*Vega OS Kernel - Knowledge Optimization*
