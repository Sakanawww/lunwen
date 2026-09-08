"""大模型封装：统一管理 LLM 与 Embedding 客户端（云端 API）。"""
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings

# 依据环境变量"平台兼容口径"选择：默认 Qwen(百炼)，可按需将 api_key/base_url
# 指向 DeepSeek 等其它 OpenAI 兼容接口，无需改动代码。
_PROVIDER = "qwen"

DEFAULT_EMBEDDING_DIMS = 1024  # text-embedding-v4


class LLMFactory:
    """按供应商创建可复用的 Chat/Embedding 客户端。"""

    @staticmethod
    def _default_provider() -> dict | None:
        """读取管理员在「Agent 服务商配置」中设为默认的启用服务商。

        返回 {name, model, api_key, base_url}；未配置或读取失败时返回 None，
        由调用方回退到 .env 的默认配置。
        """
        try:
            from app.core.database import SessionLocal

            from app.models.ai_provider import AIProvider

            db = SessionLocal()
            try:
                row = (db.query(AIProvider)
                       .filter(AIProvider.is_default == 1, AIProvider.enabled == 1)
                       .first())
            finally:
                db.close()
            if not row or not row.api_key:
                return None
            return {
                "model": row.model,
                "api_key": row.api_key,
                "base_url": row.base_url,
            }
        except Exception:
            return None

    @staticmethod
    def chat_model(model: str | None = None) -> BaseChatModel:
        """返回 LangChain 兼容的聊天模型（优先使用配置页默认服务商）。"""
        model_args = None
        _model = model or getattr(settings, "LLM_CHAT_MODEL", "qwen-plus")
        provider = LLMFactory._default_provider()
        if provider:
            model_args = dict(
                model=provider["model"] if not model else _model,
                api_key=provider["api_key"],
                base_url=provider["base_url"],
                temperature=0.3,
                max_tokens=1500,
                timeout=120,
            )
        if model_args is None:
            model_args = dict(
                model=_model,
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                temperature=0.3,
                max_tokens=1500,
                timeout=120,
            )
        if _PROVIDER == "qwen":
            # 通义千问（百炼 OpenAI 兼容口）：部分推理模型用 extra_body 关闭思链，
            # 以免回答被塞进 reasoning_content 导致 content 为空。
            model_args.setdefault("extra_body", {"enable_thinking": False})
            from langchain_openai import ChatOpenAI as _QwenChat

            return _QwenChat(**model_args)
        return ChatOpenAI(**model_args)

    @staticmethod
    def embeddings(model: str | None = None) -> OpenAIEmbeddings:
        """返回 Embedding 客户端。"""
        return OpenAIEmbeddings(
            model=model or settings.LLM_EMBEDDING_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            check_embedding_ctx_length=False,
        )


# 供各 Agent 使用的 Model 工厂方法
def get_chat_model(model: str | None = None):
    """返回一个新的 LangChain 聊天模型实例。"""
    return LLMFactory.chat_model(model)


# 预留的可复用单例（供需要全局复用的地方使用）
_default_chat_model = LLMFactory.chat_model()
_embed = LLMFactory.embeddings()

embeddings = _embed
# 保持与既有调用兼容：chat_model 作为可调用（等价于 get_chat_model）
chat_model = get_chat_model