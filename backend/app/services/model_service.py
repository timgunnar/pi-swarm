from app.engines.ollama import OllamaEngine
from app.k8s.client import K8sClient


class ModelService:
    def __init__(self, k8s: K8sClient):
        self.k8s = k8s
        self.engine = OllamaEngine()

    async def list_models(self) -> list[dict]:
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
                        all_models[key] = {"name": m["name"], "nodes": [], "status": "ready"}
                    all_models[key]["nodes"].append(n["name"])
            except Exception:
                continue
        return list(all_models.values())
