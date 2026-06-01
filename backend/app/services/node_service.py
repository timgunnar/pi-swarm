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
            namespace="pi-swarm", label_selector="app=ollama"
        )
        node_pods = [p for p in pods if p["node"] == name]
        return NodeDetail(
            **k8s_node,
            pods=node_pods,
            cpu_capacity=k8s_node.get("cpu_capacity", ""),
            memory_capacity=k8s_node.get("memory_capacity", ""),
        )

    def get_join_command(self, request: NodeJoinRequest) -> str:
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
