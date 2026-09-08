"""通用工具函数。"""
import hashlib
import uuid


def hash_password(password: str) -> str:
    """以 SHA-256 对明文密码做哈希（演示采用，生产请使用加盐 bcrypt）。"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def gen_token() -> str:
    """生成简单会话 token（本地会话方案）。"""
    return uuid.uuid4().hex


def to_dict(obj) -> dict:
    """将 SQLAlchemy 模型实例转为普通 dict。"""
    d = {}
    for col in obj.__table__.columns:
        d[col.name] = getattr(obj, col.name)
    return d