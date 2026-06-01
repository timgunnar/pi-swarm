from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    nodes: list[str] = []
    status: str = "unknown"

    model_config = {"from_attributes": True}


class ModelSwitchRequest(BaseModel):
    name: str
    version: str


class ModelScaleRequest(BaseModel):
    name: str
    replicas: int
