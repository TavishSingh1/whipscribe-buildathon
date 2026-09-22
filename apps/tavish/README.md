# Podcast Clip Factory

Podcast Clip Factory is a multi-user web app for turning one podcast episode into personalized clips, show notes, and platform-specific social content. It preserves the original WhipScribe + LangGraph prototype, but moves it behind a FastAPI backend and a React/Vite dashboard.

## User Journey

Sign up -> create a creator profile -> optionally connect tools -> upload an episode -> poll a processing job -> review clips, show notes, and X/LinkedIn/Instagram drafts -> edit, copy, download, or publish after confirmation.

## Architecture

```text
Browser
  -> React/Vite frontend
  -> FastAPI backend
  -> authenticated user context
  -> PostgreSQL/Supabase-compatible schema
  -> LangGraph workflow
      -> WhipScribe transcription and clips
      -> OpenAI generation
      -> creator profile and content examples
      -> optional integration adapters
```

## Migration Map

Current -> Keep: `src/whipscribe_client.py`, the LangGraph stage order, and the existing prompt intent.

Current -> Modify: prompts are now builder functions that inject creator profile, episode metadata, and limited historical examples. Notion/Slack are now user-specific connection records and adapters instead of global `.env` credentials.

Current -> Replace: Streamlit is replaced by `frontend/` and `backend/`. The Streamlit prototype remains as a reference.

Current -> New: authentication, user-scoped database models, upload endpoint, processing jobs, persistent results, settings pages, content examples, connection management, migrations, deployment config, and tests.

## Database Schema

The migration in `backend/migrations/001_initial.sql` creates `users`, `creator_profiles`, `content_examples`, `connected_accounts`, `episodes`, `processing_jobs`, `clips`, `show_notes`, `social_posts`, and `usage_records`.

Every private table is scoped by `user_id`. The API never accepts a browser-provided `user_id` as authority.

## Authentication Flow

`POST /auth/signup` and `POST /auth/login` issue JWT bearer tokens. Protected endpoints derive the user from the token server-side and scope all resource access to that user.

## Personalization Flow

Each job loads the transcript, creator profile, episode metadata and one-off overrides, a small set of user-owned writing examples, and optional connected-tool context when adapters are expanded. Prompt builders live in `backend/app/services/prompt_builders.py`.

## Tool Connection Flow

Connections are stored in `connected_accounts` with encrypted token fields. The frontend only sees provider, status, account name, scopes, and metadata. The current MVP includes adapter interfaces for Notion and Slack and intentionally keeps publishing preview-first.

## LangGraph Flow

`transcribe -> find_moments -> render_clips -> generate_show_notes -> generate_social_content -> finalize`

The graph is in `backend/app/worker/graph.py`; job persistence is in `backend/app/worker/processor.py`.

## API Endpoints

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `GET /profile`
- `PUT /profile`
- `GET /content-examples`
- `POST /content-examples`
- `GET /connections`
- `POST /connections`
- `DELETE /connections/{connection_id}`
- `GET /episodes`
- `POST /episodes`
- `GET /episodes/{episode_id}`
- `GET /episodes/jobs/{job_id}`
- `PATCH /episodes/social-posts/{post_id}`

## Frontend Routes

- `/`
- `/login`
- `/signup`
- `/onboarding`
- `/dashboard`
- `/episodes/new`
- `/episodes/:id`
- `/settings/profile`
- `/settings/connections`
- `/settings/content`
- `/settings/publishing`

## Environment Variables

Frontend: `VITE_API_BASE_URL`

Backend: `ENVIRONMENT`, `FRONTEND_ORIGIN`, `DATABASE_URL`, `JWT_SECRET`, `ENCRYPTION_KEY`, `OPENAI_API_KEY`, `WHIPSCRIBE_API_KEY`, `UPLOAD_DIR`, `MAX_UPLOAD_MB`, quota variables, and future Notion/Slack OAuth variables.

No backend secret belongs in Vite variables.

## Local Setup

Backend:

```bash
cd apps/tavish/backend
cp .env.example .env
pip install .
uvicorn app.main:app --reload
```

Frontend:

```bash
cd apps/tavish/frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

## Deployment

Frontend deploys to Vercel from `apps/tavish/frontend` with `npm run build`.

Backend deploys to Render from `apps/tavish/backend` with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Use PostgreSQL/Supabase for `DATABASE_URL`. Run `backend/migrations/001_initial.sql` for production schema creation.

## Testing

```bash
cd apps/tavish/backend
pip install .[test]
pytest
```

Current tests cover prompt personalization and user-scoping/security patterns. Add integration tests with a real test database before production launch.

## Security Checklist

- Protected endpoints require JWT auth.
- User-owned resources are queried with authenticated `user.id`.
- Uploads validate MIME type and size.
- OpenAI and WhipScribe keys are backend-only.
- Connection tokens are not returned to the frontend.
- Optional integrations cannot break core generation.
- `.env` remains ignored.
- CORS is restricted by `FRONTEND_ORIGIN`.
- External publishing is preview/confirmation first.

## Known Limitations

OAuth callbacks for Notion and Slack are adapter-ready but not complete. Background work currently uses FastAPI background tasks; production should move long jobs to a durable worker queue. Local development stores uploads on disk; production should use object storage. Demo mode is documented in configuration but still needs cached demo results.
