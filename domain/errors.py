class BaseAppError(Exception):
    def __init__(self, message: str, cause: str | None = None, remediation: str | None = None):
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.remediation = remediation


class ExternalServiceError(BaseAppError):
    pass


class ValidationError(BaseAppError):
    pass


class DatabaseError(BaseAppError):
    pass
