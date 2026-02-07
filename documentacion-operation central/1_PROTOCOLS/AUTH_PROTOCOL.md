# 🔐 Authentication Protocol

> How we handle users and persistent sessions.

## Tech Stack
- **Provider**: Supabase Auth
- **Session Strategy**: JWT stored in localStorage (default Supabase behavior)
- **Hooks**: `onAuthStateChange` used in `App.tsx` for real-time reactivity.

## Implementation Details
1. **Supabase Client**: Initialized in `lib/supabase.ts`.
2. **Auth Component**: Located in `components/Auth.tsx`, handles Magic Links and Password flows.
3. **Protected Routes**: Currently, search is public, but user status is reflected in the header.

## Future Plans
- Persistent package favorites for logged-in users.
- Custom user profiles and download history.

---
*Vega OS Kernel - Persistence Module*
