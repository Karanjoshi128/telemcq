# TeleMCQ

Scrape MCQs from a Telegram quiz channel into a personal, searchable practice notebook. Practice in a paginated Google-Forms-style UI, then export everything as a styled `.docx`.

**Stack (all free tier):**
- Next.js 15 + Tailwind + shadcn primitives → Vercel
- FastAPI + Telethon + python-docx → Render (free web service)
- Supabase → Postgres + Auth (Google OAuth)
- GitHub Actions → daily cron trigger

---

## 1. Create the Supabase project

1. Go to <https://supabase.com> → **New project** (free tier).
2. Once provisioned, open **SQL Editor** and run:
   - `supabase/migrations/001_init.sql`
   - `supabase/migrations/002_rls.sql`
3. **Authentication → Providers → Google**: toggle it on. Follow the Supabase guide to create a Google OAuth client in <https://console.cloud.google.com>, and paste the client id / secret. Add the Supabase callback URL to the Google app.
4. **Settings → API**: copy `Project URL`, `anon` key, `service_role` key.
5. **Settings → API → JWT Settings**: copy the `JWT Secret`.

## 2. Get your Telegram API credentials

1. Go to <https://my.telegram.org> → log in → **API development tools**.
2. Create an app. Note `api_id` and `api_hash`.

## 3. Generate the session encryption key

```bash
python -c "import os,base64;print(base64.b64encode(os.urandom(32)).decode())"
```

Save the output — you will paste it as `SESSION_ENCRYPTION_KEY`.

## 4. Pick a long random `CRON_SECRET`

Any 40+ char random string. Example:
```bash
python -c "import secrets;print(secrets.token_urlsafe(48))"
```

## 5. Fill credentials

Copy `.env.example` in the repo root — it documents every key.  
Then populate the two runtime env files:

### `backend/.env`
```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
SESSION_ENCRYPTION_KEY=...
CRON_SECRET=...
FRONTEND_ORIGIN=http://localhost:3000
```

### `frontend/.env.local`
```
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## 6. Run locally

### Backend
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

Open <http://localhost:3000>.

Flow:
1. Sign in with Google.
2. **Connect Telegram** → enter phone (with country code) → enter OTP → (2FA password if prompted).
3. **Select a channel** you've joined (the MCQ channel).
4. **Sync now** → MCQs appear.
5. **Practice** → paginated quiz, 10 per page. Answers persist across sessions. Correct/incorrect reveal only for submitted questions.
6. **Search** → full-text search over stored MCQs.
7. **Export DOCX** → styled Word file with your answers.

## 7. Deploy (all free)

### 7a. Supabase
Already live once you completed step 1.

### 7b. Backend → Render
1. Push this repo to GitHub.
2. <https://render.com> → **New + Web Service** → connect the repo → pick **`backend/`** as root dir → **Docker** environment.
3. Instance type: **Free**.
4. Add env vars under **Environment** (same keys as `backend/.env`, but set `FRONTEND_ORIGIN` to your future Vercel URL, e.g. `https://telemcq.vercel.app`).
5. Deploy. Note the URL, e.g. `https://telemcq-api.onrender.com`.

> Free tier sleeps after 15 min idle. The daily GitHub Action wakes it.

### 7c. Frontend → Vercel
1. <https://vercel.com> → **Import Git Repository** → pick **`frontend/`** as root dir.
2. Framework: Next.js (auto-detected).
3. Env vars:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_BACKEND_URL` = your Render URL from 7b
4. Deploy.
5. Back in Supabase → Auth → URL Configuration → add your Vercel URL (e.g. `https://telemcq.vercel.app`) to **Site URL** and **Redirect URLs** (`https://telemcq.vercel.app/auth/callback`).

### 7d. GitHub Actions daily cron
In your repo settings → **Secrets and variables → Actions**, add:
- `BACKEND_URL` = `https://telemcq-api.onrender.com`
- `CRON_SECRET` = same value you set on Render

The workflow at `.github/workflows/daily-scrape.yml` fires at 03:00 UTC daily and triggers `/scrape/all`. You can also run it manually via the Actions tab.

## Architecture

```
Browser ── Next.js (Vercel) ──► FastAPI (Render) ──► Telethon ──► Telegram
                 │                       │
                 └── Supabase Auth       └── Supabase DB (MCQs, answers, sessions)
                                          ▲
                             GitHub Actions cron (daily)
```

## Security notes
- Telegram session strings are encrypted with AES-GCM before DB insert (`SESSION_ENCRYPTION_KEY`).
- Supabase RLS scopes every row to `auth.uid()`.
- Backend verifies the Supabase JWT on every protected endpoint.
- `CRON_SECRET` protects `/scrape/all` from being triggered externally.
- Use only with channels you have joined on your own Telegram account.

## Troubleshooting
- **"No MCQs yet"** — the channel must use native Telegram quiz polls (the format in the project brief). Plain-text MCQs are ignored in v1.
- **Render cold start** — first request after idle takes ~30 seconds; toast will say "Syncing…".
- **Google login loop** — double-check the Supabase Redirect URL includes your production domain + `/auth/callback`.

## License
MIT.
