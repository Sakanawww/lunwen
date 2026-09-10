"""认证依赖：从 Cookie 中解析 token → 返回当前用户。"""
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as OrmSession

from app.core import session as sstore
from app.core.database import get_db
from app.models import models as m


def current_user(request: Request, db: OrmSession = Depends(get_db)) -> m.User:
    """从 Cookie 或 Authorization: Bearer 还原当前登录用户；未登录则抛出 401。"""
    token = request.cookies.get("token") or ""
    if not token:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
    sess = sstore.get_session(token)
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或会话已过期"
        )
    user = db.get(m.User, sess["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


def require_role(*roles: str):
    """返回一个依赖，要求当前用户属于指定角色。"""

    def checker(user: m.User = Depends(current_user)) -> m.User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权限执行该操作"
            )
        return user

    return checker