"""作业接口：教师发布作业、学生提交作业、查看作业列表与详情。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as OrmSession

from app.core.course_deps import require_course_role
from app.core.database import get_db
from app.core.deps import current_user, require_role
from app.models import models as m
from app.schemas.schemas import AssignmentCreateIn, SubmissionCreateIn
from app.utils.logging import write_log

router = APIRouter(prefix="/api/assignments", tags=["作业管理"])


@router.post("")
def create_assignment(body: AssignmentCreateIn, request: Request,
                      db: OrmSession = Depends(get_db),
                      user: m.User = Depends(require_role("teacher", "admin"))):
    """教师创建作业（需为该课程的 owner / teacher / assistant 或管理员）。"""
    course = db.get(m.Course, body.course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    # 校验课程角色（管理员直通）
    if user.role != "admin":
        from app.core.course_deps import course_role
        cr = course_role(user.id, body.course_id, db)
        if cr not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权在此课程发布作业")

    deadline = None
    if body.deadline:
        try:
            deadline = datetime.fromisoformat(body.deadline)
        except ValueError:
            raise HTTPException(400, "deadline 格式无效，应为 YYYY-MM-DD 或 YYYY-MM-DDTHH:MM")

    assignment = m.Assignment(
        course_id=body.course_id,
        title=body.title,
        description=body.description,
        deadline=deadline,
    )
    db.add(assignment)
    db.flush()
    db.commit()
    db.refresh(assignment)
    write_log(user.id, "CREATE_ASSIGNMENT", f"发布作业：{assignment.title}", request)
    return _serialize_assignment(assignment)


@router.get("/course/{course_id}")
def list_assignments(course_id: int, db: OrmSession = Depends(get_db),
                     user: m.User = Depends(current_user)):
    """列出课程下的所有作业，附带当前学生的提交状态。"""
    assignments = (
        db.query(m.Assignment)
        .filter(m.Assignment.course_id == course_id)
        .order_by(m.Assignment.id.desc())
        .all()
    )
    result = []
    for a in assignments:
        item = _serialize_assignment(a)
        # 查当前用户的提交
        sub = (
            db.query(m.Submission)
            .filter(
                m.Submission.assignment_id == a.id,
                m.Submission.student_id == user.id,
            )
            .first()
        )
        item["my_submission"] = {
            "id": sub.id,
            "status": sub.status,
            "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
        } if sub else None
        # 附带批改结果（如果已批改）
        item["my_submission_score"] = None
        item["my_submission_feedback"] = None
        if sub and sub.status == "graded":
            rec = db.query(m.GradingRecord).filter(m.GradingRecord.submission_id == sub.id).first()
            if rec:
                item["my_submission_score"] = float(rec.score) if rec.score is not None else None
                item["my_submission_feedback"] = rec.feedback
        # 提交人数
        item["submission_count"] = db.query(m.Submission).filter(
            m.Submission.assignment_id == a.id
        ).count()
        result.append(item)
    return result


@router.get("/{assignment_id}")
def get_assignment(assignment_id: int, db: OrmSession = Depends(get_db),
                   user: m.User = Depends(current_user)):
    """查看作业详情（含当前用户的提交信息）。"""
    a = db.get(m.Assignment, assignment_id)
    if not a:
        raise HTTPException(404, "作业不存在")
    item = _serialize_assignment(a)
    sub = (
        db.query(m.Submission)
        .filter(
            m.Submission.assignment_id == a.id,
            m.Submission.student_id == user.id,
        )
        .first()
    )
    item["my_submission"] = {
        "id": sub.id,
        "content": sub.content,
        "status": sub.status,
        "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
    } if sub else None
    return item


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, request: Request,
                      db: OrmSession = Depends(get_db),
                      user: m.User = Depends(require_role("teacher", "admin"))):
    """删除作业（需课程 owner/teacher/assistant 或管理员）。"""
    a = db.get(m.Assignment, assignment_id)
    if not a:
        raise HTTPException(404, "作业不存在")
    if user.role != "admin":
        from app.core.course_deps import course_role
        cr = course_role(user.id, a.course_id, db)
        if cr not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权删除此作业")
    title = a.title
    db.delete(a)
    db.commit()
    write_log(user.id, "DELETE_ASSIGNMENT", f"删除作业：{title}", request)
    return {"msg": f"已删除作业：{title}", "id": assignment_id}


@router.post("/{assignment_id}/submit")
def submit_assignment(assignment_id: int, body: SubmissionCreateIn, request: Request,
                      db: OrmSession = Depends(get_db),
                      user: m.User = Depends(current_user)):
    """学生提交作业内容。重复提交则更新已有提交。"""
    a = db.get(m.Assignment, assignment_id)
    if not a:
        raise HTTPException(404, "作业不存在")

    # 检查是否已有提交 → 更新或新建
    existing = (
        db.query(m.Submission)
        .filter(
            m.Submission.assignment_id == assignment_id,
            m.Submission.student_id == user.id,
        )
        .first()
    )
    if existing:
        existing.content = body.content
        existing.status = "pending"  # 重新提交后重置批改状态
        db.commit()
        db.refresh(existing)
        write_log(user.id, "SUBMIT_ASSIGNMENT", f"更新作业提交：{a.title}", request)
        sub = existing
    else:
        sub = m.Submission(
            assignment_id=assignment_id,
            student_id=user.id,
            content=body.content,
            status="pending",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        write_log(user.id, "SUBMIT_ASSIGNMENT", f"提交作业：{a.title}", request)

    return {
        "id": sub.id,
        "assignment_id": assignment_id,
        "status": sub.status,
        "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
    }


def _serialize_assignment(a: m.Assignment) -> dict:
    return {
        "id": a.id,
        "course_id": a.course_id,
        "title": a.title,
        "description": a.description,
        "deadline": a.deadline.strftime("%Y-%m-%d %H:%M") if a.deadline else None,
        "created_at": a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else None,
    }
