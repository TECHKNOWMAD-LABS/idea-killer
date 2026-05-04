"""LLM client: tries Ollama localhost:11434 first, falls back to Anthropic."""

from __future__ import annotations

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get("IDEAKILLER_OLLAMA_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = "llama3.2"
ANTHROPIC_DEFAULT_MODEL = "claude-haiku-4-5-20251001"

DEFAULT_TIMEOUT = float(os.environ.get("IDEAKILLER_LLM_TIMEOUT", "120"))
MAX_RETRIES = int(os.environ.get("IDEAKILLER_LLM_RETRIES", "3"))


class LLMClient:
    """Unified LLM client with Ollama-first, Anthropic fallback strategy."""

    def __init__(
        self,
        ollama_model: str = OLLAMA_DEFAULT_MODEL,
        anthropic_model: str = ANTHROPIC_DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        self.ollama_model = ollama_model
        self.anthropic_model = anthropic_model
        self.timeout = timeout
        self.max_retries = max_retries
        self._ollama_available: bool | None = None

    async def _probe_ollama(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def _ollama_complete(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["response"]

    async def _anthropic_complete(self, prompt: str) -> str:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set and Ollama is unavailable. "
                "Set ANTHROPIC_API_KEY or start Ollama at localhost:11434."
            )
        # Import lazily so the package works without anthropic installed for Ollama-only use
        import anthropic  # noqa: PLC0415

        aclient = anthropic.AsyncAnthropic(api_key=api_key)
        message = await aclient.messages.create(
            model=self.anthropic_model,
            max_tokens=1024,
            system=(
                "You are a JSON-only analysis API. Always respond with valid JSON and nothing else."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def _complete_with_retry(self, fn, prompt: str) -> str:
        """Execute a completion function with exponential backoff retry."""
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                return await fn(prompt)
            except Exception as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    delay = 2**attempt
                    logger.warning(
                        "LLM call failed (attempt %d/%d): %s. Retrying in %ds...",
                        attempt + 1,
                        self.max_retries,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)
        raise last_exc  # type: ignore[misc]

    async def complete(self, prompt: str) -> str:
        """Run completion, trying Ollama first then falling back to Anthropic."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if self._ollama_available is None:
            self._ollama_available = await self._probe_ollama()

        if self._ollama_available:
            try:
                return await self._complete_with_retry(self._ollama_complete, prompt)
            except Exception:
                self._ollama_available = False

        return await self._complete_with_retry(self._anthropic_complete, prompt)
