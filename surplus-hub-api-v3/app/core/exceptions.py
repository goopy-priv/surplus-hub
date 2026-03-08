from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        data: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.data = data


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "data": exc.data,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error",
        },
    )
