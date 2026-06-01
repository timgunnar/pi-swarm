from kubernetes import client, config
from kubernetes.client.rest import ApiException


class K8sClient:
    def __init__(self, kubeconfig_path: str | None = None):
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_kube_config()
        self.core = client.CoreV1Api()
        self.apps = client.AppsV1Api()

    def list_nodes(self) -> list[dict]:
        try:
            nodes = self.core.list_node()
            result = []
            for n in nodes.items:
                conditions = {c.type: c.status for c in (n.status.conditions or [])}
                result.append({
                    "name": n.metadata.name,
                    "status": "online" if conditions.get("Ready") == "True" else "offline",
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
        nodes = self.list_nodes()
        for n in nodes:
            if n["name"] == name:
                return n
        return None

    def list_pods(self, namespace: str, label_selector: str = "") -> list[dict]:
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
                    "containers": [c.name for c in (p.spec.containers or [])],
                }
                for p in pods.items
            ]
        except ApiException as e:
            raise RuntimeError(f"K8s API error: {e}")

    def get_daemonset(self, name: str, namespace: str) -> dict:
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
