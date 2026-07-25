"""Static provider catalog and runtime client implementations."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

from . import env, http, schema

GEMINI_FLASH_LITE = "gemini-3.1-flash-lite"
GEMINI_PRO = "gemini-3.1-pro-preview"
OPENAI_DEFAULT = "gpt-5.4-nano"
XAI_DEFAULT = "grok-4-1-fast"

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
XAI_RESPONSES_URL = "https://api.x.ai/v1/responses"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# OpenRouter routes the Gemini Flash Lite tier as the -preview slug; that is the
# stable form on that routing layer even though native Gemini's GEMINI_FLASH_LITE
# constant is suffix-free. If GEMINI_FLASH_LITE moves to a non-preview stable ID,
# double-check that OpenRouter's slug still maps to the same upstream model.
OPENROUTER_DEFAULT = "google/gemini-3.1-flash-lite-preview"


class ReasoningClient:
    """Shared interface for planner and rerank providers."""

    name: str

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        raise NotImplementedError

    def generate_json(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        text = self.generate_text(model, prompt, tools=tools, response_mime_type="application/json")
        return extract_json(text)


class GeminiClient(ReasoningClient):
    name = "gemini"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _generate_content(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0},
        }
        if response_mime_type:
            body["generationConfig"]["responseMimeType"] = response_mime_type
        if tools:
            body["tools"] = tools
        return http.post(
            GEMINI_URL.format(model=model, api_key=self.api_key),
            body,
            headers={"Content-Type": "application/json"},
            timeout=90,
        )

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        payload = self._generate_content(
            model,
            prompt,
            tools=tools,
            response_mime_type=response_mime_type,
        )
        return extract_gemini_text(payload)

class OpenAIClient(ReasoningClient):
    name = "openai"

    def __init__(self, token: str):
        self.token = token

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        del tools, response_mime_type
        payload = {
            "model": model,
            "store": False,
            "input": prompt,
            "temperature": 0,
        }
        response = http.post(
            os.environ.get("OPENAI_BASE_URL", OPENAI_RESPONSES_URL),
            payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=90,
        )
        return extract_openai_text(response)


class XAIClient(ReasoningClient):
    name = "xai"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        del tools, response_mime_type
        payload = {
            "model": model,
            "input": [{"role": "user", "content": prompt}],
        }
        response = http.post(
            os.environ.get("XAI_BASE_URL", XAI_RESPONSES_URL),
            payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=90,
        )
        return extract_openai_text(response)


class OpenRouterClient(ReasoningClient):
    name = "openrouter"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        del tools, response_mime_type
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        response = http.post(
            OPENROUTER_URL,
            payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=90,
        )
        return extract_openai_text(response)


_MODEL_DEFAULTS: dict[str, tuple[str, str]] = {
    "gemini": (GEMINI_FLASH_LITE, GEMINI_FLASH_LITE),
    "openai": (OPENAI_DEFAULT, OPENAI_DEFAULT),
    "xai": (XAI_DEFAULT, XAI_DEFAULT),
    "openrouter": (OPENROUTER_DEFAULT, OPENROUTER_DEFAULT),
}


def _resolve_model_pins(config: dict[str, Any], depth: str, provider_name: str) -> tuple[str, str, str]:
    """Resolve planner, rerank, and grounding model pins for a provider."""
    default_planner, default_rerank = _MODEL_DEFAULTS.get(provider_name, (GEMINI_FLASH_LITE, GEMINI_FLASH_LITE))
    if depth == "deep" and provider_name == "gemini":
        default_rerank = GEMINI_PRO

    planner_model = config.get("LAST30DAYS_PLANNER_MODEL") or default_planner
    rerank_model = config.get("LAST30DAYS_RERANK_MODEL") or default_rerank

    if provider_name == "gemini":
        _require_gemini_31(planner_model, role="planner")
        _require_gemini_31(rerank_model, role="rerank")

    return planner_model, rerank_model


def mock_runtime(config: dict[str, Any], depth: str) -> schema.ProviderRuntime:
    """Resolve model pins for mock mode without requiring live credentials."""
    provider_name = (config.get("LAST30DAYS_REASONING_PROVIDER") or "gemini").lower()
    if provider_name == "auto":
        provider_name = "gemini"
    if provider_name not in _MODEL_DEFAULTS:
        raise RuntimeError(f"Unsupported reasoning provider: {provider_name}")

    planner_model, rerank_model = _resolve_model_pins(config, depth, provider_name)
    return schema.ProviderRuntime(
        reasoning_provider=provider_name,
        planner_model=planner_model,
        rerank_model=rerank_model,

        x_search_backend=_resolve_x_backend(config),
    )


def _build_provider_client(
    provider_name: str,
    config: dict[str, Any],
    depth: str,
    google_key: str | None,
    openai_token: str | None,
    xai_key: str | None,
) -> tuple[schema.ProviderRuntime, ReasoningClient] | None:
    """Attempt to build a runtime+client for one named reasoning provider.

    Returns ``None`` (instead of raising) when the provider is unsupported or
    its required credential is missing, so ``resolve_runtime`` can fall through
    to the next candidate in an ordered failover chain. The client
    constructors only capture the key; no network call happens here.
    """
    if provider_name not in _MODEL_DEFAULTS:
        return None

    planner_model, rerank_model = _resolve_model_pins(config, depth, provider_name)
    x_backend = _resolve_x_backend(config)

    if provider_name == "gemini":
        if not google_key:
            return None
        return (
            schema.ProviderRuntime(
                reasoning_provider="gemini",
                planner_model=planner_model,
                rerank_model=rerank_model,
                x_search_backend=x_backend,
            ),
            GeminiClient(google_key),
        )

    if provider_name == "openai":
        if not openai_token or config.get("OPENAI_AUTH_STATUS") != env.AUTH_STATUS_OK:
            return None
        return (
            schema.ProviderRuntime(
                reasoning_provider="openai",
                planner_model=planner_model,
                rerank_model=rerank_model,
                x_search_backend=x_backend,
            ),
            OpenAIClient(openai_token),
        )

    if provider_name == "xai":
        if not xai_key:
            return None
        return (
            schema.ProviderRuntime(
                reasoning_provider="xai",
                planner_model=planner_model,
                rerank_model=rerank_model,
                x_search_backend=x_backend,
            ),
            XAIClient(xai_key),
        )

    if provider_name == "openrouter":
        openrouter_key = config.get("OPENROUTER_API_KEY")
        if not openrouter_key:
            return None
        return (
            schema.ProviderRuntime(
                reasoning_provider="openrouter",
                planner_model=planner_model,
                rerank_model=rerank_model,
                x_search_backend=x_backend,
            ),
            OpenRouterClient(openrouter_key),
        )

    return None


class FallbackReasoningClient(ReasoningClient):
    """Wrap an ordered list of reasoning clients with call-time failover.

    ``resolve_runtime`` builds one of these when more than one provider is
    configured (e.g. ``LAST30DAYS_REASONING_PROVIDER=openrouter,gemini``). Each
    ``generate_*`` call tries the candidates in order. If a candidate fails with
    a *retryable* HTTP error — most importantly HTTP 402 Payment Required, which
    fires when a key is present but unfunded/credit-exhausted — the next
    candidate is tried instead of raising immediately. Only after every candidate
    fails is the last error re-raised, which the planner/reranker catch and turn
    into their deterministic fallback.

    This makes the primary->fallback chain real at runtime, not just at
    key-presence time: an unfunded OpenRouter key no longer silently degrades
    the whole run to local mode when a funded Gemini key is also configured.
    """

    def __init__(self, pairs: list[tuple[schema.ProviderRuntime, ReasoningClient]]):
        # pairs: ordered (runtime, client). First pair's runtime supplies model
        # pins; model selection is provider-agnostic here (both default to the
        # same Gemini Flash Lite tier).
        self._pairs = pairs

    @property
    def name(self) -> str:
        return ",".join(p[0].reasoning_provider for p in self._pairs)

    @staticmethod
    def _retryable(exc: BaseException) -> bool:
        if isinstance(exc, http.HTTPError):
            code = exc.status_code
            if code is None:
                return False
            # 401/402/403 = auth/billing; 429 = rate; 5xx = upstream outage.
            return code in (401, 402, 403, 429) or 500 <= code <= 599
        # Transient network errors also warrant a retry on the next provider.
        return isinstance(exc, (OSError, ConnectionError, TimeoutError))

    def _run(self, method: str, model: str, prompt: str, **kwargs: Any) -> Any:
        last_exc: BaseException | None = None
        for _runtime, client in self._pairs:
            try:
                return getattr(client, method)(model, prompt, **kwargs)
            except Exception as exc:  # noqa: BLE001 - we re-raise if all fail
                last_exc = exc
                if self._retryable(exc):
                    continue
                raise
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("FallbackReasoningClient had no candidate clients")

    def generate_text(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        response_mime_type: str | None = None,
    ) -> str:
        return self._run(
            "generate_text", model, prompt,
            tools=tools, response_mime_type=response_mime_type,
        )

    def generate_json(
        self,
        model: str,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return self._run("generate_json", model, prompt, tools=tools)


def resolve_runtime(config: dict[str, Any], depth: str) -> tuple[schema.ProviderRuntime, ReasoningClient | None]:
    """Resolve the reasoning provider and pinned models, with failover.

    ``LAST30DAYS_REASONING_PROVIDER`` accepts an ordered, comma-separated list
    of provider names (e.g. ``"openrouter,gemini"``). Every candidate whose
    required credential is present is built; they are wrapped in a
    ``FallbackReasoningClient`` that retries calls across them at runtime. This
    gives a real primary->fallback chain: an unfunded/exhausted primary (HTTP
    402) falls through to the next configured provider instead of degrading the
    whole run to deterministic-local mode.

    ``"auto"`` (the default) resolves to a single provider by credential
    availability, preserving historical behavior.
    """
    raw = (config.get("LAST30DAYS_REASONING_PROVIDER") or "auto").lower()
    google_key = config.get("GOOGLE_API_KEY") or config.get("GEMINI_API_KEY") or config.get("GOOGLE_GENAI_API_KEY")
    openai_token = config.get("OPENAI_API_KEY")
    xai_key = config.get("XAI_API_KEY")

    if raw == "auto":
        if google_key:
            candidates = ["gemini"]
        elif openai_token and config.get("OPENAI_AUTH_STATUS") == env.AUTH_STATUS_OK:
            candidates = ["openai"]
        elif xai_key:
            candidates = ["xai"]
        elif config.get("OPENROUTER_API_KEY"):
            candidates = ["openrouter"]
        else:
            return schema.ProviderRuntime(
                reasoning_provider="local",
                planner_model="deterministic",
                rerank_model="local-score",
                x_search_backend=_resolve_x_backend(config),
            ), None
    else:
        candidates = [p.strip() for p in raw.split(",") if p.strip()]

    pairs: list[tuple[schema.ProviderRuntime, ReasoningClient]] = []
    for provider_name in candidates:
        built = _build_provider_client(
            provider_name, config, depth, google_key, openai_token, xai_key
        )
        if built is not None:
            pairs.append(built)

    if not pairs:
        raise RuntimeError(
            "No usable reasoning provider among: "
            + ", ".join(candidates)
            + ". Check the relevant API keys (GOOGLE/GEMINI, OPENAI, XAI, OPENROUTER)."
        )

    # Single candidate: return it directly (no wrapper overhead).
    if len(pairs) == 1:
        return pairs[0]

    first_runtime = pairs[0][0]
    return first_runtime, FallbackReasoningClient(pairs)


def _resolve_x_backend(config: dict[str, Any]) -> str | None:
    preferred = (config.get("LAST30DAYS_X_BACKEND") or "").lower()
    if preferred in {"xai", "bird"}:
        return preferred
    return env.get_x_source(config)


def _require_gemini_31(model: str, *, role: str) -> None:
    if model.startswith("gemini-3.1-"):
        return
    raise RuntimeError(
        f"{role} must use a Gemini 3.1 model. Got: {model}"
    )


def extract_json(text: str) -> dict[str, Any]:
    """Extract the first JSON object from a model response."""
    text = text.strip()
    if not text:
        raise ValueError("Expected JSON response, got empty text")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise
        return json.loads(match.group(0))


def extract_gemini_text(payload: dict[str, Any]) -> str:
    for candidate in payload.get("candidates", []):
        content = candidate.get("content") or {}
        for part in content.get("parts", []):
            text = part.get("text")
            if text:
                return text
    if payload:
        print(f"[Providers] extract_gemini_text: no text in payload keys: {list(payload.keys())}", file=sys.stderr)
    return ""


def extract_openai_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    output = payload.get("output") or payload.get("choices") or []
    for item in output:
        if isinstance(item, str):
            return item
        if isinstance(item, dict):
            if isinstance(item.get("text"), str):
                return item["text"]
            content = item.get("content") or []
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        return part["text"]
                    if isinstance(part, dict) and part.get("type") == "output_text" and isinstance(part.get("text"), str):
                        return part["text"]
            message = item.get("message") or {}
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
    if payload:
        print(f"[Providers] extract_openai_text: no text in payload keys: {list(payload.keys())}", file=sys.stderr)
    return ""
