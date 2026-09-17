from collections.abc import AsyncIterator, Sequence

from app.pal.interfaces.reasoning import ReasoningInterface
from app.pal.models.types import (
    ChatMessage,
    HealthStatus,
    ReasoningChunk,
    ReasoningResult,
    TokenUsage,
)


class MockReasoningProvider(ReasoningInterface):
    """Deterministic reasoning provider for tests and local development."""

    provider_name = "mock"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message="Mock reasoning provider is ready.",
        )

    def _extract_prompt(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
    ) -> str:
        if isinstance(messages, str):
            return messages
        parts = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                parts.append(f"{msg.role}: {msg.content}")
            elif isinstance(msg, dict):
                parts.append(f"{msg.get('role', 'user')}: {msg.get('content', '')}")
            else:
                parts.append(str(msg))
        return "\n".join(parts)

    async def reason(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ReasoningResult:
        prompt_text = self._extract_prompt(messages)
        text = f"Mock response to: {prompt_text}"
        return ReasoningResult(
            text=text,
            model=model or "mock-reasoning",
            provider=self.provider_name,
            usage=TokenUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15),
            metadata={
                "system_prompt": system_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
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
        prompt_text = self._extract_prompt(messages)
        full_text = f"Mock response to: {prompt_text}"
        tokens = full_text.split(" ")

        for i, token in enumerate(tokens):
            chunk_text = token if i == len(tokens) - 1 else token + " "
            yield ReasoningChunk(text=chunk_text)

        yield ReasoningChunk(
            text="",
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15),
        )

