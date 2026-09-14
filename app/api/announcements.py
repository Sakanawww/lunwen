"""课程公告接口：教师发布、全角色查看。

权限：
- 发布/删除公告：教师 / 管理员
- 查看公告：选课学生 + 教师 + 管理员
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.course_deps import require_course_role, course_role
from app.core.deps import current_user
from app.models import models as m
from app.schemas.schemas import AnnouncementIn
from app.utils.logging import write_log

router = APIRouter(prefix="/api/announcements", tags=["课程公告"])


def _serialize(a: m.Announcement, db: OrmSession) -> dict:
    author = db.get(m.User, a.created_by) if a.created_by else None
    return {
        "id": a.id,
        "course_id": a.course_id,
        "title": a.title,
        "content": a.content,
        "created_by": a.created_by,
        "author_name": author.real_name if author else "—",
        "created_at": a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else None,
    }


@router.get("/{course_id}")
def list_announcements(course_id: int, db: OrmSession = Depends(get_db),
                       user: m.User = Depends(require_course_role("student", "teacher", "assistant"))):
    """列出某课程的公告（按时间倒序）。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    rows = (db.query(m.Announcement)
            .filter(m.Announcement.course_id == course_id)
            .order_by(m.Announcement.created_at.desc()).all())
    return {"course_id": course_id, "course_name": course.name,
            "announcements": [_serialize(a, db) for a in rows]}


@router.post("")
def create_announcement(body: AnnouncementIn, request: Request,
                        db: OrmSession = Depends(get_db),
                        user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """发布公告。仅教师/管理员。"""
    course = db.get(m.Course, body.course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    ann = m.Announcement(course_id=body.course_id, title=body.title,
                         content=body.content, created_by=user.id)
    db.add(ann)
    db.commit()
    db.refresh(ann)
    write_log(user.id, "CREATE_ANNOUNCEMENT",
              f"发布公告：{ann.title}（课程#{body.course_id}）", request)
    return _serialize(ann, db)


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, request: Request,
                        db: OrmSession = Depends(get_db),
                        user: m.User = Depends(current_user)):
    """删除公告。仅教师/管理员，且需为该课程的教师。"""
    ann = db.get(m.Announcement, announcement_id)
    if not ann:
        raise HTTPException(404, "公告不存在")
    # 校验课程归属
    if user.role != "admin":
        role = course_role(user.id, ann.course_id, db)
        if role is None or role not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权删除该课程公告")
    title = ann.title
    db.delete(ann)
    db.commit()
    write_log(user.id, "DELETE_ANNOUNCEMENT", f"删除公告：{title}", request)
    return {"msg": "已删除", "id": announcement_id}
