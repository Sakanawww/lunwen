"""学情看板接口：统计与学生自测记录。"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.deps import current_user
from app.models import models as m

router = APIRouter(prefix="/api/dashboard", tags=["学情看板"])


def _is_allowed(user: m.User) -> bool:
    return user is not None and user.role in ("teacher", "admin")


@router.get("/{course_id}/students")
def course_students(course_id: int, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(current_user)):
    """某课程的选课学生明细（教师/管理员看板）。含学生个人信息与学习统计。"""
    if not _is_allowed(user):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="无权限")
    course = db.get(m.Course, course_id)
    if not course:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="课程不存在")

    # 通过 course_users(stu) + enrollments + courses.teacher_id 兼容汇总可见学生
    ids = {r.user_id for r in db.query(m.CourseUser).filter(
        m.CourseUser.course_id == course_id, m.CourseUser.role == "student").all()}
    ids.update(r.student_id for r in db.query(m.Enrollment).filter(
        m.Enrollment.course_id == course_id).all())
    ids = {uid for uid in ids if uid}

    # 每名学生的学习统计（一次性批量聚合）
    sub_stmt = (
        db.query(
            m.Submission.student_id.label("sid"),
            func.count(m.Submission.id).label("subs"),
            func.count(m.GradingRecord.id).label("graded"),
        )
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .outerjoin(m.GradingRecord, m.GradingRecord.submission_id == m.Submission.id)
        .filter(m.Assignment.course_id == course_id, m.Submission.student_id.in_(ids) if ids else False)
        .group_by(m.Submission.student_id)
        .all()
    )
    sub_map = {s.sid: s for s in sub_stmt}
    lr_stmt = (
        db.query(
            m.LearningRecord.student_id.label("sid"),
            func.count(m.LearningRecord.id).label("cnt"),
            func.sum(m.LearningRecord.is_correct).label("ok"),
        )
        .filter(m.LearningRecord.course_id == course_id,
                m.LearningRecord.student_id.in_(ids) if ids else False)
        .group_by(m.LearningRecord.student_id)
        .all()
    )
    lr_map = {s.sid: s for s in lr_stmt}
    msg_stmt = (
        db.query(m.Session.user_id.label("sid"), func.count(m.Message.id).label("cnt"))
        .join(m.Message, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id, m.Message.role == "user",
                m.Session.user_id.in_(ids) if ids else False)
        .group_by(m.Session.user_id)
        .all()
    )
    msg_map = {s.sid: s.cnt for s in msg_stmt}

    data = []
    for uid in sorted(ids):
        u = db.get(m.User, uid)
        if not u:
            continue
        stu = db.query(m.Student).filter(m.Student.user_id == uid).first()
        subs = sub_map.get(uid)
        lr = lr_map.get(uid)
        total = (lr.cnt if lr and lr.cnt else 0) or 0
        ok = (lr.ok if lr and lr.ok else 0) or 0
        data.append({
            "user_id": uid,
            "username": u.username,
            "real_name": u.real_name,
            "student_no": stu.student_no if stu else "",
            "class_name": stu.class_name if stu else "",
            "submissions": int(subs.subs) if subs and subs.subs else 0,
            "graded": int(subs.graded) if subs and subs.graded else 0,
            "practice_count": total,
            "accuracy": round(float(ok) / total,
                              3) if total else None,  # 0-1，前端转百分数
            "questions": int(msg_map.get(uid, 0)),
        })
    return {"course_id": course_id, "course_name": course.name, "students": data}


@router.get("/course/{course_id}")
def course_stats(course_id: int, db: OrmSession = Depends(get_db),
                 user: m.User = Depends(current_user)):
    """某课程总体学情统计（教师/管理员看板）。"""
    total_students = (
        db.query(func.count(m.Enrollment.id))
        .filter(m.Enrollment.course_id == course_id)
        .scalar()
    )
    submission_count = (
        db.query(func.count(m.Submission.id))
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
        .scalar()
    )
    graded_count = (
        db.query(func.count(m.GradingRecord.id))
        .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
        .scalar()
    )
    avg_score = (
        db.query(func.avg(m.GradingRecord.score))
        .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
        .scalar()
    )
    q_count = db.query(func.count(m.Question.id)).filter(
        m.Question.course_id == course_id).scalar()
    doc_count = db.query(func.count(m.KnowledgeDoc.id)).filter(
        m.KnowledgeDoc.course_id == course_id).scalar()
    chat_count = db.query(func.count(m.Message.id)).join(
        m.Session, m.Message.session_id == m.Session.id).filter(
        m.Session.course_id == course_id).scalar()

    return {
        "course_id": course_id,
        "total_students": total_students,
        "submission_count": submission_count,
        "graded_count": graded_count,
        "avg_score": round(float(avg_score), 1) if avg_score is not None else None,
        "question_count": q_count,
        "doc_count": doc_count,
        "chat_count": chat_count,
    }


def _active_students(db: OrmSession, course_id: int, days: int = 30):
    """统计近期活跃学生数（有答疑消息或作业提交）。"""
    since = datetime.now() - timedelta(days=days)
    ids = set()
    ids.update(
        r[0] for r in db.query(m.Session.user_id)
        .filter(m.Session.course_id == course_id,
                m.Session.created_at >= since).all()
        if r[0]
    )
    ids.update(
        r[0] for r in db.query(m.Submission.student_id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id,
                m.Submission.submitted_at >= since).all()
        if r[0]
    )
    return len(ids)


def _trend(db: OrmSession, course_id: int, days: int):
    """近 N 天学习趋势（作业提交 / 答疑提问 / 知识库访问）。返回按日期升序的标签与三组序列。"""
    if days <= 0:
        # 全部：取最早一条相关记录至今，最多回退 180 天
        first = db.query(func.min(m.Session.created_at)) \
            .filter(m.Session.course_id == course_id).scalar()
        first_sub = db.query(func.min(m.Submission.submitted_at)) \
            .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id) \
            .filter(m.Assignment.course_id == course_id).scalar()
        if first_sub and (not first or first_sub < first):
            first = first_sub
        base = first or datetime.now()
        days = max(1, min((datetime.now() - base).days, 180))
    since = datetime.now() - timedelta(days=days)
    start_day = since.date()
    # 日期序列（含当天）
    day_list = []
    for i in range(days + 1):
        d = start_day + timedelta(days=i)
        if d > datetime.now().date():
            break
        day_list.append(d)

    # 按天统计作业提交
    submissions = dict(
        db.query(func.date(m.Submission.submitted_at), func.count(m.Submission.id))
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id,
                m.Submission.submitted_at >= since).group_by(func.date(m.Submission.submitted_at)).all()
    )
    messages = dict(
        db.query(func.date(m.Message.created_at), func.count(m.Message.id))
        .join(m.Session, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id,
                m.Message.role == "user",
                m.Message.created_at >= since).group_by(func.date(m.Message.created_at)).all()
    )
    # 知识库访问：以答疑检索引用为近似 —— 统计引用来源非空的消息数
    kb_hits = dict(
        db.query(func.date(m.Message.created_at), func.count(m.Message.id))
        .join(m.Session, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id,
                m.Message.sources.isnot(None),
                m.Message.sources != "",
                m.Message.created_at >= since)
        .group_by(func.date(m.Message.created_at)).all()
    )
    labels = [d.strftime("%m-%d") for d in day_list]
    return {
        "labels": labels,
        "submissions": [submissions.get(d, 0) for d in day_list],
        "questions": [messages.get(d, 0) for d in day_list],
        "kb": [kb_hits.get(d, 0) for d in day_list],
    }


@router.get("/overview")
def dashboard_overview(course_id: int, range: int = 30,
                       db: OrmSession = Depends(get_db),
                       user: m.User = Depends(current_user)):
    """看板聚合数据：核心指标 + 四图表数据 + 热门问题 + 最近动态。"""
    if not _is_allowed(user):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="无权限")
    course = db.get(m.Course, course_id)
    if not course:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="课程不存在")

    stats = course_stats(course_id, db, user)
    total_students = stats["total_students"]

    # 动态指标按所选时间范围过滤（选课人数为存量，不随时间变化）
    since = datetime.now() - timedelta(days=range) if range > 0 else None
    sub_q = (
        db.query(func.count(m.Submission.id))
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
    )
    graded_q = (
        db.query(func.count(m.GradingRecord.id))
        .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
    )
    avg_q = (
        db.query(func.avg(m.GradingRecord.score))
        .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id)
    )
    chat_q = (
        db.query(func.count(m.Message.id))
        .join(m.Session, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id)
    )
    if since is not None:
        sub_q = sub_q.filter(m.Submission.submitted_at >= since)
        graded_q = graded_q.filter(m.GradingRecord.graded_at >= since)
        avg_q = avg_q.filter(m.GradingRecord.graded_at >= since)
        chat_q = chat_q.filter(m.Message.created_at >= since)
    range_submission = sub_q.scalar() or 0
    range_graded = graded_q.scalar() or 0
    range_avg = avg_q.scalar()
    range_chat = chat_q.scalar() or 0

    metrics = {
        "total_students": total_students,
        "submission_count": range_submission,
        "graded_count": range_graded,
        "avg_score": round(float(range_avg), 1) if range_avg is not None else None,
        "chat_count": range_chat,
        "active_students": _active_students(db, course_id, range),
    }

    # 作业完成情况：已完成/待提交/已逾期（全期存量）
    graded_done = (
        db.query(func.count(m.GradingRecord.id))
        .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id).scalar() or 0
    )
    total_submits = (
        db.query(func.count(m.Submission.id))
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .filter(m.Assignment.course_id == course_id).scalar() or 0
    )
    pending_submits = max(total_submits - graded_done, 0)
    expected = total_students * (1 if total_students else 0)  # 按人数近似应提交量
    overdue = max(expected - total_submits, 0)
    completion = {
        "done": total_submits or 0,
        "pending": pending_submits,
        "overdue": overdue,
        "expected": expected or max(total_submits, 1),
    }

    kb_usage = {
        "docs": stats["doc_count"] or 0,
        "chunks": (db.query(func.sum(m.KnowledgeDoc.chunk_num))
                   .filter(m.KnowledgeDoc.course_id == course_id).scalar()) or 0,
        "references": (db.query(func.count(m.Message.id))
                       .join(m.Session, m.Message.session_id == m.Session.id)
                       .filter(m.Session.course_id == course_id,
                               m.Message.sources.isnot(None),
                               m.Message.sources != "").scalar()) or 0,
        "gradings": (db.query(func.count(m.GradingRecord.id))
                     .join(m.Submission, m.GradingRecord.submission_id == m.Submission.id)
                     .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
                     .filter(m.Assignment.course_id == course_id).scalar()) or 0,
    }

    # 热门问题 TOP8：按 user 消息文本聚合
    hot_rows = (
        db.query(m.Message.content, func.count(m.Message.id))
        .join(m.Session, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id,
                m.Message.role == "user",
                m.Message.content.isnot(None),
                func.char_length(m.Message.content) > 2)
        .group_by(m.Message.content)
        .order_by(func.count(m.Message.id).desc())
        .limit(8).all()
    )
    hot_questions = [
        {"text": c[:40], "count": n} for c, n in hot_rows
    ]

    activities = _activities(db, course_id, range, limit=120)

    return {
        "course_id": course_id,
        "course_name": course.name,
        "range": range if range > 0 else 30,
        "metrics": metrics,
        "trend": _trend(db, course_id, range),
        "completion": completion,
        "kb_usage": kb_usage,
        "hot_questions": hot_questions,
        "activities": activities,
    }


@router.get("/{course_id}/hot-questions")
def hot_questions(course_id: int, kw: str = "", limit: int = 60,
                  db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    """热门问题全部列表（二级页）：按提问次数倒序，可分页；支持关键词过滤。"""
    if not _is_allowed(user):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="无权限")
    course = db.get(m.Course, course_id)
    if not course:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="课程不存在")
    q = (
        db.query(m.Message.content, func.count(m.Message.id))
        .join(m.Session, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id,
                m.Message.role == "user",
                m.Message.content.isnot(None),
                func.char_length(m.Message.content) > 2)
        .group_by(m.Message.content)
        .order_by(func.count(m.Message.id).desc())
    )
    kw = (kw or "").strip()
    if kw:
        q = q.filter(m.Message.content.contains(kw))
    rows = q.limit(limit).all()
    items = []
    for i, (content, n) in enumerate(rows, start=1):
        items.append({"rank": i, "text": content, "count": n})
    return {"course_id": course_id, "course_name": course.name,
            "kw": kw, "items": items}


def _activities(db: OrmSession, course_id: int, days: int = 30, limit: int = 60):
    """汇总最近学习动态：作业提交（含得分）+ 答疑提问。按时间倒序。"""
    rows = []
    _since = datetime.now() - timedelta(days=days) if days > 0 else None
    subs = (
        db.query(
            m.Submission.submitted_at.label("ts_t"),
            m.User.real_name,
            m.Student.student_no,
            m.Assignment.title,
            m.Submission.content,
            m.Submission.status,
            m.GradingRecord.score,
        )
        .join(m.User, m.Submission.student_id == m.User.id)
        .outerjoin(m.Student, m.Student.user_id == m.User.id)
        .join(m.Assignment, m.Submission.assignment_id == m.Assignment.id)
        .outerjoin(m.GradingRecord, m.GradingRecord.submission_id == m.Submission.id)
        .filter(m.Assignment.course_id == course_id)
    )
    if _since is not None:
        subs = subs.filter(m.Submission.submitted_at >= _since)
    for s in subs.all():
        rows.append({
            "ts": s.ts_t.strftime("%Y-%m-%d %H:%M") if s.ts_t else "",
            "student": s.real_name or "—",
            "student_no": s.student_no or "",
            "type": "作业提交",
            "content": (s.content or "")[:40],
            "status": s.status,
            "score": f"{float(s.score):.1f}" if s.score is not None else None,
        })
    msgs = (
        db.query(
            m.Message.created_at.label("ts_t"),
            m.User.real_name,
            m.Student.student_no,
            m.Message.content,
        )
        .join(m.Session, m.Message.session_id == m.Session.id)
        .join(m.User, m.Session.user_id == m.User.id)
        .outerjoin(m.Student, m.Student.user_id == m.User.id)
        .filter(m.Session.course_id == course_id, m.Message.role == "user")
    )
    if _since is not None:
        msgs = msgs.filter(m.Message.created_at >= _since)
    for mm in msgs.all():
        rows.append({
            "ts": mm.ts_t.strftime("%Y-%m-%d %H:%M") if mm.ts_t else "",
            "student": mm.real_name or "—",
            "student_no": mm.student_no or "",
            "type": "答疑提问",
            "content": (mm.content or "")[:40],
            "status": "answered",
            "score": None,
        })
    rows.sort(key=lambda r: r["ts"], reverse=True)
    return rows[:limit]


@router.get("/export")
def export_report(course_id: int, range: int = 30,
                  db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    """导出学情报告（文本/CSV）。返回可下载的 CSV 文件。"""
    from fastapi.responses import Response

    data = dashboard_overview(course_id, range, db, user)
    csv_lines = [
        "# 学情数据看板导出（课程：%s）" % data.get("course_name", ""),
        "# 导出时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "指标,数值",
        "选课人数,%s" % data["metrics"]["total_students"],
        "作业提交数,%s" % data["metrics"]["submission_count"],
        "已批改数,%s" % data["metrics"]["graded_count"],
        "平均分,%s" % (data["metrics"]["avg_score"] or 0),
        "答疑消息数,%s" % data["metrics"]["chat_count"],
        "活跃学生,%s" % data["metrics"]["active_students"],
        "",
        "时间,学生,学号,类型,内容,状态,得分",
    ]
    for a in data["activities"]:
        csv_lines.append("%s,%s,%s,%s,%s,%s,%s" % (
            a["ts"], a["student"], a["student_no"], a["type"],
            a["content"].replace(",", "，").replace("\n", " "),
            a["status"], a["score"] or "-"))
    body = "\n".join(csv_lines)
    return Response(
        body,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=dashboard_%s.csv" % datetime.now().strftime("%Y%m%d")
        },
    )