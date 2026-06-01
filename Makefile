.PHONY: dev-backend dev-frontend dev-all install lint test clean

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev-all:
	@echo "Start backend & frontend in separate terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

install:
	cd backend && uv sync --dev
	cd frontend && npm install
	cd cli && uv sync

lint:
	cd backend && uv run ruff check app/ tests/
	cd frontend && npm run lint

test:
	cd backend && uv run pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

k3s-apply:
	kubectl apply -f k3s/base/

k3s-status:
	kubectl get nodes -o wide
	kubectl get pods -n pi-swarm -o wide
