import httpx

DEFAULT_API = "http://localhost:8000/api/v1"


class APIClient:
    def __init__(self, base_url: str = DEFAULT_API):
        self.client = httpx.Client(base_url=base_url, timeout=30.0)

    def list_nodes(self) -> list[dict]:
        r = self.client.get("/nodes")
        r.raise_for_status()
        return r.json()

    def join_node(self, host: str, name: str | None = None) -> dict:
        r = self.client.post("/nodes/join", json={"host": host, "name": name})
        r.raise_for_status()
        return r.json()

    def drain_node(self, name: str) -> dict:
        r = self.client.delete(f"/nodes/{name}")
        r.raise_for_status()
        return r.json()

    def list_models(self) -> list[dict]:
        r = self.client.get("/models")
        r.raise_for_status()
        return r.json()

    def deploy_model(self, name: str, node_names: list[str] | None = None) -> dict:
        r = self.client.post("/inference/models/deploy", json={"name": name, "node_names": node_names})
        r.raise_for_status()
        return r.json()

    def chat(self, model: str, prompt: str, temperature: float = 0.7, stream: bool = False) -> dict:
        r = self.client.post(
            "/inference/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": stream,
            },
            timeout=300.0,
        )
        r.raise_for_status()
        return r.json()
