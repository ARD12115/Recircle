# Product Requirements Document (PRD)

## 1.1 Summary

ReCircle is a web app that helps people sort waste correctly and shows what that behavior does to a whole recycling system. A user points a camera at an item. Computer Vision names the material and says whether it is **recyclable**, **reusable**, **biodegradable**, **hazardous**, or **residual**. Every scan feeds a Digital Twin of a campus waste flow (source, bin, collection, facility). A Generative AI advisor reads the twin's computed metrics and gives personalized recommendations that push the system toward a circular economy.

## 1.2 Problem

- **Contamination** (the wrong item in the wrong bin) cuts recovery yield for a whole batch, not just one item
- People are unsure about edge cases: greasy pizza boxes, batteries, mixed-material packaging, clothes
- Facility managers see totals after the fact and cannot test changes (more bins, a new pickup schedule, an awareness campaign) before paying for them
- Reuse and repair options are rarely offered at the moment of disposal

## 1.3 Goals

1. Classify an item in under 3 seconds from a phone or webcam
2. Show how individual scans change system-level metrics in real time
3. Let a manager run what-if scenarios and see predicted impact
4. Generate recommendations grounded in the twin's numbers, never invented numbers
5. Ship a deployed, demoable product before the 4:30 PM deadline on 16 October

## 1.4 Non-Goals

- Real IoT sensor integration, robotics, or physical bin hardware
- Production-grade multi-tenant accounts, billing, or compliance certification
- Region-perfect disposal law coverage — we ship one configurable rule set for a campus scenario
- Multi-item detection in one frame (stretch only)

## 1.5 Users

| Persona | Needs | Main Screens |
|---------|-------|--------------|
| Resident / Student (Asha) | Quick answer on where an item goes, simple tips, her own impact | Scan, History, Impact |
| Facility Manager (Ravi) | See contamination hotspots, test what-if changes, get a report | Twin, What-If, Facility, Reports |
| Judge / Visitor | Understand the idea in 60 seconds, try a scan with no signup | Demo landing, Scan, Twin |

> **Persona names are fictional.**

## 1.6 User Stories

- As a resident, I take a photo of an item and learn its category, the right bin, and how to prepare it
- As a resident, when the model is unsure, I get a clear "not sure" message with a safe default instead of a wrong confident answer
- As a resident, I see how my scans reduced landfill waste and CO2e
- As a manager, I see the flow from sources to bins to facilities with live counts
- As a manager, I move sliders (compliance, pickup frequency, bins) and compare a scenario against the baseline
- As a manager, I click Generate advice and get ranked actions with expected impact and effort
- As a visitor, I use demo mode without creating an account

## 1.7 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Capture a photo by camera or file upload | P0 |
| FR-02 | Classify into recyclable / reusable / biodegradable / hazardous / residual, with material subtype, confidence, and top-3 | P0 |
| FR-03 | Show disposal guidance per class (bin, prep steps, reason) from a rule file | P0 |
| FR-04 | Low-confidence handling: clear message plus fallback classifier; uncertainty that leans hazardous gets a cautious message | P1 |
| FR-05 | Each scan writes an event that updates the twin | P0 |
| FR-06 | Twin view: graph of sources, bins, collection, and facilities with live counts and flow weights | P0 |
| FR-07 | What-if simulator with sliders and baseline comparison | P0 |
| FR-08 | Impact metrics: diversion rate, contamination rate, CO2e avoided, estimated pickup cost | P0 |
| FR-09 | AI advisor: structured, personalized recommendations from scan history and twin state | P0 |
| FR-10 | Advisor chat for reuse, repair, and upcycling questions | P1 |
| FR-11 | Exportable sustainability report | P1 |
| FR-12 | Auth with roles (Resident, Manager, Admin) and a guest demo mode | P1 |
| FR-13 | Facility dashboard: bin fill levels and contamination hotspots | P1 |
| FR-14 | Demo mode: seeded data and a traffic generator that keeps the twin moving | P0 |
| FR-15 | Reuse and donation suggestions with local-partner placeholders | P2 |
| FR-16 | Leaderboard and streaks | P2 |

## 1.8 Non-Functional Requirements

**Performance**
- Scan p95 under 3 s end to end
- Classifier under 500 ms on CPU
- Twin update under 1 s
- Advisor under 6 s

**Reliability**
- Every external call (LLM, fallback model) has a timeout and a fallback
- The demo path must work with the LLM offline using cached advice

**Usability**
- Mobile-first scan flow, large touch targets, readable in daylight

**Accessibility**
- WCAG AA contrast, keyboard operable, screen-reader labels on results

**Privacy**
- Images are processed in memory and not stored by default (see Security & Access)

## 1.9 Success Metrics

| Metric | Target |
|--------|--------|
| Top-1 accuracy on 5 grouped classes, held-out test set | ≥ 85% |
| Recall on the hazardous class | ≥ 90% (safety-critical; accept lower precision) |
| Scan latency p95 | < 3 s |
| Demo completes without a manual restart | 3 of 3 rehearsals |
| Advisor figures match twin figures | 100% (validated in code) |

## 1.10 Judging Alignment

See [docs/index.md](./index.md#judging-alignment)

## 1.11 Demo Script (3 Minutes)

See [docs/index.md](./index.md#demo-script-3-minutes)

## 1.12 Risks and Mitigations

See [docs/index.md](./index.md#risks--mitigations)