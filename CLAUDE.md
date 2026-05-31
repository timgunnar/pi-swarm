# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pi Cluster LLM — 树莓派集群分布式大模型推理管理系统。控制面/数据面分离架构，对标工业 K8s 部署实践。

## Architecture

```
PC (Windows + WSL2)  ← 控制面          │  Pi 5 × N  ← 数据面 (同构节点)
├─ K3s Server        ← 集群大脑         │  ├─ K3s Agent
├─ FastAPI Backend   ← 管理 API         │  └─ Ollama (DaemonSet)
├─ Vue 3 Frontend    ← Dashboard        │  所有 Pi 角色完全相同
├─ CLI (k3s-pi)      ← 命令行工具        │  可随时加入/退出
└─ Prometheus+Grafana+Loki ← 可观测性
```

**关键设计决策:**
- K3s Server 在 WSL2，不在 Pi 上 — 确保 Pi 资源全留给推理
- Pi 节点完全同构，无主从之分 — 支持热加入/退出
- 推理引擎抽象层 (策略模式) — Ollama 是第一实现，后续可插拔 vLLM
- 调度策略插件化 — 轮询/最少连接/资源感知，配置切换
- 数据库 SQLite 起步 + SQLAlchemy + Alembic — 后续可平滑迁移 PostgreSQL

## Full Design & Plan

- 设计文档: `docs/superpowers/specs/2026-05-31-pi-cluster-llm-design.md`
- 实施计划: `docs/superpowers/plans/2026-05-31-pi-cluster-llm-plan.md`

所有架构细节、API 端点、未来路线图均在设计文档中。实施前先查阅这两个文件。

## Tech Stack

| 层 | 技术 |
|----|------|
| 编排 | K3s (Server in WSL2, Agent on Pi) |
| 后端 | Python 3.12+ / FastAPI / SQLAlchemy / Alembic |
| 前端 | Vue 3 + TypeScript + Vite + Pinia + ECharts |
| CLI | Python typer + rich + httpx |
| 推理 | Ollama (ARM64) |
| 节点初始化 | Ansible |
| 监控 | Prometheus + Grafana + Loki + Promtail |
| CI | GitHub Actions |

## Commands

```bash
# 开发
make dev-backend     # uvicorn --reload :8000
make dev-frontend    # vite dev :5173, proxy /api → :8000
make lint            # ruff check + vue-tsc
make test            # pytest backend/tests/

# K3s
make k3s-apply       # kubectl apply -f k3s/base/
make k3s-status      # kubectl get nodes + pods

# CLI
k3s-pi node list | add <ip> | drain <name>
k3s-pi model list | deploy <name>
k3s-pi infer chat --prompt "..."
k3s-pi status

# Ansible (新 Pi 加入集群)
ansible-playbook ansible/playbooks/join-cluster.yml \
  -e "pi_ip=192.168.1.x" \
  -e "k3s_token=<token>" \
  -e "k3s_server_url=https://<PC_IP>:6443"
```

## Monorepo Structure

```
backend/     FastAPI — app/main.py 入口, api/v1/ 路由, engines/ 抽象, services/ 逻辑, k8s/ 客户端
frontend/    Vue 3 — src/views/ 页面, components/ 组件, stores/ Pinia, api/client.ts HTTP
cli/         Python CLI — pi_cli/main.py 入口, commands/ 子命令, client.py API 客户端
k3s/base/    K8s 清单 — ollama DaemonSet/Service, Prometheus, Grafana, Loki
ansible/     Pi 节点初始化 — roles/node-prep, playbooks/join|leave-cluster.yml
scripts/     setup-wsl2.sh 初始化 WSL2 K3s Server, bench-inference.sh 压测
```

## WSL2 Networking

Pi 需要访问 WSL2 内 K3s API (6443)。WSL2 默认 NAT，需在 Windows 管理员 PowerShell 配置端口转发:

```powershell
netsh interface portproxy add v4tov4 listenport=6443 listenaddress=0.0.0.0 connectport=6443 connectaddress=<WSL2_IP>
```

或启用 WSL2 mirrored 网络模式 (`.wslconfig` 中 `networkingMode=mirrored`)。
