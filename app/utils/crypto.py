"""API Key 加密工具（Fernet）。密钥从环境变量读取，未配置时使用持久化文件密钥，避免每次重启刷新导致存量数据解密失败。"""
import base64
import os

from cryptography.fernet import Fernet, InvalidToken


def _load_key() -> bytes:
    from pathlib import Path

    from app.core.config import BASE_DIR

    env_key = os.getenv("ENCRYPTION_KEY", "")
    if env_key:
        # 兼容用户直接配置的 Fernet key（44 位 base64）
        key = env_key if len(env_key) == 44 else base64.urlsafe_b64encode(env_key.encode()[:32].ljust(32, b"0"))
        return key.encode() if isinstance(key, str) else key

    keyfile = BASE_DIR / ".fernet_key"
    if keyfile.exists():
        return keyfile.read_bytes().strip()

    key = Fernet.generate_key()
    keyfile.write_bytes(key)
    try:
        keyfile.chmod(0o600)
    except Exception:
        pass
    return key


_cipher = Fernet(_load_key())


def encrypt_key(plain: str) -> str:
    if not plain:
        return ""
    return _cipher.encrypt(plain.encode()).decode()


def decrypt_key(token: str) -> str:
    if not token:
        return ""
    try:
        return _cipher.decrypt(token.encode()).decode()
    except (InvalidToken, Exception):
        return ""


def mask_key(plain: str) -> str:
    if not plain:
        return ""
    if len(plain) <= 7:
        return "****"
    prefix, tail = plain[:3], plain[-4:]
    return f"{prefix}****{tail}"