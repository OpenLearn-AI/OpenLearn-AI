from collections.abc import AsyncIterator, Sequence
from typing import Any

import pytest

from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    UnsupportedOperationError,
)


from app.pal.interfaces.ocr import OCRInterface
from app.pal.interfaces.reasoning import ReasoningInterface
from app.pal.models.types import (
    ChatMessage,
    HealthStatus,
    OCRResult,
    ReasoningChunk,
    ReasoningResult,
)
from app.pal.router import PALRouter


class SuccessfulOCRProvider(OCRInterface):
    provider_name = "success"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        return OCRResult(text=f"Success: {source}", provider=self.provider_name)

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        return [await self.extract_text(s) for s in sources]


class FailingOCRProvider(OCRInterface):
    provider_name = "failing"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=False, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        raise ProviderTimeoutError("OCR provider timed out")

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        raise ProviderTimeoutError("OCR provider timed out")


class InvalidInputOCRProvider(OCRInterface):
    provider_name = "invalid_input"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        raise InvalidInputError("File format not supported")

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        raise InvalidInputError("File format not supported")


class ConfigurationErrorOCRProvider(OCRInterface):
    provider_name = "config_error"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        raise ConfigurationError("Missing API key configuration")

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        raise ConfigurationError("Missing API key configuration")


class TimeoutOCRProvider(OCRInterface):
    provider_name = "timeout"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=False, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        raise ProviderTimeoutError("Request timed out after 5s")

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        raise ProviderTimeoutError("Request timed out after 5s")


class UnavailableOCRProvider(OCRInterface):
    provider_name = "unavailable"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=False, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        raise ProviderUnavailableError("Service connection refused")

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        raise ProviderUnavailableError("Service connection refused")



class RaisingHealthCheckProvider(OCRInterface):
    provider_name = "raising_health"

    async def health_check(self) -> HealthStatus:
        raise ProviderUnavailableError("Network unreachable")

    async def extract_text(self, source: str) -> OCRResult:
        return OCRResult(text=f"Success: {source}", provider=self.provider_name)

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        return [await self.extract_text(s) for s in sources]


# Streaming Reasoning Providers for testing streaming fallback rules
class EarlyFailingReasoningProvider(ReasoningInterface):
    provider_name = "early_failing"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=False, provider=self.provider_name)

    async def reason(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        **kwargs: Any,
    ) -> ReasoningResult:
        raise ProviderUnavailableError("LLM API unavailable")

    async def reason_stream(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        **kwargs: Any,
    ) -> AsyncIterator[ReasoningChunk]:
        # Fails before yielding any chunk
        raise ProviderUnavailableError("LLM API unavailable before stream")
        yield  # make it a generator


class MidStreamFailingReasoningProvider(ReasoningInterface):
    provider_name = "mid_stream_failing"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def reason(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        **kwargs: Any,
    ) -> ReasoningResult:
        return ReasoningResult(text="OK", model="m", provider=self.provider_name)

    async def reason_stream(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        **kwargs: Any,
    ) -> AsyncIterator[ReasoningChunk]:
        yield ReasoningChunk(text="First chunk")
        # Fails after yielding first chunk
        raise ProviderServerError("LLM disconnected mid-stream")


class SuccessfulReasoningProvider(ReasoningInterface):
    provider_name = "stream_success"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def reason(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        **kwargs: Any,
    ) -> ReasoningResult:
        return ReasoningResult(text="Success response", model="m", provider=self.provider_name)

    async def reason_stream(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        **kwargs: Any,
    ) -> AsyncIterator[ReasoningChunk]:
        yield ReasoningChunk(text="Success ")
        yield ReasoningChunk(text="stream")


@pytest.mark.asyncio
async def test_router_uses_first_successful_provider():
    router = PALRouter([SuccessfulOCRProvider()])
    result = await router.execute("extract_text", "document.pdf")

    assert result.text == "Success: document.pdf"
    assert result.provider == "success"


@pytest.mark.asyncio
async def test_router_falls_back_on_provider_error():
    router = PALRouter([FailingOCRProvider(), SuccessfulOCRProvider()])
    result = await router.execute("extract_text", "document.pdf")

    assert result.text == "Success: document.pdf"
    assert result.provider == "success"


@pytest.mark.asyncio
async def test_router_does_not_fallback_on_invalid_input_error():
    router = PALRouter([InvalidInputOCRProvider(), SuccessfulOCRProvider()])

    with pytest.raises(InvalidInputError, match="File format not supported"):
        await router.execute("extract_text", "bad_file.xyz")


@pytest.mark.asyncio
async def test_router_does_not_fallback_on_configuration_error():
    router = PALRouter([ConfigurationErrorOCRProvider(), SuccessfulOCRProvider()])

    with pytest.raises(ConfigurationError, match="Missing API key configuration"):
        await router.execute("extract_text", "document.pdf")


@pytest.mark.asyncio
async def test_router_falls_back_across_multiple_providers():
    # Provider A -> Timeout, Provider B -> Unavailable, Provider C -> Success
    router = PALRouter(
        [
            TimeoutOCRProvider(),
            UnavailableOCRProvider(),
            SuccessfulOCRProvider(),
        ]
    )
    result = await router.execute("extract_text", "multi_fallback.pdf")

    assert result.text == "Success: multi_fallback.pdf"
    assert result.provider == "success"



@pytest.mark.asyncio
async def test_router_does_not_fallback_on_programming_error():
    class BuggyOCRProvider(OCRInterface):
        async def health_check(self) -> HealthStatus:
            return HealthStatus(healthy=True, provider="buggy")

        async def extract_text(self, source: str) -> OCRResult:
            raise TypeError("unexpected argument type in provider implementation")

        async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
            return []

    router = PALRouter([BuggyOCRProvider(), SuccessfulOCRProvider()])

    with pytest.raises(TypeError, match="unexpected argument type"):
        await router.execute("extract_text", "document.pdf")


@pytest.mark.asyncio
async def test_router_all_providers_fail():
    router = PALRouter([FailingOCRProvider()])

    with pytest.raises(ProviderServerError, match="All PAL providers failed"):
        await router.execute("extract_text", "document.pdf")


@pytest.mark.asyncio
async def test_router_unsupported_operation():
    router = PALRouter([SuccessfulOCRProvider()])

    with pytest.raises(UnsupportedOperationError, match="does not support operation"):
        await router.execute("non_existent_method", "arg")


@pytest.mark.asyncio
async def test_router_health_check():
    router = PALRouter(
        [
            SuccessfulOCRProvider(),
            FailingOCRProvider(),
            RaisingHealthCheckProvider(),
        ]
    )

    statuses = await router.health_check()
    assert len(statuses) == 3
    assert statuses[0].healthy is True
    assert statuses[1].healthy is False
    assert statuses[2].healthy is False
    assert "Health check failed" in (statuses[2].message or "")


def test_router_requires_provider():
    with pytest.raises(ValueError, match="at least one provider"):
        PALRouter([])


@pytest.mark.asyncio
async def test_router_streaming_fallback_before_first_chunk():
    # If primary fails before first chunk, fallback to second provider
    router = PALRouter([EarlyFailingReasoningProvider(), SuccessfulReasoningProvider()])
    chunks = []
    async for chunk in router.execute_stream("reason_stream", "Hello"):
        chunks.append(chunk.text)

    assert "".join(chunks) == "Success stream"


@pytest.mark.asyncio
async def test_router_streaming_failure_after_first_chunk_is_terminal():
    # If primary fails after emitting first chunk, it MUST fail terminally and NOT switch to fallback
    router = PALRouter([MidStreamFailingReasoningProvider(), SuccessfulReasoningProvider()])
    chunks = []

    with pytest.raises(ProviderServerError, match="LLM disconnected mid-stream"):
        async for chunk in router.execute_stream("reason_stream", "Hello"):
            chunks.append(chunk.text)

    # First chunk was received, then failure was terminal
    assert chunks == ["First chunk"]
