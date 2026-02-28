from typing import Any, Optional


class FootballResearchError(Exception):
    """Базовое исключение приложения"""

    def __init__(
        self, message: str, status_code: int = 500, details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(FootballResearchError):
    """Ресурс не найден"""

    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with id {resource_id} not found", status_code=404
        )


class ValidationError(FootballResearchError):
    """Ошибка валидации"""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=400, details=details)


class ExternalAPIError(FootballResearchError):
    """Ошибка внешнего API"""

    def __init__(self, api_name: str, original_error: str):
        super().__init__(
            message=f"Error calling {api_name}: {original_error}", status_code=503
        )
