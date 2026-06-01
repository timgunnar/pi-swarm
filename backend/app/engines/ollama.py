import json
from typing import AsyncIterator

import httpx

from app.engines.base import InferenceEngine


class OllamaEngine(InferenceEngine):
    engine_name = "ollama"

    def __init__(self, port: int = 11434, timeout: float = 300.0):
        self.port = port
        self.timeout = timeout

    def _base_url(self, node_host: str) -> str:
        return f"http://{node_host}:{self.port}"

    async def health(self, node_host: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self._base_url(node_host)}/")
                return r.status_code == 200
        except Exception:
            return False

    async def list_models(self, node_host: str) -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self._base_url(node_host)}/api/tags")
            r.raise_for_status()
            return [
                {"name": m["name"], "size": m.get("size", ""), "modified": m.get("modified_at", "")}
                for m in r.json().get("models", [])
            ]

    async def pull_model(self, node_host: str, model_name: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self._base_url(node_host)}/api/pull",
                json={"name": model_name, "stream": False},
            )
            r.raise_for_status()
            return r.json()

    async def infer(self, node_host: str, model_name: str, messages: list[dict], **params) -> dict:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {k: v for k, v in params.items() if k in ("temperature", "top_p", "num_predict")},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self._base_url(node_host)}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            return {
                "model": data.get("model", model_name),
                "message": data.get("message", {}),
                "done": True,
                "total_duration": data.get("total_duration", 0),
                "eval_count": data.get("eval_count", 0),
            }

    async def infer_stream(self, node_host: str, model_name: str, messages: list[dict], **params) -> AsyncIterator[str]:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "options": {k: v for k, v in params.items() if k in ("temperature", "top_p", "num_predict")},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self._base_url(node_host)}/api/chat", json=payload) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk:
                                yield chunk["message"].get("content", "")
                        except json.JSONDecodeError:
                            continue
