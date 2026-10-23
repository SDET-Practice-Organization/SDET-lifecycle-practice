import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Test run configuration, read from environment variables.

    API_BASE_URL  target service; when unset, the framework starts a local app instance
    API_KEY       key sent in X-API-Key (defaults to the app's dev key)
    API_TIMEOUT   per-request timeout in seconds
    """

    base_url: str | None
    api_key: str
    timeout: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=os.environ.get("API_BASE_URL") or None,
            api_key=os.environ.get("API_KEY", "dev-key"),
            timeout=float(os.environ.get("API_TIMEOUT", "10")),
        )
