"""B4 tests: LiteLLM reasoning provider against the frozen PAL contract.

No network, no real credentials: the ``openai.AsyncOpenAI`` class used by the
provider is replaced with a deterministic fake (installed on the provider
module's namespace), while the REAL ``openai`` exception classes are used and
constructed the way openai 3.24.0 requires (status errors need an ``httpx2``
``Response``; ``APITimeoutError`` wraps a real ``httpx2`` timeout), so error
mapping is genuinely verified. Streaming events are shaped like the wire
format (delta/finish_reason/usage) without importing SDK internals.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import httpx2
import openai
import pytest

from app.config import settings
from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.pal.factory import get_reasoning_provider
from app.pal.models.types import ChatMessage, ReasoningChunk, ReasoningResult
from app.pal.providers.reasoning import litellm_provider
from app.pal.providers.reasoning.litellm_provider import LiteLLMReasoningProvider
from app.pal.providers.reasoning.mock_provider import MockReasoningProvider

_GATEWAY_KEY = "sk-test-gateway-key"
_GATEWAY_URL = "http://litellm:4000"
_GATEWAY_MODEL = "gemini-2.5-flash"


# ---------------------------------------------------------------------------
# Real openai 3.24.0 exception builders
# ---------------------------------------------------------------------------


def _status_error(cls: type, code: int, message: str) -> openai.APIStatusError:
    """Build a REAL openai status error the way 3.24.0 requires.

    ``APIStatusError`` subclasses dereference an ``httpx2.Response`` for
    ``status_code``; the response must carry its request. Mirrors the payloads
    the SDK itself builds for error responses without a JSON body.
    """
    request = httpx2.Request("POST", f"{_GATEWAY_URL}/chat/completions")
    response = httpx2.Response(
        code,
        headers={"content-type": "application/json"},
        content=b"{}",
        request=request,
    )
    return cls(message, response=response, body=None)


def _connection_error(message: str = "Connection error.") -> openai.APIConnectionError:
    """Build a REAL openai.APIConnectionError (openai 3.24.0 requires the
    keyword-only ``request``; the transport-level detail is carried in the
    message, mirroring what the SDK itself embeds there)."""
    return openai.APIConnectionError(
        message=message,
        request=httpx2.Request("POST", f"{_GATEWAY_URL}/chat/completions"),
    )


# ---------------------------------------------------------------------------
# Fake openai plumbing
# ---------------------------------------------------------------------------


class _FakeAsyncStream:
    """Async iterator over pre-built wire-format events (or one raised error)."""

    def __init__(self, outcome: Any) -> None:
        self._events: list[Any] = (
            [] if isinstance(outcome, BaseException) else list(outcome)
        )
        self._error: BaseException | None = (
            outcome if isinstance(outcome, BaseException) else None
        )
        self._index = 0

    def __aiter__(self) -> "_FakeAsyncStream":
        return self

    async def __anext__(self) -> Any:
        if self._error is not None:
            raise self._error
        if self._index >= len(self._events):
            raise StopAsyncIteration
        event = self._events[self._index]
        self._index += 1
        if isinstance(event, BaseException):
            raise event
        return event


def _install_fake_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    results: list[Any] | None = None,
    streams: list[Any] | None = None,
    models_list: list[Any] | None = None,
) -> dict[str, Any]:
    """Replace ``litellm_provider.AsyncOpenAI`` with a deterministic fake.

    ``results`` is consumed one entry per non-streaming ``create`` call,
    ``streams`` one entry per streaming ``create`` call (an entry is either a
    list of events or an exception), ``models_list`` one entry per
    ``models.list()`` call; the last entry repeats. Entries are returned
    as-is, or raised when they are exception instances. Returns a capture
    dict for assertions.
    """
    results = results if results is not None else []
    streams = streams if streams is not None else []
    models_list = models_list if models_list is not None else []
    captured: dict[str, Any] = {
        "ctor": [],
        "create_kwargs": [],
        "models_list_calls": 0,
    }
    counters = {"create": 0, "models": 0}

    class _FakeCompletions:
        async def create(self, **kwargs: Any) -> Any:
            index = counters["create"]
            counters["create"] += 1
            captured["create_kwargs"].append(kwargs)
            if kwargs.get("stream"):
                outcome = streams[index] if index < len(streams) else streams[-1]
                return _FakeAsyncStream(outcome)
            outcome = results[index] if index < len(results) else results[-1]
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    class _FakeModels:
        async def list(self) -> Any:
            index = counters["models"]
            counters["models"] += 1
            captured["models_list_calls"] += 1
            outcome = (
                models_list[index] if index < len(models_list) else models_list[-1]
            )
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    class _FakeAsyncOpenAI:
        def __init__(self, **kwargs: Any) -> None:
            captured["ctor"].append(kwargs)
            self.chat = SimpleNamespace(completions=_FakeCompletions())
            self.models = _FakeModels()

    monkeypatch.setattr(litellm_provider, "AsyncOpenAI", _FakeAsyncOpenAI)
    return captured


def _configured_provider(
    monkeypatch: pytest.MonkeyPatch,
    **fake_kwargs: Any,
) -> tuple[LiteLLMReasoningProvider, dict[str, Any]]:
    monkeypatch.setattr(settings, "litellm_api_key", _GATEWAY_KEY)
    monkeypatch.setattr(settings, "litellm_api_base", _GATEWAY_URL)
    monkeypatch.setattr(settings, "ai_reasoning_model", _GATEWAY_MODEL)
    captured = _install_fake_client(monkeypatch, **fake_kwargs)
    return LiteLLMReasoningProvider(), captured


# ---------------------------------------------------------------------------
# Wire-format builders (attribute-shaped like the OpenAI chat objects)
# ---------------------------------------------------------------------------


def _usage(prompt: int = 10, completion: int = 20, total: int = 30) -> Any:
    return SimpleNamespace(
        prompt_tokens=prompt, completion_tokens=completion, total_tokens=total
    )


def _chat_response(
    text: str | None = "Hello world",
    model: str = "gemini-2.5-flash",
    finish_reason: str | None = "stop",
    usage: Any = None,
) -> Any:
    message = SimpleNamespace(content=text)
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice], model=model, usage=usage)


def _stream_chunk(
    content: str | None = None,
    finish_reason: str | None = None,
    usage: Any = None,
) -> Any:
    delta = SimpleNamespace(content=content)
    choice = SimpleNamespace(delta=delta, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice], usage=usage)


def _usage_only_chunk(usage: Any) -> Any:
    return SimpleNamespace(choices=[], usage=usage)


async def _collect(iterator: Any) -> list[ReasoningChunk]:
    return [chunk async for chunk in iterator]


# ---------------------------------------------------------------------------
# A. Factory registration
# ---------------------------------------------------------------------------


def test_factory_selects_litellm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "litellm_api_key", _GATEWAY_KEY)
    monkeypatch.setattr(settings, "litellm_api_base", _GATEWAY_URL)
    monkeypatch.setattr(settings, "ai_reasoning_model", _GATEWAY_MODEL)
    captured = _install_fake_client(monkeypatch)

    provider = get_reasoning_provider("litellm")

    assert isinstance(provider, LiteLLMReasoningProvider)
    ctor = captured["ctor"][0]
    assert ctor["api_key"] == _GATEWAY_KEY  # gateway key passed to the client
    assert ctor["base_url"] == _GATEWAY_URL  # gateway URL passed to the client
    assert ctor["max_retries"] == 0  # no client-side retries (gateway owns them)


@pytest.mark.asyncio
async def test_factory_provider_uses_configured_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, results=[_chat_response()]
    )

    result = await provider.reason("hi")

    assert captured["create_kwargs"][0]["model"] == _GATEWAY_MODEL
    assert result.model == "gemini-2.5-flash"


def test_mock_remains_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ai_reasoning_provider", "mock")

    assert isinstance(get_reasoning_provider(), MockReasoningProvider)
    assert isinstance(get_reasoning_provider("mock"), MockReasoningProvider)


# ---------------------------------------------------------------------------
# B. Configuration
# ---------------------------------------------------------------------------


def test_missing_api_key_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "litellm_api_key", "")

    with pytest.raises(ConfigurationError, match="API key"):
        LiteLLMReasoningProvider()


def test_missing_base_url_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "litellm_api_key", _GATEWAY_KEY)
    monkeypatch.setattr(settings, "litellm_api_base", "")

    with pytest.raises(ConfigurationError, match="base URL"):
        LiteLLMReasoningProvider()


# ---------------------------------------------------------------------------
# C. Non-streaming reasoning
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reason_maps_successful_response_to_pal_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = _configured_provider(
        monkeypatch, results=[_chat_response(usage=_usage(7, 11, 18))]
    )

    result = await provider.reason("What is RAG?")

    assert isinstance(result, ReasoningResult)
    assert result.text == "Hello world"
    assert result.model == "gemini-2.5-flash"  # served model reported by the gateway
    assert result.provider == "litellm"
    assert result.usage is not None
    assert result.usage.prompt_tokens == 7
    assert result.usage.completion_tokens == 11
    assert result.usage.total_tokens == 18
    assert result.metadata["finish_reason"] == "stop"
    # Request-context metadata, mirroring the mock provider's convention.
    assert result.metadata["system_prompt"] is None
    assert result.metadata["temperature"] is None
    assert result.metadata["max_tokens"] is None


@pytest.mark.asyncio
async def test_reason_builds_expected_chat_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, results=[_chat_response()]
    )

    await provider.reason("What is RAG?", system_prompt="You are a tutor.")

    kwargs = captured["create_kwargs"][0]
    assert kwargs["messages"] == [
        {"role": "system", "content": "You are a tutor."},
        {"role": "user", "content": "What is RAG?"},
    ]
    # Optional sampling params are omitted entirely when not set.
    assert "temperature" not in kwargs
    assert "max_tokens" not in kwargs
    assert "stream" not in kwargs


@pytest.mark.asyncio
async def test_reason_accepts_chatmessage_and_dict_sequences(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, results=[_chat_response()]
    )
    messages: list[ChatMessage | dict[str, str]] = [
        ChatMessage(role="user", content="First question."),
        {"content": "Second question."},  # tolerant dict: default role
    ]

    await provider.reason(messages)

    assert captured["create_kwargs"][0]["messages"] == [
        {"role": "user", "content": "First question."},
        {"role": "user", "content": "Second question."},
    ]


@pytest.mark.asyncio
async def test_reason_honors_explicit_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, results=[_chat_response(model="served-model-id")]
    )

    result = await provider.reason(
        "hi",
        model="gemini-2.0-flash",
        temperature=0.2,
        max_tokens=64,
    )

    kwargs = captured["create_kwargs"][0]
    assert kwargs["model"] == "gemini-2.0-flash"  # explicit override wins
    assert kwargs["temperature"] == 0.2
    assert kwargs["max_tokens"] == 64
    assert result.model == "served-model-id"  # the gateway's served model


@pytest.mark.asyncio
async def test_reason_without_usage_returns_none_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = _configured_provider(
        monkeypatch, results=[_chat_response(usage=None)]
    )

    result = await provider.reason("hi")

    assert result.usage is None


@pytest.mark.asyncio
async def test_reason_no_choices_raises_provider_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = _configured_provider(
        monkeypatch, results=[SimpleNamespace(choices=[], model="gemini-2.5-flash")]
    )

    with pytest.raises(ProviderServerError, match="no choices"):
        await provider.reason("hi")


@pytest.mark.asyncio
async def test_reason_missing_text_raises_provider_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = _configured_provider(
        monkeypatch, results=[_chat_response(text=None)]
    )

    with pytest.raises(ProviderServerError, match="no text content"):
        await provider.reason("hi")


# ---------------------------------------------------------------------------
# D. Error mapping (real openai 3.24.0 exception classes)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_timeout_maps_to_provider_timeout_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # APITimeoutError subclasses APIConnectionError — the timeout handler
    # must win (verified with the REAL SDK classes).
    sdk_error = openai.APITimeoutError(httpx2.ReadTimeout("timed out"))
    provider, _ = _configured_provider(monkeypatch, results=[sdk_error])

    with pytest.raises(ProviderTimeoutError, match="timed out") as excinfo:
        await provider.reason("hi")

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_connection_error_maps_to_provider_unavailable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _connection_error("refused")
    provider, _ = _configured_provider(monkeypatch, results=[sdk_error])

    with pytest.raises(
        ProviderUnavailableError, match="connection failed"
    ) as excinfo:
        await provider.reason("hi")

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_rate_limit_maps_to_provider_rate_limit_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _status_error(openai.RateLimitError, 429, "Budget exceeded")
    provider, _ = _configured_provider(monkeypatch, results=[sdk_error])

    with pytest.raises(ProviderRateLimitError, match="429") as excinfo:
        await provider.reason("hi")

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error_cls", "code"),
    [(openai.AuthenticationError, 401), (openai.PermissionDeniedError, 403)],
)
async def test_auth_errors_map_to_configuration_error(
    monkeypatch: pytest.MonkeyPatch, error_cls: type, code: int
) -> None:
    sdk_error = _status_error(error_cls, code, "bad key")
    provider, _ = _configured_provider(monkeypatch, results=[sdk_error])

    with pytest.raises(
        ConfigurationError, match="authentication/permission"
    ) as excinfo:
        await provider.reason("hi")

    assert f"HTTP {code}" in str(excinfo.value)
    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_server_error_maps_to_provider_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _status_error(openai.InternalServerError, 500, "boom")
    provider, _ = _configured_provider(monkeypatch, results=[sdk_error])

    with pytest.raises(ProviderServerError, match="500") as excinfo:
        await provider.reason("hi")

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_other_4xx_maps_to_invalid_input_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _status_error(openai.BadRequestError, 400, "bad request shape")
    provider, _ = _configured_provider(monkeypatch, results=[sdk_error])

    with pytest.raises(
        InvalidInputError, match="rejected the reasoning request"
    ) as excinfo:
        await provider.reason("hi")

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_unexpected_exception_propagates_unwrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Guards against a broad "except Exception" fallback in the provider.
    provider, _ = _configured_provider(monkeypatch, results=[TypeError("unexpected")])

    with pytest.raises(TypeError, match="unexpected"):
        await provider.reason("hi")


# ---------------------------------------------------------------------------
# E. Streaming reasoning
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reason_stream_maps_chunks_in_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _configured_provider(
        monkeypatch,
        streams=[
            [
                _stream_chunk(),  # role-only first chunk: nothing to report
                _stream_chunk(content="Hello"),
                _stream_chunk(content=" world"),
                _stream_chunk(finish_reason="stop", usage=_usage(7, 11, 18)),
            ]
        ],
    )

    chunks = await _collect(provider.reason_stream("hi"))

    assert [chunk.text for chunk in chunks] == ["Hello", " world", ""]
    assert "".join(chunk.text for chunk in chunks) == "Hello world"
    assert [chunk.finish_reason for chunk in chunks] == [None, None, "stop"]
    assert all(chunk.usage is None for chunk in chunks[:-1])  # usage final-only
    final = chunks[-1]
    assert final.usage is not None
    assert final.usage.prompt_tokens == 7
    assert final.usage.completion_tokens == 11
    assert final.usage.total_tokens == 18
    assert captured["create_kwargs"][0]["stream"] is True


@pytest.mark.asyncio
async def test_reason_stream_trailing_usage_only_chunk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # OpenAI-compatible include_usage shape: a trailing chunk with empty
    # choices carrying the usage object.
    provider, _ = _configured_provider(
        monkeypatch,
        streams=[
            [
                _stream_chunk(content="Hi"),
                _stream_chunk(finish_reason="stop"),
                _usage_only_chunk(_usage(1, 2, 3)),
            ]
        ],
    )

    chunks = await _collect(provider.reason_stream("hi"))

    assert [chunk.text for chunk in chunks] == ["Hi", "", ""]
    assert [chunk.finish_reason for chunk in chunks] == [None, "stop", None]
    assert chunks[-1].usage is not None
    assert chunks[-1].usage.total_tokens == 3
    assert all(chunk.usage is None for chunk in chunks[:-1])


@pytest.mark.asyncio
async def test_reason_stream_create_error_maps_to_pal_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _status_error(openai.RateLimitError, 429, "rate limited")
    provider, _ = _configured_provider(monkeypatch, streams=[sdk_error])

    with pytest.raises(ProviderRateLimitError, match="429") as excinfo:
        await _collect(provider.reason_stream("hi"))

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_reason_stream_mid_stream_error_maps_to_pal_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _connection_error("connection dropped")
    provider, _ = _configured_provider(
        monkeypatch,
        streams=[[_stream_chunk(content="Hello"), sdk_error]],
    )

    with pytest.raises(
        ProviderUnavailableError, match="connection failed"
    ) as excinfo:
        await _collect(provider.reason_stream("hi"))

    assert excinfo.value.__cause__ is sdk_error


# ---------------------------------------------------------------------------
# F. Health check and credential hygiene
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check_success_reports_reachable_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _configured_provider(monkeypatch, models_list=[[]])

    health = await provider.health_check()

    assert health.healthy is True
    assert health.provider == "litellm"
    assert captured["models_list_calls"] == 1  # cheap authenticated probe


@pytest.mark.asyncio
async def test_health_check_failure_reports_unhealthy_without_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, _ = _configured_provider(
        monkeypatch,
        models_list=[_connection_error("refused")],
    )

    health = await provider.health_check()

    assert health.healthy is False
    assert health.provider == "litellm"


@pytest.mark.asyncio
async def test_no_credentials_in_errors_or_health_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk_error = _status_error(openai.AuthenticationError, 401, "invalid key")
    connection_error = _connection_error("refused")
    provider, _ = _configured_provider(
        monkeypatch, results=[sdk_error], streams=[sdk_error], models_list=[connection_error]
    )

    with pytest.raises(ConfigurationError) as excinfo:
        await provider.reason("hi")
    assert _GATEWAY_KEY not in str(excinfo.value)
    assert _GATEWAY_KEY not in repr(excinfo.value)

    with pytest.raises(ConfigurationError) as stream_excinfo:
        await _collect(provider.reason_stream("hi"))
    assert _GATEWAY_KEY not in str(stream_excinfo.value)

    health = await provider.health_check()
    assert _GATEWAY_KEY not in (health.message or "")
