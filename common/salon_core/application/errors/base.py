class AppServiceError(Exception):
    """Controlled application-level error for interface layers."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
