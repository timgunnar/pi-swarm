# Changelog

[English](./CHANGELOG.md) | [中文](./CHANGELOG_CN.md)

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
