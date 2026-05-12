from typing import Protocol

from src.common.application.user_context import UserContext


class IUserProvider(Protocol):
    def get_user_context(self, token: str) -> UserContext:
        raise NotImplementedError
