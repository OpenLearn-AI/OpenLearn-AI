class PALError(Exception):
    """Base exception for all PAL errors."""


class ProviderError(PALError):
    """Base exception for provider failures that may trigger fallback."""


class ProviderUnavailableError(ProviderError):
    """Provider is unreachable, connection refused, or service down."""


class ProviderTimeoutError(ProviderError):
    """Provider request timed out."""


class ProviderRateLimitError(ProviderError):
    """Provider returned rate limit (e.g. HTTP 429)."""


class ProviderServerError(ProviderError):
    """Provider returned server error (e.g. HTTP 5xx)."""


class InvalidInputError(PALError):
    """Caller provided invalid input (do NOT trigger provider fallback)."""


class ConfigurationError(PALError):
    """Provider configuration is invalid or missing (do NOT trigger fallback)."""


class UnsupportedOperationError(PALError):
    """Requested operation is not supported by the provider (do NOT trigger fallback)."""
