from abc import abstractmethod
from collections.abc import AsyncIterator, Sequence

from app.pal.interfaces.base import BasePALInterface
from app.pal.models.types import ChatMessage, ReasoningChunk, ReasoningResult


class ReasoningInterface(BasePALInterface):
    """Provider-independent LLM reasoning contract."""

    @abstractmethod
    async def reason(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ReasoningResult:
        """Generate a reasoning response for the given messages/prompt."""
        raise NotImplementedError

    @abstractmethod
    async def reason_stream(
        self,
        messages: Sequence[ChatMessage | dict[str, str]] | str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[ReasoningChunk]:
        """Stream reasoning token chunks for the given messages/prompt."""
        raise NotImplementedError

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ReasoningResult:
        """Compatibility wrapper forwarding prompt generation to reason()."""
        return await self.reason(
            prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

