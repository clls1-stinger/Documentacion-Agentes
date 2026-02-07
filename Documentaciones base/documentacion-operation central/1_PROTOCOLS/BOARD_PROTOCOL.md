# 📋 Board Protocol (v4.0 - Three Worlds Architecture)

> Logic, interactions, and state management for the npmx-style Scrum Board.

## Spatial Architecture: The "Three Worlds"
The board is no longer a single flat scroll. It is divided into three specialized full-page "Worlds" managed via the Operational Header:

1.  **Scrum Board (Active Context)**: The main horizontal layout.
    - **Independent Column Scrolling**: Each column (e.g., READY, IN PROGRESS) scrolls vertically within its own container. The main viewport remains fixed (`overflow-hidden`).
    - **Column Width**: Fixed at `340px` to maintain consistent density.
2.  **Backlog Reservoir (Planning context)**: A full-page grid view for unassigned or long-term tasks.
    - Features a simplified card style optimized for scanning.
    - Provides a "Move to Protocol" quick action to release tasks into the "Ready" column.
3.  **Execution Archive (History context)**: A grayscale, faded view of all "Done" tasks.
    - Transitions to full color on hover to signify "Reactivation potential".
    - Displays a specialized "Protocol finalized" subtitle for each record.

## Navigation & Interface
- **Sticky Hide-on-Scroll Header**: Maximizes vertical focus by hiding when scrolling down and reappearing on upward movement.
- **Analytics Metadata Bar**: Integrated mono-spaced counters in the header showing `GLOBAL OPS` (total archived tasks) and `MY PROTOCOLS` (personal archive count) for real-time performance tracking.
- **Vertical Utility Tabs**:
    - **Backlog Tab**: Persistent trigger on the left edge that slides out a high-speed "Backlog Reservoir" sidebar without leaving the current view.
    - **New Task Tab**: Persistent trigger for the Task Drawer.

## Interaction Policies
- **Drag & Drop**: Powered by `@hello-pangea/dnd` with **Optimistic Updates**.
- **Task Drawer**: Sliding panel (Spring transition). Supports full editing of content, priority, tags, and collaborators.
- **Search Logic**: Global real-time filtering across all worlds and columns (Filters by content, description, and tags).

## Board Structure
- **Columns**: `id`, `title`, `position`.
- **Tasks**: `id`, `content`, `column_id`, `position`, `subtasks` (JSONB), `user_id` (UUID), `description` (TEXT), `priority` (TEXT), `emoji` (TEXT), `tags` (TEXT[]), `due_date` (TIMESTAMPTZ), `reminder_at` (TIMESTAMPTZ).

---
*Vega OS Kernel - Productivity Module*
