# Frontend Specification

## 4.1 Principles
- Mobile-first for the scan flow, desktop-first for the twin and what-if views
- One clear result per scan: the class badge and the bin come first, details second
- Never present simulated data as measured data. Label it.
- Fast: the scan page loads first, heavy views (twin graph, charts) are code-split

## 4.2 Stack
React 18, TypeScript, Vite, React Router, TanStack Query (server state), Zustand (UI and scan session state), Tailwind CSS, React Flow (twin graph), Recharts (charts), Framer Motion (sparingly), small accessible component set (Radix primitives or shadcn/ui)

## 4.3 Routes and Screens

| Route | Screen | Roles | Priority |
|-------|--------|-------|----------|
| `/` | Landing with "Try demo" and short value statement | All | P0 |
| `/scan` | Camera or upload, result card, guidance, confirm-bin action | Guest+ | P0 |
| `/twin` | Live flow graph, node details, metric strip | Guest+ | P0 |
| `/simulate` | What-if sliders, baseline vs scenario comparison | Guest+ | P0 |
| `/impact` | KPI cards and trend charts | Guest+ | P0 |
| `/advisor` | Structured advice cards and chat | Resident+ | P0 (cards), P1 (chat) |
| `/history` | Past scans with filters | Resident+ | P1 |
| `/facility` | Bin fill levels, hotspot list, report export | Manager+ | P1 |
| `/login` | Sign in and demo accounts | Public | P1 |

> The twin is running on demo traffic.

## 4.4 Layout
- Persistent shell: top bar (logo, role badge, demo-mode indicator, sign-in) and left navigation on desktop that becomes bottom tab bar on mobile (Scan, Twin, What-If, Impact, Advisor)
- Slim banner at top reads "Simulated campus data" whenever the environment is demo

## 4.5 Key Components

| Component | Purpose and Behavior |
|-----------|---------------------|
| CameraCapture | `getUserMedia` with `facingMode`, capture to canvas, downscale to max 1024 px, JPEG 0.85, retake button, file-upload fallback when permission denied |
| ResultCard | Class badge, subtype, confidence bar, top-3 list, bin and prep steps, "I put it in..." confirm buttons, "Not right?" report action |
| UncertainState | Shown below confidence threshold: plain-language "not sure", retake tip, cautious default when hazardous is plausible |
| TwinGraph | React Flow canvas with custom nodes (source, bin, collection, facility), edge thickness by flow, animated dashes for active flow, node click opens detail drawer |
| MetricStrip | Diversion rate, contamination rate, CO2e avoided, pickup cost, with small delta arrows |
| ScenarioPanel | Sliders for compliance, awareness boost, pickup frequency, bins per stream, with reset and Run buttons |
| CompareChart | Baseline vs scenario bars plus delta KPI cards, colored by good/bad direction |
| AdviceCards | Ranked actions with impact and effort chips, expandable "why" text, reuse ideas list |
| AdvisorChat | Streaming message list, suggested prompts, clear disclaimer |
| StatusBanner | Demo mode, offline, and degraded-AI messages |

## 4.6 Visual System

**Class colors (also used in legend)**:
- Recyclable: blue
- Reusable: amber
- Biodegradable: green
- Hazardous: red
- Residual: gray

> Never rely on color alone: each badge also has an icon and a text label.

**Typography**: One sans-serif family, large result text (at least 24 px class name on mobile), tabular numerals for metrics

**Spacing and shape**: 8 px grid, rounded cards, restrained shadows

**Themes**: Light theme required; dark theme is P2 using CSS variables defined from day one

## 4.7 State and Data Flow

- **TanStack Query** for `/twin`, `/scans`, `/advice` with sensible stale times
- **Mutations** for `/scan`, `/simulate`
- **Zustand** for current scan session (image, result), selected twin node, scenario slider values
- **useTwinStream hook** opens SSE connection, patches query cache on `scan.created` and `metrics.updated`, reconnects with backoff, falls back to 3-second polling
- **API client** (`api/client.ts`) attaches token, maps standard error shape to typed errors, adds `request_id` to bug reports

## 4.8 Interaction Details

**Scan**: Capture, show loading skeleton, then result within 3 seconds. Announce result with `aria-live=polite`.

**Confirm bin**: One tap on the bin the user actually used. Feeds real routing into twin — source of "real vs simulated" split.

**Twin**: Newly scanned items animate along their path. Time slider replays last N ticks.

**What-if**: Slider changes preview instantly with debounced call (300 ms). "Run full scenario" returns complete comparison.

**Advice**: Generate button with progress state. If LLM down, show cached advice with "cached" tag.

**Report**: Export from facility page using browser's print-to-PDF on print stylesheet (P1 backend report endpoint can replace this).

## 4.9 States and Errors

Every screen defines:
- **Loading** (skeletons)
- **Empty** (short prompt plus action)
- **Error** (message plus retry and `request_id`)
- **Offline** states

Camera permission denied → shows upload fallback. Rate-limited requests → friendly wait message.

## 4.10 Accessibility

- WCAG AA contrast
- Visible focus rings
- Full keyboard operation for sliders and dialogs
- Labels for all controls
- Alt text on preview image
- Reduced-motion respected for animated edges
- Touch targets ≥ 44 px

## 4.11 Performance Budget

- Initial JS under 250 KB gzipped on `/scan`
- Lazy-load `/twin` and `/simulate`
- Compress images client-side before upload
- Memoize graph nodes to keep canvas smooth with ~40 nodes

## 4.12 Acceptance Criteria

| Screen | Done When |
|--------|-----------|
| Scan | Photo from phone returns result card in under 3s; denied camera falls back to upload; low-confidence path renders |
| Twin | Scanning an item updates a count on the graph within 1s without refresh |
| What-if | Moving compliance changes diversion and CO2e deltas; reset restores baseline |
| Impact | KPIs match the API values exactly |
| Advisor | Cards render from valid advice JSON; cached fallback works with LLM disabled |
| All | No console errors on demo path; works at 375 px and 1440 px widths |