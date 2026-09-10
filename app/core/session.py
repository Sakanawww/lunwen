"""会话存储模块。

支持两种存储方式：
1. Redis 存储（生产环境）
2. 内存存储（开发/降级方案）

通过环境变量 SESSION_STORAGE 控制：
- SESSION_STORAGE=redis  # 使用 Redis
- SESSION_STORAGE=memory  # 使用内存（默认）
"""
import os
import threading
from datetime import datetime, timedelta

# 尝试导入 Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# 配置
STORAGE_TYPE = os.getenv("SESSION_STORAGE", "memory")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
TTL_SECONDS = int(os.getenv("SESSION_TTL", "28800"))  # 默认 8 小时

# Redis 客户端
_redis_client = None
if STORAGE_TYPE == "redis" and REDIS_AVAILABLE:
    try:
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        _redis_client.ping()  # 测试连接
        STORAGE_TYPE = "redis"  # 连接成功，使用 Redis
    except Exception:
        STORAGE_TYPE = "memory"  # 连接失败，降级为内存

# 内存存储（降级方案）
_sessions: dict[str, dict] = {}
_lock = threading.Lock()


def create_session(user_id: int, real_name: str, role: str) -> str:
    """创建新会话。"""
    from app.utils.helpers import gen_token

    token = gen_token()
    session_data = {
        "user_id": user_id,
        "real_name": real_name,
        "role": role,
        "created_at": datetime.now().isoformat(),
    }

    if STORAGE_TYPE == "redis" and _redis_client:
        # 存储到 Redis
        key = f"session:{token}"
        _redis_client.hset(key, mapping=session_data)
        _redis_client.expire(key, TTL_SECONDS)
    else:
        # 存储到内存
        with _lock:
            _sessions[token] = {
                **session_data,
                "expire": datetime.now() + timedelta(seconds=TTL_SECONDS),
            }

    return token


def get_session(token: str) -> dict | None:
    """获取会话信息。"""
    if not token:
        return None

    if STORAGE_TYPE == "redis" and _redis_client:
        # 从 Redis 获取
        key = f"session:{token}"
        data = _redis_client.hgetall(key)
        if not data:
            return None
        # 检查过期时间
        ttl = _redis_client.ttl(key)
        if ttl < 0:
            return None
        return {
            "user_id": int(data["user_id"]),
            "real_name": data["real_name"],
            "role": data["role"],
        }
    else:
        # 从内存获取
        with _lock:
            s = _sessions.get(token)
            if not s:
                return None
            if s["expire"] < datetime.now():
                del _sessions[token]
                return None
            return {
                "user_id": s["user_id"],
                "real_name": s["real_name"],
                "role": s["role"],
            }


def destroy_session(token: str):
    """销毁会话。"""
    if STORAGE_TYPE == "redis" and _redis_client:
        key = f"session:{token}"
        _redis_client.delete(key)
    else:
        with _lock:
            _sessions.pop(token, None)


def cleanup_expired():
    """清理过期会话（仅内存模式需要）。"""
    if STORAGE_TYPE != "memory":
        return

    now = datetime.now()
    with _lock:
        expired = [k for k, v in _sessions.items() if v["expire"] < now]
        for k in expired:
            del _sessions[k]


# 定时清理（仅内存模式）
if STORAGE_TYPE == "memory":
    import atexit
    
    def _cleanup_on_exit():
        """程序退出时清理。"""
        pass
    
    atexit.register(_cleanup_on_exit)