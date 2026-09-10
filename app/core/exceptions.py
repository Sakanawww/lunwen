"""统一异常处理器。"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理。"""
    logger.warning(
        f"验证失败：{exc.errors()}",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "validation_error",
            "title": "请求验证失败",
            "detail": exc.errors(),
        },
    )


async def http_exception_handler(request: Request, exc):
    """HTTP 异常处理。"""
    logger.warning(
        f"HTTP 错误 {exc.status_code}: {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "http_error",
            "title": exc.detail,
            "status": exc.status_code,
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """全局异常处理。"""
    logger.error(
        f"服务器内部错误：{str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exc_info": True,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "internal_error",
            "title": "服务器内部错误",
            "detail": "请稍后重试",
        },
    )


async def pydantic_exception_handler(request: Request, exc: ValidationError):
    """Pydantic 验证异常处理。"""
    logger.warning(f"Pydantic 验证失败：{exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "validation_error",
            "title": "数据验证失败",
            "detail": exc.errors(),
        },
    )
