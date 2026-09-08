"""操作日志工具：装饰器 + 异步落库，供各写操作接口记录审计日志。"""
import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def write_log(user_id, action, detail, request=None, status="success"):
    """同步写入一条系统日志（内部默认新建独立会话，避免与业务事务耦合）。"""
    from app.core.config import settings
    from app.core.database import SessionLocal
    from app.models import models as m

    ip = None
    if request is not None:
        client = getattr(request, "client", None)
        ip = client.host if client else None
    try:
        db = SessionLocal()
        db.add(m.SystemLog(user_id=user_id, action=action, detail=detail, ip=ip, status=status))
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("写日志失败 action=%s", action)
    finally:
        db.close()
    _ = settings  # 引用以兼容未来基于配置的日志写通道


async def write_log_async(user_id, action, detail, request=None, status="success"):
    """异步写日志：放入事件循环，不阻塞主流程。"""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, write_log, user_id, action, detail, request, status)


def log_operation(action: str = "", resource_type: str = ""):
    """操作日志装饰器。

    用法：
        @router.post("/xxx")
        @log_operation(action="CREATE_QUESTION", resource_type="question")
        async def create_question(...):
            ...

    约定：被装饰函数签名中需包含名为 `request`（可选）与 `current_user`（需持有 .id）的参数。
    """

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            request = kwargs.get("request")
            user = kwargs.get("current_user") or kwargs.get("user")
            user_id = getattr(user, "id", None)
            detail = kwargs.get("detail", "")
            start = asyncio.get_event_loop().time()
            try:
                result = await func(*args, **kwargs)
                _record(after=True, request=request, user_id=user_id,
                        action=action, resource_type=resource_type, detail=detail,
                        ms=asyncio.get_event_loop().time() - start, status="success")
                return result
            except Exception as exc:
                _record(after=True, request=request, user_id=user_id,
                        action=action, resource_type=resource_type, detail=f"{detail} {exc}",
                        ms=asyncio.get_event_loop().time() - start, status="failed")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            request = kwargs.get("request")
            user = kwargs.get("current_user") or kwargs.get("user")
            user_id = getattr(user, "id", None)
            detail = kwargs.get("detail", "")
            start = __import__("time").time()
            try:
                result = func(*args, **kwargs)
                _record(request=request, user_id=user_id,
                        action=action, resource_type=resource_type, detail=detail,
                        ms=__import__("time").time() - start, status="success")
                return result
            except Exception as exc:
                _record(request=request, user_id=user_id,
                        action=action, resource_type=resource_type, detail=f"{detail} {exc}",
                        ms=__import__("time").time() - start, status="failed")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _record(after, request, user_id, action, resource_type, detail, ms, status):
    import threading

    prefix = f"{action}[{resource_type}]" if resource_type else action
    text = f"{prefix} {detail} ({int(ms * 1000)}ms)"
    write_log(user_id, action or "OPERATION", text.strip(), request, status)