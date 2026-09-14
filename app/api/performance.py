"""平时表现评估 + 学情分析接口：四维平时分计算 + SSE 流式学情诊断。

平时分公式（固定权重四维）：
  total = attendance*0.3 + assignment*0.3 + practice*0.2 + engagement*0.2

权限：
- 计算与查看平时分：教师 / 管理员
- 学情诊断：教师 / 管理员（也可为学生本人）
- 学生查看自己的平时分：学生本人
"""
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session as OrmSession

from app.agents.performance_agent import diagnose_stream
from app.core.database import get_db
from app.core.course_deps import require_course_role, course_role
from app.core.deps import current_user
from app.models import models as m
from app.schemas.schemas import PerformanceDiagnoseIn

router = APIRouter(prefix="/api/performance", tags=["平时表现评估"])

# 固定权重
W_ATTENDANCE = 0.30
W_ASSIGNMENT = 0.30
W_PRACTICE = 0.20
W_ENGAGEMENT = 0.20


def _course_students(db: OrmSession, course_id: int) -> list[int]:
    ids = {r.user_id for r in db.query(m.CourseUser).filter(
        m.CourseUser.course_id == course_id, m.CourseUser.role == "student").all()}
    ids.update(r.student_id for r in db.query(m.Enrollment).filter(
        m.Enrollment.course_id == course_id).all())
    return sorted(uid for uid in ids if uid)


def _compute_attendance_score(db: OrmSession, course_id: int, student_id: int) -> float:
    """出勤维度得分：出勤率 * 100。present=1.0, late=0.8, leave=0.7, absent=0。"""
    recs = (db.query(m.AttendanceRecord)
            .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
            .filter(m.AttendanceSession.course_id == course_id,
                    m.AttendanceRecord.student_id == student_id).all())
    if not recs:
        return 0.0
    weight_map = {"present": 1.0, "late": 0.8, "leave": 0.7, "absent": 0.0}
    total_weight = sum(weight_map.get(r.status, 0) for r in recs)
    return round(total_weight / len(recs) * 100, 1)


def _compute_assignment_score(db: OrmSession, course_id: int, student_id: int) -> tuple[float, dict]:
    """作业维度得分：已完成且批改的作业比例 * 100 + 平均分加权。

    返回 (score, detail)  其中 detail 含 submission_count, avg_score
    """
    assignments = db.query(m.Assignment).filter(m.Assignment.course_id == course_id).all()
    total_assignments = len(assignments)
    if total_assignments == 0:
        return 0.0, {"submission_count": 0, "avg_score": None}
    assignment_ids = [a.id for a in assignments]
    subs = (db.query(m.Submission)
            .filter(m.Submission.assignment_id.in_(assignment_ids),
                    m.Submission.student_id == student_id).all())
    sub_count = len(subs)
    # 批改记录
    graded = (db.query(m.GradingRecord)
              .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
              .filter(m.Submission.student_id == student_id,
                      m.Submission.assignment_id.in_(assignment_ids)).all())
    avg_score = None
    if graded:
        scores = [float(g.score) for g in graded if g.score is not None]
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)
    # 得分：提交率 60% + 平均分占比 40%
    completion_rate = sub_count / total_assignments
    score_component = completion_rate * 60
    if avg_score is not None:
        score_component += (avg_score / 100) * 40
    else:
        score_component += completion_rate * 40
    return round(min(score_component, 100), 1), {
        "submission_count": sub_count,
        "avg_score": avg_score,
    }


def _compute_practice_score(db: OrmSession, course_id: int, student_id: int) -> tuple[float, dict]:
    """练习维度得分：正确率 * 100。"""
    recs = (db.query(m.LearningRecord)
            .filter(m.LearningRecord.course_id == course_id,
                    m.LearningRecord.student_id == student_id).all())
    total = len(recs)
    if total == 0:
        return 0.0, {"practice_count": 0, "accuracy": 0}
    correct = sum(1 for r in recs if r.is_correct)
    accuracy = round(correct / total * 100, 1)
    return accuracy, {"practice_count": total, "accuracy": accuracy}


def _compute_engagement_score(db: OrmSession, course_id: int, student_id: int) -> tuple[float, dict]:
    """答疑活跃度得分：基于提问数量，按对数曲线归一到 0-100。"""
    q_count = (db.query(func.count(m.Message.id))
               .join(m.Session, m.Message.session_id == m.Session.id)
               .filter(m.Session.course_id == course_id,
                       m.Session.user_id == student_id,
                       m.Message.role == "user").scalar()) or 0
    # 对数归一：0问=0, 5问≈70, 10问≈100
    import math
    score = min(100, round(math.log1p(q_count) / math.log1p(10) * 100, 1)) if q_count > 0 else 0.0
    return score, {"question_count": q_count}


def _compute_one(db: OrmSession, course_id: int, student_id: int) -> dict:
    """计算单个学生的四维平时分。"""
    att = _compute_attendance_score(db, course_id, student_id)
    asg, asg_detail = _compute_assignment_score(db, course_id, student_id)
    pra, pra_detail = _compute_practice_score(db, course_id, student_id)
    eng, eng_detail = _compute_engagement_score(db, course_id, student_id)
    total = round(att * W_ATTENDANCE + asg * W_ASSIGNMENT +
                  pra * W_PRACTICE + eng * W_ENGAGEMENT, 1)
    # 考勤明细
    recs = (db.query(m.AttendanceRecord)
            .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
            .filter(m.AttendanceSession.course_id == course_id,
                    m.AttendanceRecord.student_id == student_id).all())
    total_att = len(recs)
    absent_count = sum(1 for r in recs if r.status == "absent")
    att_rate = round((total_att - absent_count) / total_att * 100, 1) if total_att else 0
    return {
        "course_id": course_id,
        "student_id": student_id,
        "attendance_score": att,
        "assignment_score": asg,
        "practice_score": pra,
        "engagement_score": eng,
        "total_score": total,
        "detail": {
            "attendance_rate": att_rate,
            "absent_count": absent_count,
            "submission_count": asg_detail["submission_count"],
            "avg_score": asg_detail["avg_score"],
            "practice_count": pra_detail["practice_count"],
            "accuracy": pra_detail["accuracy"],
            "question_count": eng_detail["question_count"],
        },
    }


def _persist(db: OrmSession, course_id: int, student_id: int, data: dict) -> None:
    """物化写入 performance_scores 表。"""
    row = (db.query(m.PerformanceScore)
           .filter(m.PerformanceScore.course_id == course_id,
                   m.PerformanceScore.student_id == student_id).first())
    if not row:
        row = m.PerformanceScore(course_id=course_id, student_id=student_id)
        db.add(row)
    row.attendance_score = data["attendance_score"]
    row.assignment_score = data["assignment_score"]
    row.practice_score = data["practice_score"]
    row.engagement_score = data["engagement_score"]
    row.total_score = data["total_score"]


# ---------- 平时分计算 ----------
@router.post("/compute/{course_id}")
def compute_scores(course_id: int, db: OrmSession = Depends(get_db),
                   user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """计算并物化某课程全体学生的平时分。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    student_ids = _course_students(db, course_id)
    results = []
    for uid in student_ids:
        data = _compute_one(db, course_id, uid)
        _persist(db, course_id, uid, data)
        results.append(data)
    db.commit()
    return {"course_id": course_id, "course_name": course.name,
            "count": len(results), "scores": results}


@router.get("/scores/{course_id}")
def list_scores(course_id: int, db: OrmSession = Depends(get_db),
                user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """查看某课程全体学生平时分（实时计算，不依赖物化）。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    student_ids = _course_students(db, course_id)
    results = []
    for uid in student_ids:
        u = db.get(m.User, uid)
        if not u:
            continue
        stu = db.query(m.Student).filter(m.Student.user_id == uid).first()
        data = _compute_one(db, course_id, uid)
        data["real_name"] = u.real_name
        data["username"] = u.username
        data["student_no"] = stu.student_no if stu else ""
        data["class_name"] = stu.class_name if stu else ""
        results.append(data)
    # 按总分降序
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return {"course_id": course_id, "course_name": course.name, "scores": results}


@router.get("/my/{course_id}")
def my_score(course_id: int, db: OrmSession = Depends(get_db),
             user: m.User = Depends(current_user)):
    """学生查看自己的平时分。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    data = _compute_one(db, course_id, user.id)
    u = db.get(m.User, user.id)
    stu = db.query(m.Student).filter(m.Student.user_id == user.id).first()
    data["real_name"] = u.real_name if u else ""
    data["student_no"] = stu.student_no if stu else ""
    return data


# ---------- 学情诊断 Agent ----------
@router.post("/diagnose")
def diagnose(body: PerformanceDiagnoseIn, db: OrmSession = Depends(get_db),
             user: m.User = Depends(current_user)):
    """SSE 流式学情诊断（调用学情分析 Agent）。

    教师/管理员可诊断任意学生；学生只能诊断自己。
    """
    course = db.get(m.Course, body.course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    # 权限：学生只能诊断自己；教师/管理员需为该课程的教师
    if user.role == "student":
        if body.student_id != user.id:
            raise HTTPException(403, "只能查看自己的学情诊断")
    else:
        role = course_role(user.id, body.course_id, db)
        if role is None or role not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权诊断该课程学生")

    data = _compute_one(db, body.course_id, body.student_id)
    u = db.get(m.User, body.student_id)
    data["real_name"] = u.real_name if u else ""
    data["username"] = u.username if u else ""
    data["course_name"] = course.name

    def _gen():
        for token in diagnose_stream(data):
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
