from collections.abc import Callable
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., object])


def requires_auth(endpoint: F) -> F:
    endpoint_any = cast(Any, endpoint)
    endpoint_any.__auth_required__ = True
    return endpoint
