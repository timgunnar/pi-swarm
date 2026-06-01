# Changelog

[English](./CHANGELOG.md) | [中文](./CHANGELOG_CN.md)

## v0.0.2

### 关键升级

- **推理引擎抽象层** — `InferenceEngine` 基类 + Ollama 实现，后续可插拔 vLLM/llama.cpp
- **调度策略** — 轮询/最少连接/随机，策略模式插件化切换
- **推理 API** — OpenAI 兼容 `/v1/inference/chat/completions`、SSE 流式输出、模型部署端点
- **模型管理 API** — 聚合所有 Pi 节点的模型列表、一键部署
- **Dashboard（5 个页面）** — 总览、节点管理、节点详情、模型管理、日志/设置占位
- **NodeCard 组件** — 实时 CPU/内存/温度进度条、状态指示灯、标签展示
- **CLI 工具 (k3s-pi)** — `node list/add/drain`、`model list/deploy`、`infer chat`、`status` 命令，rich 终端美化输出
- **可观测性栈** — Prometheus + Grafana + Loki + Promtail K3s 资源清单
- **压测脚本** — `scripts/bench-inference.sh` 推理延迟测试
- **CI 修复** — import 排序检查通过、开发依赖迁移到 dependency-groups

### 测试

- 后端 health 端点测试（1 个测试，通过）
- `ruff check` — 全部检查通过
- `vue-tsc --noEmit` — 类型检查通过

## v0.0.1

### 关键升级

- **项目脚手架** — Monorepo 工作区（pyproject.toml、Makefile、.gitignore）
- **后端骨架** — FastAPI 应用入口、health 端点、配置管理、SQLAlchemy + Alembic 数据库层（Node、ModelInfo 模型）
- **前端骨架** — Vue 3 + TypeScript + Vite、路由系统、Pinia 状态管理、Layout 布局组件、Dashboard 占位页
- **节点管理 API** — 节点列表/加入/下线的 GET/POST/DELETE 端点
- **K8s 客户端封装** — Kubernetes Python SDK 对接 K3s Server
- **K3s 资源清单** — Namespace、Ollama DaemonSet 和 Service
- **Ansible Playbooks** — 节点初始化（node-prep role）、加入/退出集群自动化
- **WSL2 安装脚本** — 一键安装 K3s Server
- **CI 流水线** — GitHub Actions 后端 lint/测试 + 前端类型检查/构建

### 测试

- 后端 health 端点测试（1 个测试，通过）
