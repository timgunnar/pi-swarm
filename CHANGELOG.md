# Changelog

[English](./CHANGELOG.md) | [中文](./CHANGELOG_CN.md)

## v0.0.2

### Key Upgrades

- **Inference engine abstraction** — `InferenceEngine` base class with Ollama implementation, pluggable vLLM/llama.cpp in the future
- **Scheduling strategies** — Round-robin, least-connection, random with pluggable strategy pattern
- **Inference API** — OpenAI-compatible `/v1/inference/chat/completions` with SSE streaming and model deploy endpoints
- **Model management API** — List deployed models across all Pi nodes, deploy models with one command
- **Dashboard (5 pages)** — Overview, node management, node detail, model management, logs/settings placeholders
- **NodeCard component** — Real-time CPU/MEM/TEMP bars, status indicators, label tags
- **CLI tool (k3s-pi)** — `node list/add/drain`, `model list/deploy`, `infer chat`, `status` commands with rich terminal output
- **Observability stack** — Prometheus + Grafana + Loki + Promtail manifests for metrics, dashboards, and log aggregation
- **Benchmark script** — `scripts/bench-inference.sh` for inference latency testing
- **CI fix** — Import order linting pass, dev dependency group migration

### Tests

- Backend health endpoint test (1 test, passing)
- `ruff check` — all checks passed
- `vue-tsc --noEmit` — type-check passed

## v0.0.1

### Key Upgrades

- **Project scaffold** — Monorepo workspace with pyproject.toml, Makefile, .gitignore
- **Backend skeleton** — FastAPI app with health endpoint, config management, SQLAlchemy + Alembic database layer (Node, ModelInfo models)
- **Frontend skeleton** — Vue 3 + TypeScript + Vite with router, Pinia stores, Layout component, Dashboard placeholder
- **Node management API** — GET/POST/DELETE endpoints for node listing, join, and drain operations
- **K8s client wrapper** — Kubernetes Python SDK integration for K3s Server communication
- **K3s manifests** — Namespace, Ollama DaemonSet and Service for Pi agent deployment
- **Ansible playbooks** — Node initialization (node-prep role), join-cluster and leave-cluster automation
- **WSL2 setup script** — One-command K3s Server installation on WSL2
- **CI pipeline** — GitHub Actions for backend lint/test and frontend type-check/build

### Tests

- Backend health endpoint test (1 test, passing)
