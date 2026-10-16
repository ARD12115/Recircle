# ReCircle Demo Script (3 Minutes)

## 0:00 – Hook (15 sec)
> "Every year, 2.1 billion tonnes of municipal solid waste are generated globally. **Contamination** — the wrong item in the wrong bin — cuts recycling yield for an entire batch, not just one item. Today we show how a single scan can change a whole campus system."

## 0:15 – Live Scan Demo (45 sec)
**Scan 1: Plastic bottle**
- Point camera → result in <3s
- Shows: Recyclable / Plastic / 94% confidence
- Guidance: "Yellow bin, rinse, leave caps on"
- Tap "I put it in Recyclable Bin" → confirm

**Scan 2: Battery**
- Point camera → result
- Shows: Hazardous / Battery / 98% confidence
- Guidance: "Hazardous collection, tape terminals, DO NOT CRUSH"
- Tap "I put it in Hazardous Bin"

**Scan 3: Banana peel**
- Point camera → result
- Shows: Biodegradable / Organic / 91% confidence
- Guidance: "Green compost bin, no plastic bags"

## 1:00 – Digital Twin (40 sec)
- Switch to **Twin** tab
- Three scans appear as animated flow on graph
- Metric strip updates live:
  - Diversion: 62% → 64%
  - Contamination: 18% → 17%
  - CO₂e avoided: +2.3 kg
- "Every scan updates the system in real time"

## 1:40 – What-If Simulator (40 sec)
- Switch to **What-If** tab
- Slider: Compliance 60% → 80%
- Click **Run Simulation**
- CompareChart shows:
  - Diversion: +12% (62% → 74%)
  - Contamination: -5% (18% → 13%)
  - CO₂e: +15 kg/day
  - Cost: -$200/day
- "Test changes before spending budget"

## 2:20 – AI Advisor (30 sec)
- Switch to **Advisor** tab
- Click **Generate Advice**
- Cards render:
  1. "Add bin signage" — Low effort, reduces contamination 3-5%
  2. "Organic bins at Canteen" — Medium effort, +8-12% diversion
  3. "Battery awareness drive" — Low effort, eliminates hazardous in residual
- Reuse ideas: glass jars → storage, cardboard → organizers
- "All numbers grounded in twin metrics — never invented"

## 2:50 – Close (10 sec)
- Architecture slide: React + FastAPI + PyTorch + SSE
- Team roles: ML, Backend, Frontend
- Next steps: Resin code reading, multi-item detection, smart bin prototype, campus pilot
- "ReCircle: Scan → Twin → Advise → Circular Economy"

---

## Backup Plan
- If Wi-Fi fails: Run `docker compose up` on laptop
- If LLM fails: Cached advice shows automatically
- If camera fails: File upload fallback
- Recorded video: `backup-demo.mp4` in Drive folder

## Demo Credentials (DEMO_MODE)
| Role | Email | Password |
|------|-------|----------|
| Resident | resident@demo.recircle | demo123 |
| Manager | manager@demo.recircle | demo123 |
| Admin | admin@demo.recircle | demo123 |