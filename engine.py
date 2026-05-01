"""Thin Groq client wrapper — blocking and streaming completions.

Pure Python; no Streamlit dependency. Initialise once with `init_client(api_key)`
then call `call_groq` or iterate `stream_groq`.
"""

from typing import Iterator
from groq import Groq

_MAX_TOKENS = 120
_client: Groq | None = None


def init_client(api_key: str) -> None:
    """Set the module-level Groq client. Call once at app startup."""
    global _client
    _client = Groq(api_key=api_key)


def _ensure_client() -> Groq:
    if _client is None:
        raise RuntimeError("Groq client not initialised. Call init_client(api_key) first.")
    return _client


def call_groq(messages: list[dict], model: str, temperature: float = 1.0,
              max_tokens: int = _MAX_TOKENS) -> str:
    """Blocking completion. Returns the full assistant message."""
    response = _ensure_client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def stream_groq(messages: list[dict], model: str, temperature: float = 1.0,
                max_tokens: int = _MAX_TOKENS) -> Iterator[str]:
    """Streaming completion. Yields content deltas as they arrive."""
    stream = _ensure_client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
