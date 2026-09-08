"""AI 服务商模型：多服务商配置，API Key 用 Fernet 加密存储。"""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class AIProvider(Base):
    __tablename__ = "ai_providers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)      # 服务商名称
    provider = Column(String(30), nullable=False, default="custom")  # deepseek/qwen/glm/custom
    base_url = Column(String(255), nullable=False)
    model = Column(String(100), nullable=False)
    api_key_enc = Column(Text, nullable=False)                  # Fernet 加密后的 Key
    key_masked = Column(String(100))                            # 前端展示用脱敏串 sk-****abcd
    quota_limit = Column(Integer)                               # 额度限制（可选）
    is_default = Column(Integer, nullable=False, default=0)     # 是否默认服务商
    enabled = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def api_key(self):
        from app.utils.crypto import decrypt_key

        return decrypt_key(self.api_key_enc) if self.api_key_enc else ""