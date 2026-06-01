#!/bin/bash
set -euo pipefail

echo "=== pi-swarm — WSL2 K3s Server Setup ==="

echo "[1/5] Updating system..."
sudo apt update && sudo apt upgrade -y

echo "[2/5] Installing K3s Server..."
if systemctl is-active --quiet k3s; then
    echo "  K3s already running, skipping install"
else
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server \
        --write-kubeconfig-mode 644 \
        --node-label pi-role=management \
        --disable-agent" sh -
fi

echo "[3/5] Waiting for K3s..."
for i in $(seq 1 30); do
    if kubectl get nodes &>/dev/null; then
        echo "  K3s ready"
        break
    fi
    sleep 2
done

echo "[4/5] Configuring kubeconfig..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

echo "[5/5] Done!"
echo ""
echo "=== K3s Server Ready ==="
echo "Join token (for Pi nodes):"
sudo cat /var/lib/rancher/k3s/server/node-token
echo ""
echo "kubectl get nodes:"
kubectl get nodes
echo ""
echo "Next: configure port forwarding on Windows (PowerShell as Admin):"
echo '  netsh interface portproxy add v4tov4 \'
echo '    listenport=6443 listenaddress=0.0.0.0 \'
echo '    connectport=6443 connectaddress=$(wsl hostname -I | cut -d" " -f1)'
