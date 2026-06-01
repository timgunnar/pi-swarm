# pi-swarm

[English](./README.md) | [中文](./README_CN.md)

**树莓派集群管理系统。** pi-swarm 将你的树莓派集群变成统一的算力平台——从一个 Dashboard 管理节点、部署大模型、将工作负载分布到整个 Pi 集群。

---

### 你遇到的问题

单台树莓派跑大模型速度慢、内存受限。手动管理多台 Pi——装模型、看健康状态、分配任务——既繁琐又无法规模化。

### pi-swarm 怎么解决

pi-swarm 在你的电脑上部署控制面，在每个 Pi 上部署 Agent。新 Pi 加入自动注册。模型部署一次，自动分发到所有节点。推理请求自动负载均衡到集群。pi-swarm 让你的 Pi 集群像一台机器一样工作。

---

## 快速开始

```bash
npm install -g pi-swarm

# 初始化控制面（WSL2）
bash scripts/setup-wsl2.sh

# 添加 Pi 节点
k3s-pi node add 192.168.1.x

# 部署模型
k3s-pi model deploy qwen2.5:7b

# 测试推理
k3s-pi infer chat --prompt "你好，介绍一下你自己"
```

## 架构

```
PC (Windows + WSL2)  ← 控制面           │  Pi 5 × N  ← 数据面
├─ K3s Server        ← 集群调度          │  ├─ K3s Agent
├─ FastAPI Backend   ← 管理 API         │  └─ Ollama
├─ Vue 3 Frontend    ← Dashboard        │  节点同构
└─ CLI (k3s-pi)      ← 命令行工具        │  热加入/退出
```

## 安装

```bash
npm install -g pi-swarm          # 推荐
git clone git@github.com:timgunnar/pi-swarm.git  # 源码安装
```

## CLI

```bash
k3s-pi node list                  # 列出所有节点
k3s-pi node add <ip>              # 添加节点
k3s-pi node drain <name>          # 下线节点
k3s-pi model list                 # 列出已部署模型
k3s-pi model deploy <name>        # 部署模型
k3s-pi infer chat --prompt "..."  # 推理
k3s-pi status                     # 集群总览
```

## 技术栈

K3s · FastAPI (Python) · Vue 3 + TypeScript · Ollama · Ansible · Prometheus + Grafana + Loki

## License

MIT
