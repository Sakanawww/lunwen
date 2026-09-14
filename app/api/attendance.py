"""考勤管理接口：考勤课次 CRUD + 学生签到 + 出勤率统计 + 考勤预警 Agent。

权限：
- 发起/关闭考勤课次：教师 / 管理员
- 修正签到状态：教师 / 管理员
- 学生签到：学生本人
- 查看考勤数据：教师 / 管理员
- 生成预警：教师 / 管理员（调用考勤预警 Agent）
"""
import json
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session as OrmSession

from app.agents.attendance_agent import generate_warning_stream
from app.core.database import get_db
from app.core.course_deps import require_course_role, course_role
from app.core.deps import current_user, require_role
from app.models import models as m
from app.schemas.schemas import AttendanceSessionCreateIn, AttendanceSignIn, AttendanceUpdateIn
from app.utils.logging import write_log

router = APIRouter(prefix="/api/attendance", tags=["考勤管理"])


def _is_teacher(user: m.User) -> bool:
    return user is not None and user.role in ("teacher", "admin")


def _course_students(db: OrmSession, course_id: int) -> list[int]:
    """获取课程选课学生 user_id 列表。"""
    ids = {r.user_id for r in db.query(m.CourseUser).filter(
        m.CourseUser.course_id == course_id, m.CourseUser.role == "student").all()}
    ids.update(r.student_id for r in db.query(m.Enrollment).filter(
        m.Enrollment.course_id == course_id).all())
    return sorted(uid for uid in ids if uid)


# ---------- 考勤课次 ----------
@router.get("/sessions/{course_id}")
def list_sessions(course_id: int, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_course_role("student", "teacher", "assistant"))):
    """列出某课程的全部考勤课次，附带签到率。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    rows = (db.query(m.AttendanceSession)
            .filter(m.AttendanceSession.course_id == course_id)
            .order_by(m.AttendanceSession.session_date.desc())
            .all())
    total_students = len(_course_students(db, course_id))
    data = []
    for s in rows:
        records = (db.query(m.AttendanceRecord)
                   .filter(m.AttendanceRecord.session_id == s.id).all())
        present = sum(1 for r in records if r.status in ("present", "late"))
        rate = round(present / len(records) * 100, 1) if records else 0
        data.append({
            "id": s.id,
            "course_id": s.course_id,
            "session_date": s.session_date.strftime("%Y-%m-%d") if s.session_date else None,
            "status": s.status,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else None,
            "signed_count": len(records),
            "present_count": present,
            "total_students": total_students,
            "attendance_rate": rate,
        })
    return {"course_id": course_id, "course_name": course.name, "sessions": data}


@router.post("/sessions")
def create_session(body: AttendanceSessionCreateIn, request: Request,
                   db: OrmSession = Depends(get_db),
                   user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """发起一次考勤课次：自动为所有选课学生创建 absent 记录。"""
    course = db.get(m.Course, body.course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    if body.session_date:
        try:
            sess_date = datetime.strptime(body.session_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(400, "日期格式应为 YYYY-MM-DD")
    else:
        sess_date = date.today()

    sess = m.AttendanceSession(course_id=body.course_id, session_date=sess_date,
                               status="open", created_by=user.id)
    db.add(sess)
    db.flush()

    # 为全部选课学生初始化 absent 记录
    student_ids = _course_students(db, body.course_id)
    for sid in student_ids:
        db.add(m.AttendanceRecord(session_id=sess.id, student_id=sid, status="absent"))

    db.commit()
    db.refresh(sess)
    write_log(user.id, "CREATE_ATTENDANCE",
              f"发起考勤：{course.name} {sess_date}", request)
    return {"id": sess.id, "course_id": sess.course_id,
            "session_date": sess.session_date.strftime("%Y-%m-%d"),
            "status": sess.status, "total_records": len(student_ids)}


@router.put("/sessions/{session_id}/close")
def close_session(session_id: int, request: Request, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    """关闭考勤课次（停止签到）。"""
    sess = db.get(m.AttendanceSession, session_id)
    if not sess:
        raise HTTPException(404, "考勤课次不存在")
    # 校验课程归属
    if user.role != "admin":
        role = course_role(user.id, sess.course_id, db)
        if role is None or role not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权操作该课程考勤")
    sess.status = "closed"
    db.commit()
    write_log(user.id, "CLOSE_ATTENDANCE", f"关闭考勤课次#{session_id}", request)
    return {"msg": "已关闭", "id": session_id, "status": "closed"}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, request: Request, db: OrmSession = Depends(get_db),
                   user: m.User = Depends(current_user)):
    """删除考勤课次（连带签到明细）。"""
    sess = db.get(m.AttendanceSession, session_id)
    if not sess:
        raise HTTPException(404, "考勤课次不存在")
    # 校验课程归属
    if user.role != "admin":
        role = course_role(user.id, sess.course_id, db)
        if role is None or role not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权删除该课程考勤")
    db.delete(sess)
    db.commit()
    write_log(user.id, "DELETE_ATTENDANCE", f"删除考勤课次#{session_id}", request)
    return {"msg": "已删除", "id": session_id}


# ---------- 签到 / 修正 ----------
@router.post("/sign")
def sign_in(body: AttendanceSignIn, request: Request, db: OrmSession = Depends(get_db),
            user: m.User = Depends(current_user)):
    """学生签到：更新自己的签到记录。"""
    sess = db.get(m.AttendanceSession, body.session_id)
    if not sess:
        raise HTTPException(404, "考勤课次不存在")
    if sess.status == "closed":
        raise HTTPException(400, "考勤已关闭")
    # 校验选课归属
    if user.role != "admin":
        role = course_role(user.id, sess.course_id, db)
        if role is None:
            raise HTTPException(403, "未选课，无法签到")
    record = (db.query(m.AttendanceRecord)
              .filter(m.AttendanceRecord.session_id == body.session_id,
                      m.AttendanceRecord.student_id == user.id).first())
    if not record:
        # 若教师未预创建记录，学生签到时自动建一条
        record = m.AttendanceRecord(session_id=body.session_id, student_id=user.id)
        db.add(record)
    record.status = body.status
    record.signed_at = datetime.now()
    db.commit()
    write_log(user.id, "ATTENDANCE_SIGN",
              f"签到：状态={body.status}", request)
    return {"msg": "签到成功", "status": body.status}


@router.put("/records")
def update_record(body: AttendanceUpdateIn, request: Request, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    """教师修正某条签到记录的状态。"""
    record = db.get(m.AttendanceRecord, body.record_id)
    if not record:
        raise HTTPException(404, "签到记录不存在")
    # 校验课程归属
    sess = db.get(m.AttendanceSession, record.session_id)
    if sess and user.role != "admin":
        role = course_role(user.id, sess.course_id, db)
        if role is None or role not in ("owner", "teacher", "assistant"):
            raise HTTPException(403, "无权修改该课程考勤记录")
    record.status = body.status
    db.commit()
    write_log(user.id, "UPDATE_ATTENDANCE_RECORD",
              f"修正签到记录#{body.record_id} → {body.status}", request)
    return {"msg": "已修正", "record_id": body.record_id, "status": body.status}


# ---------- 考勤明细与统计 ----------
@router.get("/sessions/{session_id}/records")
def session_records(session_id: int, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(current_user)):
    """某次考勤课次的全部签到明细。"""
    sess = db.get(m.AttendanceSession, session_id)
    if not sess:
        raise HTTPException(404, "考勤课次不存在")
    # 校验课程归属
    if user.role != "admin":
        role = course_role(user.id, sess.course_id, db)
        if role is None:
            raise HTTPException(403, "无权查看该课程考勤")
    records = (db.query(m.AttendanceRecord)
               .filter(m.AttendanceRecord.session_id == session_id)
               .order_by(m.AttendanceRecord.student_id.asc()).all())
    data = []
    for r in records:
        u = db.get(m.User, r.student_id)
        stu = db.query(m.Student).filter(m.Student.user_id == r.student_id).first()
        data.append({
            "record_id": r.id,
            "student_id": r.student_id,
            "real_name": u.real_name if u else "—",
            "student_no": stu.student_no if stu else "",
            "status": r.status,
            "signed_at": r.signed_at.strftime("%Y-%m-%d %H:%M") if r.signed_at else None,
        })
    return {"session_id": session_id,
            "session_date": sess.session_date.strftime("%Y-%m-%d") if sess.session_date else None,
            "status": sess.status, "records": data}


@router.get("/stats/{course_id}")
def attendance_stats(course_id: int, db: OrmSession = Depends(get_db),
                     user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """某课程考勤统计：总体出勤率 + 每名学生出勤明细 + 缺勤榜。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")

    sessions = (db.query(m.AttendanceSession)
                .filter(m.AttendanceSession.course_id == course_id)
                .order_by(m.AttendanceSession.session_date.asc()).all())

    # 总体统计
    total_records = (db.query(func.count(m.AttendanceRecord.id))
                     .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
                     .filter(m.AttendanceSession.course_id == course_id).scalar()) or 0
    present_records = (db.query(func.count(m.AttendanceRecord.id))
                       .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
                       .filter(m.AttendanceSession.course_id == course_id,
                               m.AttendanceRecord.status.in_(("present", "late"))).scalar()) or 0
    overall_rate = round(present_records / total_records * 100, 1) if total_records else 0

    # 按日期出勤率趋势
    trend = []
    for s in sessions:
        recs = db.query(m.AttendanceRecord).filter(m.AttendanceRecord.session_id == s.id).all()
        present = sum(1 for r in recs if r.status in ("present", "late"))
        rate = round(present / len(recs) * 100, 1) if recs else 0
        trend.append({"date": s.session_date.strftime("%Y-%m-%d") if s.session_date else "",
                      "rate": rate, "session_id": s.id})

    # 每名学生的出勤统计
    student_ids = _course_students(db, course_id)
    student_stats = []
    for uid in student_ids:
        u = db.get(m.User, uid)
        if not u:
            continue
        stu = db.query(m.Student).filter(m.Student.user_id == uid).first()
        recs = (db.query(m.AttendanceRecord)
                .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
                .filter(m.AttendanceSession.course_id == course_id,
                        m.AttendanceRecord.student_id == uid).all())
        total = len(recs)
        present = sum(1 for r in recs if r.status == "present")
        late = sum(1 for r in recs if r.status == "late")
        leave = sum(1 for r in recs if r.status == "leave")
        absent = sum(1 for r in recs if r.status == "absent")
        rate = round((present + late) / total * 100, 1) if total else 0
        student_stats.append({
            "user_id": uid,
            "real_name": u.real_name,
            "student_no": stu.student_no if stu else "",
            "class_name": stu.class_name if stu else "",
            "total": total, "present": present, "late": late,
            "leave": leave, "absent": absent,
            "attendance_rate": rate,
        })
    # 按出勤率升序（缺勤多的在前）
    student_stats.sort(key=lambda x: x["attendance_rate"])

    return {
        "course_id": course_id,
        "course_name": course.name,
        "session_count": len(sessions),
        "total_records": total_records,
        "present_records": present_records,
        "overall_rate": overall_rate,
        "trend": trend,
        "students": student_stats,
    }


# ---------- 考勤预警 Agent ----------
@router.get("/warnings/{course_id}")
def attendance_warnings(course_id: int, threshold: int = 3,
                        db: OrmSession = Depends(get_db),
                        user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """识别连续缺勤 ≥ threshold 次的学生（供教师查看后再生成预警文案）。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    student_ids = _course_students(db, course_id)
    warnings = []
    for uid in student_ids:
        u = db.get(m.User, uid)
        if not u:
            continue
        # 取该学生本课程全部考勤，按日期排序
        recs = (db.query(m.AttendanceRecord, m.AttendanceSession.session_date)
                .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
                .filter(m.AttendanceSession.course_id == course_id,
                        m.AttendanceRecord.student_id == uid)
                .order_by(m.AttendanceSession.session_date.desc()).all())
        absent_dates = [sd.strftime("%Y-%m-%d") for r, sd in recs
                        if r.status == "absent"]
        absent_count = len(absent_dates)
        if absent_count >= threshold:
            warnings.append({
                "user_id": uid,
                "real_name": u.real_name,
                "username": u.username,
                "absent_count": absent_count,
                "absent_dates": absent_dates,
            })
    return {"course_id": course_id, "course_name": course.name,
            "threshold": threshold, "count": len(warnings), "students": warnings}


@router.post("/warnings/{course_id}/generate")
def generate_warnings_api(course_id: int, request: Request, threshold: int = 3,
                          db: OrmSession = Depends(get_db),
                          user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """SSE 流式生成考勤预警文案（调用考勤预警 Agent）。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    student_ids = _course_students(db, course_id)
    students = []
    for uid in student_ids:
        u = db.get(m.User, uid)
        if not u:
            continue
        recs = (db.query(m.AttendanceRecord, m.AttendanceSession.session_date)
                .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
                .filter(m.AttendanceSession.course_id == course_id,
                        m.AttendanceRecord.student_id == uid)
                .order_by(m.AttendanceSession.session_date.desc()).all())
        absent_dates = [sd.strftime("%Y-%m-%d") for r, sd in recs
                        if r.status == "absent"]
        if len(absent_dates) >= threshold:
            students.append({
                "user_id": uid,
                "real_name": u.real_name,
                "username": u.username,
                "absent_count": len(absent_dates),
                "absent_dates": absent_dates,
            })

    def _gen():
        for token in generate_warning_stream(students):
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- 学生端：我的考勤 ----------
@router.get("/my/{course_id}")
def my_attendance(course_id: int, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_course_role("student", "teacher", "assistant"))):
    """学生查看自己在某课程的考勤记录。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    recs = (db.query(m.AttendanceRecord, m.AttendanceSession)
            .join(m.AttendanceSession, m.AttendanceRecord.session_id == m.AttendanceSession.id)
            .filter(m.AttendanceSession.course_id == course_id,
                    m.AttendanceRecord.student_id == user.id)
            .order_by(m.AttendanceSession.session_date.desc()).all())
    records = []
    for r, s in recs:
        records.append({
            "session_id": s.id,
            "session_date": s.session_date.strftime("%Y-%m-%d") if s.session_date else "",
            "status": s.status,
            "my_status": r.status,
            "signed_at": r.signed_at.strftime("%Y-%m-%d %H:%M") if r.signed_at else None,
        })
    # 统计
    total = len(records)
    present = sum(1 for r in records if r["my_status"] == "present")
    late = sum(1 for r in records if r["my_status"] == "late")
    absent = sum(1 for r in records if r["my_status"] == "absent")
    leave = sum(1 for r in records if r["my_status"] == "leave")
    rate = round((present + late) / total * 100, 1) if total else 0
    # 找当前进行中的考勤课次
    open_session = None
    for r in records:
        if r["status"] == "open":
            open_session = {"session_id": r["session_id"], "session_date": r["session_date"]}
            break
    return {
        "course_id": course_id,
        "course_name": course.name,
        "total": total, "present": present, "late": late, "absent": absent, "leave": leave,
        "attendance_rate": rate,
        "open_session": open_session,
        "records": records,
    }
