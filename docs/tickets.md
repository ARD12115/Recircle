# Feature Ticket List

## Estimates & Capacity

| Team Size | Total Hours | Notes |
|-----------|-------------|-------|
| 4 people | ~39 hrs | Slack for P1 work |
| 3 people | ~39 hrs | Tight but workable |
| 2 people | ~26 hrs | Use cut list (Section 5.3) |

**P0 tickets**: ~32 person-hours (must ship)
**P1 tickets**: ~7 person-hours (should ship)
**P2 tickets**: ~5 person-hours (only if time remains)

---

## E0 Setup

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-001 | Init monorepo, FastAPI and Vite skeletons, lint, .env.example | P0 | 0.75 | BE, FE | none | Both apps start locally |
| RC-002 | Seed files: class map, bin rules, emission factors (placeholders), twin topology | P0 | 0.5 | BE | none | Files load without errors |
| RC-003 | Docker Compose and Makefile | P1 | 0.5 | BE | RC-001 | `docker compose up` works from clean |

---

## E1 Vision (ML: model and data)

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-010 | Download dataset, map to 5 classes, make train/val/test split | P0 | 1.0 | ML | RC-001 | Class counts printed, split saved |
| RC-011 | Fine-tune classifier and save weights | P0 | 1.5 | ML | RC-010 | Val accuracy ≥ 80% on first pass |
| RC-012 | Eval script: confusion matrix, per-class recall, own-photo set | P0 | 0.5 | ML | RC-011 | Metrics.json & confusion_matrix.png chart saved |
| RC-013 | POST /scan: validate, preprocess, infer, top-3, guidance lookup | P0 | 1.0 | BE | RC-011, RC-002 | Returns contract in 2.7 under 500 ms |
| RC-014 | Low-confidence fallback and unsure path | P1 | 1.0 | BE | RC-013, RC-002 | Blurry photo returns unsure result |

---

## E2 Digital Twin

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-020 | Twin graph schema, seed campus topology, GET /twin and metrics.json | P0 | 1.0 | BE | RC-002 | Graph and metrics return as JSON |
| RC-021 | POST /scan → twin event ingestion | P0 | 0.75 | BE | RC-013, RC-020 | A scan changes node counts |
| RC-022 | Simulation engine with seeded RNG (compliance, contamination, yield) | P0 | 2.0 | BE | RC-020 | Same seed gives same output |
| RC-023 | Metrics: diversion, contamination, CO2e, pickup cost | P0 | 1.0 | BE | RC-022 | Unit tests pass on hand-computed cases |
| RC-024 | POST /simulate: baseline vs scenario deltas | P0 | 0.75 | BE | RC-023 | Deltas returned for all KPIs |
| RC-025 | Demo traffic generator and SSE stream | P0 | 1.0 | BE | RC-021 | Events stream to a curl client |

---

## E3 Advisor

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-030 | LLM client: provider config, failover, timeout, cache | P0 | 1.0 | BE | RC-001 | Fallback triggers when primary forced to fail |
| RC-031 | Advice prompt, Pydantic schema, number validator, template fallback | P0 | 1.5 | BE | RC-030 | Invented figures rejected in test |
| RC-032 | POST /advice with cached sample for guests | P0 | 0.5 | BE | RC-031, RC-023 | Works with LLM disabled |
| RC-033 | POST /chat streaming | P1 | 1.0 | BE | RC-030 | Tokens stream to client |
| RC-034 | Report endpoint (markdown to PDF) | P2 | 1.0 | BE | RC-031 | Downloadable report |

---

## E4 Frontend

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-040 | App shell, routing, tokens, API client, status banner | P0 | 1.0 | FE | RC-001 | All routes render placeholders |
| RC-041 | Scan page with CameraCapture upload fallback and client downscale | P0 | 1.25 | FE | RC-040 | Works on phone browser |
| RC-042 | ResultCard, UncertainState, confirm-bin action | P0 | 1.0 | FE | RC-041, RC-013 | Result shows within 3s |
| RC-043 | TwinGraph, MetricStrip, useTwinStream | P0 | 2.5 | FE | RC-020, RC-025, RC-040 | Count updates live after scan |
| RC-044 | Simulate page: ScenarioPanel, CompareChart | P0 | 2.0 | FE | RC-024 | Slider change shows deltas |
| RC-045 | Impact page | P0 | 1.0 | FE | RC-023 | KPIs match API |
| RC-046 | AdviceCards | P0 | 1.25 | FE | RC-032 | Cards render from sample JSON |
| RC-047 | AdvisorChat | P1 | 1.0 | FE | RC-033 | Streaming reply visible |
| RC-048 | History page | P1 | 0.75 | FE | RC-013 | Lists past scans |
| RC-049 | Facility page (bin fill, hotspots) | P1 | 1.25 | FE | RC-021 | Hotspot list renders |
| RC-050 | Loading, empty, error states, accessibility and mobile pass | P0 | 1.25 | FE | RC-042, RC-043, RC-044 | Passes checks in 4.10 |

---

## E5 Auth & Security

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-060 | JWT auth, roles, demo accounts | P1 | 1.5 | BE | RC-001 | Role matrix enforced in tests |
| RC-061 | Upload hardening, rate limits, CORS, security headers | P0 | 1.0 | BE | RC-013 | Checklist items in 3.7 pass |
| RC-062 | Prompt-injection guards and secrets check | P0 | 0.5 | BE | RC-030 | Injection test strings don't change behavior |

---

## E6 Deploy & Submit

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-070 | Backend deploy (Docker) and env wiring | P0 | 1.0 | BE | RC-013 | Public /health returns OK |
| RC-071 | Frontend deploy | P0 | 0.5 | FE | RC-040 | Public URL loads and calls API |
| RC-072 | Smoke test script, warm-up routine, backup video, local fallback | P0 | 0.75 | All | RC-070, RC-071 | `smoke_test.sh` exits 0 |
| RC-073 | README, repo hygiene, Google Drive folder with Slide deck and 3 demo rehearsals | P0 | 0.5 | FE | none | Stranger can run the project |
| RC-074 | Submit the form (PPT, GitHub, deployed link, Drive) | P0 | 0.25 | All | RC-072 | Confirmation received |

---

## Additions (P2 - Can Drop)

| ID | Ticket | Pri | Est | Role | Depends On | Done When |
|----|--------|-----|-----|------|------------|-----------|
| RC-080 | Flow data adapter: map /twin nodes/edges to Sankey links | P2 | 0.5 | FE | RC-020, RC-043 | Unit test: link values = edge weights |
| RC-081 | FlowSankey component, Graph/Flow toggle, legend, tooltip, hidden table | P2 | 1.5 | FE | RC-080 | Scan updates link within 1s |
| RC-082 | Baseline vs scenario Sankey on /simulate (stretch) | P2 | 1.0 | FE | RC-044, RC-081 | Both diagrams from one /simulate response |

---

## 5.2 Schedule (Indicative)

| Block | Time | Focus | Milestone |
|-------|------|-------|-----------|
| Day 1, 10:00–10:45 | Kickoff & briefing, repo init (RC-001, RC-002) | |
| Day 1, 10:45–12:30 | ML: dataset & training (RC-010, RC-011). BE: twin schema (RC-020). FE: shell (RC-040) | |
| Day 1, afternoon–16:30 | ML: eval (RC-012). BE: /scan, ingestion, engine (RC-013, 021, 022). FE: camera & result UI (RC-041, 042) | M1: live scan shows result |
| Day 1, 16:30–22:00 | BE: metrics, simulate, advisor, twin UI (RC-023, 024, 030, 031, 032). FE: twin UI, simulate UI, impact, advice cards (RC-043, 044, 045, 046) | M2: scan→twin→what-if→advice end-to-end |
| Day 2, 10:00–13:00 | Bug fixes, auth, security, accessibility pass (RC-048, 049, 060, 061, 062) | P0 feature freeze |
| Day 2, 13:00 | **P0 FREEZE** — no new features | |
| Day 2, 13:00–14:30 | Deploy, hardening, smoke test (RC-070, 071, 072) | Deployed and warm |
| Day 2, 14:30–16:00 | 3 clean rehearsals, backup video (RC-073) | Demo ready |
| Day 2, 16:00–16:30 | Submit with buffer (RC-074) | Submitted |

---

## 5.3 Cut List for 2-Person Team

**In this order, drop or simplify:**

1. Replace SSE with 3-second polling (RC-025, saves ~0.5h)
2. Render static twin graph without edge animation (RC-043, saves ~1h)
3. Fold Impact page into twin metric strip (RC-045, saves ~1h)
4. Use template advice only + cached sample (RC-031, saves ~0.75h)
5. Skip: RC-014, RC-033, RC-047, RC-048, RC-049, RC-080–082

**Add RC-080 and RC-081 to cut list as first items to drop.**

---

## 5.4 Definition of Done

A ticket is done when:
- Its "Done when" check passes
- Code is merged to main
- No console or server errors on demo path
- Any new env variable is in `.env.example`