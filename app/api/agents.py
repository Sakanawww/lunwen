"""AI 服务商配置接口：多服务商 CRUD + 连接测试。仅管理员可管理。"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.deps import require_role
from app.models.ai_provider import AIProvider
from app.models import models as m
from app.utils import crypto
from app.utils.logging import write_log
from sqlalchemy.orm import Session as OrmSession

router = APIRouter(prefix="/api/agents/providers", tags=["Agent配置"])


class ProviderIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    provider: str = "custom"
    base_url: str = Field(..., max_length=255)
    model: str = Field(..., max_length=100)
    api_key: str = ""
    quota_limit: int | None = None
    is_default: bool = False
    enabled: bool = True


def _serialize(p: AIProvider) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "provider": p.provider,
        "base_url": p.base_url,
        "model": p.model,
        "key_masked": p.key_masked or crypto.mask_key(crypto.decrypt_key(p.api_key_enc)),
        "has_key": bool(p.api_key_enc),
        "quota_limit": p.quota_limit,
        "is_default": bool(p.is_default),
        "enabled": bool(p.enabled),
        "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M") if p.updated_at else None,
    }


@router.get("")
def list_providers(db: OrmSession = Depends(get_db),
                   user: m.User = Depends(require_role("admin"))):
    rows = db.query(AIProvider).order_by(AIProvider.is_default.desc(), AIProvider.id.asc()).all()
    return [_serialize(p) for p in rows]


@router.post("")
def create_provider(body: ProviderIn, request: Request, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(require_role("admin"))):
    if db.query(AIProvider).filter(AIProvider.name == body.name).first():
        raise HTTPException(400, "服务商名称已存在")
    row = AIProvider(
        name=body.name,
        provider=body.provider or "custom",
        base_url=body.base_url,
        model=body.model,
        api_key_enc=crypto.encrypt_key(body.api_key or ""),
        key_masked=crypto.mask_key(body.api_key or ""),
        quota_limit=body.quota_limit,
        is_default=1 if body.is_default else 0,
        enabled=1 if body.enabled else 0,
    )
    if body.is_default:
        db.query(AIProvider).update({AIProvider.is_default: 0})
    db.add(row)
    db.commit()
    db.refresh(row)
    write_log(user.id, "CREATE_PROVIDER", f"新增服务商：{body.name}（{body.model}）", request)
    return _serialize(row)


@router.put("/{pid}")
def update_provider(pid: int, body: ProviderIn, request: Request, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(require_role("admin"))):
    row = db.get(AIProvider, pid)
    if not row:
        raise HTTPException(404, "服务商不存在")
    dup = db.query(AIProvider).filter(AIProvider.name == body.name, AIProvider.id != pid).first()
    if dup:
        raise HTTPException(400, "服务商名称已存在")
    row.name = body.name
    row.provider = body.provider or "custom"
    row.base_url = body.base_url
    row.model = body.model
    if body.api_key:  # 留空则不修改
        row.api_key_enc = crypto.encrypt_key(body.api_key)
        row.key_masked = crypto.mask_key(body.api_key)
    row.quota_limit = body.quota_limit
    row.enabled = 1 if body.enabled else 0
    if body.is_default:
        db.query(AIProvider).update({AIProvider.is_default: 0})
    row.is_default = 1 if body.is_default else 0
    db.commit()
    db.refresh(row)
    write_log(user.id, "UPDATE_PROVIDER", f"更新服务商：{body.name}", request)
    return _serialize(row)


@router.delete("/{pid}")
def delete_provider(pid: int, request: Request, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(require_role("admin"))):
    row = db.get(AIProvider, pid)
    if not row:
        raise HTTPException(404, "服务商不存在")
    if row.is_default:
        raise HTTPException(400, "默认服务商不可删除，请先切换默认")
    name = row.name
    db.delete(row)
    db.commit()
    write_log(user.id, "DELETE_PROVIDER", f"删除服务商：{name}", request)
    return {"msg": "已删除", "id": pid}


@router.post("/{pid}/test")
def test_provider(pid: int, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_role("admin"))):
    """连接测试：用存储的 Key 向服务商发一次最小请求。"""
    row = db.get(AIProvider, pid)
    if not row:
        raise HTTPException(404, "服务商不存在")
    api_key = row.api_key
    if not api_key:
        raise HTTPException(400, "该服务商未配置 API Key")
    try:
        from langchain_openai import ChatOpenAI

        model_kwargs = dict(
            model=row.model,
            api_key=api_key,
            base_url=row.base_url,
            temperature=0,
            max_tokens=8,
            timeout=20,
        )
        if row.provider == "qwen":
            # 通义千问（百炼 OpenAI 兼容口）：关闭思考链，避免回答进入 reasoning_content
            model_kwargs["extra_body"] = {"enable_thinking": False}
        model = ChatOpenAI(**model_kwargs)
        resp = model.invoke("回复：ok")
        text = getattr(resp, "content", "")
        ok = bool(text)
        return {"ok": ok, "message": "连接成功" if ok else "返回为空，请检查模型名或接口"}
    except Exception as exc:
        return {"ok": False, "message": f"连接失败：{exc}"}