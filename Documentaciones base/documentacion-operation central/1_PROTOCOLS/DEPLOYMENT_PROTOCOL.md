# 🚀 Deployment Protocol (v4.0)

> Operational procedures for deploying the Vega Scrum Master "Three Worlds" environment.

## Architecture Stack
- **Frontend**: Astro + React + Vite.
- **Backend**: Supabase (PostgREST + Realtime + Auth).
- **Containerization**: Docker + Docker Compose.
- **Orchestration**: Nginx (serving static assets).

## Environment Variables
The system requires a `.env` file at the root with the following parameters:
- `PUBLIC_SUPABASE_URL`: Your project endpoint.
- `PUBLIC_SUPABASE_ANON_KEY`: Client-side access key.
- `SUPABASE_SERVICE_ROLE_KEY`: Admin-level key (for migrations).
- `ADMIN_USER`: Root operator designation.
- `ADMIN_PASS`: Root operator credentials.

## Deployment Flow (Local/Portainer)
1.  **Preparation**: Ensure `.env` is populated correctly.
2.  **Snapshot**: Run `python3 bin/snapshot.py` to document the current state.
3.  **Build & Deploy**:
    ```bash
    docker-compose -f scrum-master-stack.yml up --build -d
    ```
4.  **Verification**: 
    - Check logs: `docker logs scrum-master-v2`
    - Healthcheck: Access `http://localhost:5173`

## Persistence
- Critical knowledge history is stored in `/app/data/context.sqlite`.
- This file is mounted as a volume in the Docker Stack to ensure continuity across deployments.

## Troubleshooting
- **400 Bad Request**: Verify RLS policies and `profiles` table existence.
- **Build Failures**: Check that `PUBLIC_` prefix is present for client-side variables in the Docker `ARG` phase.

---
*Vega OS Kernel - Infrastructure Module*
