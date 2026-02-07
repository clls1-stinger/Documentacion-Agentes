# 🗄️ Database Schema

> Current state of the Supabase operational schema for the Scrum Board.

## Tables

### `columns`
Structural elements of the board.
- `id` (TEXT, PK): Unique identifier.
- `title` (TEXT): Display name.
- `position` (INTEGER): Ordering on the board.

### `tasks`
Core operational units.
- `id` (TEXT, PK): Unique identifier.
- `content` (TEXT): Task objective/title.
- `description` (TEXT): Detailed execution parameters.
- `column_id` (TEXT, FK): Reference to `columns.id`.
- `position` (INTEGER): Ordering within the column.
- `subtasks` (JSONB): Array of checklist items `[{id, text, done}]`. **(Encrypted if is_encrypted=true)**
- `user_id` (UUID, FK): Reference to the creator (`auth.users.id`).
- `priority` (TEXT): Urgent, High, Medium, Low.
- `emoji` (TEXT): Identifier icon.
- `tags` (TEXT[]): Obsidian-style tags.
- `due_date` (TIMESTAMPTZ): Target completion date.
- `reminder_at` (TIMESTAMPTZ): Notification trigger time.
- `visibility` (TEXT): Access control (`public` or `private`).
- `is_encrypted` (BOOLEAN): Flag indicating if content/description are client-side encrypted.
- `whiteboard_data` (JSONB): Encapsulated Excalidraw scene data. **(Encrypted if is_encrypted=true)**

### `task_editions`
Traceable history of changes (Chronos Protocol).
- `id` (UUID, PK): Unique identifier.
- `task_id` (TEXT, FK): Reference to `tasks.id`.
- `user_id` (UUID, FK): Who performed the update.
- `edit_type` (TEXT): Nature of change (e.g., `task_update`, `priority_change`).
- `old_value` (JSONB): Snapshot before change.
- `new_value` (JSONB): Snapshot after change.
- `created_at` (TIMESTAMPTZ): Timestamp of the event.

### `task_attachments`
External protocol links.
- `id` (UUID, PK): Unique identifier.
- `task_id` (TEXT, FK): Reference to `tasks.id`.
- `user_id` (UUID, FK): Uploader.
- `file_name` (TEXT): Original filename.
- `file_path` (TEXT): Storage path.
- `file_size` (BIGINT): Size in bytes.
- `content_type` (TEXT): MIME type.
- `created_at` (TIMESTAMPTZ): Upload timestamp.

### `task_collaborators`
Multi-person assignment.
- `task_id` (TEXT): Reference to `tasks.id`.
- `user_id` (UUID): Reference to `profiles.id`.

### `profiles`
User metadata synchronization.
- `id` (UUID, PK): Reference to `auth.users.id`.
- `username` (TEXT): User display name.
- `updated_at` (TIMESTAMPTZ): Last sync time.

---
*Vega OS Kernel - Documentation Module*
