"""系统日志接口：操作日志查询与统计分析（管理员）。"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models import models as m

router = APIRouter(prefix="/api/logs", tags=["日志系统"])


def _ensure_admin(user: m.User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问日志")


@router.get("/operations")
def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: int | None = None,
    action: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    keyword: str | None = None,
    db: OrmSession = Depends(get_db),
    user: m.User = Depends(require_role("admin")),
):
    """分页查询操作日志，支持多条件筛选。"""
    _ensure_admin(user)
    q = db.query(m.SystemLog)

    if user_id is not None:
        q = q.filter(m.SystemLog.user_id == user_id)
    if action:
        q = q.filter(m.SystemLog.action == action)
    if status:
        q = q.filter(m.SystemLog.status == status)
    if start_date:
        try:
            q = q.filter(m.SystemLog.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            raise HTTPException(400, "start_date 格式应为 YYYY-MM-DD")
    if end_date:
        try:
            q = q.filter(m.SystemLog.created_at <= datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))
        except ValueError:
            raise HTTPException(400, "end_date 格式应为 YYYY-MM-DD")
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            func.concat_ws(" ", m.SystemLog.action, m.SystemLog.detail, func.ifnull(m.SystemLog.user_id, ""))
            .like(like)
        )

    total = q.count()
    rows = q.order_by(m.SystemLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "action": r.action,
                "detail": r.detail,
                "status": r.status,
                "ip": r.ip,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/statistics")
def get_log_statistics(
    days: int = Query(7, ge=1, le=90),
    db: OrmSession = Depends(get_db),
    user: m.User = Depends(require_role("admin")),
):
    """近 N 天日志按操作 / 状态聚合统计。"""
    _ensure_admin(user)
    since = datetime.now() - timedelta(days=days)
    action_stats = (
        db.query(m.SystemLog.action, func.count(m.SystemLog.id).label("count"))
        .filter(m.SystemLog.created_at >= since)
        .group_by(m.SystemLog.action)
        .all()
    )
    status_stats = (
        db.query(m.SystemLog.status, func.count(m.SystemLog.id).label("count"))
        .filter(m.SystemLog.created_at >= since)
        .group_by(m.SystemLog.status)
        .all()
    )
    return {
        "period_days": days,
        "action_statistics": [{"action": a, "count": int(c)} for a, c in action_stats],
        "status_statistics": [{"status": s, "count": int(c)} for s, c in status_stats],
    }