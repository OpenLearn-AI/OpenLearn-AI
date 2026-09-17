from abc import ABC, abstractmethod

from app.pal.models.types import HealthStatus


class BasePALInterface(ABC):
    """Base contract shared by all PAL capabilities."""

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Return the current health status of the provider."""
        raise NotImplementedError
