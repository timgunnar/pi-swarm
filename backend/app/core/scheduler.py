import random
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NodeInfo:
    name: str
    host: str
    is_ready: bool
    active_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


class SchedulingStrategy(ABC):
    @abstractmethod
    async def select_node(self, model_name: str, nodes: list[NodeInfo]) -> NodeInfo | None: ...


class RoundRobinStrategy(SchedulingStrategy):
    def __init__(self):
        self._index = 0

    async def select_node(self, model_name: str, nodes: list[NodeInfo]) -> NodeInfo | None:
        ready = [n for n in nodes if n.is_ready]
        if not ready:
            return None
        node = ready[self._index % len(ready)]
        self._index += 1
        return node


class LeastConnectionStrategy(SchedulingStrategy):
    async def select_node(self, model_name: str, nodes: list[NodeInfo]) -> NodeInfo | None:
        ready = [n for n in nodes if n.is_ready]
        if not ready:
            return None
        return min(ready, key=lambda n: n.active_connections)


class RandomStrategy(SchedulingStrategy):
    async def select_node(self, model_name: str, nodes: list[NodeInfo]) -> NodeInfo | None:
        ready = [n for n in nodes if n.is_ready]
        if not ready:
            return None
        return random.choice(ready)


STRATEGIES: dict[str, SchedulingStrategy] = {
    "round_robin": RoundRobinStrategy(),
    "least_connection": LeastConnectionStrategy(),
    "random": RandomStrategy(),
}


def get_strategy(name: str = "round_robin") -> SchedulingStrategy:
    return STRATEGIES.get(name, RoundRobinStrategy())
