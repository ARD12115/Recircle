# Independent Inspector Feedback — ReCircle reconnect demo path

**Verdict: BLOCKED**  
**Reviewed:** builder commit `eeda34c` plus the four specified uncommitted follow-ups. No product files were changed, and nothing was staged or committed.

## Evidence

- **Scan → twin path:** `frontend/src/pages/Scan.tsx` loads campus source nodes, requires a source selection, and passes its ID to `scanApi.scan`. `backend/app/api/v1/scan.py` validates that ID as a source and persists it with the scan. The confirmation endpoint stores the user's chosen bin once; `backend/app/services/twin/events.py` updates source/bin counts and the source-to-bin edge, commits, and broadcasts updated events/metrics.
- **Twin visualization:** `frontend/src/pages/Twin.tsx` maps the API's graph nodes and edges into React Flow elements and provides loading, error, and empty-node states. The placeholder graph text is gone.
- **Persisted metrics/advisor inputs:** `compute_current_metrics` reads scans and bin capacities from the database. `generate_advice` uses those metrics, confirmed scans, source nodes, and the latest persisted snapshot's scenario deltas; `derive_advisor_context` derives misroutes/hotspots from confirmed scan records. The focused test file covers persisted metric calculation/event updates, seed idempotence, and advisor context, but I could not execute it.
- **Model paths/fallback:** runtime defaults in `backend/app/core/config.py` target `./app/data/weights/model.pt` and `model_config.json`; Docker Compose mounts `backend/app/data/weights` at `/app/app/data/weights`, and `ml/scripts/export.py` exports those same filenames there. `classifier.load_model` returns `False` when either file is absent; `scan_item` then tries the zero-shot fallback and otherwise returns the unsure response. However, `.env.example` still sets `MODEL_PATH=./weights/best.pt` and omits `MODEL_CONFIG_PATH`, so copying the example overrides the aligned default with a path inconsistent with the Docker mount/export contract. The actual root `.env` was not inspected.

## Quality gates and blockers

- **Frontend build:** `npm run build` was dispatched from `frontend`, but the command was moved to a user-managed background terminal and no completion/exit result was available to this inspection. Build success is therefore unverified.
- **Backend tests:** blocked because `pytest` is unavailable; per instruction, I did not install dependencies or retry tests.
- **Python compile:** not completed; the configured Python launcher attempted to start a missing `C:\python\python3.13t.exe`. No installation or retry was performed.

I cannot award PASS without verifiable build and backend-test results. The stale model path in `.env.example` is also a directly related configuration inconsistency to resolve or explicitly validate against the actual runtime environment before calling the model-path criterion satisfied.
