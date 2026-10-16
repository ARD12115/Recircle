# Technical Requirements Document (TRD)

## 2.1 Architecture

```
[Browser: React SPA] │ REST (JSON, multipart) ▲ SSE (twin events, chat tokens) ▼
[FastAPI app /api/v1] ───────────────────────────────────────────┐
├─ Auth + RBAC (JWT) │
├─ Vision service ── PyTorch classifier (MobileNetV3 / ResNet18)│
│ └─ low confidence → fallback (zero-shot / vision LLM) │
├─ Twin service ── graph state + simulation engine + metrics │
├─ Advisor service ── LLM client (primary + fallback) + validator│
└─ Report service │
▼
[SQLite or Postgres: users, scans, nodes, edges, snapshots, advice]◄┘
```

## 2.2 Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | React 18, TypeScript, Vite, Tailwind, TanStack Query, Zustand, React Flow, Recharts | Fast to build, strong graph and chart support |
| Backend | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy | Same language as ML code, auto-generated OpenAPI docs |
| ML | PyTorch, torchvision, MobileNetV3-Small or ResNet18 with transfer learning | Small and CPU-friendly at inference |
| Database | SQLite locally, Postgres if host provides it | Zero setup |
| Realtime | Server-Sent Events | One-way twin updates, simpler than WebSockets |
| LLM | Provider-agnostic client (OpenAI-compatible endpoints or Anthropic API), primary plus fallback | Avoids single point of failure |
| Hosting | Frontend on Vercel/Netlify; Backend on Render, Railway, or Hugging Face Spaces (Docker) | Free tiers, quick deploy |
| Tooling | Docker Compose, Makefile, pytest, ESLint, Ruff | Reproducible local runs |

## 2.3 Computer Vision Module

### Classes
Map a public 12-class garbage dataset (e.g., Kaggle Garbage Classification) into five output classes:

| Source Label | Output Class | Subtype |
|--------------|--------------|---------|
| cardboard, paper | recyclable | paper / cardboard |
| plastic | recyclable | plastic |
| metal | recyclable | metal |
| white / brown / green glass | recyclable | glass |
| clothes, shoes | reusable | textile / footwear |
| biological | biodegradable | organic |
| battery | hazardous | battery |
| trash | residual | mixed / non-recyclable |

> Check the dataset's licence and actual class list when you download it.

### Model
- Fine-tune pretrained MobileNetV3-Small or ResNet18 (ImageNet weights) at 224 px for 5–8 epochs
- Augment with flips, rotation, color jitter, random crops
- Use class-weighted loss to protect hazardous recall

### Inference
- Softmax, top-3, temperature-scaled confidence
- Start with 0.60 confidence threshold; tune on validation set

### Fallback
- Below threshold → call zero-shot or vision-LLM check
- If still unsure → return unsure
- When hazardous probability > 0.20 → guidance: "Do not put in general bin, hand to facility staff"

### Evaluation
- Confusion matrix, per-class precision and recall
- Small set of own phone photos as realism check
- Put numbers in the deck

### Serving
- Load model once at startup
- Run on CPU in torch inference mode
- Resize and normalize server-side

## 2.4 Digital Twin

### Graph
**Nodes**: Source (hostel, canteen, library, department blocks), Bin (one per stream), Collection (route), Facility (recycling, compost, hazardous handling, reuse & donation, landfill)

**Edges**: Directed flow with weight (items per tick) and routing probability

**State per node**: counts by class, fill level (bins), contamination rate (bins), throughput (facilities)

### Simulation (discrete ticks; one tick = one simulated day)
1. Generate items per source from seeded, editable waste-mix distribution
2. Each item has a true class. Resident puts it in right bin with probability = compliance parameter, otherwise wrong bin
3. Wrong placements raise bin contamination. Contamination above threshold downgrades batch (yield loss)
4. Collection empties bins on schedule. Facilities apply yield (e.g., recycling 0.85 clean, 0.55 contaminated)
5. Metrics update. Real scan adds one item with predicted class and confirmed bin routing

### Metrics
- **Diversion rate** = items recovered ÷ total items
- **Contamination rate** = misrouted items ÷ items in recyclable and organic bins
- **CO2e avoided** = Σ mass × (virgin factor − recycled factor)
  - Mass from average-item-weight table
  - All factors in `emission_factors.json` (placeholders first; cite EPA WARM before demo)
- **Pickup cost** = trips × cost per trip

### Scenarios
Parameters: compliance, awareness_boost, pickup_frequency, bins_per_stream, facility_yield_override
Engine runs baseline and scenario on same random seed → returns deltas

**Principle**: The twin computes, the LLM explains.

## 2.5 Generative AI Advisor

### Input
JSON summary built by code:
- Top metrics
- Top 3 contamination causes (class pairs)
- Hotspot nodes
- Scenario deltas
- User's scan stats
- Relevant snippets from local disposal knowledge base

### Output Contract (validated with Pydantic)
```json
{
  "summary": "string",
  "issues": [],
  "actions": [
    {"title": "", "why": "", "expected_impact": "", "effort": "", "owner": ""}
  ],
  "reuse_ideas": [],
  "disclaimer": "string"
}
```

### Rules
- The model may not introduce numbers
- Validator checks every figure in output appears in input
- On failure → regenerate once → fall back to template

### Client
- Provider-agnostic, primary + fallback, 20s timeout, one retry
- Response cache keyed by input hash

### Chat
- Same client with system prompt limited to waste, reuse, circular-economy topics
- Tokens stream over SSE

## 2.6 Data Model

| Table | Key Columns |
|-------|-------------|
| users | id, email, password_hash, role, created_at |
| scans | id, user_id, created_at, predicted_class, subtype, confidence, source_node_id, confirmed_bin, image_ref (nullable), latency_ms |
| twin_nodes | id, type, name, config_json |
| twin_edges | id, from_id, to_id, weight, route_prob |
| twin_snapshots | id, tick, metrics_json, created_at |
| scenarios | id, user_id, params_json, result_json, created_at |
| advice_log | id, user_id, input_hash, output_json, provider, created_at |

## 2.7 API (base path /api/v1)

| Method | Path | Purpose | Minimum Role |
|--------|------|---------|--------------|
| POST | /auth/login, /auth/refresh | Sign in, rotate token | public |
| POST | /scan | Multipart image + optional source_node_id; returns classification & guidance | Guest |
| GET | /scans | Scan history | Resident |
| GET | /twin | Graph + current metrics | Guest |
| GET | /twin/stream | SSE twin events | Guest |
| POST | /simulate | Params in; baseline, scenario, deltas out | Guest (rate-limited) |
| POST | /advice | Structured advice (guests get cached sample) | Resident |
| POST | /chat | Streaming advisor chat | Resident |
| POST | /reports | Generate report | Manager |
| GET | /health, /version | Health checks | public |
| POST | /admin/demo/reset, /admin/demo/traffic | Reset or drive demo data | Admin |

**Error format**: `{ "error": { "code", "message", "request_id" } }`

**Example scan response**:
```json
{
  "scan_id": "8f3c1a",
  "predicted_class": "hazardous",
  "subtype": "battery",
  "confidence": 0.93,
  "top3": ["battery 0.93", "metal 0.04", "trash 0.02"],
  "guidance": {
    "bin": "Hazardous collection point",
    "steps": ["Do not crush", "Tape terminals if loose", "Hand to facility staff"],
    "why": "Lithium cells can ignite in compactors",
    "twin_effect": { "node": "Hostel A", "contamination_delta": 0.0 }
  },
  "latency_ms": 410
}
```

OpenAPI docs at `/docs`.

## 2.8 Realtime
- SSE channel emits: `scan.created`, `twin.tick`, `metrics.updated`
- Client reconnects with backoff and falls back to polling every 3 seconds
- Avoid cold starts: model loads at startup

## 2.9 Deployment and Environments

| Environment | Command |
|-------------|---------|
| Local | `docker compose up` starts API and web app |
| Demo | Deployed frontend and backend; ping `/health` 10 min before presenting |
| Backup | Same compose stack on laptop + recorded backup video |

**Config**: All secrets and provider settings from environment variables (see Section 6.2)

## 2.10 Testing

- **ML**: Eval script on fixed test split + smoke set of own phone photos
- **Backend**: pytest for twin determinism (same seed = same result), API contract tests, advisor number-validator
- **Frontend**: Component smoke tests + manual script for demo path
- **Release gate**: `scripts/smoke_test.sh` must exit 0 against deployed URL