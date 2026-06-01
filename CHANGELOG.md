# Changelog

[English](./CHANGELOG.md) | [中文](./CHANGELOG_CN.md)

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
