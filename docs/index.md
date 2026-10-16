# ReCircle: Project Documentation Pack

**Smart Recycling Assistant for Code Clash 2.0 (Track 06) · Computer Vision × Digital Twin × Generative AI**
Prepared 9 October 2026 for the event on 15–16 October 2026.

---

## In This Pack

1. [PRD](./prd.md) — Product Requirements Document
2. [TRD](./trd.md) — Technical Requirements Document
3. [Security & Access](./security.md) — Security & Access Control
4. [Frontend Spec](./frontend-spec.md) — Frontend Specification
5. [Feature Ticket List](./tickets.md) — Feature Tickets with Estimates
6. [Folder & File Structure](./folder-structure.md) — Repository Layout

---

## Working Assumptions

- **ReCircle** is a working title
- Team of 2 to 4 people
- Tickets are tagged by role (ML, BE, FE), so one person can hold several roles
- Stack follows skills already visible in your repos: Python/FastAPI, React/TypeScript, PyTorch
- Code Clash requires all code to be written during the event — this pack is planning only
- Confirm with organizers whether reusing your own boilerplate is allowed
- Public datasets and pretrained weights count as open-source tools (FAQ allows)

---

## Quick Reference: Success Metrics

| Metric | Target |
|--------|--------|
| Top-1 accuracy on 5 grouped classes (held-out test) | ≥ 85% |
| Recall on hazardous class | ≥ 90% (safety-critical) |
| Scan latency p95 | < 3 s |
| Demo completes without manual restart | 3 of 3 rehearsals |
| Advisor figures match twin figures | 100% (validated in code) |

---

## Demo Script (3 Minutes)

| Time | Action |
|------|--------|
| 0:00 | State problem in one sentence with one sourced statistic |
| 0:20 | Scan plastic bottle, battery, banana peel live — show class, bin, tip |
| 1:00 | Switch to twin — three scans appear as flow, contamination metric updates |
| 1:40 | What-if: raise compliance 60% → 80% — show diversion & CO2e deltas |
| 2:20 | Click Generate advice — ranked actions with effort & impact |
| 2:45 | Close with architecture slide, team roles, next steps |

---

## Judging Alignment

| Criterion | Weight | How ReCircle Scores |
|-----------|--------|---------------------|
| Technical Implementation | 30% | Trained model with eval report, real simulation engine, deployed full stack |
| Innovation & Creativity | 25% | Closed loop: scans drive twin, twin grounds LLM, manager tests changes before spending |
| Practicality & Impact | 20% | Campus pilot framing, measurable KPIs (diversion, contamination, CO2e), cost view |
| Presentation & Demo | 15% | 3-min story: live scan, twin update, advice |
| Teamwork | 10% | Clear role split (ML, BE, FE) shown in deck |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Twin looks fake | Show assumptions on screen, label simulated vs real, expose every parameter |
| LLM outage or slow API | Failover provider, response cache, pre-generated advice for demo scenario |
| Venue Wi-Fi unreliable | Local docker compose fallback + recorded backup video |
| Scope creep | **P0 freeze Day 2 at 1:00 PM** |
| Dataset class imbalance / domain shift | Augmentation, test on own phone photos, confidence threshold with fallback |

---

*Full details in individual docs. Start with [PRD](./prd.md) → [TRD](./trd.md) → [Tickets](./tickets.md).*