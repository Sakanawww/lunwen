"""作业批改接口：AI 辅助批改、评分与评语。"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as OrmSession

from app.agents.grader_agent import grade
from app.core.database import get_db
from app.core.deps import current_user, require_role
from app.models import models as m

router = APIRouter(prefix="/api/grade", tags=["作业批改"])


@router.post("/{submission_id}")
def grade_submission(submission_id: int, request: Request, db: OrmSession = Depends(get_db),
                     user: m.User = Depends(require_role("teacher", "admin"))):
    """对指定作业提交进行 AI 批改。"""
    sub = db.get(m.Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="提交不存在")

    result = grade(sub.content)
    rec = m.GradingRecord(
        submission_id=sub.id,
        score=result["score"],
        feedback=result["feedback"],
        grade_by="ai",
    )
    sub.status = "graded"
    db.add(rec)
    db.commit()
    db.refresh(rec)
    from app.utils.logging import write_log

    write_log(user.id, "GRADE_SUBMISSION", f"AI 批改作业提交#{sub.id}，得分{float(rec.score)}", request)
    return {"submission_id": sub.id,
            "score": float(rec.score),
            "feedback": rec.feedback,
            "graded_at": rec.graded_at.strftime("%Y-%m-%d %H:%M:%S") if rec.graded_at else None}


@router.get("/submissions/{course_id}")
def get_submissions(course_id: int, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(current_user)):
    """按课程列出作业提交（含批改状态）。"""
    rows = (
        db.query(m.Submission)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
        .all()
    )
    data = []
    for s in rows:
        rec = db.query(m.GradingRecord).filter(
            m.GradingRecord.submission_id == s.id
        ).first()
        student = db.get(m.User, s.student_id)
        assignment = db.get(m.Assignment, s.assignment_id)
        data.append({
            "id": s.id,
            "assignment_id": s.assignment_id,
            "assignment_title": assignment.title if assignment else "",
            "student_id": s.student_id,
            "student_name": student.real_name if student else "",
            "content": s.content,
            "status": s.status,
            "score": float(rec.score) if rec else None,
            "feedback": rec.feedback if rec else None,
        })
    return data