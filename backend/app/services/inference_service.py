import asyncio
from typing import AsyncIterator

from app.core.scheduler import NodeInfo, SchedulingStrategy, get_strategy
from app.engines.ollama import OllamaEngine
from app.k8s.client import K8sClient


class InferenceService:
    def __init__(self, k8s: K8sClient, engine: OllamaEngine | None = None):
        self.k8s = k8s
        self.engine = engine or OllamaEngine()

    async def _get_inference_nodes(self) -> list[NodeInfo]:
        nodes = self.k8s.list_nodes()
        result = []
        for n in nodes:
            labels = n.get("labels", {})
            if labels.get("pi-role") == "inference":
                result.append(NodeInfo(
                    name=n["name"], host=n["name"],
                    is_ready=n["status"] == "online",
                ))
        return result

    async def chat(self, model: str, messages: list[dict], **params) -> dict:
        nodes = await self._get_inference_nodes()
        strategy: SchedulingStrategy = get_strategy("round_robin")
        target = await strategy.select_node(model, nodes)
        if not target:
            raise RuntimeError("No inference node available")
        return await self.engine.infer(target.host, model, messages, **params)

    async def chat_stream(self, model: str, messages: list[dict], **params) -> AsyncIterator[str]:
        nodes = await self._get_inference_nodes()
        strategy = get_strategy("round_robin")
        target = await strategy.select_node(model, nodes)
        if not target:
            raise RuntimeError("No inference node available")
        async for token in self.engine.infer_stream(target.host, model, messages, **params):
            yield token

    async def deploy_model(self, model_name: str, node_names: list[str] | None = None) -> dict:
        nodes = await self._get_inference_nodes()
        if node_names:
            nodes = [n for n in nodes if n.name in node_names]
        results = await asyncio.gather(
            *[self.engine.pull_model(n.host, model_name) for n in nodes],
            return_exceptions=True,
        )
        succeeded = [n.name for n, r in zip(nodes, results) if not isinstance(r, Exception)]
        return {
            "success": len(succeeded) > 0,
            "model": model_name,
            "nodes": succeeded,
            "message": f"Deployed to {len(succeeded)}/{len(nodes)} nodes",
        }

    async def list_models(self) -> list[dict]:
        nodes = await self._get_inference_nodes()
        all_models: dict[str, dict] = {}
        for n in nodes:
            try:
                models = await self.engine.list_models(n.host)
                for m in models:
                    key = m["name"]
                    if key not in all_models:
                        all_models[key] = {"name": m["name"], "nodes": []}
                    all_models[key]["nodes"].append(n.name)
            except Exception:
                continue
        return list(all_models.values())
