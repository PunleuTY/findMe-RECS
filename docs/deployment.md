# Deployment Guide

## Option A — Railway (recommended for personal hosting)

Railway gives you a MySQL addon + Python service + static frontend deploy in one platform.

### Steps

1. **Create a Railway project** and add a MySQL plugin. Note the connection string.

2. **Backend service**
   - Connect your GitHub repo.
   - Set the root directory to `/` (not `backend/`).
   - Set the start command:
     ```
     pip install -r backend/requirements.txt && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - Add environment variables from `.env.example` using your Railway MySQL credentials.

3. **Frontend service**
   - Add a second service in the same Railway project.
   - Set root directory to `frontend/`.
   - Build command: `npm install && npm run build`
   - Start command: `npm start`
   - Add env var: `NEXT_PUBLIC_API_BASE=<your-backend-url>`

4. **Database setup**
   ```bash
   mysql -h <railway-host> -P <port> -u <user> -p<password> <db> < backend/database/schema.sql
   ```

---

## Option B — Render

Similar to Railway. Create two web services (backend + frontend) and one MySQL instance.

- Backend: Python runtime, `pip install -r backend/requirements.txt && uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Frontend: Node runtime, build `npm install && npm run build`, start `npm start`

---

## Option C — VPS (DigitalOcean / Linode / Hetzner)

```bash
# Install deps
sudo apt install python3.11 python3.11-venv nodejs npm mysql-server nginx

# Clone and set up
git clone <your-repo>
cd findMe-RS-repo
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# Set up MySQL
mysql -u root -p < backend/database/schema.sql

# Create .env from .env.example and fill in values
cp .env.example .env

# Run backend with systemd or screen
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Build and run frontend
cd frontend && npm install && npm run build
npm start  # runs on port 3000

# Nginx reverse proxy
# → proxy /api/* to localhost:8000
# → proxy /* to localhost:3000
```

---

## Environment variables

| Variable | Description |
|---|---|
| `DB_HOST` | MySQL host |
| `DB_PORT` | MySQL port (default 3306) |
| `DB_NAME` | Database name (default `findme_rs_db`) |
| `DB_USER` | MySQL user |
| `DB_PASSWORD` | MySQL password |
| `CORS_ORIGINS` | Comma-separated frontend origin(s) |
| `RECS_CACHE_TTL_SECONDS` | Cache TTL for recommendations (default 300) |
| `DEFAULT_TOP_N` | Default result count (default 12) |

Frontend:

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_BASE` | Backend API base URL (e.g. `https://api.yourdomain.com`) |
