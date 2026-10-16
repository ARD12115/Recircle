# Goal: Reconnect the ReCircle Demo Path

## User Request

“can u fix it?”

## Refined Goal

Make ReCircle’s implementation support the project’s Smart Recycling Assistant demo path: capture/classify a waste item, record its source and actual bin choice, reflect it in the campus twin and its metrics, and generate recommendations from real current twin data. Fix the React Flow placeholder and frontend build blocker, and align model loading configuration so missing local model artifacts fail safely rather than crashing scans. Do not claim trained-model or deployment readiness when required assets or credentials are unavailable.

## Acceptance Criteria

- [ ] The frontend TypeScript/Vite production build completes successfully.
- [ ] The normal scan experience can associate a scan with a campus source and persist the user's confirmed bin; scan-originated updates are visible in the twin graph/metrics.
- [ ] The twin screen renders the returned nodes and edges as a usable graph rather than placeholder text.
- [ ] Live twin metrics and advisor inputs are derived from persisted application state; remove hard-coded contamination/hotspot/scenario data and zero-only metric placeholders.
- [ ] The configured model and model-config paths agree with the Docker/runtime mount and model export contract; a missing local model follows an explicit safe fallback/unsure path instead of an unhandled inference error.
- [ ] Add or update focused tests for the changed scan/twin/metrics/advisor behavior and report actual build/test results.

## Scope Boundaries

**In scope:**
- The identified frontend build, scan-to-twin, twin graph, metrics/advisor grounding, and model path/failure-handling gaps.
- Targeted tests and directly related documentation/configuration updates.

**Out of scope:**
- Deployment, physical IoT integration, model training or dataset/weight downloads, provisioning external credentials, and submission materials.
- Unrelated pre-existing bugs or broad redesign.

## Applicable Project Conventions

**Quality gate command:**
- `make test` (backend tests)
- `cd frontend && npm run build` (TypeScript and Vite production build)

**Commit convention:**
- No project-specific convention found during discovery; use the goal workflow's conventional commit format with role markers.
- Assisted-by trailer required by the goal workflow; include the repository-required Copilot co-author trailer when creating commits.

**Guidelines:**
- No `AGENTS.md`, `CONSTITUTION.md`, `.agents/guidelines/`, or `.github/guidelines/` found in the project.

**Rules:**
- Preserve unrelated untracked files; `misceleneous/` is pre-existing and out of scope.
- Keep any absent model weights or external credentials as explicit prerequisites, not generated or fabricated assets.
