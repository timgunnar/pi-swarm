from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, ge=1)
    stream: bool = False


class ChatResponse(BaseModel):
    model: str
    message: ChatMessage
    total_duration: int = 0
    eval_count: int = 0


class ModelDeployRequest(BaseModel):
    name: str
    replicas: int = Field(default=0, description="0 = all nodes")
    node_names: list[str] = Field(default_factory=list)


class ModelDeployResponse(BaseModel):
    success: bool
    model: str
    nodes: list[str]
    message: str
