"""会话存储模块：完全采用 Redis 存储会话。

生产环境要求：
1. 必须配置 Redis 服务
2. 通过环境变量设置 Redis 连接参数
3. 不再支持内存降级方案

环境变量：
- REDIS_HOST: Redis 主机地址（默认 localhost）
- REDIS_PORT: Redis 端口（默认 6379）
- REDIS_DB: Redis 数据库编号（默认 0）
- SESSION_TTL: 会话过期时间（秒，默认 28800=8 小时）
"""
import os
from datetime import datetime, timedelta

import redis

# 配置 - 完全从环境变量读取
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
TTL_SECONDS = int(os.getenv("SESSION_TTL", "28800"))  # 默认 8 小时


class SessionStore:
    """Redis 会话存储类。"""
    
    def __init__(
        self,
        host: str = REDIS_HOST,
        port: int = REDIS_PORT,
        db: int = REDIS_DB,
        ttl: int = TTL_SECONDS,
    ):
        """初始化 Redis 会话存储。
        
        Args:
            host: Redis 主机地址
            port: Redis 端口
            db: Redis 数据库编号
            ttl: 会话过期时间（秒）
        """
        self.ttl = ttl
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        # 测试连接
        self._client.ping()
    
    def create_session(self, user_id: int, real_name: str, role: str) -> str:
        """创建新会话。
        
        Args:
            user_id: 用户 ID
            real_name: 真实姓名
            role: 用户角色
            
        Returns:
            会话 token
        """
        from app.utils.helpers import gen_token
        
        token = gen_token()
        session_data = {
            "user_id": str(user_id),
            "real_name": real_name,
            "role": role,
            "created_at": datetime.now().isoformat(),
        }
        
        key = f"session:{token}"
        pipe = self._client.pipeline()
        pipe.hset(key, mapping=session_data)
        pipe.expire(key, self.ttl)
        pipe.execute()
        
        return token
    
    def get_session(self, token: str) -> dict | None:
        """获取会话信息。
        
        Args:
            token: 会话 token
            
        Returns:
            会话数据，若不存在或已过期则返回 None
        """
        if not token:
            return None
        
        key = f"session:{token}"
        data = self._client.hgetall(key)
        
        if not data:
            return None
        
        # 检查过期时间
        ttl = self._client.ttl(key)
        if ttl < 0:
            return None
        
        return {
            "user_id": int(data["user_id"]),
            "real_name": data["real_name"],
            "role": data["role"],
        }
    
    def destroy_session(self, token: str):
        """销毁会话。
        
        Args:
            token: 会话 token
        """
        key = f"session:{token}"
        self._client.delete(key)
    
    def extend_session(self, token: str) -> bool:
        """延长会话过期时间。
        
        Args:
            token: 会话 token
            
        Returns:
            是否成功延长
        """
        key = f"session:{token}"
        if not self._client.exists(key):
            return False
        
        self._client.expire(key, self.ttl)
        return True


# 全局单例
_store: SessionStore | None = None


def get_store() -> SessionStore:
    """获取会话存储单例。
    
    Returns:
        SessionStore 实例
    """
    global _store
    if _store is None:
        _store = SessionStore()
    return _store


# 便捷函数（保持向后兼容）
def create_session(user_id: int, real_name: str, role: str) -> str:
    """创建新会话。"""
    return get_store().create_session(user_id, real_name, role)


def get_session(token: str) -> dict | None:
    """获取会话信息。"""
    return get_store().get_session(token)


def destroy_session(token: str):
    """销毁会话。"""
    get_store().destroy_session(token)
