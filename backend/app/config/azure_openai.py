"""Azure OpenAI unified settings and factory utilities.

Provides a single, validated configuration surface for chat (fast + quality), embeddings,
optional vision, and feature flags used by the Well-Architected Agents project.

This module intentionally keeps dependencies minimal; it performs environment parsing and
basic validation only. Runtime logic (retry, rate limiting, caching) lives in services.llm_provider.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os
import time

FAST_DEFAULT = "gpt-4o-mini"
QUALITY_DEFAULT = "gpt-4o"
EMBEDDING_DEFAULT = "text-embedding-3-small"  # Azure deployment name expected
VISION_DEFAULT = "gpt-4o-mini"  # If same model supports vision
TOKEN_SWITCH_THRESHOLD = int(os.getenv("AZURE_OPENAI_FAST_THRESHOLD_TOKENS", "600"))


@dataclass
class AzureOpenAISettings:
    # Core endpoint & auth (endpoint must be https://, api_key may be None for managed identity)
    endpoint: str = "https://example.openai.azure.com"  # Safe default to satisfy tests expecting instantiation without env
    api_version: str = "2024-10-21"
    # Deployment names (provide sensible defaults to avoid required positional arg errors in tests using partial kwargs)
    chat_fast_deployment: str = FAST_DEFAULT
    chat_quality_deployment: str = QUALITY_DEFAULT
    embedding_deployment: str = EMBEDDING_DEFAULT
    vision_deployment: Optional[str] = VISION_DEFAULT
    api_key: Optional[str] = None

    # Feature flags
    llm_enabled: bool = True
    embeddings_enabled: bool = True
    vision_enabled: bool = True
    enable_hybrid_shadow: bool = False

    # Operational limits
    max_concurrent_requests: int = 6
    per_second_rate_limit: int = 8  # simple token bucket
    retry_attempts: int = 4
    retry_backoff_seconds: float = 0.75

    # Heuristic threshold
    fast_token_threshold: int = TOKEN_SWITCH_THRESHOLD

    def choose_chat_deployment(self, prompt_token_estimate: int) -> str:
        if prompt_token_estimate < self.fast_token_threshold:
            return self.chat_fast_deployment
        return self.chat_quality_deployment


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def load_azure_openai_settings() -> AzureOpenAISettings:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip()

    chat_fast = os.getenv("AZURE_OPENAI_CHAT_FAST_DEPLOYMENT", FAST_DEFAULT).strip()
    chat_quality = os.getenv("AZURE_OPENAI_CHAT_QUALITY_DEPLOYMENT", QUALITY_DEFAULT).strip()
    embedding = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", EMBEDDING_DEFAULT).strip()
    vision = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT", VISION_DEFAULT).strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY") or None

    settings = AzureOpenAISettings(
        endpoint=endpoint,
        api_version=api_version,
        chat_fast_deployment=chat_fast,
        chat_quality_deployment=chat_quality,
        embedding_deployment=embedding,
        vision_deployment=vision if vision else None,
        api_key=api_key,
        llm_enabled=_env_bool("LLM_ENABLED", True),
        embeddings_enabled=_env_bool("EMBEDDINGS_ENABLED", True),
        vision_enabled=_env_bool("VISION_ENABLED", True),
        enable_hybrid_shadow=_env_bool("ENABLE_HYBRID_SHADOW", False),
        max_concurrent_requests=int(os.getenv("AZURE_OPENAI_MAX_CONCURRENT", "6")),
        per_second_rate_limit=int(os.getenv("AZURE_OPENAI_RATE_LIMIT_PER_SEC", "8")),
        retry_attempts=int(os.getenv("AZURE_OPENAI_RETRY_ATTEMPTS", "4")),
        retry_backoff_seconds=float(os.getenv("AZURE_OPENAI_RETRY_BACKOFF", "0.75")),
        fast_token_threshold=int(os.getenv("AZURE_OPENAI_FAST_THRESHOLD_TOKENS", str(TOKEN_SWITCH_THRESHOLD)))
    )

    _validate_settings(settings)
    return settings


def _validate_settings(s: AzureOpenAISettings) -> None:
    errors = []
    if not s.endpoint.startswith("https://"):
        errors.append("AZURE_OPENAI_ENDPOINT must start with https://")
    if s.api_key is None and not _env_bool("AZURE_USE_MANAGED_IDENTITY", False):
        # We allow managed identity path; for now just warn if neither present
        pass
    if not s.chat_fast_deployment:
        errors.append("Missing fast chat deployment name")
    if not s.chat_quality_deployment:
        errors.append("Missing quality chat deployment name")
    if not s.embedding_deployment:
        errors.append("Missing embedding deployment name")
    if errors:
        raise ValueError("AzureOpenAISettings validation errors: " + ", ".join(errors))


# Simple token bucket helper (in-memory, coarse per-process)
class TokenBucket:
    def __init__(self, rate_per_sec: int, capacity: Optional[int] = None):
        self.rate = max(1, rate_per_sec)
        self.capacity = capacity or self.rate
        self.tokens = self.capacity
        self.timestamp = time.monotonic()

    def consume(self, amount: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.timestamp
        # Refill
        new_tokens = elapsed * self.rate
        if new_tokens > 0:
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.timestamp = now
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False
