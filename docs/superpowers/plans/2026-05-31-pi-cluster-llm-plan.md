# Pi Cluster LLM 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个控制面/数据面分离的树莓派集群 LLM 推理管理系统——K3s Server 在 WSL2，K3s Agent 在 Pi，FastAPI + Vue 3 管理平台，Ollama 推理引擎。

**Architecture:** PC (WSL2) 运行 K3s Server + 管理平台；Pi 集群运行 K3s Agent + Ollama DaemonSet；Backend 通过 K3s API + Ollama API 管理集群和推理；Frontend 通过 REST API 提供 Dashboard；CLI 封装管理操作。

**Tech Stack:** Python 3.12+ / FastAPI / Vue 3 + TypeScript + Vite / K3s / Ollama / Ansible / Prometheus + Grafana + Loki / SQLAlchemy + SQLite

**Design Doc:** `docs/superpowers/specs/2026-05-31-pi-cluster-llm-design.md`

---

## 迭代概览

| 迭代 | 内容 | 预计工时 |
|------|------|---------|
| 1 | Foundation — 项目脚手架、K3s 初始化、Backend/Frontend 骨架 | 2-3h |
| 2 | Node Management — Ansible Playbooks、节点 CRUD API | 2-3h |
| 3 | Model & Inference — 引擎抽象、Ollama 集成、推理 API | 2-3h |
| 4 | Dashboard — Vue 3 所有页面、图表、API 对接 | 2-3h |
| 5 | CLI — Python CLI 全命令实现 | 1-2h |
| 6 | Observability — Prometheus + Grafana + Loki | 1-2h |
| 7 | Polish — 文档、错误处理、端到端验证 | 1h |

---

## 文件结构

```
pi-cluster-llm/
├── ansible/
│   ├── inventory/hosts.yml
│   ├── playbooks/
│   │   ├── join-cluster.yml
│   │   └── leave-cluster.yml
│   └── roles/node-prep/
│       └── tasks/main.yml
├── k3s/base/
│   ├── namespace.yaml
│   ├── ollama-daemonset.yaml
│   ├── ollama-service.yaml
│   └── promtail-daemonset.yaml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/v1/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py
│   │   │   ├── models.py
│   │   │   ├── inference.py
│   │   │   └── system.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── engine.py
│   │   │   └── scheduler.py
│   │   ├── engines/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── ollama.py
│   │   ├── models/ (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── node.py
│   │   │   └── model.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── node_service.py
│   │   │   ├── model_service.py
│   │   │   └── inference_service.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── node.py
│   │   │   ├── model.py
│   │   │   └── inference.py
│   │   └── k8s/
│   │       ├── __init__.py
│   │       └── client.py
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Nodes.vue
│   │   │   ├── NodeDetail.vue
│   │   │   ├── Models.vue
│   │   │   ├── Logs.vue
│   │   │   └── Settings.vue
│   │   ├── components/
│   │   │   ├── Layout.vue
│   │   │   ├── NodeCard.vue
│   │   │   ├── ResourceChart.vue
│   │   │   └── ModelDeployDialog.vue
│   │   ├── composables/useApi.ts
│   │   ├── api/client.ts
│   │   ├── router/index.ts
│   │   └── stores/
│   │       ├── nodes.ts
│   │       └── models.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── tsconfig.json
├── cli/
│   ├── pi_cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py
│   │   │   ├── models.py
│   │   │   └── inference.py
│   │   └── client.py
│   └── pyproject.toml
├── scripts/
│   ├── setup-wsl2.sh
│   └── bench-inference.sh
├── docs/
├── .github/workflows/ci.yml
├── Makefile
└── README.md
```

---

## Iteration 1: Foundation — 项目脚手架 & 基础设施

### Task 1.1: 创建项目根目录文件

**Files:**
- Create: `pyproject.toml` (workspace root)
- Create: `Makefile`
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: 创建根 pyproject.toml 作为 workspace 配置**

```toml
# pyproject.toml
[tool.uv.workspace]
members = ["backend", "cli"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["backend/tests", "cli/tests"]
```

- [ ] **Step 2: 创建 Makefile**

```makefile
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
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

# K3s operations
k3s-apply:
	kubectl apply -f k3s/base/

k3s-status:
	kubectl get nodes -o wide
	kubectl get pods -n pi-cluster -o wide
```

- [ ] **Step 3: 创建 .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
venv/

# Node
node_modules/
frontend/dist/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Env
.env
.env.local

# Database
*.db
*.sqlite3

# K3s
kubeconfig.*
```

- [ ] **Step 4: 创建 README.md 项目简介**

```markdown
# Pi Cluster LLM

树莓派集群分布式大模型推理管理系统。

## 架构

- **控制面**: Windows PC (WSL2) → K3s Server + 管理平台
- **数据面**: Raspberry Pi 5 集群 → K3s Agent + Ollama

## 快速开始

见 [部署文档](docs/architecture.md)
```

- [ ] **Step 5: 初始化 Git 并提交**

```bash
cd e:/develop/pi-cluster-llm__developing
git init
git add pyproject.toml Makefile README.md .gitignore
git commit -m "chore: init project scaffold with workspace config"
```

---

### Task 1.2: Backend 项目初始化

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: 创建 backend/pyproject.toml**

```toml
[project]
name = "pi-cluster-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy>=2.0",
    "alembic>=1.14",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "httpx>=0.28.0",
    "kubernetes>=31.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "ruff>=0.8.0",
]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

- [ ] **Step 2: 创建 backend/app/core/config.py**

```python
"""应用配置 —— 所有环境变量通过 pydantic-settings 集中管理."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PI_CLUSTER_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # 应用
    app_name: str = "Pi Cluster LLM"
    debug: bool = False

    # 数据库 (SQLite 起步)
    database_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent.parent / 'data' / 'pi_cluster.db'}"

    # K3s
    k3s_kubeconfig: str = str(Path.home() / ".kube" / "config")

    # Ollama
    ollama_default_port: int = 11434

    # 推理
    inference_timeout: int = 300  # 秒
    inference_max_concurrency: int = 10


settings = Settings()
```

- [ ] **Step 3: 创建 backend/app/main.py — FastAPI 应用入口**

```python
"""Pi Cluster LLM — FastAPI 管理平台入口."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭时资源管理."""
    # 启动时: 初始化 DB 连接池等
    yield
    # 关闭时: 清理资源


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
```

- [ ] **Step 4: 创建 backend/tests/test_health.py**

```python
"""Health endpoint 测试."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
```

- [ ] **Step 5: 安装依赖并运行测试**

```bash
cd backend
uv sync --dev
uv run pytest tests/test_health.py -v
# Expected: 1 passed
```

- [ ] **Step 6: 提交**

```bash
git add backend/
git commit -m "feat(backend): init FastAPI app with health endpoint and config"
```

---

### Task 1.3: Frontend 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/components/Layout.vue`
- Create: `frontend/src/views/Dashboard.vue` (placeholder)

- [ ] **Step 1: 创建 frontend/package.json**

```json
{
  "name": "pi-cluster-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.5.0",
    "pinia": "^2.3.0",
    "axios": "^1.7.0",
    "echarts": "^5.6.0",
    "vue-echarts": "^7.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0",
    "vue-tsc": "^2.2.0"
  }
}
```

- [ ] **Step 2: 创建 frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: 创建 frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noEmit": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "baseUrl": "."
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: 创建 frontend/tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: 创建 frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pi Cluster LLM</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 6: 创建 frontend/src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 7: 创建 frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
// App root — router-view renders Layout or standalone pages
</script>
```

- [ ] **Step 8: 创建 frontend/src/router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
      ],
    },
  ],
})

export default router
```

- [ ] **Step 9: 创建 frontend/src/components/Layout.vue**

```vue
<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h1 class="logo">🖥 Pi Cluster</h1>
      <nav>
        <router-link to="/">📊 总览</router-link>
        <!-- 后续迭代加入更多导航项 -->
      </nav>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
}
.sidebar {
  width: 220px;
  background: #1a1a2e;
  color: #eee;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.logo {
  font-size: 18px;
  margin: 0;
}
nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
nav a {
  color: #aaa;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}
nav a:hover,
nav a.router-link-active {
  background: #16213e;
  color: #fff;
}
.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f5f5f5;
}
</style>
```

- [ ] **Step 10: 创建 frontend/src/views/Dashboard.vue (placeholder)**

```vue
<template>
  <div class="dashboard">
    <h2>集群总览</h2>
    <p>节点数: --</p>
    <p>在线: --</p>
    <p>模型: --</p>
  </div>
</template>

<script setup lang="ts">
</script>
```

- [ ] **Step 11: 安装并启动前端验证**

```bash
cd frontend
npm install
npm run dev
# 浏览器访问 http://localhost:5173
# 确认看到侧边栏 + 总览页 placeholder
```

- [ ] **Step 12: 提交**

```bash
git add frontend/
git commit -m "feat(frontend): init Vue 3 + TypeScript + Vite project with router and layout"
```

---

### Task 1.4: K3s 基础资源清单

**Files:**
- Create: `k3s/base/namespace.yaml`
- Create: `k3s/base/ollama-daemonset.yaml`
- Create: `k3s/base/ollama-service.yaml`

- [ ] **Step 1: 创建 k3s/base/namespace.yaml**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pi-cluster
```

- [ ] **Step 2: 创建 k3s/base/ollama-daemonset.yaml**

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ollama
  namespace: pi-cluster
  labels:
    app: ollama
spec:
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      nodeSelector:
        pi-role: inference
      containers:
        - name: ollama
          image: ollama/ollama:0.5.13
          ports:
            - containerPort: 11434
              name: http
          env:
            - name: OLLAMA_HOST
              value: "0.0.0.0"
            - name: OLLAMA_KEEP_ALIVE
              value: "24h"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "7Gi"
              cpu: "3000m"
          volumeMounts:
            - name: ollama-data
              mountPath: /root/.ollama
          readinessProbe:
            httpGet:
              path: /
              port: 11434
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 11434
            initialDelaySeconds: 30
            periodSeconds: 30
      volumes:
        - name: ollama-data
          hostPath:
            path: /data/ollama
            type: DirectoryOrCreate
```

- [ ] **Step 3: 创建 k3s/base/ollama-service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ollama
  namespace: pi-cluster
  labels:
    app: ollama
spec:
  type: ClusterIP
  selector:
    app: ollama
  ports:
    - port: 11434
      targetPort: 11434
      protocol: TCP
      name: http
```

- [ ] **Step 4: 提交**

```bash
git add k3s/
git commit -m "feat(k3s): add namespace, ollama DaemonSet and Service manifests"
```

---

### Task 1.5: WSL2 K3s Server 初始化脚本

**Files:**
- Create: `scripts/setup-wsl2.sh`

- [ ] **Step 1: 创建 scripts/setup-wsl2.sh**

```bash
#!/bin/bash
# WSL2 环境 K3s Server 一键安装脚本
# 在 WSL2 Ubuntu 内执行: bash scripts/setup-wsl2.sh

set -euo pipefail

echo "=== Pi Cluster LLM — WSL2 环境初始化 ==="

# 1. 更新系统
echo "[1/5] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 K3s Server
echo "[2/5] 安装 K3s Server..."
if systemctl is-active --quiet k3s; then
    echo "  K3s 已在运行，跳过安装"
else
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server \
        --write-kubeconfig-mode 644 \
        --node-label pi-role=management \
        --disable-agent" sh -
fi

# 3. 等待 K3s 就绪
echo "[3/5] 等待 K3s 就绪..."
for i in $(seq 1 30); do
    if kubectl get nodes &>/dev/null; then
        echo "  K3s 已就绪"
        break
    fi
    sleep 2
done

# 4. 创建 kubeconfig 副本到用户目录
echo "[4/5] 配置 kubeconfig..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# 5. 显示加入 Token
echo "[5/5] 完成！"
echo ""
echo "=== K3s Server 就绪 ==="
echo ""
echo "加入 Token (Pi 加入集群时需要):"
sudo cat /var/lib/rancher/k3s/server/node-token
echo ""
echo "节点状态:"
kubectl get nodes
echo ""
echo "下一步: Windows 管理员 PowerShell 中执行端口转发:"
echo '  netsh interface portproxy add v4tov4 \'
echo '    listenport=6443 listenaddress=0.0.0.0 \'
echo '    connectport=6443 connectaddress=$(wsl hostname -I | cut -d" " -f1)'
```

```bash
chmod +x scripts/setup-wsl2.sh
```

- [ ] **Step 2: 提交**

```bash
git add scripts/setup-wsl2.sh
git commit -m "feat(scripts): add WSL2 K3s Server setup script"
```

---

### Task 1.6: CI Pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 创建 .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.12"
      - run: uv sync --dev
      - run: uv run ruff check app/ tests/
      - run: uv run pytest tests/ -v

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run build
```

- [ ] **Step 2: 提交**

```bash
git add .github/
git commit -m "ci: add GitHub Actions CI for backend lint/test and frontend build"
```

---

## Iteration 2: Node Management — 节点管理

### Task 2.1: 数据库模型 & Alembic 初始化

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/node.py`
- Create: `backend/app/models/model.py`
- Modify: `backend/app/core/config.py` (添加 database_url)
- Initialize: `backend/alembic/`

- [ ] **Step 1: 创建 backend/app/models/__init__.py**

```python
"""SQLAlchemy models."""

from app.models.node import Node
from app.models.model import ModelInfo

__all__ = ["Node", "ModelInfo"]
```

- [ ] **Step 2: 创建 backend/app/models/node.py**

```python
"""节点数据模型."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import TEXT as SQLiteText


class Node:
    """Pi 推理节点."""

    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(
        SQLiteText, primary_key=True,
        default=lambda: str(uuid.uuid4())[:8]
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending | online | offline | draining
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    memory_usage: Mapped[float] = mapped_column(Float, default=0.0)
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    labels: Mapped[str] = mapped_column(String(500), default="{}")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

还需先创建 Base。实际创建 backend/app/models/base.py:

```python
"""SQLAlchemy declarative base."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

然后修正 Node 继承 Base。完整文件见下一步。

- [ ] **Step 3: 创建 backend/app/models/model.py**

```python
"""模型信息数据模型."""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import TEXT as SQLiteText
from app.models.base import Base


class ModelInfo(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(
        SQLiteText, primary_key=True,
        default=lambda: str(uuid.uuid4())[:8]
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag: Mapped[str] = mapped_column(String(50), default="latest")
    size: Mapped[str] = mapped_column(String(50), default="")  # e.g. "7B"
    quantization: Mapped[str] = mapped_column(String(20), default="Q4_K_M")
    replicas: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(20), default="deploying"
    )  # deploying | ready | error | unloaded
    engine: Mapped[str] = mapped_column(String(30), default="ollama")
    deployed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- [ ] **Step 4: 初始化 Alembic 并创建首次迁移**

```bash
cd backend
uv run alembic init alembic
# 编辑 alembic/env.py 配置 target_metadata
# 编辑 alembic.ini 设置 sqlalchemy.url
uv run alembic revision --autogenerate -m "init: nodes and models tables"
uv run alembic upgrade head
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/models/ backend/alembic/ backend/alembic.ini
git commit -m "feat(backend): add Node and ModelInfo SQLAlchemy models with Alembic"
```

---

### Task 2.2: K8s Client 封装

**Files:**
- Create: `backend/app/k8s/__init__.py`
- Create: `backend/app/k8s/client.py`

- [ ] **Step 1: 创建 backend/app/k8s/client.py**

```python
"""K8s API 客户端封装 —— 与 K3s Server 交互."""

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class K8sClient:
    """封装 kubernetes Python SDK 常用操作."""

    def __init__(self, kubeconfig_path: str | None = None):
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_kube_config()  # 默认 ~/.kube/config

        self.core = client.CoreV1Api()
        self.apps = client.AppsV1Api()

    def list_nodes(self) -> list[dict]:
        """列出所有 K3s 节点（含 Agent）."""
        try:
            nodes = self.core.list_node()
            result = []
            for n in nodes.items:
                conditions = {
                    c.type: c.status for c in (n.status.conditions or [])
                }
                result.append({
                    "name": n.metadata.name,
                    "status": (
                        "online" if conditions.get("Ready") == "True"
                        else "offline"
                    ),
                    "labels": n.metadata.labels or {},
                    "cpu_capacity": n.status.capacity.get("cpu", ""),
                    "memory_capacity": n.status.capacity.get("memory", ""),
                    "kubelet_version": n.status.node_info.kubelet_version
                    if n.status.node_info else "",
                    "created": str(n.metadata.creation_timestamp),
                })
            return result
        except ApiException as e:
            raise RuntimeError(f"K8s API error: {e}")

    def get_node(self, name: str) -> dict | None:
        """获取单个节点详情."""
        nodes = self.list_nodes()
        for n in nodes:
            if n["name"] == name:
                return n
        return None

    def list_pods(self, namespace: str, label_selector: str = "") -> list[dict]:
        """列出 Pod."""
        try:
            pods = self.core.list_namespaced_pod(
                namespace=namespace, label_selector=label_selector
            )
            return [
                {
                    "name": p.metadata.name,
                    "namespace": p.metadata.namespace,
                    "node": p.spec.node_name,
                    "status": p.status.phase,
                    "containers": [
                        c.name for c in (p.spec.containers or [])
                    ],
                }
                for p in pods.items
            ]
        except ApiException as e:
            raise RuntimeError(f"K8s API error: {e}")

    def get_daemonset(
        self, name: str, namespace: str
    ) -> dict:
        """获取 DaemonSet 状态."""
        try:
            ds = self.apps.read_namespaced_daemon_set(name, namespace)
            return {
                "name": ds.metadata.name,
                "desired": ds.status.desired_number_scheduled,
                "ready": ds.status.number_ready,
                "updated": ds.status.updated_number_scheduled,
            }
        except ApiException as e:
            raise RuntimeError(f"K8s API error: {e}")
```

- [ ] **Step 2: 测试 K8s Client 连接**

```bash
cd backend
# 确保 K3s 在 WSL2 运行
kubectl get nodes
uv run python -c "
from app.k8s.client import K8sClient
c = K8sClient()
print(c.list_nodes())
"
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/k8s/
git commit -m "feat(backend): add K8s client wrapper for K3s API operations"
```

---

### Task 2.3: Node Service & API

**Files:**
- Create: `backend/app/schemas/node.py`
- Create: `backend/app/services/node_service.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/nodes.py`
- Modify: `backend/app/main.py` (register router)

- [ ] **Step 1: 创建 backend/app/schemas/node.py**

```python
"""节点相关 Pydantic schemas."""

from pydantic import BaseModel, Field


class NodeSummary(BaseModel):
    name: str
    host: str = ""
    status: str = "pending"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: float = 0.0
    labels: dict = Field(default_factory=dict)
    kubelet_version: str = ""
    is_active: bool = True

    model_config = {"from_attributes": True}


class NodeDetail(NodeSummary):
    cpu_capacity: str = ""
    memory_capacity: str = ""
    pods: list[dict] = Field(default_factory=list)
    joined_at: str = ""
    last_heartbeat: str = ""


class NodeJoinRequest(BaseModel):
    host: str
    name: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class NodeJoinResponse(BaseModel):
    success: bool
    message: str
    join_command: str = ""
```

- [ ] **Step 2: 创建 backend/app/services/node_service.py**

```python
"""节点管理业务逻辑."""

from app.k8s.client import K8sClient
from app.schemas.node import NodeSummary, NodeDetail, NodeJoinRequest


class NodeService:
    def __init__(self, k8s: K8sClient):
        self.k8s = k8s

    def list_nodes(self) -> list[NodeSummary]:
        k8s_nodes = self.k8s.list_nodes()
        return [
            NodeSummary(
                name=n["name"],
                status=n["status"],
                labels=n["labels"],
                kubelet_version=n.get("kubelet_version", ""),
            )
            for n in k8s_nodes
        ]

    def get_node(self, name: str) -> NodeDetail | None:
        k8s_node = self.k8s.get_node(name)
        if not k8s_node:
            return None
        pods = self.k8s.list_pods(
            namespace="pi-cluster",
            label_selector=f"app=ollama",
        )
        node_pods = [p for p in pods if p["node"] == name]
        return NodeDetail(
            **k8s_node,
            pods=node_pods,
            cpu_capacity=k8s_node.get("cpu_capacity", ""),
            memory_capacity=k8s_node.get("memory_capacity", ""),
        )

    def get_join_command(self, request: NodeJoinRequest) -> str:
        """生成 Pi 加入集群的 Ansible 命令."""
        name = request.name or request.host.replace(".", "-")
        labels = ",".join(
            f"{k}={v}" for k, v in request.labels.items()
        ) or "pi-role=inference"
        return (
            f"ansible-playbook ansible/playbooks/join-cluster.yml "
            f"-e 'pi_ip={request.host}' "
            f"-e 'pi_name={name}' "
            f"-e 'pi_labels={labels}'"
        )
```

- [ ] **Step 3: 创建 backend/app/api/v1/nodes.py**

```python
"""节点管理 API 端点."""

from fastapi import APIRouter, Depends, HTTPException
from app.k8s.client import K8sClient
from app.services.node_service import NodeService
from app.schemas.node import (
    NodeSummary,
    NodeDetail,
    NodeJoinRequest,
    NodeJoinResponse,
)

router = APIRouter(prefix="/nodes", tags=["nodes"])


def get_node_service() -> NodeService:
    k8s = K8sClient()
    return NodeService(k8s)


@router.get("", response_model=list[NodeSummary])
async def list_nodes(service: NodeService = Depends(get_node_service)):
    """获取所有节点列表."""
    return service.list_nodes()


@router.get("/{name}", response_model=NodeDetail)
async def get_node(
    name: str, service: NodeService = Depends(get_node_service)
):
    """获取单个节点详情."""
    node = service.get_node(name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{name}' not found")
    return node


@router.post("/join", response_model=NodeJoinResponse)
async def join_node(
    request: NodeJoinRequest,
    service: NodeService = Depends(get_node_service),
):
    """生成节点加入集群的命令."""
    cmd = service.get_join_command(request)
    return NodeJoinResponse(
        success=True,
        message=f"Run the following command to join {request.host}",
        join_command=cmd,
    )


@router.delete("/{name}")
async def drain_node(
    name: str, service: NodeService = Depends(get_node_service)
):
    """安全下线节点."""
    node = service.get_node(name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{name}' not found")
    # kubectl drain + delete
    import subprocess
    try:
        subprocess.run(["kubectl", "drain", name, "--ignore-daemonsets", "--delete-emptydir-data"], check=True)
        subprocess.run(["kubectl", "delete", "node", name], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Drain failed: {e}")
    return {"success": True, "message": f"Node '{name}' drained and removed"}
```

- [ ] **Step 4: 在 main.py 注册 router**

```python
# 在 backend/app/main.py 中添加:

from app.api.v1 import nodes

app.include_router(nodes.router, prefix="/api/v1")
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/schemas/ backend/app/services/ backend/app/api/
git commit -m "feat(backend): add node management API (list, get, join, drain)"
```

---

### Task 2.4: Ansible Playbooks

**Files:**
- Create: `ansible/inventory/hosts.yml`
- Create: `ansible/roles/node-prep/tasks/main.yml`
- Create: `ansible/playbooks/join-cluster.yml`
- Create: `ansible/playbooks/leave-cluster.yml`

- [ ] **Step 1: 创建 ansible/inventory/hosts.yml**

```yaml
# Pi 推理节点清单
all:
  children:
    pis:
      hosts:
        # pi-1:
        #   ansible_host: 192.168.1.101
        # pi-2:
        #   ansible_host: 192.168.1.102
        # pi-3:
        #   ansible_host: 192.168.1.103
  vars:
    ansible_user: pi
    ansible_python_interpreter: /usr/bin/python3
```

- [ ] **Step 2: 创建 ansible/roles/node-prep/tasks/main.yml**

```yaml
---
# Pi 节点系统初始化 tasks

- name: Update apt cache
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Install required packages
  apt:
    name:
      - curl
      - wget
      - ca-certificates
      - gnupg
      - lsb-release
      - vim
      - htop
      - iotop
    state: present

- name: Disable swap (K3s requires)
  command: dphys-swapfile swapoff
  ignore_errors: yes

- name: Disable swap permanently
  command: dphys-swapfile uninstall
  ignore_errors: yes

- name: Enable cgroup memory
  lineinfile:
    path: /boot/firmware/cmdline.txt
    regexp: 'cgroup_memory=1 cgroup_enable=memory'
    line: "{{ lookup('file', '/boot/firmware/cmdline.txt') }} cgroup_memory=1 cgroup_enable=memory"
    backrefs: yes
  notify: reboot

- name: Set hostname
  hostname:
    name: "{{ pi_name | default(inventory_hostname) }}"

- name: Add hostname to /etc/hosts
  lineinfile:
    path: /etc/hosts
    regexp: '127.0.1.1'
    line: "127.0.1.1 {{ pi_name | default(inventory_hostname) }}"
```

- [ ] **Step 3: 创建 ansible/playbooks/join-cluster.yml**

```yaml
---
- name: 初始化 Pi 节点并加入 K3s 集群
  hosts: all
  vars:
    pi_name: "{{ ansible_host | replace('.', '-') }}"
    pi_labels: "pi-role=inference"
    k3s_server_url: "https://{{ lookup('env', 'K3S_SERVER_IP') }}:6443"
    k3s_token: "{{ lookup('env', 'K3S_TOKEN') }}"

  tasks:
    - name: Run node preparation
      import_role:
        name: node-prep

    - name: Install K3s Agent
      shell: |
        curl -sfL https://get.k3s.io | K3S_URL="{{ k3s_server_url }}" \
          K3S_TOKEN="{{ k3s_token }}" \
          INSTALL_K3S_EXEC="agent \
            --node-label {{ pi_labels }} \
            --node-name {{ pi_name }}" \
          sh -
      args:
        creates: /usr/local/bin/k3s

    - name: Wait for node to be ready
      pause:
        seconds: 10

    - name: Verify K3s Agent is running
      command: systemctl is-active k3s-agent
      register: agent_status
      failed_when: agent_status.stdout != "active"
```

- [ ] **Step 4: 创建 ansible/playbooks/leave-cluster.yml**

```yaml
---
- name: 将 Pi 节点从 K3s 集群中安全移除
  hosts: all

  tasks:
    - name: Stop K3s Agent
      systemd:
        name: k3s-agent
        state: stopped
      ignore_errors: yes

    - name: Uninstall K3s Agent
      command: /usr/local/bin/k3s-agent-uninstall.sh
      ignore_errors: yes

    - name: Clean up K3s data
      file:
        path: "{{ item }}"
        state: absent
      loop:
        - /var/lib/rancher/k3s
        - /var/lib/kubelet
        - /etc/rancher
      ignore_errors: yes

    - name: Reboot
      reboot:
        msg: "Rebooting after K3s removal"
```

- [ ] **Step 5: 提交**

```bash
git add ansible/
git commit -m "feat(ansible): add node-prep role and join/leave cluster playbooks"
```

---

### Task 2.5: System Info API

**Files:**
- Create: `backend/app/api/v1/system.py`

- [ ] **Step 1: 创建 backend/app/api/v1/system.py**

```python
"""系统信息 API."""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/info")
async def system_info():
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "api_versions": ["v1"],
    }


@router.get("/healthz")
async def healthz():
    """K8s-style health check."""
    return {"status": "healthy"}
```

- [ ] **Step 2: 注册到 main.py**

```python
from app.api.v1 import system
app.include_router(system.router, prefix="/api/v1")
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/api/v1/system.py
git commit -m "feat(backend): add system info and healthz endpoints"
```

---

## Iteration 3: Model & Inference — 模型管理 & 推理服务

### Task 3.1: 推理引擎抽象层

**Files:**
- Create: `backend/app/engines/__init__.py`
- Create: `backend/app/engines/base.py`
- Create: `backend/app/engines/ollama.py`

- [ ] **Step 1: 创建 backend/app/engines/base.py**

```python
"""推理引擎抽象接口."""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class InferenceEngine(ABC):
    """所有推理引擎的统一抽象."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """引擎名称: ollama, vllm, llamacpp."""
        ...

    @abstractmethod
    async def health(self, node_host: str) -> bool:
        """检查引擎健康状态."""
        ...

    @abstractmethod
    async def list_models(self, node_host: str) -> list[dict]:
        """列出节点上已加载的模型."""
        ...

    @abstractmethod
    async def pull_model(
        self, node_host: str, model_name: str
    ) -> dict:
        """拉取模型到节点."""
        ...

    @abstractmethod
    async def infer(
        self,
        node_host: str,
        model_name: str,
        messages: list[dict],
        **params,
    ) -> dict:
        """同步推理."""
        ...

    @abstractmethod
    async def infer_stream(
        self,
        node_host: str,
        model_name: str,
        messages: list[dict],
        **params,
    ) -> AsyncIterator[str]:
        """流式推理，逐 token yield."""
        ...
```

- [ ] **Step 2: 创建 backend/app/engines/ollama.py**

```python
"""Ollama 推理引擎实现."""

import json
from typing import AsyncIterator
import httpx
from app.engines.base import InferenceEngine


class OllamaEngine(InferenceEngine):
    engine_name = "ollama"

    def __init__(self, port: int = 11434, timeout: float = 300.0):
        self.port = port
        self.timeout = timeout

    def _base_url(self, node_host: str) -> str:
        return f"http://{node_host}:{self.port}"

    async def health(self, node_host: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self._base_url(node_host)}/")
                return r.status_code == 200
        except Exception:
            return False

    async def list_models(self, node_host: str) -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self._base_url(node_host)}/api/tags"
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "name": m["name"],
                    "size": m.get("size", ""),
                    "modified": m.get("modified_at", ""),
                }
                for m in data.get("models", [])
            ]

    async def pull_model(
        self, node_host: str, model_name: str
    ) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self._base_url(node_host)}/api/pull",
                json={"name": model_name, "stream": False},
            )
            r.raise_for_status()
            return r.json()

    async def infer(
        self,
        node_host: str,
        model_name: str,
        messages: list[dict],
        **params,
    ) -> dict:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                k: v
                for k, v in params.items()
                if k in ("temperature", "top_p", "num_predict")
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self._base_url(node_host)}/api/chat",
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            return {
                "model": data.get("model", model_name),
                "message": data.get("message", {}),
                "done": True,
                "total_duration": data.get("total_duration", 0),
                "eval_count": data.get("eval_count", 0),
            }

    async def infer_stream(
        self,
        node_host: str,
        model_name: str,
        messages: list[dict],
        **params,
    ) -> AsyncIterator[str]:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "options": {
                k: v
                for k, v in params.items()
                if k in ("temperature", "top_p", "num_predict")
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url(node_host)}/api/chat",
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk:
                                yield chunk["message"].get(
                                    "content", ""
                                )
                        except json.JSONDecodeError:
                            continue
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/engines/
git commit -m "feat(backend): add InferenceEngine abstraction and Ollama implementation"
```

---

### Task 3.2: Scheduler 调度器

**Files:**
- Create: `backend/app/core/scheduler.py`

- [ ] **Step 1: 创建 backend/app/core/scheduler.py**

```python
"""推理调度策略 —— 选择最优节点处理请求."""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NodeInfo:
    name: str
    host: str
    is_ready: bool
    active_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


class SchedulingStrategy(ABC):
    @abstractmethod
    async def select_node(
        self, model_name: str, nodes: list[NodeInfo]
    ) -> NodeInfo | None:
        """选择一个可用节点."""
        ...


class RoundRobinStrategy(SchedulingStrategy):
    """轮询分发."""

    def __init__(self):
        self._index = 0

    async def select_node(
        self, model_name: str, nodes: list[NodeInfo]
    ) -> NodeInfo | None:
        ready = [n for n in nodes if n.is_ready]
        if not ready:
            return None
        node = ready[self._index % len(ready)]
        self._index += 1
        return node


class LeastConnectionStrategy(SchedulingStrategy):
    """最少活跃连接."""

    async def select_node(
        self, model_name: str, nodes: list[NodeInfo]
    ) -> NodeInfo | None:
        ready = [n for n in nodes if n.is_ready]
        if not ready:
            return None
        return min(ready, key=lambda n: n.active_connections)


class RandomStrategy(SchedulingStrategy):
    """随机选择."""

    async def select_node(
        self, model_name: str, nodes: list[NodeInfo]
    ) -> NodeInfo | None:
        ready = [n for n in nodes if n.is_ready]
        if not ready:
            return None
        return random.choice(ready)


# 策略注册表
STRATEGIES: dict[str, SchedulingStrategy] = {
    "round_robin": RoundRobinStrategy(),
    "least_connection": LeastConnectionStrategy(),
    "random": RandomStrategy(),
}


def get_strategy(name: str = "round_robin") -> SchedulingStrategy:
    return STRATEGIES.get(name, RoundRobinStrategy())
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/core/scheduler.py
git commit -m "feat(backend): add pluggable scheduling strategies"
```

---

### Task 3.3: Inference Service & API

**Files:**
- Create: `backend/app/schemas/inference.py`
- Create: `backend/app/services/inference_service.py`
- Create: `backend/app/api/v1/inference.py`

- [ ] **Step 1: 创建 backend/app/schemas/inference.py**

```python
"""推理请求/响应 schemas."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, ge=1)
    stream: bool = False


class ChatResponse(BaseModel):
    model: str
    message: ChatMessage
    total_duration: int = 0
    eval_count: int = 0


class ModelDeployRequest(BaseModel):
    name: str  # e.g. "qwen2.5:7b"
    replicas: int = Field(default=0, description="0 = all nodes")
    node_names: list[str] = Field(default_factory=list)


class ModelDeployResponse(BaseModel):
    success: bool
    model: str
    nodes: list[str]
    message: str
```

- [ ] **Step 2: 创建 backend/app/services/inference_service.py**

```python
"""推理服务业务逻辑."""

import asyncio
from typing import AsyncIterator
from app.engines.ollama import OllamaEngine
from app.k8s.client import K8sClient
from app.core.scheduler import (
    NodeInfo,
    get_strategy,
    SchedulingStrategy,
)


class InferenceService:
    def __init__(
        self,
        k8s: K8sClient,
        engine: OllamaEngine | None = None,
    ):
        self.k8s = k8s
        self.engine = engine or OllamaEngine()

    async def _get_inference_nodes(self) -> list[NodeInfo]:
        """获取所有带 inference 标签的在线节点."""
        nodes = self.k8s.list_nodes()
        result = []
        for n in nodes:
            labels = n.get("labels", {})
            if labels.get("pi-role") == "inference":
                result.append(NodeInfo(
                    name=n["name"],
                    host=n["name"],  # 假设 hostname = IP可达
                    is_ready=n["status"] == "online",
                ))
        return result

    async def chat(
        self, model: str, messages: list[dict], **params
    ) -> dict:
        """同步 Chat Completion."""
        nodes = await self._get_inference_nodes()
        strategy: SchedulingStrategy = get_strategy("round_robin")
        target = await strategy.select_node(model, nodes)
        if not target:
            raise RuntimeError("No inference node available")
        return await self.engine.infer(
            target.host, model, messages, **params
        )

    async def chat_stream(
        self, model: str, messages: list[dict], **params
    ) -> AsyncIterator[str]:
        """流式 Chat Completion."""
        nodes = await self._get_inference_nodes()
        strategy = get_strategy("round_robin")
        target = await strategy.select_node(model, nodes)
        if not target:
            raise RuntimeError("No inference node available")
        async for token in self.engine.infer_stream(
            target.host, model, messages, **params
        ):
            yield token

    async def deploy_model(
        self, model_name: str, node_names: list[str] | None = None
    ) -> dict:
        """在所有推理节点上拉取模型."""
        nodes = await self._get_inference_nodes()
        if node_names:
            nodes = [n for n in nodes if n.name in node_names]
        results = await asyncio.gather(
            *[
                self.engine.pull_model(n.host, model_name)
                for n in nodes
            ],
            return_exceptions=True,
        )
        succeeded = [
            n.name for n, r in zip(nodes, results) if not isinstance(r, Exception)
        ]
        return {
            "success": len(succeeded) > 0,
            "model": model_name,
            "nodes": succeeded,
            "message": f"Deployed to {len(succeeded)}/{len(nodes)} nodes",
        }

    async def list_models(self) -> list[dict]:
        """聚合所有节点的模型列表."""
        nodes = await self._get_inference_nodes()
        all_models: dict[str, dict] = {}
        for n in nodes:
            try:
                models = await self.engine.list_models(n.host)
                for m in models:
                    key = m["name"]
                    if key not in all_models:
                        all_models[key] = {
                            "name": m["name"],
                            "nodes": [],
                        }
                    all_models[key]["nodes"].append(n.name)
            except Exception:
                continue
        return list(all_models.values())
```

- [ ] **Step 3: 创建 backend/app/api/v1/inference.py**

```python
"""推理服务 API 端点."""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.k8s.client import K8sClient
from app.services.inference_service import InferenceService
from app.schemas.inference import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ModelDeployRequest,
    ModelDeployResponse,
)

router = APIRouter(prefix="/inference", tags=["inference"])


def get_inference_service() -> InferenceService:
    return InferenceService(K8sClient())


@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completion(
    req: ChatRequest,
    service: InferenceService = Depends(get_inference_service),
):
    """OpenAI 兼容 Chat Completion."""
    if req.stream:
        # 流式走 SSE
        async def stream():
            async for token in service.chat_stream(
                req.model,
                [m.model_dump() for m in req.messages],
                temperature=req.temperature,
                top_p=req.top_p,
                num_predict=req.max_tokens,
            ):
                chunk = {
                    "choices": [{
                        "delta": {"content": token},
                        "index": 0,
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            stream(), media_type="text/event-stream"
        )

    try:
        result = await service.chat(
            req.model,
            [m.model_dump() for m in req.messages],
            temperature=req.temperature,
            top_p=req.top_p,
            num_predict=req.max_tokens,
        )
        return ChatResponse(
            model=result["model"],
            message=ChatMessage(
                role=result["message"].get("role", "assistant"),
                content=result["message"].get("content", ""),
            ),
            total_duration=result.get("total_duration", 0),
            eval_count=result.get("eval_count", 0),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_inference_models(
    service: InferenceService = Depends(get_inference_service),
):
    """列出集群中所有可用模型."""
    return await service.list_models()


@router.post("/models/deploy", response_model=ModelDeployResponse)
async def deploy_model(
    req: ModelDeployRequest,
    service: InferenceService = Depends(get_inference_service),
):
    """部署模型到推理节点."""
    result = await service.deploy_model(req.name, req.node_names or None)
    return ModelDeployResponse(**result)
```

- [ ] **Step 4: 注册 router**

```python
# 在 main.py 中添加:
from app.api.v1 import inference
app.include_router(inference.router, prefix="/api/v1")
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/schemas/inference.py backend/app/services/inference_service.py backend/app/api/v1/inference.py
git commit -m "feat(backend): add inference API with OpenAI-compatible chat endpoint"
```

---

### Task 3.4: Model Management API

**Files:**
- Create: `backend/app/api/v1/models.py`
- Create: `backend/app/schemas/model.py`
- Create: `backend/app/services/model_service.py`

- [ ] **Step 1: 创建 backend/app/schemas/model.py**

```python
"""模型管理 schemas."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    nodes: list[str] = []
    status: str = "unknown"

    model_config = {"from_attributes": True}


class ModelSwitchRequest(BaseModel):
    name: str
    version: str


class ModelScaleRequest(BaseModel):
    name: str
    replicas: int
```

- [ ] **Step 2: 创建 backend/app/services/model_service.py**

```python
"""模型管理业务逻辑."""

from app.k8s.client import K8sClient
from app.engines.ollama import OllamaEngine


class ModelService:
    def __init__(self, k8s: K8sClient):
        self.k8s = k8s
        self.engine = OllamaEngine()

    async def list_models(self) -> list[dict]:
        """聚合所有节点模型."""
        nodes = self.k8s.list_nodes()
        inference_nodes = [
            n for n in nodes
            if n.get("labels", {}).get("pi-role") == "inference"
        ]
        all_models: dict[str, dict] = {}
        for n in inference_nodes:
            try:
                models = await self.engine.list_models(n["name"])
                for m in models:
                    key = m["name"]
                    if key not in all_models:
                        all_models[key] = {
                            "name": m["name"],
                            "nodes": [],
                            "status": "ready",
                        }
                    all_models[key]["nodes"].append(n["name"])
            except Exception:
                continue
        return list(all_models.values())
```

- [ ] **Step 3: 创建 backend/app/api/v1/models.py**

```python
"""模型管理 API 端点."""

from fastapi import APIRouter, Depends
from app.k8s.client import K8sClient
from app.services.model_service import ModelService
from app.schemas.model import ModelInfo

router = APIRouter(prefix="/models", tags=["models"])


def get_model_service() -> ModelService:
    return ModelService(K8sClient())


@router.get("", response_model=list[ModelInfo])
async def list_models(
    service: ModelService = Depends(get_model_service),
):
    """列出集群中已部署的模型."""
    return await service.list_models()
```

- [ ] **Step 4: 注册到 main.py 并提交**

```bash
git add backend/app/api/v1/models.py backend/app/services/model_service.py backend/app/schemas/model.py
git commit -m "feat(backend): add model management API"
```

---

## Iteration 4: Dashboard — Vue 3 前端

### Task 4.1: API 客户端 & 状态管理

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/stores/nodes.ts`
- Create: `frontend/src/stores/models.ts`

- [ ] **Step 1: 创建 frontend/src/api/client.ts**

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 节点 API
export const nodeApi = {
  list: () => api.get('/nodes'),
  get: (name: string) => api.get(`/nodes/${name}`),
  join: (data: { host: string; name?: string; labels?: Record<string, string> }) =>
    api.post('/nodes/join', data),
  drain: (name: string) => api.delete(`/nodes/${name}`),
}

// 模型 API
export const modelApi = {
  list: () => api.get('/models'),
  deploy: (name: string, nodeNames?: string[]) =>
    api.post('/inference/models/deploy', { name, node_names: nodeNames }),
}

// 推理 API
export const inferenceApi = {
  models: () => api.get('/inference/models'),
  chat: (data: {
    model: string
    messages: { role: string; content: string }[]
    temperature?: number
    max_tokens?: number
    stream?: boolean
  }) => api.post('/inference/chat/completions', data),
}

// 系统 API
export const systemApi = {
  info: () => api.get('/system/info'),
}

export default api
```

- [ ] **Step 2: 创建 frontend/src/stores/nodes.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nodeApi } from '@/api/client'

export interface NodeSummary {
  name: string
  status: string
  cpu_usage: number
  memory_usage: number
  temperature: number
  labels: Record<string, string>
  kubelet_version: string
  is_active: boolean
}

export const useNodesStore = defineStore('nodes', () => {
  const nodes = ref<NodeSummary[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchNodes() {
    loading.value = true
    error.value = null
    try {
      const { data } = await nodeApi.list()
      nodes.value = data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function joinNode(host: string, name?: string) {
    await nodeApi.join({ host, name })
    await fetchNodes()
  }

  async function drainNode(name: string) {
    await nodeApi.drain(name)
    await fetchNodes()
  }

  return { nodes, loading, error, fetchNodes, joinNode, drainNode }
})
```

- [ ] **Step 3: 创建 frontend/src/stores/models.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { modelApi } from '@/api/client'

export interface ModelSummary {
  name: string
  nodes: string[]
  status: string
}

export const useModelsStore = defineStore('models', () => {
  const models = ref<ModelSummary[]>([])
  const loading = ref(false)

  async function fetchModels() {
    loading.value = true
    try {
      const { data } = await modelApi.list()
      models.value = data
    } finally {
      loading.value = false
    }
  }

  async function deployModel(name: string, nodeNames?: string[]) {
    await modelApi.deploy(name, nodeNames)
    await fetchModels()
  }

  return { models, loading, fetchModels, deployModel }
})
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/api/ frontend/src/stores/
git commit -m "feat(frontend): add API client and Pinia stores for nodes and models"
```

---

### Task 4.2: Dashboard 页面 + NodeCard 组件

**Files:**
- Create: `frontend/src/components/NodeCard.vue`
- Create: `frontend/src/components/ResourceChart.vue`
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/components/Layout.vue` (添加导航)

- [ ] **Step 1: 创建 frontend/src/components/NodeCard.vue**

```vue
<template>
  <div class="node-card" :class="`status-${node.status}`">
    <div class="node-header">
      <span class="status-dot" :title="node.status"></span>
      <strong>{{ node.name }}</strong>
      <span class="version">{{ node.kubelet_version }}</span>
    </div>
    <div class="node-metrics">
      <div class="metric">
        <label>CPU</label>
        <div class="bar"><div class="fill" :style="{ width: node.cpu_usage + '%' }"></div></div>
        <span>{{ node.cpu_usage.toFixed(1) }}%</span>
      </div>
      <div class="metric">
        <label>MEM</label>
        <div class="bar"><div class="fill" :style="{ width: node.memory_usage + '%' }"></div></div>
        <span>{{ node.memory_usage.toFixed(1) }}%</span>
      </div>
      <div class="metric">
        <label>TEMP</label>
        <span :class="{ hot: node.temperature > 75 }">{{ node.temperature }}°C</span>
      </div>
    </div>
    <div class="node-labels">
      <span v-for="(v, k) in node.labels" :key="k" class="tag">{{ k }}={{ v }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NodeSummary } from '@/stores/nodes'

defineProps<{ node: NodeSummary }>()
</script>

<style scoped>
.node-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border-left: 4px solid #ccc;
}
.node-card.status-online { border-left-color: #4caf50; }
.node-card.status-offline { border-left-color: #f44336; }
.node-card.status-pending { border-left-color: #ff9800; }
.node-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.status-dot {
  width: 10px; height: 10px; border-radius: 50%; background: #ccc;
}
.status-online .status-dot { background: #4caf50; }
.status-offline .status-dot { background: #f44336; }
.version { font-size: 12px; color: #999; margin-left: auto; }
.node-metrics { display: flex; flex-direction: column; gap: 8px; }
.metric { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.metric label { width: 40px; color: #666; }
.bar { flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
.bar .fill { height: 100%; background: #2196f3; border-radius: 3px; transition: width 0.3s; }
.tag { font-size: 11px; background: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 3px; }
.hot { color: #f44336; font-weight: bold; }
</style>
```

- [ ] **Step 2: 更新 frontend/src/views/Dashboard.vue**

```vue
<template>
  <div class="dashboard">
    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-value">{{ nodes.length }}</span>
        <span class="stat-label">节点总数</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ onlineCount }}</span>
        <span class="stat-label">在线</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ models.length }}</span>
        <span class="stat-label">已部署模型</span>
      </div>
    </div>
    <h3>节点列表</h3>
    <div v-if="nodesStore.loading">加载中...</div>
    <div v-else class="node-grid">
      <NodeCard v-for="node in nodes" :key="node.name" :node="node" />
    </div>
    <div v-if="nodes.length === 0 && !nodesStore.loading" class="empty">
      暂无节点 — 运行 <code>k3s-pi node add &lt;ip&gt;</code> 添加 Pi 节点
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useNodesStore } from '@/stores/nodes'
import { useModelsStore } from '@/stores/models'
import NodeCard from '@/components/NodeCard.vue'

const nodesStore = useNodesStore()
const modelsStore = useModelsStore()

const nodes = computed(() => nodesStore.nodes)
const models = computed(() => modelsStore.models)
const onlineCount = computed(() => nodes.value.filter(n => n.status === 'online').length)

onMounted(() => {
  nodesStore.fetchNodes()
  modelsStore.fetchModels()
})
</script>

<style scoped>
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card {
  background: #fff; padding: 16px 24px; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; min-width: 120px;
}
.stat-value { display: block; font-size: 28px; font-weight: bold; color: #1a1a2e; }
.stat-label { font-size: 13px; color: #999; }
.node-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.empty { color: #999; text-align: center; padding: 40px; }
.empty code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }
</style>
```

- [ ] **Step 3: 更新 Layout.vue 导航**

```vue
<nav>
  <router-link to="/">📊 总览</router-link>
  <router-link to="/nodes">🖥 节点管理</router-link>
  <router-link to="/models">🧠 模型管理</router-link>
  <router-link to="/logs">📋 日志</router-link>
  <router-link to="/settings">⚙️ 设置</router-link>
</nav>
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/NodeCard.vue frontend/src/views/Dashboard.vue frontend/src/components/Layout.vue
git commit -m "feat(frontend): add Dashboard page with NodeCard and stats"
```

---

### Task 4.3: Nodes & Models 页面

**Files:**
- Create: `frontend/src/views/Nodes.vue`
- Create: `frontend/src/views/NodeDetail.vue`
- Create: `frontend/src/views/Models.vue`
- Create: `frontend/src/components/ModelDeployDialog.vue`
- Modify: `frontend/src/router/index.ts` (add routes)

- [ ] **Step 1: 添加路由**

```typescript
// frontend/src/router/index.ts 添加:
{
  path: '/nodes',
  name: 'nodes',
  component: () => import('@/views/Nodes.vue'),
},
{
  path: '/nodes/:name',
  name: 'node-detail',
  component: () => import('@/views/NodeDetail.vue'),
  props: true,
},
{
  path: '/models',
  name: 'models',
  component: () => import('@/views/Models.vue'),
},
{
  path: '/logs',
  name: 'logs',
  component: () => import('@/views/Logs.vue'),
},
{
  path: '/settings',
  name: 'settings',
  component: () => import('@/views/Settings.vue'),
},
```

- [ ] **Step 2: 创建 frontend/src/views/Nodes.vue**

```vue
<template>
  <div class="nodes-page">
    <div class="page-header">
      <h2>节点管理</h2>
      <button class="btn-primary" @click="showJoinDialog = true">+ 添加节点</button>
    </div>
    <div v-if="nodesStore.loading">加载中...</div>
    <div v-else class="node-grid">
      <NodeCard v-for="node in nodes" :key="node.name" :node="node"
        @click="$router.push(`/nodes/${node.name}`)" />
    </div>
    <!-- 添加节点 Dialog -->
    <div v-if="showJoinDialog" class="dialog-overlay" @click.self="showJoinDialog = false">
      <div class="dialog">
        <h3>添加 Pi 节点</h3>
        <form @submit.prevent="handleJoin">
          <label>Pi IP 地址</label>
          <input v-model="joinHost" placeholder="192.168.1.x" required />
          <label>节点名称 (可选)</label>
          <input v-model="joinName" placeholder="pi-4" />
          <div class="dialog-actions">
            <button type="button" @click="showJoinDialog = false">取消</button>
            <button type="submit" class="btn-primary">加入集群</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useNodesStore } from '@/stores/nodes'
import NodeCard from '@/components/NodeCard.vue'

const nodesStore = useNodesStore()
const nodes = computed(() => nodesStore.nodes)
const showJoinDialog = ref(false)
const joinHost = ref('')
const joinName = ref('')

async function handleJoin() {
  await nodesStore.joinNode(joinHost.value, joinName.value || undefined)
  showJoinDialog.value = false
  joinHost.value = ''
  joinName.value = ''
}
</script>
```

- [ ] **Step 3: 创建 frontend/src/views/Models.vue**

```vue
<template>
  <div class="models-page">
    <div class="page-header">
      <h2>模型管理</h2>
      <button class="btn-primary" @click="showDeployDialog = true">+ 部署模型</button>
    </div>
    <div v-if="modelsStore.loading">加载中...</div>
    <div v-else class="model-list">
      <div v-for="model in models" :key="model.name" class="model-card">
        <div class="model-name">
          <span class="icon">🧠</span>
          <strong>{{ model.name }}</strong>
          <span class="status-badge" :class="model.status">{{ model.status }}</span>
        </div>
        <div class="model-nodes">
          部署节点: <span v-for="n in model.nodes" :key="n" class="tag">{{ n }}</span>
        </div>
      </div>
    </div>
    <ModelDeployDialog v-if="showDeployDialog" @close="showDeployDialog = false"
      @deploy="handleDeploy" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useModelsStore } from '@/stores/models'
import ModelDeployDialog from '@/components/ModelDeployDialog.vue'

const modelsStore = useModelsStore()
const models = computed(() => modelsStore.models)
const showDeployDialog = ref(false)

async function handleDeploy(name: string) {
  await modelsStore.deployModel(name)
  showDeployDialog.value = false
}
</script>
```

- [ ] **Step 4: 创建 placeholder 页面 (Logs.vue, Settings.vue, NodeDetail.vue)**

```vue
<!-- frontend/src/views/Logs.vue -->
<template>
  <div><h2>日志查看</h2><p>Loki 集成将在后续迭代实现</p></div>
</template>

<!-- frontend/src/views/Settings.vue -->
<template>
  <div><h2>系统设置</h2><p>配置项将在后续迭代实现</p></div>
</template>

<!-- frontend/src/views/NodeDetail.vue -->
<template>
  <div><h2>节点详情: {{ name }}</h2><p>详细信息将在后续迭代实现</p></div>
</template>
<script setup lang="ts">
defineProps<{ name: string }>()
</script>
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/views/ frontend/src/router/ frontend/src/components/ModelDeployDialog.vue
git commit -m "feat(frontend): add Nodes, Models pages with join and deploy dialogs"
```

---

## Iteration 5: CLI — 命令行工具

### Task 5.1: CLI 项目初始化 & 基础命令

**Files:**
- Create: `cli/pyproject.toml`
- Create: `cli/pi_cli/__init__.py`
- Create: `cli/pi_cli/main.py`
- Create: `cli/pi_cli/client.py`
- Create: `cli/pi_cli/commands/__init__.py`
- Create: `cli/pi_cli/commands/nodes.py`
- Create: `cli/pi_cli/commands/models.py`
- Create: `cli/pi_cli/commands/inference.py`

- [ ] **Step 1: 创建 cli/pyproject.toml**

```toml
[project]
name = "pi-cli"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.15.0",
    "rich>=13.0.0",
    "httpx>=0.28.0",
]

[project.scripts]
k3s-pi = "pi_cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: 创建 cli/pi_cli/client.py**

```python
"""后端 API 客户端."""

import httpx

DEFAULT_API = "http://localhost:8000/api/v1"


class APIClient:
    def __init__(self, base_url: str = DEFAULT_API):
        self.client = httpx.Client(
            base_url=base_url, timeout=30.0
        )

    def list_nodes(self) -> list[dict]:
        r = self.client.get("/nodes")
        r.raise_for_status()
        return r.json()

    def join_node(self, host: str, name: str | None = None) -> dict:
        r = self.client.post(
            "/nodes/join", json={"host": host, "name": name}
        )
        r.raise_for_status()
        return r.json()

    def drain_node(self, name: str) -> dict:
        r = self.client.delete(f"/nodes/{name}")
        r.raise_for_status()
        return r.json()

    def list_models(self) -> list[dict]:
        r = self.client.get("/models")
        r.raise_for_status()
        return r.json()

    def deploy_model(self, name: str, node_names: list[str] | None = None) -> dict:
        r = self.client.post(
            "/inference/models/deploy",
            json={"name": name, "node_names": node_names},
        )
        r.raise_for_status()
        return r.json()

    def chat(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        r = self.client.post(
            "/inference/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": stream,
            },
            timeout=300.0,
        )
        r.raise_for_status()
        return r.json()
```

- [ ] **Step 3: 创建 cli/pi_cli/main.py**

```python
"""k3s-pi CLI 入口."""

import typer
from pi_cli.commands import nodes, models, inference

app = typer.Typer(
    name="k3s-pi",
    help="Pi Cluster LLM 集群管理命令行工具",
    no_args_is_help=True,
)

app.add_typer(nodes.app, name="node", help="节点管理")
app.add_typer(models.app, name="model", help="模型管理")
app.add_typer(inference.app, name="infer", help="推理操作")


@app.command()
def status():
    """集群状态总览."""
    from pi_cli.client import APIClient
    from rich.console import Console
    from rich.table import Table

    client = APIClient()
    console = Console()

    # 系统信息
    try:
        nodes_list = client.list_nodes()
    except Exception as e:
        console.print(f"[red]无法连接后端: {e}[/red]")
        return

    online = sum(1 for n in nodes_list if n["status"] == "online")

    console.print(f"\n[bold]🖥 Pi Cluster LLM[/bold]")
    console.print(f"节点: {len(nodes_list)} 总数 / {online} 在线\n")

    table = Table(title="节点列表")
    table.add_column("名称")
    table.add_column("状态")
    table.add_column("版本")

    for n in nodes_list:
        status_icon = {"online": "🟢", "offline": "🔴"}.get(
            n["status"], "🟡"
        )
        table.add_row(
            n["name"],
            f"{status_icon} {n['status']}",
            n.get("kubelet_version", ""),
        )

    console.print(table)


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: 创建命令文件**

```python
# cli/pi_cli/commands/nodes.py
import typer
from rich.console import Console
from rich.table import Table
from pi_cli.client import APIClient

app = typer.Typer(help="节点管理", no_args_is_help=True)
console = Console()


@app.command("list")
def list_nodes():
    """列出所有节点."""
    client = APIClient()
    nodes = client.list_nodes()
    table = Table(title="Pi 推理节点")
    table.add_column("名称")
    table.add_column("状态")
    table.add_column("角色")
    for n in nodes:
        labels = n.get("labels", {})
        role = labels.get("pi-role", "-")
        icon = {"online": "🟢", "offline": "🔴"}.get(n["status"], "🟡")
        table.add_row(n["name"], f"{icon} {n['status']}", role)
    console.print(table)


@app.command("add")
def add_node(host: str, name: str = typer.Option(None, "--name", "-n")):
    """添加 Pi 节点到集群."""
    client = APIClient()
    result = client.join_node(host, name)
    console.print(f"[green]{result['message']}[/green]")
    if result.get("join_command"):
        console.print(f"\n运行命令:")
        console.print(f"  [bold]{result['join_command']}[/bold]")


@app.command("drain")
def drain_node(name: str):
    """安全下线节点."""
    client = APIClient()
    client.drain_node(name)
    console.print(f"[yellow]节点 {name} 已下线[/yellow]")
```

```python
# cli/pi_cli/commands/models.py
import typer
from rich.console import Console
from rich.table import Table
from pi_cli.client import APIClient

app = typer.Typer(help="模型管理", no_args_is_help=True)
console = Console()


@app.command("list")
def list_models():
    """列出已部署模型."""
    client = APIClient()
    models = client.list_models()
    table = Table(title="已部署模型")
    table.add_column("模型名")
    table.add_column("节点数")
    table.add_column("节点")
    for m in models:
        table.add_row(m["name"], str(len(m.get("nodes", []))), ", ".join(m.get("nodes", [])))
    console.print(table)


@app.command("deploy")
def deploy_model(name: str):
    """部署模型到所有推理节点."""
    client = APIClient()
    result = client.deploy_model(name)
    console.print(f"[green]✓ 模型 {name} 部署到: {', '.join(result['nodes'])}[/green]")
```

```python
# cli/pi_cli/commands/inference.py
import typer
from rich.console import Console
from pi_cli.client import APIClient

app = typer.Typer(help="推理服务", no_args_is_help=True)
console = Console()


@app.command("chat")
def chat(
    prompt: str = typer.Option(..., "--prompt", "-p", help="输入提示词"),
    model: str = typer.Option("qwen2.5:7b", "--model", "-m", help="模型名"),
    temperature: float = typer.Option(0.7, "--temp", "-t"),
):
    """发送 Chat 请求."""
    client = APIClient()
    try:
        result = client.chat(model, prompt, temperature)
        msg = result.get("message", {})
        console.print(f"\n[bold cyan]🤖 {result['model']}[/bold cyan]")
        console.print(msg.get("content", ""))
        console.print(
            f"\n[dim]tokens: {result.get('eval_count', 0)} | "
            f"duration: {result.get('total_duration', 0) / 1e9:.2f}s[/dim]"
        )
    except Exception as e:
        console.print(f"[red]推理失败: {e}[/red]")
```

- [ ] **Step 5: 安装并验证 CLI**

```bash
cd cli
uv sync
uv run k3s-pi --help
# Expected: 显示命令树
```

- [ ] **Step 6: 提交**

```bash
git add cli/
git commit -m "feat(cli): add k3s-pi CLI with node, model, and inference commands"
```

---

## Iteration 6: Observability — 可观测性

### Task 6.1: Prometheus + Node Exporter 部署

**Files:**
- Create: `k3s/base/prometheus-config.yaml`
- Create: `k3s/base/prometheus-deployment.yaml`
- Create: `k3s/base/grafana-deployment.yaml`

- [ ] **Step 1: 创建 Prometheus 配置**

```yaml
# k3s/base/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: pi-cluster
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'k3s-nodes'
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - source_labels: [__address__]
            regex: '(.*):10250'
            target_label: __address__
            replacement: '${1}:9100'

      - job_name: 'ollama'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: [pi-cluster]
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            regex: ollama
            action: keep
          - source_labels: [__address__]
            regex: '(.*):11434'
            target_label: __address__
            replacement: '${1}:11434'
```

- [ ] **Step 2: 创建 Prometheus Deployment**

```yaml
# k3s/base/prometheus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: pi-cluster
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:v3.1.0
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
          args:
            - --config.file=/etc/prometheus/prometheus.yml
      volumes:
        - name: config
          configMap:
            name: prometheus-config
```

- [ ] **Step 3: 创建 Grafana Deployment**

```yaml
# k3s/base/grafana-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: pi-cluster
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:11.4.0
          ports:
            - containerPort: 3000
          env:
            - name: GF_AUTH_ANONYMOUS_ENABLED
              value: "true"
            - name: GF_SERVER_HTTP_PORT
              value: "3000"
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: pi-cluster
spec:
  type: NodePort
  ports:
    - port: 3000
      nodePort: 30300
  selector:
    app: grafana
```

- [ ] **Step 4: 提交**

```bash
git add k3s/base/prometheus-*.yaml k3s/base/grafana-*.yaml
git commit -m "feat(k3s): add Prometheus and Grafana deployments"
```

---

### Task 6.2: Loki + Promtail 日志采集

**Files:**
- Create: `k3s/base/loki-deployment.yaml`
- Create: `k3s/base/promtail-daemonset.yaml`

- [ ] **Step 1: 创建 Loki Deployment**

```yaml
# k3s/base/loki-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loki
  namespace: pi-cluster
spec:
  replicas: 1
  selector:
    matchLabels:
      app: loki
  template:
    metadata:
      labels:
        app: loki
    spec:
      containers:
        - name: loki
          image: grafana/loki:3.3.0
          ports:
            - containerPort: 3100
          args:
            - -config.file=/etc/loki/local-config.yaml
---
apiVersion: v1
kind: Service
metadata:
  name: loki
  namespace: pi-cluster
spec:
  ports:
    - port: 3100
  selector:
    app: loki
```

- [ ] **Step 2: 创建 Promtail DaemonSet**

```yaml
# k3s/base/promtail-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
  namespace: pi-cluster
spec:
  selector:
    matchLabels:
      app: promtail
  template:
    metadata:
      labels:
        app: promtail
    spec:
      nodeSelector:
        pi-role: inference
      containers:
        - name: promtail
          image: grafana/promtail:3.3.0
          args:
            - -config.file=/etc/promtail/config.yml
          volumeMounts:
            - name: config
              mountPath: /etc/promtail
            - name: varlog
              mountPath: /var/log
              readOnly: true
            - name: docker
              mountPath: /var/lib/docker/containers
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: promtail-config
        - name: varlog
          hostPath:
            path: /var/log
        - name: docker
          hostPath:
            path: /var/lib/docker/containers
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: pi-cluster
data:
  config.yml: |
    server:
      http_listen_port: 9080
    positions:
      filename: /tmp/positions.yaml
    clients:
      - url: http://loki.pi-cluster:3100/loki/api/v1/push
    scrape_configs:
      - job_name: containers
        static_configs:
          - targets: [localhost]
            labels:
              job: container-logs
              __path__: /var/log/containers/*.log
```

- [ ] **Step 3: 提交**

```bash
git add k3s/base/loki-*.yaml k3s/base/promtail-*.yaml
git commit -m "feat(k3s): add Loki and Promtail for log aggregation"
```

---

## Iteration 7: Polish — 收尾

### Task 7.1: 端到端测试 & 文档

**Files:**
- Create: `docs/architecture.md`
- Create: `scripts/bench-inference.sh`

- [ ] **Step 1: 创建 docs/architecture.md**

```markdown
# Pi Cluster LLM 架构说明

## 快速开始

### 1. 初始化 WSL2 控制面

```bash
# 在 WSL2 Ubuntu 中
bash scripts/setup-wsl2.sh
```

### 2. 配置 Windows 端口转发

```powershell
# Windows PowerShell (管理员)
$wsl_ip = wsl hostname -I
netsh interface portproxy add v4tov4 listenport=6443 listenaddress=0.0.0.0 connectport=6443 connectaddress=$wsl_ip
```

### 3. 启动管理平台

```bash
# 终端1: Backend
make dev-backend

# 终端2: Frontend
make dev-frontend
```

### 4. 烧录 Pi 并加入集群

```bash
# 烧录 Pi OS → 开机 → 运行:
k3s-pi node add 192.168.1.x
```

### 5. 部署模型

```bash
k3s-pi model deploy qwen2.5:7b
```

### 6. 测试推理

```bash
k3s-pi infer chat --prompt "你好，介绍一下你自己"
```

浏览器访问 http://localhost:5173 查看 Dashboard。
```

- [ ] **Step 2: 创建 scripts/bench-inference.sh**

```bash
#!/bin/bash
# 推理性能压测脚本
set -euo pipefail

API="${PI_CLUSTER_API:-http://localhost:8000/api/v1}"
MODEL="${1:-qwen2.5:7b}"
CONCURRENCY="${2:-5}"
REQUESTS="${3:-20}"

echo "=== 推理压测 ==="
echo "模型: $MODEL | 并发: $CONCURRENCY | 请求数: $REQUESTS"
echo ""

total_time=0
success=0

for i in $(seq 1 $REQUESTS); do
    start=$(date +%s%N)
    response=$(curl -s -X POST "$API/inference/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":50}" \
        2>/dev/null) || true
    end=$(date +%s%N)
    elapsed=$(( (end - start) / 1000000 ))  # ms

    if echo "$response" | grep -q '"content"'; then
        success=$((success + 1))
        echo "  [$i/$REQUESTS] ${elapsed}ms ✓"
    else
        echo "  [$i/$REQUESTS] ${elapsed}ms ✗ FAILED"
    fi
    total_time=$((total_time + elapsed))
done

avg=$((total_time / REQUESTS))
echo ""
echo "=== 结果 ==="
echo "成功: $success/$REQUESTS"
echo "平均延迟: ${avg}ms"
```

```bash
chmod +x scripts/bench-inference.sh
```

- [ ] **Step 3: 最终提交**

```bash
git add docs/architecture.md scripts/bench-inference.sh
git commit -m "docs: add architecture guide and inference benchmark script"
```

---

## 验证清单

在每次迭代结束时，确认以下检查点:

- [ ] `make test` 通过（所有后端测试）
- [ ] `make lint` 通过（ruff + vue-tsc）
- [ ] `cd frontend && npm run build` 成功
- [ ] Backend 在 WSL2 内 `curl http://localhost:8000/health` 返回 `{"status":"ok"}`
- [ ] Frontend `curl http://localhost:5173` 返回 HTML
- [ ] `kubectl get nodes` 能看到 K3s 节点
- [ ] Git commit 原子化，每个 Task 一个 commit

---

## 风险提醒

1. **WSL2 网络**: 每次 WSL2 重启 IP 可能变化，需要重新配端口转发。考虑用脚本自动化。
2. **Ollama ARM 版本**: 确保拉取的 Ollama 镜像支持 `linux/arm64`。
3. **Pi SD 卡**: 模型文件放在 `/data/ollama` (hostPath)，建议挂载 USB SSD 到该路径。
4. **WiFi 稳定性**: 如果频繁心跳丢失，调大 K3s `--node-monitor-grace-period` 参数。
