# Folder & File Structure

## 6.1 Repository Tree

```
recircle/
├── README.md                    # what it is, quick start, architecture
├── docker-compose.yml           # api + web for local and backup demo
├── Makefile                     # make dev, make test, make train, make deploy
├── .env.example                 # every variable, no secrets
├── .gitignore                   # .env, weights/, node_modules, __pycache__
├── docs/
│   ├── index.md                 # this pack overview
│   ├── prd.md                   # Product Requirements Document
│   ├── trd.md                   # Technical Requirements Document
│   ├── security.md              # Security & Access
│   ├── frontend-spec.md         # Frontend Specification
│   ├── tickets.md               # Feature Ticket List
│   ├── architecture.png         # architecture diagram
│   └── demo-script.md           # 3-minute demo script
├── ml/
│   ├── README.md                # dataset source, licence, how to reproduce
│   ├── configs/
│   │   └── classes.yaml         # source label to output class and subtype
│   ├── scripts/
│   │   ├── download_data.py     # download dataset
│   │   ├── prepare_dataset.py   # mapping and train/val/test split
│   │   ├── train.py             # fine-tune classifier
│   │   ├── evaluate.py          # confusion matrix, per-class recall
│   │   └── export.py            # writes weights for the backend
│   ├── reports/                 # metrics.json, confusion_matrix.png
│   ├── weights/                 # git-ignored; downloaded or copied at deploy
│   └── own_photos/              # small realism test set (committed or on Drive)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # app factory, middleware, router mount
│   │   ├── core/
│   │   │   ├── config.py        # settings from env
│   │   │   ├── security.py      # hashing, JWT, role dependencies
│   │   │   ├── rate_limit.py
│   │   │   └── logging.py       # structured logs, request_id
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   ├── auth.py
│   │   │   ├── scan.py
│   │   │   ├── history.py
│   │   │   ├── twin.py
│   │   │   ├── simulate.py
│   │   │   ├── advice.py
│   │   │   ├── chat.py
│   │   │   ├── reports.py
│   │   │   ├── admin.py
│   │   │   └── health.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── scan.py
│   │   │   ├── twin.py
│   │   │   └── advice.py
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── vision/
│   │   │   │   ├── classifier.py    # model load and predict
│   │   │   │   ├── preprocess.py    # validate, strip EXIF, resize
│   │   │   │   ├── fallback.py      # low-confidence path
│   │   │   │   └── guidance.py      # class to bin and steps
│   │   │   ├── twin/
│   │   │   │   ├── graph.py         # nodes, edges, state
│   │   │   │   ├── engine.py        # tick simulation
│   │   │   │   ├── metrics.py
│   │   │   │   ├── events.py        # scan ingestion, SSE bus
│   │   │   │   └── generator.py     # demo traffic
│   │   │   ├── advisor/
│   │   │   │   ├── llm_client.py    # providers, failover, cache
│   │   │   │   ├── prompts.py       # build input, system prompt
│   │   │   │   ├── advisor.py       # call, validate, fallback
│   │   │   │   └── guard.py         # injection and number checks
│   │   │   └── reports/
│   │   ├── data/
│   │   │   ├── classes.json
│   │   │   ├── bin_rules.json
│   │   │   ├── emission_factors.json
│   │   │   ├── twin_seed.json
│   │   │   ├── sample_advice.json   # cached advice for guests and LLM outage
│   │   │   └── knowledge/           # short disposal and reuse notes (markdown)
│   │   └── db/
│   │       ├── session.py
│   │       └── seed.py              # demo users, topology, history
│   └── tests/
│       ├── test_twin_engine.py      # determinism and metric cases
│       ├── test_scan_api.py         # upload validation, contract
│       ├── test_advisor_guard.py    # invented numbers rejected
│       └── test_access.py           # role matrix and IDOR
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   index.html
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── routes.tsx
│       ├── api/
│       │   ├── client.ts            # fetch wrapper, auth, typed errors
│       │   ├── scan.ts
│       │   ├── twin.ts
│       │   ├── simulate.ts
│       │   ├── advice.ts
│       │   └── auth.ts
│       ├── pages/
│       │   ├── Landing.tsx
│       │   ├── Scan.tsx
│       │   ├── Twin.tsx
│       │   ├── Simulate.tsx
│       │   ├── Impact.tsx
│       │   ├── Advisor.tsx
│       │   ├── History.tsx
│       │   ├── Facility.tsx
│       │   └── Login.tsx
│       ├── components/
│       │   ├── ui/                  # buttons, cards, badges, sliders, drawer
│       │   ├── layout/              # Shell, NavBar, TabBar, StatusBanner
│       │   ├── scan/                # CameraCapture, ResultCard, UncertainState
│       │   ├── twin/                # TwinGraph, nodes, MetricStrip, NodeDrawer
│       │   ├── simulate/            # ScenarioPanel, CompareChart
│       │   └── advisor/             # AdviceCards, AdvisorChat
│       ├── hooks/                   # useTwinStream, useCamera, useDebounce
│       ├── stores/                  # scanSession.ts, scenario.ts, ui.ts
│       ├── lib/                     # image.ts (downscale), format.ts, classMeta.ts
│       ├── types/                   # API types shared across the app
│       ├── styles/                  # tokens.css, globals.css
│       └── scripts/
│           ├── smoke_test.sh        # hits health, scan sample, twin, advice, warmup
│           ├── warmup.sh            # pings deployed API before demo
│           └── seed_demo.sh         # resets demo data
```

## 6.2 Environment Variables (all in `.env.example`)

| Variable | Used By | Purpose |
|----------|---------|---------|
| APP_ENV | API | `dev` or `prod` |
| DEMO_MODE | API | Enables demo accounts and guest endpoints |
| DATABASE_URL | API | SQLite path or Postgres URL |
| JWT_SECRET, JWT_ACCESS_MINUTES | API | Token signing and lifetime |
| CORS_ORIGINS | API | Exact allowed frontend origins |
| MODEL_PATH, CONFIDENCE_THRESHOLD | API | Weights file and unsure cut-off |
| MAX_UPLOAD_MB, RATE_LIMIT_PER_MIN | API | Upload size and request limits |
| LLM_PRIMARY_PROVIDER, LLM_PRIMARY_MODEL, LLM_PRIMARY_API_KEY | API | Main advisor model |
| LLM_FALLBACK_PROVIDER, LLM_FALLBACK_MODEL, LLM_FALLBACK_API_KEY | API | Backup model |
| LLM_TIMEOUT_SECONDS | API | Per-call timeout |
| VITE_API_BASE_URL | Web | Backend base URL (public value, no secrets) |

## 6.3 Conventions

**Branches**: `main` is always deployable. Work on `feat/RC-0xx-short-name`, merge by small PR or fast-forward after quick review.

**Commits**: Start with ticket id, e.g., `RC-022 add tick loop and seeded RNG`

**Ports**: API 8000, Web 5173

**Naming**: Python in snake_case, React components in PascalCase, one component per file, API types mirrored in `frontend/src/types`

**Contract first**: Agree the JSON shapes in Section 2.7 before coding. Backend and frontend then build in parallel against a mock if needed.

---

## README Must Include

- One-paragraph pitch
- Architecture image
- Quick start (`make dev`)
- Env setup
- Dataset and licence note
- Team roles
- Demo credentials for judges

## Submission Bundle

- PPT
- GitHub link
- Deployed link
- Drive folder with project files
- Submitted through form before 4:30 PM on 16 October