# ReCircle: Smart Recycling Assistant

**Code Clash 2.0 — Track 06** | Computer Vision × Digital Twin × Generative AI

---

## One-Paragraph Pitch

ReCircle helps people sort waste correctly and shows how individual actions change a whole recycling system. A user points a camera at an item; computer vision classifies it into recyclable, reusable, biodegradable, hazardous, or residual waste. Every scan feeds a digital twin of a campus waste flow (source → bin → collection → facility). A generative AI advisor reads the twin's computed metrics and gives personalized, grounded recommendations that push the system toward a circular economy.

---

## Architecture

```
┌─────────────────┐     REST / SSE     ┌──────────────────────────────────────┐
│  React SPA      │ ◄────────────────► │  FastAPI /api/v1                     │
│  (Vite, TS,     │                    │  ├─ Auth + RBAC (JWT)                │
│   Tailwind,     │                    │  ├─ Vision: MobileNetV3/ResNet18      │
│   React Flow,   │                    │  ├─ Twin: Graph + Sim Engine + Metrics │
│   Recharts)     │                    │  ├─ Advisor: LLM Client + Validator  │
└─────────────────┘                    │  └─ Report Service                   │
                                       │  ▼ SQLite / Postgres                 │
                                       └──────────────────────────────────────┘
```

---

## Quick Start

```bash
# 1. Clone and enter
cd recircle

# 2. Copy environment template
cp .env.example .env
# Edit .env with your API keys (LLM_PRIMARY_API_KEY, etc.)

# 3. Start everything (API:8000, Web:5173)
make dev
# or: docker compose up --build
```

### Local Development URLs
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Environment Setup

All variables in `.env.example`:

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | Yes | `dev` or `prod` |
| `DEMO_MODE` | Yes | Enables demo accounts & guest endpoints |
| `DATABASE_URL` | Yes | SQLite path or Postgres URL |
| `JWT_SECRET` | Yes | Token signing secret (32+ chars) |
| `JWT_ACCESS_MINUTES` | Yes | Access token lifetime (default 15) |
| `CORS_ORIGINS` | Yes | Exact allowed frontend origins |
| `MODEL_PATH` | Yes | Path to trained weights (`.pt`) |
| `CONFIDENCE_THRESHOLD` | Yes | Unsure cutoff (default 0.60) |
| `MAX_UPLOAD_MB` | Yes | Upload size limit (default 5) |
| `RATE_LIMIT_PER_MIN` | Yes | Requests per minute per IP |
| `LLM_PRIMARY_PROVIDER` | Yes | `openai` or `anthropic` |
| `LLM_PRIMARY_MODEL` | Yes | e.g., `gpt-4o-mini` |
| `LLM_PRIMARY_API_KEY` | Yes | Primary LLM API key |
| `LLM_FALLBACK_PROVIDER` | Yes | Fallback provider |
| `LLM_FALLBACK_MODEL` | Yes | Fallback model |
| `LLM_FALLBACK_API_KEY` | Yes | Fallback API key |
| `LLM_TIMEOUT_SECONDS` | Yes | Per-call timeout (default 20) |
| `VITE_API_BASE_URL` | Yes | Backend base URL for frontend |

---

## Dataset & License

- **Dataset**: [Kaggle Garbage Classification](https://www.kaggle.com/datasets/mostafaabla/garbage-classification)
- **License**: CC0 / MIT (verify on download)
- **Classes**: 12 source labels → mapped to 5 output classes (recyclable, reusable, biodegradable, hazardous, residual)
- **Mapping**: See `ml/configs/classes.yaml`

---

## Team Roles

| Role | Person | Primary Tickets |
|------|--------|-----------------|
| ML Lead | | RC-010–014 |
| Backend Lead | | RC-001–003, 013–025, 030–034, 060–062, 070 |
| Frontend Lead | | RC-040–050, 071 |
| DevOps / Full-Stack | | RC-001–003, 061, 043, 044, 070–074 |

---

## Demo Credentials (when DEMO_MODE=true)

| Role | Email | Password |
|------|-------|----------|
| Guest | — | — (no login needed) |
| Resident | resident@demo.recircle | demo123 |
| Manager | manager@demo.recircle | demo123 |
| Admin | admin@demo.recircle | demo123 |

---

## Submission Bundle

- **Slide Deck**: 10 slides (Problem, Solution, Architecture, Demo, Results, Team, Next Steps)
- **GitHub**: Clean `main` branch, this README, demo credentials
- **Deployed Link**: Working demo on Vercel/Render/HF Spaces
- **Drive Folder**: Project files, backup video, slide deck (PPT)

---

## License

MIT License — see LICENSE file.

---

## Commands Reference

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for ML/local backend)
- Node.js 18+ (for frontend)
- Kaggle API token (for dataset): `~/.kaggle/kaggle.json`

### Quick Start (Docker)
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 2. Start all services (API:8000, Web:5173)
make dev
# or: docker compose up --build

# 3. With Postgres (optional)
make dev-postgres
# or: docker compose --profile postgres up --build
```

### ML Pipeline
```bash
# Download dataset from Kaggle
make data
# or: cd ml && python scripts/download_data.py && python scripts/prepare_dataset.py

# Train classifier (MobileNetV3-Small, 8 epochs)
make train
# or: cd ml && python scripts/train.py

# Evaluate on test set + own photos
make eval
# or: cd ml && python scripts/evaluate.py

# Export model for backend (ONNX/TorchScript)
make export-model
# or: cd ml && python scripts/export.py
```

### Development
```bash
# Backend tests
make test
make test-cov

# Linting
make lint

# Format backend code
make fmt

# View logs
make logs-log        # Follow build.log
make logs-errors     # Show all errors
make logs-ml         # ML training/eval logs
make logs-api        # API logs
make logs-frontend   # Frontend logs
make logs-docker     # Docker logs

# Clean build artifacts
make clean
```

### Frontend Setup (First Time)
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install @tanstack/react-query zustand react-flow recharts tailwindcss @tailwindcss/vite
npm install -D typescript @types/react @types/node
npm run dev
```

### Backend Local (Without Docker)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env .env
uvicorn app.main:app --reload --port 8000
```

### Deployment
```bash
# Backend (Docker) - configure CI/CD for Render/Railway/HF Spaces
make deploy-backend

# Frontend - configure CI/CD for Vercel/Netlify
make deploy-frontend

# Smoke test deployed URLs
make smoke

# Warm up API before demo (10 min prior)
make warmup

# Seed demo data
make seed
```

### Demo Mode
```bash
# Enable in .env
DEMO_MODE=true
# No login needed for Guest access
# Demo accounts:
#   Resident: resident@demo.recircle / demo123
#   Manager:  manager@demo.recircle  / demo123
#   Admin:    admin@demo.recircle    / demo123
```