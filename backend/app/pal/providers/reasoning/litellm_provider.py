"""LiteLLM-gateway reasoning provider (W2 / B4).

Implements the frozen PAL ``ReasoningInterface`` contract using the official
``openai`` SDK's ``AsyncOpenAI`` client pointed at the LiteLLM gateway's
OpenAI-compatible chat surface (ADR-0005; decisions.md §3.3). The application
path stays:

    application/worker -> PAL ReasoningInterface -> LiteLLM gateway -> model provider

The provider is responsible ONLY for:

    messages/prompt -> gateway chat completion -> ReasoningResult
    messages/prompt -> gateway streaming chat completion -> ReasoningChunk(s)

It knows nothing about Celery, DB sessions, storage, OCR, embeddings, or the
document pipeline. Model/key/fallback routing belongs to the gateway and the
PAL router (ADR-0005; decisions.md §3.5) — never to this module, and the
application never talks to a model provider (or OmniRoute) directly.

Exception surface (introspected against the installed openai 3.24.0, not
assumed):

* ``APITimeoutError`` subclasses ``APIConnectionError`` — the timeout handler
  MUST win over the connection-error handler (the same ordering lesson as the
  Gemini provider's requests timeout/connection pair).
* ``BadRequestError`` / ``AuthenticationError`` / ``PermissionDeniedError`` /
  ``NotFoundError`` / ``RateLimitError`` / ``UnprocessableEntityError`` /
  ``InternalServerError`` all subclass ``APIStatusError`` (⊂ ``APIError``).

Mapping (mirrors the Gemini provider's conventions and decisions.md §3.3):
``APITimeoutError`` -> ``ProviderTimeoutError``; ``APIConnectionError`` ->
``ProviderUnavailableError``; ``RateLimitError`` -> ``ProviderRateLimitError``;
``InternalServerError`` -> ``ProviderServerError``; ``AuthenticationError`` /
``PermissionDeniedError`` (HTTP 401/403) -> ``ConfigurationError`` (not
fallback-eligible); any other 4xx status error -> ``InvalidInputError``; any
other typed ``APIError`` -> ``ProviderServerError``. Anything else propagates
unwrapped — no broad ``except Exception``.

Retries, fallback routing, and key handling are gateway capabilities
(ADR-0005). The SDK client is therefore constructed with ``max_retries=0``
so no transport-level retry is silently introduced client-side. No API key or
other credential is ever logged or embedded in exception messages.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Any

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    APIStatusError,
    AsyncOpenAI,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    RateLimitError,
)

from app.config import settings
from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.pal.interfaces.reasoning import ReasoningInterface
from app.pal.models.types import (
    ChatMessage,
    HealthStatus,
    ReasoningChunk,
    ReasoningResult,
    TokenUsage,
)


class LiteLLMReasoningProvider(ReasoningInterface):
    """Reasoning provider backed by the LiteLLM gateway via the openai SDK."""

    provider_name = "litellm"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.litellm_api_key
        self._model = model if model is not None else settings.ai_reasoning_model
        self._base_url = (
            base_url if base_url is not None else settings.litellm_api_base
        )
        if not self._api_key:
            raise ConfigurationError(
                "LiteLLM reasoning provider requires an API key "
                "(set LITELLM_API_KEY)."
            )
        if not self._base_url:
            # Never silently fall back to the SDK's default public endpoint:
            # a gateway key sent to a non-gateway host would be a credential
            # leak, not a working configuration.
            raise ConfigurationError(
                "LiteLLM reasoning provider requires a gateway base URL "
                "(set LITELLM_API_BASE)."
            )
        # Local construction only — no network access happens here.
        # max_retries=0: retries belong to the gateway (ADR-0005), so no
        # transport-level retry is silently introduced client-side.
        self._client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
            max_retries=0,
        )

    async def health_check(self) -> HealthStatus:
        """Cheap authenticated gateway probe — ``GET {base_url}/models``.

        Never performs a reasoning request. Failures are reported as an
        unhealthy status (not raised), mirroring how the PAL router renders
        failed health checks.
        """
        try:
            await self._client.models.list()
        except APIError as exc:
            mapped = self._map_gateway_error(exc)
            return HealthStatus(
                healthy=False,
                provider=self.provider_name,
                message=f"LiteLLM reasoning gateway unhealthy: {mapped}",
            )
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message=(
                f"LiteLLM reasoning gateway is reachable (model: {self._model})."
            ),
        )

    async def reason(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ReasoningResult:
        request_model = model or self._model
        chat_messages = self._normalize_messages(messages, system_prompt)
        try:
            response = await self._client.chat.completions.create(
                model=request_model,
                messages=chat_messages,
                **self._request_kwargs(temperature, max_tokens),
            )
        except APIError as exc:
            raise self._map_gateway_error(exc) from exc

        return self._build_result(
            response, system_prompt, temperature, max_tokens
        )

    async def reason_stream(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ReasoningChunk]:
        request_model = model or self._model
        chat_messages = self._normalize_messages(messages, system_prompt)
        try:
            stream = await self._client.chat.completions.create(
                model=request_model,
                messages=chat_messages,
                stream=True,
                **self._request_kwargs(temperature, max_tokens),
            )
            async for event in stream:
                chunk = self._build_chunk(event)
                if chunk is not None:
                    yield chunk
        except APIError as exc:
            raise self._map_gateway_error(exc) from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_messages(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        system_prompt: str | None,
    ) -> list[dict[str, str]]:
        """Build the OpenAI-compatible chat message list.

        Same tolerant conversion the mock provider applies: ``ChatMessage``
        models map field-for-field, plain dicts use their ``role``/``content``
        with the mock's defaults, anything else is stringified as a user turn.
        """
        payload: list[dict[str, str]] = []
        if system_prompt:
            payload.append({"role": "system", "content": system_prompt})
        if isinstance(messages, str):
            payload.append({"role": "user", "content": messages})
            return payload
        for msg in messages:
            if isinstance(msg, ChatMessage):
                payload.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                payload.append(
                    {
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    }
                )
            else:
                payload.append({"role": "user", "content": str(msg)})
        return payload

    @staticmethod
    def _request_kwargs(
        temperature: float | None,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        """Optional sampling parameters — omitted entirely when not set."""
        kwargs: dict[str, Any] = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        return kwargs

    @staticmethod
    def _map_gateway_error(exc: APIError) -> Exception:
        """Map a typed openai SDK error onto the existing PAL hierarchy.

        Returns the PAL exception; callers raise it with ``from exc`` so the
        SDK error stays chained for diagnosis. ``isinstance`` ordering matters:
        ``APITimeoutError`` before ``APIConnectionError`` (subclass), the
        status-error siblings before the generic ``APIStatusError`` catch-all.
        """
        if isinstance(exc, APITimeoutError):
            return ProviderTimeoutError(
                f"LiteLLM reasoning request timed out: {exc}"
            )
        if isinstance(exc, APIConnectionError):
            return ProviderUnavailableError(
                f"LiteLLM reasoning connection failed: {exc}"
            )
        if isinstance(exc, RateLimitError):
            return ProviderRateLimitError(
                f"LiteLLM reasoning rate limited (HTTP {exc.status_code}): {exc}"
            )
        if isinstance(exc, (AuthenticationError, PermissionDeniedError)):
            return ConfigurationError(
                f"LiteLLM reasoning authentication/permission error "
                f"(HTTP {exc.status_code}): {exc}"
            )
        if isinstance(exc, InternalServerError):
            return ProviderServerError(
                f"LiteLLM reasoning server error (HTTP {exc.status_code}): {exc}"
            )
        if isinstance(exc, APIStatusError):
            return InvalidInputError(
                f"LiteLLM gateway rejected the reasoning request "
                f"(HTTP {exc.status_code}): {exc}"
            )
        return ProviderServerError(f"LiteLLM reasoning API error: {exc}")

    def _build_result(
        self,
        response: Any,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> ReasoningResult:
        choices = getattr(response, "choices", None) or []
        if not choices:
            # No candidates: provider-side anomaly. Never silently return a
            # non-answer; safe to retry via PAL fallback.
            raise ProviderServerError("LiteLLM reasoning returned no choices.")
        choice = choices[0]
        text = getattr(getattr(choice, "message", None), "content", None)
        if text is None:
            raise ProviderServerError(
                "LiteLLM reasoning returned no text content."
            )
        return ReasoningResult(
            text=text,
            # The gateway reports the model that actually served the request;
            # fall back to the requested model if the response omits it.
            model=getattr(response, "model", None) or self._model,
            provider=self.provider_name,
            usage=self._build_usage(getattr(response, "usage", None)),
            metadata=self._request_metadata(
                choice, system_prompt, temperature, max_tokens
            ),
        )

    def _build_chunk(self, event: Any) -> ReasoningChunk | None:
        """Map one streaming SDK event.

        ``None`` for events with nothing to report (role-only first chunk,
        keep-alives). Chunks that carry content, a finish reason, or usage are
        mapped as-is: deltas concatenate in order, and usage is attached only
        where the gateway supplied it (per ADR-0009 it may appear only on the
        final chunk — a property of the wire format, not something this
        provider manufactures).
        """
        choices = getattr(event, "choices", None) or []
        usage = getattr(event, "usage", None)
        if not choices:
            # OpenAI-compatible trailing usage-only chunk (empty choices).
            if usage is not None:
                return ReasoningChunk(
                    text="", usage=self._build_usage(usage)
                )
            return None
        choice = choices[0]
        delta = getattr(choice, "delta", None)
        text = getattr(delta, "content", None) if delta is not None else None
        finish_reason = getattr(choice, "finish_reason", None)
        if not text and finish_reason is None and usage is None:
            return None
        return ReasoningChunk(
            text=text or "",
            finish_reason=finish_reason,
            usage=self._build_usage(usage),
        )

    @staticmethod
    def _build_usage(usage: Any) -> TokenUsage | None:
        if usage is None:
            return None
        return TokenUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            total_tokens=getattr(usage, "total_tokens", 0) or 0,
        )

    @staticmethod
    def _request_metadata(
        choice: Any,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        """Small, stable metadata only — the raw SDK response is never dumped
        and no credential is ever included."""
        metadata: dict[str, Any] = {
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        finish_reason = getattr(choice, "finish_reason", None)
        if finish_reason is not None:
            metadata["finish_reason"] = getattr(
                finish_reason, "name", str(finish_reason)
            )
        return metadata
