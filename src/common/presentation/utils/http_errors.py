from typing import NoReturn

from fastapi import HTTPException, status


def raise_forbidden(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )
