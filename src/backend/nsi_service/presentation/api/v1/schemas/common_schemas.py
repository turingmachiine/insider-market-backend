from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Базовая схема ответа"""

    success: bool = True
    message: str | None = None


class PaginatedResponse(BaseModel):
    """Пагинированный ответ"""

    items: list
    total: int
    limit: int
    offset: int
