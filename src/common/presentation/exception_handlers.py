import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    structlog.get_logger(__name__).exception(
        "Unhandled request exception",
        method=request.method,
        path=request.url.path,
        exception_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unhandled_exception_handler)


__all__ = ["register_exception_handlers", "unhandled_exception_handler"]
