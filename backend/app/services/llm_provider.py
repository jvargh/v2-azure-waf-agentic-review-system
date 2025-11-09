"""Unified Azure OpenAI provider abstraction.

Minimal implementation: exposes async chat(), embed(), vision() with:
- Deployment auto selection (fast vs quality)
- Simple retry (linear backoff)
- In-memory embedding cache
- Token bucket rate limiting
- Concurrency semaphore
- Minimal JSON logging

NOTE: Actual Azure client construction deferred; placeholder methods accept an injected low-level client object
(e.g., AsyncAzureOpenAI or Azure AI Foundry wrapper). This keeps this module decoupled for tests.
"""
from __future__ import annotations

import asyncio
import json
import logging
import hashlib
import time
from typing import Any, Dict, List, Optional

try:
    # We attempt to import AsyncAzureOpenAI lazily; if unavailable tests can mock
    from openai import AsyncAzureOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncAzureOpenAI = Any  # type: ignore

from backend.app.config.azure_openai import AzureOpenAISettings, TokenBucket

logger = logging.getLogger(__name__)


class LLMProvider:
    def __init__(self, settings: AzureOpenAISettings, client: Optional[Any] = None) -> None:
        self.settings = settings
        self.client = client  # May be None in test contexts; methods will short-circuit
        self._bucket = TokenBucket(settings.per_second_rate_limit)
        self._sem = asyncio.Semaphore(settings.max_concurrent_requests)
        self._embed_cache: Dict[str, List[float]] = {}

    # -------------------- Public API --------------------
    async def chat(self, messages: List[Dict[str, str]], force_mode: Optional[str] = None) -> Dict[str, Any]:
        if not self.settings.llm_enabled:
            return {"disabled": True, "messages": messages}
        if not self.client:
            return {"error": "no_client"}

        prompt_tokens_estimate = sum(len(m.get("content", "")) // 4 for m in messages)
        deployment = self._select_deployment(prompt_tokens_estimate, force_mode)

        return await self._run_with_retry(
            op="chat",
            fn=lambda: self.client.chat.completions.create(
                model=deployment,
                messages=messages,
                temperature=0.2,
            ),
            meta={"deployment": deployment, "prompt_tokens_estimate": prompt_tokens_estimate, "mode": force_mode or "auto"},
        )

    async def vision(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.settings.vision_enabled:
            return {"disabled": True}
        if not self.client:
            return {"error": "no_client"}
        deployment = self.settings.vision_deployment or self.settings.chat_quality_deployment
        return await self._run_with_retry(
            op="vision", fn=lambda: self.client.chat.completions.create(model=deployment, messages=messages), meta={"deployment": deployment}
        )

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if not self.settings.embeddings_enabled:
            return []
        if not self.client:
            return []
        # Cache lookup
        results: List[List[float]] = []
        to_fetch: List[str] = []
        for t in texts:
            h = self._hash_text(t)
            if h in self._embed_cache:
                results.append(self._embed_cache[h])
            else:
                to_fetch.append(t)
        if to_fetch:
            fetched = await self._run_with_retry(
                op="embed",
                fn=lambda: self.client.embeddings.create(model=self.settings.embedding_deployment, input=to_fetch),
                meta={"count": len(to_fetch)},
            )
            data = fetched.get("data") or getattr(fetched, "data", [])
            for original, item in zip(to_fetch, data):
                vec = item.get("embedding") if isinstance(item, dict) else getattr(item, "embedding", None)
                if vec:
                    self._embed_cache[self._hash_text(original)] = vec
                    results.append(vec)
        return results

    # -------------------- Internal Helpers --------------------
    def _select_deployment(self, prompt_tokens: int, force_mode: Optional[str]) -> str:
        if force_mode == "fast":
            return self.settings.chat_fast_deployment
        if force_mode == "quality":
            return self.settings.chat_quality_deployment
        return self.settings.choose_chat_deployment(prompt_tokens)

    async def _run_with_retry(self, op: str, fn, meta: Dict[str, Any]) -> Any:  # noqa: ANN001
        if not self._consume_token():
            await asyncio.sleep(1 / max(1, self.settings.per_second_rate_limit))
        attempt = 0
        last_err: Optional[Exception] = None

        async with self._sem:
            while attempt < self.settings.retry_attempts:
                start = time.perf_counter()
                try:
                    result = await fn()
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    self._log_event(op, attempt, latency_ms, meta, success=True)
                    # Convert result to dict if SDK object
                    if hasattr(result, "model") and hasattr(result, "choices"):
                        # Chat completion style object - serialize message to dict
                        return {
                            "model": getattr(result, "model", None),
                            "choices": [
                                {
                                    "message": {
                                        "role": getattr(getattr(c, "message", None), "role", None),
                                        "content": getattr(getattr(c, "message", None), "content", None)
                                    }
                                } for c in getattr(result, "choices", [])
                            ],
                            "usage": getattr(result, "usage", None),
                        }
                    return result
                except Exception as e:  # pragma: no cover - broad safeguard
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    last_err = e
                    self._log_event(op, attempt, latency_ms, meta, success=False, error=str(e))
                    attempt += 1
                    await asyncio.sleep(self.settings.retry_backoff_seconds * attempt)
            return {"error": str(last_err) if last_err else "unknown_error", "op": op, "meta": meta}

    def _consume_token(self) -> bool:
        return self._bucket.consume(1)

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _log_event(self, op: str, attempt: int, latency_ms: int, meta: Dict[str, Any], success: bool, error: Optional[str] = None) -> None:
        payload = {
            "event": op,
            "attempt": attempt,
            "latency_ms": latency_ms,
            "success": success,
            "error": error,
            **meta,
        }
        logger.info(json.dumps(payload))
