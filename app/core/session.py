"""简易会话存储（降级方案，未启用 Redis 时用内存 dict + token 关联）。

说明：需求书允许 Redis 可降级为"本地简单会话"。
本模块提供一个与 Redis 同接口的内存实现，便于本地演示；接入 Redis 时，
将 _sessions 替换为 Redis 客户端即可，接口不变。
"""
import threading
from datetime import datetime, timedelta

_sessions: dict[str, dict] = {}
_lock = threading.Lock()
TTL = timedelta(hours=8)


def create_session(user_id: int, real_name: str, role: str) -> str:
    from app.utils.helpers import gen_token

    token = gen_token()
    with _lock:
        _sessions[token] = {
            "user_id": user_id,
            "real_name": real_name,
            "role": role,
            "expire": datetime.now() + TTL,
        }
    return token


def get_session(token: str) -> dict | None:
    if not token:
        return None
    with _lock:
        s = _sessions.get(token)
        if not s:
            return None
        if s["expire"] < datetime.now():
            del _sessions[token]
            return None
        return s


def destroy_session(token: str):
    with _lock:
        _sessions.pop(token, None)