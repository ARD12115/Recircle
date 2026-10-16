# ReCircle Makefile
# Commands: make dev, make train, make eval, make test, make lint, make smoke, make warmup, make seed

.PHONY: dev train eval test lint smoke warmup seed deploy-backend deploy-frontend logs-log

# Local development (starts API + Web + optional Postgres)
dev:
	docker compose up --build 2>&1 | tee -a logs/docker.log

# Start with Postgres profile
dev-postgres:
	docker compose --profile postgres up --build 2>&1 | tee -a logs/docker.log

# ML Training
train:
	cd ml && python scripts/train.py 2>&1 | tee -a ../logs/ml_train.log

# ML Evaluation
eval:
	cd ml && python scripts/evaluate.py 2>&1 | tee -a ../logs/ml_eval.log

# Download and prepare dataset
data:
	cd ml && python scripts/download_data.py && python scripts/prepare_dataset.py 2>&1 | tee -a ../logs/ml_train.log

# Backend tests
test:
	cd backend && pytest -v 2>&1 | tee -a ../logs/build.log

# Backend tests with coverage
test-cov:
	cd backend && pytest --cov=app --cov-report=term-missing 2>&1 | tee -a ../logs/build.log

# Linting (backend + frontend)
lint:
	cd backend && ruff check . 2>&1 | tee -a ../logs/build.log && cd ../frontend && npm run lint 2>&1 | tee -a ../logs/frontend.log

# Format (backend)
fmt:
	cd backend && ruff check --fix . && black . 2>&1 | tee -a ../logs/build.log

# Smoke test against deployed URLs
smoke:
	./scripts/smoke_test.sh 2>&1 | tee -a logs/build.log

# Warm up deployed API (ping /health 10 min before demo)
warmup:
	./scripts/warmup.sh 2>&1 | tee -a logs/api.log

# Seed demo data
seed:
	./scripts/seed_demo.sh 2>&1 | tee -a logs/api.log

# Deploy backend (Render/Railway/HF Spaces) - configure in CI/CD
deploy-backend:
	@echo "Configure your CI/CD for backend deployment"
	@echo "Target: Render, Railway, or Hugging Face Spaces"

# Deploy frontend (Vercel/Netlify) - configure in CI/CD
deploy-frontend:
	@echo "Configure your CI/CD for frontend deployment"
	@echo "Target: Vercel or Netlify"

# Clean build artifacts
clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Export model for backend
export-model:
	cd ml && python scripts/export.py 2>&1 | tee -a ../logs/ml_train.log

# Full CI pipeline
ci: lint test train eval
	@echo "CI pipeline complete"

# ===== Log Viewing =====
logs-log:
	python scripts/log_view.py --follow

logs-errors:
	python scripts/log_view.py --errors

logs-ml:
	python scripts/log_view.py --ml

logs-api:
	python scripts/log_view.py --api

logs-frontend:
	python scripts/log_view.py --frontend

logs-docker:
	python scripts/log_view.py --docker

logs-since:
	@read -p "Since (e.g. '1 hour ago'): " t; python scripts/log_view.py --since "$$t"