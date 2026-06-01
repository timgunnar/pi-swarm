from abc import ABC, abstractmethod
from typing import AsyncIterator


class InferenceEngine(ABC):
    @property
    @abstractmethod
    def engine_name(self) -> str: ...

    @abstractmethod
    async def health(self, node_host: str) -> bool: ...

    @abstractmethod
    async def list_models(self, node_host: str) -> list[dict]: ...

    @abstractmethod
    async def pull_model(self, node_host: str, model_name: str) -> dict: ...

    @abstractmethod
    async def infer(self, node_host: str, model_name: str, messages: list[dict], **params) -> dict: ...

    @abstractmethod
    async def infer_stream(
        self, node_host: str, model_name: str, messages: list[dict], **params
    ) -> AsyncIterator[str]: ...
