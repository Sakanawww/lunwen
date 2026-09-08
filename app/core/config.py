"""系统配置：统一从 .env 读取，密钥不进入代码仓库。"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（app/ 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """集中管理系统运行所需的常量配置。"""

    # ---- 大模型（云端 API，阿里云百炼 / Qwen）----
    LLM_API_KEY = os.getenv("QWEN_API_KEY", "")
    LLM_BASE_URL = os.getenv(
        "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    LLM_CHAT_MODEL = os.getenv("QWEN_CHAT_MODEL", "qwen-plus")
    LLM_EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4")

    # ---- MySQL ----
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "course_ta")

    # ---- 数据库连接串（PyMySQL 兼容，供 SQLAlchemy 使用）----
    SQLALCHEMY_DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )

    # ---- 项目路径 ----
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = BASE_DIR / "data" / "uploads"   # 知识库上传文件
    FAISS_INDEX_DIR = BASE_DIR / "data" / "faiss_index"  # 向量索引持久化


settings = Settings()

# 运行前确保关键目录存在
for _d in (settings.UPLOAD_DIR, settings.FAISS_INDEX_DIR):
    _d.mkdir(parents=True, exist_ok=True)