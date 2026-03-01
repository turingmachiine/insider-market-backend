from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

from src.application.protocols import HasTransactionManager

# TypeVar для асинхронных функций
AsyncFunc = TypeVar("AsyncFunc", bound=Callable[..., Awaitable[Any]])


def transactional(nested: bool = False) -> Callable[[AsyncFunc], AsyncFunc]:
    def decorator(func: AsyncFunc) -> AsyncFunc:
        @wraps(func)
        async def wrapper(
            self: HasTransactionManager, *args: Any, **kwargs: Any
        ) -> Any:
            if nested:
                async with self.transaction_manager.nested_transaction():
                    return await func(self, *args, **kwargs)
            else:
                async with self.transaction_manager.transaction():
                    return await func(self, *args, **kwargs)

        return cast(AsyncFunc, wrapper)

    return decorator


__all__ = ["transactional"]
