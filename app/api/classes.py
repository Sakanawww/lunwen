"""班级管理接口：班级 CRUD + 班级课程关联。

权限：
- 创建/修改/删除班级：教师 / 管理员
- 查看班级列表：任意登录用户
- 关联班级与课程：课程 owner / 管理员
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as OrmSession

from app.core.course_deps import require_course_role
from app.core.database import get_db
from app.core.deps import current_user, require_role
from app.models import models as m
from app.schemas.schemas import ClassCourseIn, ClassIn
from app.utils.logging import write_log

router = APIRouter(prefix="/api/classes", tags=["班级管理"])


def _serialize(c: m.Class) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "grade": c.grade,
        "major": c.major,
        "created_at": c.created_at.strftime("%Y-%m-%d") if c.created_at else None,
    }


@router.get("")
def list_classes(db: OrmSession = Depends(get_db),
                 user: m.User = Depends(current_user)):
    """列出全部班级，附带学生人数和关联课程数。"""
    rows = db.query(m.Class).order_by(m.Class.id.asc()).all()
    result = []
    for c in rows:
        item = _serialize(c)
        item["student_count"] = (
            db.query(m.Student).filter(m.Student.class_id == c.id).count()
        )
        item["course_count"] = (
            db.query(m.ClassCourse).filter(m.ClassCourse.class_id == c.id).count()
        )
        result.append(item)
    return result


@router.post("")
def create_class(body: ClassIn, request: Request, db: OrmSession = Depends(get_db),
                 user: m.User = Depends(require_role("teacher", "admin"))):
    """创建班级。仅教师/管理员。"""
    exists = db.query(m.Class).filter(m.Class.name == body.name).first()
    if exists:
        raise HTTPException(400, "班级名称已存在")
    cls = m.Class(name=body.name, grade=body.grade, major=body.major)
    db.add(cls)
    db.commit()
    db.refresh(cls)
    write_log(user.id, "CREATE_CLASS", f"创建班级：{cls.name}", request)
    return _serialize(cls)


@router.put("/{class_id}")
def update_class(class_id: int, body: ClassIn, request: Request,
                 db: OrmSession = Depends(get_db),
                 user: m.User = Depends(require_role("teacher", "admin"))):
    cls = db.get(m.Class, class_id)
    if not cls:
        raise HTTPException(404, "班级不存在")
    cls.name = body.name
    cls.grade = body.grade
    cls.major = body.major
    db.commit()
    db.refresh(cls)
    write_log(user.id, "UPDATE_CLASS", f"更新班级：{cls.name}", request)
    return _serialize(cls)


@router.delete("/{class_id}")
def delete_class(class_id: int, request: Request, db: OrmSession = Depends(get_db),
                 user: m.User = Depends(require_role("teacher", "admin"))):
    cls = db.get(m.Class, class_id)
    if not cls:
        raise HTTPException(404, "班级不存在")
    name = cls.name
    db.delete(cls)
    db.commit()
    write_log(user.id, "DELETE_CLASS", f"删除班级：{name}", request)
    return {"msg": f"已删除班级：{name}", "id": class_id}


@router.get("/{class_id}/students")
def class_students(class_id: int, db: OrmSession = Depends(get_db),
                   user: m.User = Depends(current_user)):
    """班级花名册：该班学生列表。"""
    cls = db.get(m.Class, class_id)
    if not cls:
        raise HTTPException(404, "班级不存在")
    students = db.query(m.Student).filter(m.Student.class_id == class_id).all()
    data = []
    for s in students:
        u = db.get(m.User, s.user_id)
        if not u:
            continue
        data.append({
            "user_id": u.id, "username": u.username, "real_name": u.real_name,
            "student_no": s.student_no, "class_name": cls.name,
        })
    return {"class_id": class_id, "class_name": cls.name, "students": data}


# ---------- 班级 ↔ 课程关联 ----------
@router.post("/courses")
def link_course(body: ClassCourseIn, request: Request, db: OrmSession = Depends(get_db),
                user: m.User = Depends(require_course_role("owner"))):
    """关联班级与课程（或取消关联 undo=True）。仅课程 owner / 管理员。"""
    cls = db.get(m.Class, body.class_id)
    if not cls:
        raise HTTPException(404, "班级不存在")
    if body.undo:
        db.query(m.ClassCourse).filter(
            m.ClassCourse.class_id == body.class_id,
            m.ClassCourse.course_id == body.course_id,
        ).delete()
        db.commit()
        write_log(user.id, "UNLINK_CLASS_COURSE",
                  f"取消班级「{cls.name}」关联课程#{body.course_id}", request)
        return {"msg": "已取消关联", "class_id": body.class_id, "course_id": body.course_id}
    existing = db.query(m.ClassCourse).filter(
        m.ClassCourse.class_id == body.class_id,
        m.ClassCourse.course_id == body.course_id,
    ).first()
    if existing:
        return {"msg": "已关联过", "class_id": body.class_id, "course_id": body.course_id}
    db.add(m.ClassCourse(class_id=body.class_id, course_id=body.course_id))
    db.commit()
    write_log(user.id, "LINK_CLASS_COURSE",
              f"班级「{cls.name}」关联课程#{body.course_id}", request)
    return {"msg": "关联成功", "class_id": body.class_id, "course_id": body.course_id}


@router.get("/{class_id}/courses")
def class_courses(class_id: int, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    """班级关联的课程列表。"""
    cls = db.get(m.Class, class_id)
    if not cls:
        raise HTTPException(404, "班级不存在")
    rows = db.query(m.ClassCourse).filter(m.ClassCourse.class_id == class_id).all()
    data = []
    for r in rows:
        c = db.get(m.Course, r.course_id)
        if c:
            data.append({"id": c.id, "name": c.name, "code": c.code})
    return {"class_id": class_id, "class_name": cls.name, "courses": data}
