# pi-swarm — 分布式推理集群管理系统 · 设计文档

> **版本**: v2.2  
> **日期**: 2026-05-31  
> **状态**: 待评审  
> **变更**: v2.2 — 项目正式命名为 pi-swarm  
> v2.1 — 新增 Agent 分布式执行引擎 (Scatter/Gather)

---

## 1. 项目概述

### 1.1 目标

构建一个**可扩展的树莓派集群管理系统**，以**本地大语言模型分布式推理**为核心工作负载。系统对标工业级部署实践，覆盖集群管理、模型管理、推理服务、可观测性全链路。

### 1.2 硬件拓扑

```
┌────────────────────────────────────────────────────────────┐
│                     你的电脑 (Windows + WSL2)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  K3s Server (控制面)      │  管理平台                  │  │
│  │  - 集群调度               │  - Backend (FastAPI)       │  │
│  │  - 服务发现               │  - Frontend (Vue 3)        │  │
│  │  - 状态存储               │  - CLI 工具                │  │
│  │                           │  - kubectl                 │  │
│  └───────────────────────────┴───────────────────────────┘  │
└──────────────────────┬─────────────────────────────────────┘
                       │ WiFi 局域网
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Pi #1   │   │ Pi #2   │   │ Pi #3   │   │ Pi #N   │
   │ Agent   │   │ Agent   │   │ Agent   │   │ Agent   │
   │ 8 GB    │   │ 8 GB    │   │ 8 GB    │   │ 8 GB    │
   │ Ollama  │   │ Ollama  │   │ Ollama  │   │ Ollama  │
   └─────────┘   └─────────┘   └─────────┘   └─────────┘
   ▲ 所有 Pi 角色完全相同，可随时加入/退出
```

| 角色 | 设备 | 职责 |
|------|------|------|
| **管理节点** | 你的电脑 (WSL2) | K3s Server、管理平台、CLI、可观测性 |
| **推理节点** | Pi 5 × N | K3s Agent、Ollama 推理容器 |

| 项目 | 规格 |
|------|------|
| 推理节点 | Pi 5 × 3（初始），可动态扩展 |
| 每节点内存 | 8 GB |
| 网络 | WiFi 局域网 |
| 每 Pi 可用内存 | ~7.5 GB（K3s Agent 仅占 ~100MB） |

### 1.3 核心原则

- **工业对标** — 控制面/数据面分离，技术栈对标公司 K8s 实践
- **渐进扩展** — Pi 节点可热加入/退出，架构预留高级功能扩展点
- **同构节点** — 所有 Pi 角色完全相同，无主从之分
- **可操作性强** — Web + CLI 双重管理入口

---

## 2. 整体架构

### 2.1 核心思想：控制面/数据面分离

```

         你的电脑 (管理节点)                    Pi 集群 (推理节点池)
    ┌─────────────────────────┐       ┌──────────────────────────────┐
    │                         │       │                              │
    │  ┌───────────────────┐  │       │  Pi #1    Pi #2    Pi #3    │
    │  │   K3s Server      │  │       │  ┌──┐     ┌──┐     ┌──┐    │
    │  │   (WSL2 内运行)   │◄─┼─WiFi──┼─►│  │     │  │     │  │    │
    │  │   集群大脑         │  │       │  │  │     │  │     │  │    │
    │  └───────────────────┘  │       │  └──┘     └──┘     └──┘    │
    │                         │       │  K3s      K3s      K3s      │
    │  ┌───────────────────┐  │       │  Agent    Agent    Agent    │
    │  │  FastAPI Backend  │  │       │  ┌──┐     ┌──┐     ┌──┐    │
    │  │  (直接运行/Pod)    │  │       │  │O │     │O │     │O │    │
    │  └───────────────────┘  │       │  │l │     │l │     │l │    │
    │                         │       │  │l │     │l │     │l │    │
    │  ┌───────────────────┐  │       │  │a │     │a │     │a │    │
    │  │  Vue 3 Frontend   │  │       │  │m │     │m │     │m │    │
    │  │  (开发服务器/Pod)   │  │       │  │a │     │a │     │a │    │
    │  └───────────────────┘  │       │  └──┘     └──┘     └──┘    │
    │                         │       │                              │
    │  ┌───────────────────┐  │       │  所有 Pi 角色完全相同         │
    │  │  Prometheus       │  │       │  所有 Pi 跑同样的 ollama     │
    │  │  Grafana + Loki   │  │       │  任意 Pi 可随时加入/退出     │
    │  └───────────────────┘  │       │                              │
    │                         │       │                              │
    └─────────────────────────┘       └──────────────────────────────┘
       控制面 + 管理面                      数据面（纯推理负载）
```

- **K3s Server** 跑在你电脑的 WSL2 里——集群调度、状态存储、API Server
- **K3s Agent** 跑在每个 Pi 上——只负责运行推理容器，几乎不占额外资源
- **管理平台**（Backend + Frontend）也在你电脑上——开发阶段直接跑，生产阶段可容器化部署

### 2.2 为什么控制面放电脑上？

公司在 K8s 集群里，Master 节点也是独立部署在管控服务器上的，Worker 是纯计算节点。你的架构和公司完全对应：

| 公司 | 本项目 |
|------|--------|
| K8s Master（管控服务器） | 你的电脑 WSL2 → K3s Server |
| K8s Worker × N（计算集群） | Pi 5 × N → K3s Agent |
| 管理平台 Pod（跑在集群内） | FastAPI + Vue 3（跑在电脑上） |
| kubectl 入口 | 你的电脑直接 kubectl |

### 2.3 系统分层

```
┌─────────────────────────────────────────────────────────┐
│                    接入层 (你的电脑)                       │
│  浏览器 Dashboard  │  CLI 工具  │  kubectl  │  外部 API   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────┐
│              应用层 (你的电脑: FastAPI + Vue 3)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 节点管理  │  │ 模型管理  │  │ 推理服务  │  │ 系统信息 │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Engine Adapter (策略模式)                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Scheduler (调度策略插件化)                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │       Agent 分布式执行引擎 (Scatter/Gather)         │   │
│  │  Scatter(任务拆分) → Map(并行分发Pi) → Reduce(聚合) │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP → Ollama API
┌────────────────────────┼────────────────────────────────┐
│              运行时层 (Pi 集群)                           │
│                                                         │
│   Pi #1: Ollama ─┐  Pi #2: Ollama ─┐  Pi #3: Ollama    │
│        qwen2.5:7b │       qwen2.5:7b │    qwen2.5:7b    │
│                   ▼                  ▼                   │
│            K3s Service (ClusterIP → 负载均衡)             │
└─────────────────────────────────────────────────────────┘
```

### 2.4 请求流

**普通 Chat 请求:**
```
用户发 Chat 请求
    │
    ▼
Backend (你的电脑)
    ├── 鉴权/校验
    ├── Scheduler 选一个 Pi 节点
    │
    ▼
Ollama @ Pi #N (通过 WiFi)
    │
    ▼
流式返回 SSE token → Backend → 用户
```

**Agent 分布式执行 (Scatter/Gather):**
```
Claude Code 子 Agent 任务 (你的电脑)
    │  所有子 Agent 连同一个 API 地址
    │  http://localhost:8000/api/v1/inference
    │
    ▼
Backend Agent Dispatcher
    ├── Scatter: 大任务拆分为 N 个子任务
    ├── Map: 并发分发到 N 个 Pi
    │   ├── 子任务₁ → Pi #1 Ollama
    │   ├── 子任务₂ → Pi #2 Ollama
    │   ├── 子任务₃ → Pi #3 Ollama
    │   └── 子任务ₙ → Pi #N Ollama
    ├── Gather: 收集所有 Pi 的返回结果
    └── Reduce: 聚合为最终答案 → 返回给 Claude Code
```

**Dashboard 打开时:**
```
Frontend (Vue 3) → Backend API → K3s API / Prometheus
    │
    ▼
实时展示节点状态、推理指标
```

---

## 3. 技术栈

| 层级 | 工业标准 | 本项目 | 迁移价值 |
|------|---------|--------|---------|
| 容器编排 | Kubernetes | **K3s** (Server 在 WSL2, Agent 在 Pi) | API/工具链 100% K8s 兼容 |
| 容器运行时 | containerd | **containerd** (K3s 内置) | 一致 |
| 模型推理 | vLLM / TGI | **Ollama on Pi** (vLLM 后续) | API 层对接 OpenAI 格式 |
| 后端框架 | FastAPI / Go | **FastAPI (Python 3.12+)** | 异步 + 自动 OpenAPI |
| 前端框架 | React / Vue | **Vue 3 + TypeScript + Vite** | 国内主流，生态成熟 |
| CLI 工具 | Go (cobra) / Python | **Python (typer/click)** | 与后端共享代码 |
| 数据库 | PostgreSQL | **SQLite** (WSL2 本地) → PostgreSQL | SQLAlchemy + Alembic |
| 指标监控 | Prometheus | **Prometheus + Grafana** (WSL2) | 工业标配 |
| 日志聚合 | ELK / Loki | **Loki + Promtail** (Pi 上采集, WSL2 聚合) | 与 Grafana 同一面板 |
| 节点初始化 | Ansible / Terraform | **Ansible** (WSL2 → Pi) | Playbook 化管理 |
| CI/CD | GitHub Actions | **GitHub Actions** | 免费即用 |

---

## 4. 仓库结构 (Monorepo)

```
pi-swarm-llm/
├── ansible/                    # Ansible Playbooks — Pi 节点初始化
│   ├── inventory/
│   │   └── hosts.yml           # Pi 节点清单
│   ├── playbooks/
│   │   ├── site.yml            # 主 Playbook
│   │   ├── init-pi.yml         # 单 Pi 系统初始化
│   │   ├── join-cluster.yml    # Pi 加入 K3s 集群
│   │   └── leave-cluster.yml   # Pi 退出 K3s 集群
│   └── roles/
│       └── node-prep/          # 系统初始化 (containerd/cgroups/Docker)
│
├── k3s/                        # K8s 资源清单 → 部署到 Pi Agent
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── ollama-daemonset.yaml      # 每 Pi 一个 Ollama Pod
│   │   ├── ollama-service.yaml        # ClusterIP 负载均衡
│   │   └── promtail-daemonset.yaml    # 日志采集
│   └── overlays/
│       ├── dev/
│       └── prod/
│
├── backend/                    # FastAPI 管理平台 (跑在电脑上)
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── nodes.py
│   │   │   │   ├── models.py
│   │   │   │   ├── inference.py
│   │   │   │   └── system.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── engine.py          # 推理引擎抽象
│   │   │   └── scheduler.py       # 调度策略
│   │   ├── engines/
│   │   │   ├── base.py            # InferenceEngine 抽象类
│   │   │   ├── ollama.py          # Ollama 实现
│   │   │   └── vllm.py            # vLLM 实现 (未来)
│   │   ├── k8s/
│   │   │   └── client.py          # K8s API 客户端封装
│   │   ├── models/                # SQLAlchemy 数据模型
│   │   ├── agent/                    # Agent 分布式执行引擎
│   │   │   ├── __init__.py
│   │   │   ├── scatter.py            # 任务拆分
│   │   │   ├── executor.py           # Map 并行执行
│   │   │   └── reducer.py            # Reduce 结果聚合
│   │   ├── services/              # 业务逻辑层
│   │   └── schemas/               # Pydantic 请求/响应模型
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/                   # Vue 3 Dashboard (跑在电脑上)
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue      # 总览页
│   │   │   ├── Nodes.vue          # 节点管理页
│   │   │   ├── Models.vue         # 模型管理页
│   │   │   ├── Logs.vue           # 日志查看页
│   │   │   └── Settings.vue       # 系统设置页
│   │   ├── components/
│   │   ├── composables/
│   │   ├── api/                   # Axios HTTP 客户端
│   │   ├── router/
│   │   └── stores/                # Pinia 状态管理
│   ├── Dockerfile
│   ├── vite.config.ts
│   └── package.json
│
├── cli/                        # Python CLI 工具
│   ├── pi_cli/
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── nodes.py
│   │   │   ├── models.py
│   │   │   └── inference.py
│   │   └── client.py
│   └── pyproject.toml
│
├── scripts/                    # 运维脚本
│   ├── setup-wsl2.sh           # WSL2 环境初始化
│   ├── init-cluster.sh         # 一键初始化集群
│   └── bench-inference.sh      # 推理性能压测
│
├── docs/
│   ├── superpowers/specs/
│   └── architecture.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docker-compose.dev.yml      # 本地开发环境
└── Makefile                    # 常用命令入口
```

---

## 5. 核心功能模块

### 5.1 节点管理

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 节点注册/发现 | Ansible Playbook 一键初始化新 Pi → 自动加入 K3s 集群 | P0 |
| 健康检查 | CPU / 内存 / 温度 / 磁盘 / 网络延迟采集 (Prometheus) | P0 |
| 节点状态 Dashboard | 实时卡片展示（在线/离线/负载/温度色标） | P0 |
| 节点热加入 | `k3s-pi node add 192.168.1.x` 或 Web UI 一键添加 | P0 |
| 节点热退出 | 安全驱逐 Pod → 从集群移除 → 清理残留数据 | P0 |
| 节点标签/污点 | K8s node labels & taints，用于调度策略 | P1 |
| 温度保护 | 温度超过阈值自动限流/迁移 Pod | P1 |

**API 端点**:
- `GET /api/v1/nodes` — 节点列表
- `GET /api/v1/nodes/{name}` — 节点详情
- `POST /api/v1/nodes/join` — 触发新节点加入
- `DELETE /api/v1/nodes/{name}` — 安全下线节点

### 5.2 模型管理

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 模型仓库 | 列出集群中已部署的模型、版本、副本分布 | P0 |
| 一键部署 | Web UI 选模型 → 自动拉取到各节点 → 注册 Service | P0 |
| 模型版本切换 | 同一模型多量化版本并存，热切换（不中断服务） | P1 |
| 模型预热 | 部署后自动发预热请求，降低首次推理延迟 | P1 |
| 模型流水线部署 | 流水线并行场景，指定每段部署到哪个节点 | P2 (未来) |
| 模型微调/LoRA | 在集群上运行 LoRA 微调，微调后自动注册为新版本 | P3 (未来) |

**API 端点**:
- `GET /api/v1/models` — 模型列表
- `POST /api/v1/models/deploy` — 部署模型
- `PUT /api/v1/models/{name}/switch` — 切换版本
- `DELETE /api/v1/models/{name}` — 卸载模型

### 5.3 推理服务

| 功能 | 描述 | 优先级 |
|------|------|--------|
| OpenAI 兼容 API | `/v1/chat/completions` — 任何用 OpenAI SDK 的工具直接接入 | P0 |
| 负载均衡 | K3s Service 轮询分发 → 后续智能路由（最少连接/资源感知） | P0 |
| 流式输出 (SSE) | Server-Sent Events 逐 token 返回 | P0 |
| 并发管理 | 请求队列、超时控制、失败重试 | P0 |
| 推理指标采集 | 首 token 延迟、总延迟、token/s、并发数 (Prometheus) | P1 |
| 智能调度 | 基于当前负载/队列深度的最优节点选择 | P2 (未来) |
| 流水线并行推理 | 模型按层切分多节点协同，支持超单机内存的大模型 | P3 (未来) |

**API 端点**:
- `POST /api/v1/inference/chat/completions` — Chat Completion
- `POST /api/v1/inference/completions` — Text Completion
- `GET /api/v1/inference/models` — 可用模型列表
- `POST /api/v1/inference/benchmark` — 压测接口

### 5.4 Dashboard (Vue 3)

| 页面 | 内容 | 优先级 |
|------|------|--------|
| 总览页 | 集群拓扑图、节点数/在线率、总吞吐量、活跃告警数 | P0 |
| 节点详情 | 单节点资源曲线（CPU/内存/温度）、推理耗时分布、Pod 列表 | P0 |
| 模型管理 | 模型列表、部署/切换/卸载操作、副本数调整 | P0 |
| 日志查看 | Loki 日志查询，按节点/容器/时间/关键词过滤 | P1 |
| Grafana 嵌入 | iframe 嵌入预置 Grafana 面板，统一入口 | P1 |
| 系统设置 | 告警规则配置、引擎配置、用户偏好 | P1 |

### 5.5 CLI 工具 (`k3s-pi`)

```bash
# 节点管理
k3s-pi node list                    # 列出所有节点
k3s-pi node status <name>           # 节点详情
k3s-pi node add <ip>                # 添加节点
k3s-pi node drain <name>            # 安全下线

# 模型管理
k3s-pi model list                   # 已部署模型
k3s-pi model deploy <name>          # 部署模型
k3s-pi model switch <name> --ver    # 切换版本
k3s-pi model scale <name> -n 5      # 调整副本数

# 推理
k3s-pi infer chat --prompt "你好"   # 测试推理
k3s-pi infer bench --concurrency 10 # 压测

# 集群
k3s-pi cluster init                 # 初始化集群
k3s-pi cluster status               # 集群状态总览
k3s-pi cluster backup               # 备份配置
```

### 5.6 可观测性

| 组件 | 用途 | 优先级 |
|------|------|--------|
| Prometheus | 采集 K3s 集群指标 + 节点指标 + 推理指标 | P0 |
| Grafana | 预置 Dashboard（集群总览 / 节点详情 / 推理性能） | P0 |
| Loki + Promtail | 聚合所有容器日志，Grafana 内直接查询 | P1 |
| Alertmanager | 告警规则（节点宕机/温度>80°C/内存>90%/推理队列积压） | P1 |
| 告警通知 | Webhook → 企业微信/钉钉/邮件 | P2 (未来) |

### 5.7 Agent 分布式执行引擎 (Scatter/Gather)

集群的核心差异化能力——让 Pi 集群像一台超级计算机一样并行执行 LLM 任务。上层应用（如 Claude Code）连接一个 API 地址，Backend 自动将子 Agent 任务并行分发到不同 Pi，结果聚合后返回。

```
外部工具 (Claude Code / 自研应用)
    │  所有子 Agent 连接同一个地址:
    │  http://localhost:8000/api/v1
    │
    ▼
┌─────────────────────────────────────────────┐
│           Agent 分布式执行引擎                │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  Scatter (任务拆分)                     │  │
│  │  - 接收大任务描述                      │  │
│  │  - 用主 LLM 拆分为 N 个独立子任务       │  │
│  │  - 输出: [SubTask₁, SubTask₂, ...]     │  │
│  └───────────────┬───────────────────────┘  │
│                  ▼                          │
│  ┌───────────────────────────────────────┐  │
│  │  Map (并行分发)                        │  │
│  │  - N 个子任务并发调用 Inference API    │  │
│  │  - Scheduler 自动分发到不同 Pi         │  │
│  │  - 每个 Pi 独立推理，互不依赖          │  │
│  └───────────────┬───────────────────────┘  │
│                  ▼                          │
│  ┌───────────────────────────────────────┐  │
│  │  Reduce (结果聚合)                     │  │
│  │  - 收集所有 Pi 的子任务结果            │  │
│  │  - 用主 LLM 合并/去重/总结             │  │
│  │  - 输出: 最终答案                      │  │
│  └───────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

**MapReduce 类比:**

| MapReduce 概念 | 你的架构对应 |
|---------------|------------|
| **Master** | Backend Agent Dispatcher (Scatter + Reduce) |
| **Map** | 子任务并发分发到不同 Pi 的 Ollama |
| **Reduce** | 聚合所有 Pi 结果，用主 LLM 总结 |
| **Worker** | 每个 Pi 上的 Ollama 实例 |
| **Shuffle** | 不需要 — 各子任务独立，无数据依赖 |

**适合/不适合的任务:**

| 适合分布式到 Pi | 不适合 |
|---------------|--------|
| ✅ 并行扫描大量文件（每 Pi 扫一部分） | ❌ 链式推理（需要上一步结果才能下一步） |
| ✅ 同时评价多个设计方案的优劣 | ❌ 需要大模型能力的复杂推理（Pi 7B 能力有限） |
| ✅ 并行 summarize 多份文档 | ❌ 子任务之间有数据依赖 |
| ✅ 独立跑测试并汇总结果 | ❌ 需要跨任务共享中间状态 |
| ✅ 并发分析代码库的不同模块 | ❌ 单个复杂推理任务无法拆分 |

**API 端点:**

- `POST /api/v1/agent/scatter` — 拆分任务，返回子任务列表及预估 Pi 分配
- `POST /api/v1/agent/execute` — Map: 并行执行所有子任务
- `POST /api/v1/agent/run` — 一站式 Scatter → Map → Reduce (推荐)
- `GET /api/v1/agent/jobs/{id}` — 查询分布式任务执行状态

**使用示例:**

```bash
# CLI 一站式执行
k3s-pi agent run \
  --task "分析 backend/ 目录下所有 .py 文件的代码质量问题" \
  --workers 3

# 内部流程:
#  1. Scatter: 将 backend/ 下 30 个 .py 文件拆成 3 份
#  2. Map: Pi#1 分析 10 个、Pi#2 分析 10 个、Pi#3 分析 10 个
#  3. Reduce: 汇总 3 份分析结果，去重排序，输出最终质量报告

# Claude Code 集成方式
export OPENAI_BASE_URL=http://localhost:8000/api/v1/inference
# Claude Code 子 Agent 的推理请求自动被调度器分发到不同 Pi
```

| 子功能 | 描述 | 优先级 |
|--------|------|--------|
| Scatter (任务拆分) | 输入大任务描述 → 主 LLM 拆分为独立子任务列表 | P2 |
| Map (并行分发) | 子任务并发分发到不同 Pi，基于 Scheduler 策略 | P2 |
| Reduce (结果聚合) | 收集所有子任务结果 → 去重/合并/总结 | P2 |
| 任务状态追踪 | 查询分布式任务进度、每个子任务状态 | P2 |
| 失败重试 | 单个子任务失败自动重试其他 Pi | P2 |
| 自适应拆分 | 根据当前在线 Pi 数量自动调整子任务数量 | P3 |
| 优先级队列 | 紧急任务优先调度 | P3 |

---

## 6. 扩展性设计

### 6.1 推理引擎抽象层

```python
# backend/app/engines/base.py

from abc import ABC, abstractmethod
from typing import AsyncIterator


class InferenceEngine(ABC):
    """所有推理引擎的统一抽象接口"""

    @abstractmethod
    async def load(self, model_id: str, **config) -> bool:
        """加载模型到内存"""
        ...

    @abstractmethod
    async def unload(self, model_id: str) -> bool:
        """卸载模型释放内存"""
        ...

    @abstractmethod
    async def infer(
        self, model_id: str, messages: list[dict], **params
    ) -> dict:
        """同步推理"""
        ...

    @abstractmethod
    async def infer_stream(
        self, model_id: str, messages: list[dict], **params
    ) -> AsyncIterator[str]:
        """流式推理"""
        ...

    @abstractmethod
    async def health(self) -> dict:
        """引擎健康状态"""
        ...
```

- **Ollama** (`engines/ollama.py`) — 第一实现
- **vLLM** (`engines/vllm.py`) — 后续引擎，支持张量/流水线并行
- **llama.cpp** (`engines/llamacpp.py`) — 纯 CPU 场景的备选
- 新增引擎只需实现接口并注册，上层 API/调度器完全不改

### 6.2 调度策略插件化

```python
# backend/app/core/scheduler.py

class SchedulingStrategy(ABC):
    @abstractmethod
    async def select_node(
        self, model_id: str, nodes: list[NodeInfo]
    ) -> NodeInfo:
        """选择一个节点处理当前推理请求"""
        ...


class RoundRobinStrategy(SchedulingStrategy):       # 默认
class LeastConnectionStrategy(SchedulingStrategy):   # 最少活跃连接
class ResourceAwareStrategy(SchedulingStrategy):     # 基于 CPU/内存利用率
class PipelineStageStrategy(SchedulingStrategy):     # 流水线并行调度 (未来)
class ModelAffinityStrategy(SchedulingStrategy):     # 模型段亲和性 (未来)
class CustomStrategy(SchedulingStrategy):            # 用户自定义插件
```

调度策略通过配置文件切换，不重启服务：
```yaml
# k3s/base/backend-configmap.yaml
scheduler:
  strategy: least_connection  # round_robin | least_connection | resource_aware
```

### 6.3 API 版本化

```
/api/v1/nodes          ← 当前版本
/api/v2/nodes          ← 大版本升级时新增，v1 保留至少 6 个月
/api/v1/inference/chat ← OpenAI 兼容路径
/api/latest/...        ← 自动重定向到最新稳定版
```

- 所有端点带版本号
- 废弃 API 先标记 deprecated header，后移除
- Dashboard 和 CLI 通过 `api/v1/info` 检测支持的最高版本

### 6.4 数据库迁移路径

```
现在: SQLite (单文件，零运维)
  │  使用 SQLAlchemy + Alembic
  │  所有查询走 ORM，不写原生 SQL
  │
  ▼
未来: PostgreSQL (高并发、主备)
  │  改连接字符串 + 改 Driver
  │  无需改一行业务代码
  │
  ▼
更远: TimescaleDB (推理性能数据时序分片) + Redis (热点缓存)
```

### 6.5 节点间通信演进

```
REST API (HTTP/1.1)
  │  现在：管理 API 调用，推理请求分发
  │
  ▼
gRPC (HTTP/2, Protobuf)
  │  未来：引擎间低延迟通信
  │  流水线并行需要频繁传输中间层输出
  │  Protobuf 序列化比 JSON 快 5-10 倍
  │
  ▼
自定义协议 / RDMA
  │  更远：如果上 NVLink 级别的互联
```

---

## 7. 未来功能路线图

### Phase 2: 高级推理 & Agent 分布式执行（v1.1）

- **Agent 分布式执行引擎 (Scatter/Gather)** — 大任务自动拆分到多 Pi 并行执行、结果聚合，Pi 集群作为超级计算机
- **Claude Code 集成** — 子 Agent 推理请求自动分发到不同 Pi，OpenAI 兼容 API 直连
- **流水线并行推理** — 模型按层切分到多个 Pi，支持超过 8GB 单机内存的大模型
- **vLLM 引擎集成** — 替换 Ollama 为 vLLM，支持 PagedAttention、连续批处理
- **智能调度** — 资源感知路由 + 最少连接 + 队列深度混合策略
- **模型预热** — 部署后自动跑预热推理，消除冷启动

### Phase 3: 模型运维（v1.2）

- **模型微调 / LoRA** — 在集群上跑轻量微调，QLoRA 适配 Pi 内存限制
- **模型版本管理** — 多版本并存、A/B 测试、灰度发布
- **模型仓库集成** — 对接 HuggingFace / ModelScope，UI 内浏览/搜索/一键导入
- **自动量化** — 上传模型 → 自动 GGUF/GPTQ 量化 → 注册部署

### Phase 4: 平台化（v1.3）

- **用户体系 + 认证** — JWT/OAuth2 + RBAC 权限控制
- **API 配额管理** — 按用户/团队设置速率限制和用量统计
- **多集群联邦** — 管理中心管理多组 Pi 集群，跨集群调度
- **GPU/NPU 加速卡支持** — 接入 Hailo-8 / Google Coral TPU
- **告警通知** — Webhook → 企业微信/钉钉/邮件/Telegram
- **审计日志** — 所有管理操作记录、可回溯

### Phase 5: 性能极致（v2.0）

- **张量并行** — 如果升级千兆/万兆网络，探索单层内矩阵切分
- **投机解码** — 小模型快速出 draft token，大模型验证
- **KV Cache 共享** — 多请求间复用 prefix 的 KV Cache
- **模型压缩** — AWQ/GPTQ/SpQR 量化流水线
- **自适应批处理** — 动态调整 batch size 最大化吞吐

---

## 8. 网络拓扑

### 8.1 当前（WiFi）

```
                Internet
                   │
              ┌────┴────┐
              │  路由器   │ (DHCP: 192.168.1.0/24)
              └────┬────┘
                   │ WiFi
     ┌─────────────┼─────────────────┐
     ▼             ▼                 ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 你的电脑   │ │ Pi #1    │ │ Pi #2 .. │
│ Windows  │ │ Agent    │ │ Agent    │
│ ┌──────┐ │ │ Ollama   │ │ Ollama   │
│ │ WSL2 │ │ │          │ │          │
│ │K3s   │ │ └──────────┘ └──────────┘
│ │Server│ │
│ └──────┘ │  Pi 节点通过 WiFi 与 K3s Server 通信
└──────────┘
```

- 所有设备同一 WiFi 子网
- Pi 设固定 IP（路由器 DHCP 保留）
- **关键**：K3s Server (WSL2) 的 API 端口 6443 必须能从 Pi 访问
- WSL2 默认是 NAT 网络——需要配置端口转发或桥接模式

### 8.2 WSL2 网络注意事项

WSL2 默认跑在 NAT 后面，Pi 无法直接访问 WSL2 的 IP。解决方案：

| 方案 | 复杂度 | 推荐 |
|------|--------|------|
| **Windows 端口转发** — `netsh interface portproxy` 把宿主机 6443 转发到 WSL2 | 低 | ✅ 推荐 |
| **WSL2 桥接模式** — 让 WSL2 获得局域网独立 IP | 中 | 可选，更干净 |
| **mirrored 网络模式** — WSL2 新版支持，直接共享宿主机网络 | 低 | ✅ 最简 |

### 8.3 未来（千兆交换机）

```
路由器 ── 千兆交换机 ─┐
               │       │
       ┌───────┼───────┼───────┬───────┐
       ▼       ▼       ▼       ▼       ▼
     你的电脑  Pi #1   Pi #2   Pi #3   Pi #N ...
     管理节点  交换机有线直连，延迟 < 1ms，带宽 1Gbps
```

- 推荐型号：TP-Link TL-SG108 / Netgear GS308（无风扇、省电）
- 流水线并行场景下，中间层输出通过有线传输，延迟可接受

---

## 9. 部署流程

### 9.1 首次搭建（你的电脑）

```bash
# 1. WSL2 安装 Ubuntu 22.04/24.04
wsl --install -d Ubuntu-24.04

# 2. 进入 WSL2，安装 K3s Server
curl -sfL https://get.k3s.io | sh -
# K3s Server 启动在 WSL2 内

# 3. 获取 join token（Pi 加入集群用）
sudo cat /var/lib/rancher/k3s/server/node-token

# 4. 配置 Windows → WSL2 端口转发（让 Pi 能连上 K3s API）
#    在 Windows PowerShell (管理员):
netsh interface portproxy add v4tov4 `
  listenport=6443 listenaddress=0.0.0.0 `
  connectport=6443 connectaddress=<WSL2_IP>

# 5. 安装管理平台依赖
cd backend && pip install -e ".[dev]"
cd frontend && npm install
```

### 9.2 烧录 Pi 并加入集群

```bash
# 1. 用 Raspberry Pi Imager 烧录 Pi OS Lite (64-bit)
#    预设: SSH 开启、用户名/密码、WiFi 配置

# 2. Pi 开机，确认可达
ping 192.168.1.x

# 3. Ansible 一键初始化并加入集群
ansible-playbook ansible/playbooks/join-cluster.yml \
  -e "pi_ip=192.168.1.x" \
  -e "k3s_token=<node-token>" \
  -e "k3s_server_url=https://<你的电脑IP>:6443"

# 内部自动执行:
#  1. 系统更新 + 安装依赖
#  2. 安装 K3s Agent 并注册到 Server
#  3. 等待节点 Ready
#  4. 给节点打标签 pi-role=inference
```

### 9.3 部署推理服务

```bash
# 部署 Ollama DaemonSet → 所有 Pi 节点各跑一个 Ollama
kubectl apply -f k3s/base/ollama-daemonset.yaml

# 拉取模型
k3s-pi model deploy qwen2.5:7b
# 内部: 通过 K3s API 在每个 Pi 的 Ollama 容器里执行 ollama pull

# 验证
k3s-pi infer chat --prompt "你好，介绍一下你自己"
```

### 9.4 日常开发

```bash
# 启动后端 (你的电脑)
cd backend && uvicorn app.main:app --reload --port 8000

# 启动前端 (你的电脑)
cd frontend && npm run dev

# 浏览器打开 http://localhost:5173
# CLI 调用后端 API: http://localhost:8000/api/v1
```

---

## 10. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| **WSL2 NAT 网络** | Pi 无法直接访问 WSL2 内 K3s API | 配置 Windows 端口转发 / WSL2 mirrored 网络模式 / 桥接模式 |
| **电脑关机 → 控制面停** | Pi 上的推理不受影响（Ollama 继续运行），但管理面不可用 | 可接受——推理服务独立于控制面。重启电脑后 K3s 自动恢复 |
| **WiFi 网络不稳定** | 推理延迟抖动、心跳丢失 | 健康检查阈值调高，后续升级有线 |
| **Pi 温度过高** | 降频、推理速度断崖下降 | Prometheus 温度监控 + 自动限流 + 物理散热 |
| **SD 卡写入寿命** | 日志/模型文件写坏 SD 卡 | 模型放 USB SSD；日志采集到中央 Loki |
| **Ollama ARM 兼容性** | 部分 GGUF 模型 ARM 不兼容 | 维护验证过的模型兼容性矩阵 |

---

## 12. 成功标准

| 标准 | 目标值 |
|------|--------|
| 单节点推理速度 | ≥ 3 token/s (Qwen2.5-7B Q4) |
| 集群初始化时间 | ≤ 30 分钟（3 节点） |
| 添加新节点时间 | ≤ 10 分钟 |
| Dashboard 首屏加载 | ≤ 2 秒 |
| 节点故障检测延迟 | ≤ 15 秒 |
| 模型部署到就绪 | ≤ 5 分钟 (7B Q4) |

---

## 附录 A: 已验证 ARM64 模型列表

| 模型 | 参数量 | 量化 | 内存占用 | 单 Pi 预期速度 |
|------|--------|------|---------|---------------|
| Qwen2.5 | 7B | Q4_K_M | ~5 GB | 3-5 tok/s |
| Qwen2.5 | 1.5B | Q4_K_M | ~1.2 GB | 15-20 tok/s |
| Llama 3.2 | 3B | Q4_K_M | ~2 GB | 8-12 tok/s |
| Gemma 3 | 4B | Q4_K_M | ~2.8 GB | 6-10 tok/s |
| Phi-4-mini | 3.8B | Q4_K_M | ~2.5 GB | 7-11 tok/s |

---

## 附录 B: 端口规划

### 你的电脑 (管理节点)

| 服务 | 端口 | 说明 |
|------|------|------|
| K3s API Server | 6443 | **需端口转发**，供 Pi Agent 连接 |
| Backend API | 8000 | FastAPI 开发服务器 |
| Frontend Dev | 5173 | Vite 开发服务器 |
| Prometheus | 9090 | 指标采集 |
| Grafana | 30300 | 可视化面板 |
| Loki | 3100 | 日志查询入口 |

### Pi 节点 (推理节点)

| 服务 | 端口 | 说明 |
|------|------|------|
| Ollama API | 11434 | 推理请求 (仅内网) |
| K3s Agent | 10250 | Kubelet API |
| Node Exporter | 9100 | Prometheus 指标采集 |
| Promtail | 9080 | 日志采集 (推送到 Loki) |
