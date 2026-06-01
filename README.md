# pi-swarm

[English](./README.md) | [中文](./README_CN.md)

**A Raspberry Pi cluster management system.** pi-swarm turns your Raspberry Pi cluster into a unified computing platform — manage nodes, deploy LLMs, and distribute workloads across your entire Pi fleet from a single dashboard.

---

### The Problem

Running LLMs on a single Raspberry Pi is slow and limited by memory. Managing multiple Pis manually — installing models, monitoring health, distributing workloads — is tedious and doesn't scale.

### The Solution

pi-swarm gives you a control plane on your PC and agents on every Pi. Add a new Pi and it auto-joins the cluster. Deploy a model once and it lands on every node. Send inference requests and they're load-balanced across the fleet. pi-swarm makes your Pi cluster behave like a single machine.

---

## Quick Start

```bash
npm install -g pi-swarm

# Initialize control plane (WSL2 on Windows)
bash scripts/setup-wsl2.sh

# Add a Pi node
k3s-pi node add 192.168.1.x

# Deploy a model
k3s-pi model deploy qwen2.5:7b

# Run inference
k3s-pi infer chat --prompt "Hello, who are you?"
```

## Architecture

```
PC (Windows + WSL2)  ← Control Plane    │  Pi 5 × N  ← Data Plane
├─ K3s Server        ← Scheduler        │  ├─ K3s Agent
├─ FastAPI Backend   ← Management API   │  └─ Ollama
├─ Vue 3 Frontend    ← Dashboard        │  Homogeneous nodes
└─ CLI (k3s-pi)      ← Terminal         │  Hot-join / leave
```

## Installation

```bash
npm install -g pi-swarm          # Recommended
git clone git@github.com:timgunnar/pi-swarm.git  # From source
```

## CLI

```bash
k3s-pi node list                  # List all nodes
k3s-pi node add <ip>              # Add a node
k3s-pi node drain <name>          # Drain a node
k3s-pi model list                 # List deployed models
k3s-pi model deploy <name>        # Deploy a model
k3s-pi infer chat --prompt "..."  # Run inference
k3s-pi status                     # Cluster overview
```

## Tech Stack

K3s · FastAPI (Python) · Vue 3 + TypeScript · Ollama · Ansible · Prometheus + Grafana + Loki

## License

MIT
