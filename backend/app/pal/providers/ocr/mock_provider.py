from collections.abc import Sequence

from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import HealthStatus, OCRResult


class MockOCRProvider(OCRInterface):
    """Deterministic OCR provider for tests and local development."""

    provider_name = "mock"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message="Mock OCR provider is ready.",
        )

    async def extract_text(self, source: str) -> OCRResult:
        return OCRResult(
            text=f"Mock OCR result for: {source}",
            provider=self.provider_name,
            metadata={"source": source},
        )

    async def extract_text_batch(
        self,
        sources: Sequence[str],
    ) -> list[OCRResult]:
        return [await self.extract_text(source) for source in sources]

