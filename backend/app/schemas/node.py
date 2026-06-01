from pydantic import BaseModel, Field


class NodeSummary(BaseModel):
    name: str
    host: str = ""
    status: str = "pending"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: float = 0.0
    labels: dict = Field(default_factory=dict)
    kubelet_version: str = ""
    is_active: bool = True

    model_config = {"from_attributes": True}


class NodeDetail(NodeSummary):
    cpu_capacity: str = ""
    memory_capacity: str = ""
    pods: list[dict] = Field(default_factory=list)
    joined_at: str = ""
    last_heartbeat: str = ""


class NodeJoinRequest(BaseModel):
    host: str
    name: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class NodeJoinResponse(BaseModel):
    success: bool
    message: str
    join_command: str = ""
