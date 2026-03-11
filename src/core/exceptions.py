class DomainError(Exception):
    pass


class ProductNotFoundError(DomainError):
    pass


class AIProviderError(DomainError):
    pass


class SurveyFlowNotFoundError(DomainError):
    pass


class AIRetryableError(AIProviderError):
    """Transient error — can retry (429, 5xx)."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AIFatalError(AIProviderError):
    """Non-retryable error (400, 401, 403)."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AIRetryExhaustedError(AIProviderError):
    """All retries failed."""

    def __init__(self, message: str, attempts: int, last_error: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error
