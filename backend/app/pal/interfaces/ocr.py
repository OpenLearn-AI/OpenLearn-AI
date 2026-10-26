from abc import abstractmethod
from collections.abc import Sequence

from app.pal.interfaces.base import BasePALInterface
from app.pal.models.types import OCRResult


class OCRInterface(BasePALInterface):
    """Provider-independent OCR contract."""

    @abstractmethod
    async def extract_text(
        self,
        source: str,
    ) -> OCRResult:
        """Extract and normalize text from a document source."""
        raise NotImplementedError

    @abstractmethod
    async def extract_text_batch(
        self,
        sources: Sequence[str],
    ) -> list[OCRResult]:
        """Extract and normalize text from a batch of document sources."""
        raise NotImplementedError

