"""课程管理接口（模块3）：课程 CRUD + 选课 + 课程成员（RBAC）。

权限：
- 创建课程：教师 / 管理员（创建者自动成为 owner）
- 修改 / 删除课程：管理员，或课程的 owner
- 查看课程列表：任意登录用户（管理员 / 教师 / 学生分别看到各自视角）
- 学生选课 / 退课：学生本人
- 分配角色：管理员，或课程的 owner
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session as OrmSession

from app.core.course_deps import course_role, require_course_role
from app.core.database import get_db
from app.core.deps import current_user, require_role
from app.models import models as m
from app.schemas.schemas import CourseEnrollIn, CourseIn, CourseMemberIn
from app.utils.logging import write_log

router = APIRouter(prefix="/api/courses", tags=["课程管理"])


def _serialize(c: m.Course) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "code": c.code,
        "teacher_id": c.teacher_id,
        "description": c.description,
        "created_at": c.created_at.strftime("%Y-%m-%d") if c.created_at else None,
    }


def _member_row(db: OrmSession, course_id: int, user_id: int):
    return (
        db.query(m.CourseUser)
        .filter(m.CourseUser.course_id == course_id,
                m.CourseUser.user_id == user_id)
        .first()
    )


@router.get("")
def list_courses(request: Request, db: OrmSession = Depends(get_db),
                 user: m.User = Depends(current_user)):
    """列出当前用户可见的课程，并附带用户在课程内的角色。

    学生看到已选课程（course_users/enrollments），教师看到其授课/协教课程，
    管理员看到全部课程。
    """
    if user.role == "admin":
        rows = db.query(m.Course).order_by(m.Course.id.asc()).all()
    else:
        ids = {c.course_id for c in db.query(m.CourseUser).filter(m.CourseUser.user_id == user.id).all()}
        ids.update(e.course_id for e in db.query(m.Enrollment).filter(m.Enrollment.student_id == user.id).all())
        ids.update(c.id for c in db.query(m.Course).filter(m.Course.teacher_id == user.id).all())
        rows = []
        for cid in sorted(ids):
            row = db.get(m.Course, cid)
            if row:
                rows.append(row)
    result = []
    for c in rows:
        item = _serialize(c)
        # 管理员展示角色取 "admin"，便于前端正确显示权限芯片
        item["my_role"] = "admin" if user.role == "admin" else (course_role(user.id, c.id, db) or "student")
        result.append(item)
    return result


@router.post("")
def create_course(body: CourseIn, request: Request, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_role("teacher", "admin"))):
    """创建课程。创建者自动登记为 owner（并回填 courses.teacher_id 兼容旧逻辑）。"""
    course = m.Course(name=body.name, code=body.code,
                      teacher_id=user.id, description=body.description)
    db.add(course)
    db.flush()
    member = _member_row(db, course.id, user.id)
    if not member:
        db.add(m.CourseUser(course_id=course.id, user_id=user.id, role="owner"))
    db.commit()
    db.refresh(course)
    write_log(user.id, "CREATE_COURSE", f"创建课程：{course.name}", request)
    item = _serialize(course)
    item["my_role"] = "owner"
    return item


@router.get("/{course_id}")
def get_course(course_id: int, request: Request, db: OrmSession = Depends(get_db),
               user: m.User = Depends(current_user)):
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    item = _serialize(course)
    item["my_role"] = "admin" if user.role == "admin" else (course_role(user.id, course_id, db) or "student")
    return item


@router.put("/{course_id}")
def update_course(course_id: int, body: CourseIn, request: Request,
                  db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_course_role("owner"))):
    """更新课程信息。仅管理员 / owner。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    course.name = body.name
    course.code = body.code
    course.description = body.description
    db.commit()
    db.refresh(course)
    write_log(user.id, "UPDATE_COURSE", f"更新课程：{course.name}", request)
    return _serialize(course)


@router.delete("/{course_id}")
def delete_course(course_id: int, request: Request, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_course_role("owner"))):
    """删除课程。仅管理员 / owner。关联数据因外键级联一并删除。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    name = course.name
    db.delete(course)
    db.commit()
    write_log(user.id, "DELETE_COURSE", f"删除课程：{name}", request)
    return {"msg": f"已删除课程：{name}", "id": course_id}


# ---------- 选课 / 退课 ----------
@router.post("/enroll")
def enroll_course(body: CourseEnrollIn, request: Request, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    """学生加入课程（同时登记为 student 课程成员，并写入 enrollments 兼容旧数据）。"""
    course = db.get(m.Course, body.course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    if body.undo:
        db.query(m.CourseUser).filter(
            m.CourseUser.course_id == body.course_id,
            m.CourseUser.user_id == user.id,
            m.CourseUser.role == "student",
        ).delete()
        db.query(m.Enrollment).filter(
            m.Enrollment.course_id == body.course_id,
            m.Enrollment.student_id == user.id,
        ).delete()
        db.commit()
        write_log(user.id, "UNENROLL_COURSE", f"退出课程：{course.name}", request)
        return {"msg": "已退出课程", "course_id": body.course_id}
    # 加入：登记课程成员（避开已有 owner/teacher 抢名）
    if not _member_row(db, body.course_id, user.id):
        db.add(m.CourseUser(course_id=body.course_id, user_id=user.id, role="student"))
    if not db.query(m.Enrollment).filter(
            m.Enrollment.course_id == body.course_id,
            m.Enrollment.student_id == user.id).first():
        db.add(m.Enrollment(student_id=user.id, course_id=body.course_id))
    db.commit()
    write_log(user.id, "ENROLL_COURSE", f"加入课程：{course.name}", request)
    return {"msg": "选课成功", "course_id": body.course_id}


# ---------- 课程成员（RBAC） ----------
@router.get("/{course_id}/members")
def list_members(course_id: int, db: OrmSession = Depends(get_db),
                 user: m.User = Depends(require_course_role("teacher", "assistant"))):
    """列出课程成员及其角色。管理员 / owner / 协教可查看。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    rows = db.query(m.CourseUser).filter(m.CourseUser.course_id == course_id).all()
    data = []
    for r in rows:
        u = db.get(m.User, r.user_id)
        if not u:
            continue
        data.append({"user_id": u.id, "username": u.username,
                     "real_name": u.real_name, "role": r.role})
    return data


@router.post("/{course_id}/members")
def add_member(course_id: int, body: CourseMemberIn, request: Request,
               db: OrmSession = Depends(get_db),
               user: m.User = Depends(require_course_role("owner"))):
    """为某用户在某课程内分配/调整角色。仅管理员 / owner。"""
    course = db.get(m.Course, course_id)
    if not course:
        raise HTTPException(404, "课程不存在")
    target = db.get(m.User, body.user_id)
    if not target:
        raise HTTPException(404, "用户不存在")
    if target.role == "admin":
        raise HTTPException(400, "管理员无需分配课程角色")
    existing = _member_row(db, course_id, body.user_id)
    if existing:
        if existing.role == "owner" and body.role != "owner" and user.role != "admin":
            raise HTTPException(403, "仅管理员可调整 owner 角色")
        existing.role = body.role
        if body.role == "teacher":
            if not course.teacher_id:
                course.teacher_id = target.id
            # 同步 enrollments 兼容旧答疑过滤
            db.query(m.Enrollment).filter(
                m.Enrollment.course_id == course_id,
                m.Enrollment.student_id == target.id).delete()
    else:
        db.add(m.CourseUser(course_id=course_id, user_id=target.id, role=body.role))
        if body.role == "teacher":
            if not course.teacher_id:
                course.teacher_id = target.id
    db.commit()
    write_log(user.id, "SET_COURSE_MEMBER",
              f"课程「{course.name}」角色设置：{target.real_name} → {body.role}", request)
    return {"msg": "角色已设置", "user_id": target.id, "role": body.role}


@router.delete("/{course_id}/members/{member_id}")
def remove_member(course_id: int, member_id: int, request: Request,
                  db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_course_role("owner"))):
    """移除课程成员。仅管理员 / owner。"""
    row = _member_row(db, course_id, member_id)
    if not row:
        raise HTTPException(404, "该成员不在课程内")
    if row.role == "owner" and user.role != "admin":
        raise HTTPException(403, "仅管理员可移除 owner")
    db.delete(row)
    db.query(m.Enrollment).filter(
        m.Enrollment.course_id == course_id,
        m.Enrollment.student_id == member_id).delete()
    db.commit()
    write_log(user.id, "REMOVE_COURSE_MEMBER", f"移除课程成员：{member_id}", request)
    return {"msg": "已移除", "user_id": member_id}