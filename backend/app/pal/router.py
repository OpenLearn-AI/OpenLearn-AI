import asyncio
import time
from collections.abc import AsyncIterator, Sequence
from typing import Any, TypeVar

import structlog

from app.pal.exceptions import (
    ProviderError,
    ProviderServerError,
    UnsupportedOperationError,
)
from app.pal.interfaces.base import BasePALInterface
from app.pal.models.types import HealthStatus

ProviderT = TypeVar("ProviderT", bound=BasePALInterface)

logger = structlog.get_logger(__name__)


class PALRouter:
    """Route requests through an ordered list of PAL providers with typed fallback."""

    def __init__(self, providers: Sequence[ProviderT]):
        if not providers:
            raise ValueError("PALRouter requires at least one provider.")

        self.providers = list(providers)

    async def health_check(self) -> list[HealthStatus]:
        """Return the health status of all configured providers concurrently."""
        tasks = [provider.health_check() for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        statuses: list[HealthStatus] = []
        for provider, res in zip(self.providers, results, strict=False):
            if isinstance(res, HealthStatus):
                statuses.append(res)
            elif isinstance(res, Exception):
                provider_name = getattr(
                    provider, "provider_name", provider.__class__.__name__
                )
                statuses.append(
                    HealthStatus(
                        healthy=False,
                        provider=provider_name,
                        message=f"Health check failed: {res}",
                    )
                )
        return statuses

    async def execute(self, operation: str, *args: Any, **kwargs: Any) -> Any:
        """
        Execute an operation using the first provider that succeeds.

        Fallback is attempted ONLY on ProviderError.
        InvalidInputError, ConfigurationError, and programming errors raise immediately.
        """
        last_error: ProviderError | None = None

        for idx, provider in enumerate(self.providers):
            if not hasattr(provider, operation):
                raise UnsupportedOperationError(
                    f"Provider '{getattr(provider, 'provider_name', provider.__class__.__name__)}' "
                    f"does not support operation '{operation}'."
                )

            method = getattr(provider, operation)
            start_time = time.perf_counter()

            try:
                return await method(*args, **kwargs)
            except ProviderError as exc:
                latency_ms = (time.perf_counter() - start_time) * 1000
                last_error = exc
                provider_name = getattr(
                    provider, "provider_name", provider.__class__.__name__
                )

                has_next = idx < len(self.providers) - 1
                if has_next:
                    logger.warning(
                        "pal_provider_fallback",
                        operation=operation,
                        provider=provider_name,
                        error_class=exc.__class__.__name__,
                        latency_ms=round(latency_ms, 2),
                    )
                continue

        if last_error is not None:
            raise ProviderServerError(
                f"All PAL providers failed for operation '{operation}'."
            ) from last_error

        raise UnsupportedOperationError(
            f"No PAL provider could execute operation '{operation}'."
        )

    async def execute_stream(
        self, operation: str, *args: Any, **kwargs: Any
    ) -> AsyncIterator[Any]:
        """
        Execute a streaming operation with fallback only allowed before the first chunk.

        Once the first chunk has been yielded, failures are terminal.
        """
        last_error: ProviderError | None = None

        for idx, provider in enumerate(self.providers):
            if not hasattr(provider, operation):
                raise UnsupportedOperationError(
                    f"Provider '{getattr(provider, 'provider_name', provider.__class__.__name__)}' "
                    f"does not support operation '{operation}'."
                )

            method = getattr(provider, operation)
            start_time = time.perf_counter()
            first_chunk_emitted = False

            try:
                stream = method(*args, **kwargs)
                async for chunk in stream:
                    first_chunk_emitted = True
                    yield chunk
                return
            except ProviderError as exc:
                latency_ms = (time.perf_counter() - start_time) * 1000
                provider_name = getattr(
                    provider, "provider_name", provider.__class__.__name__
                )

                if first_chunk_emitted:
                    logger.error(
                        "pal_streaming_provider_failed_midstream",
                        operation=operation,
                        provider=provider_name,
                        error_class=exc.__class__.__name__,
                        latency_ms=round(latency_ms, 2),
                    )
                    raise

                last_error = exc
                has_next = idx < len(self.providers) - 1
                if has_next:
                    logger.warning(
                        "pal_provider_fallback",
                        operation=operation,
                        provider=provider_name,
                        error_class=exc.__class__.__name__,
                        latency_ms=round(latency_ms, 2),
                    )
                continue

        if last_error is not None:
            raise ProviderServerError(
                f"All PAL providers failed for operation '{operation}'."
            ) from last_error

        raise UnsupportedOperationError(
            f"No PAL provider could execute operation '{operation}'."
        )

