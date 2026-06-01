from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PI_SWARM_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "pi-swarm"
    debug: bool = False
    database_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent.parent / 'data' / 'pi_swarm.db'}"
    k3s_kubeconfig: str = str(Path.home() / ".kube" / "config")
    ollama_default_port: int = 11434
    inference_timeout: int = 300
    inference_max_concurrency: int = 10


settings = Settings()
