"""课程级 RBAC 依赖：基于 course_users 判断用户在课程内的角色。

角色等级：admin > owner > teacher > assistant > student。
- 管理员（users.role == admin）默认对任意课程有全部权限。
- 否则以 course_users 记录为准；兼容旧数据：
  - courses.teacher_id 视为 owner；
  - enrollments 视为 student。
"""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.deps import current_user
from app.models import models as m

# 角色等级：数字越小权限越高
_ROLE_RANK = {"admin": 0, "owner": 1, "teacher": 2, "assistant": 3, "student": 4}

# 旧数据兼容：courses.teacher_id 对应角色、enrollments 对应角色
_LEGACY_TEACHER = "teacher"
_LEGACY_STUDENT = "student"


def course_role(user_id: int, course_id: int, db: OrmSession) -> str | None:
    """返回用户在某课程内的角色名；无成员关系返回 None。"""
    row = (
        db.query(m.CourseUser)
        .filter(m.CourseUser.course_id == course_id,
                m.CourseUser.user_id == user_id)
        .first()
    )
    if row:
        return row.role
    course = db.get(m.Course, course_id)
    if course:
        # 兼容旧数据：teachers / enrollments
        if course.teacher_id == user_id:
            return _LEGACY_TEACHER
        enr = (
            db.query(m.Enrollment)
            .filter(m.Enrollment.course_id == course_id,
                    m.Enrollment.student_id == user_id)
            .first()
        )
        if enr:
            return _LEGACY_STUDENT
    return None


def _at_least(role: str | None, required: str) -> bool:
    if role is None:
        return False
    if role == "admin":
        return True
    if required == "admin":
        return role == "admin"
    if required not in _ROLE_RANK or role not in _ROLE_RANK:
        return False
    return _ROLE_RANK[role] <= _ROLE_RANK[required]


def require_course_role(*required: str):
    """返回一个依赖，要求当前用户至少具备指定课程角色的任一权限。

    用法：
        @router.get("/{course_id}")
        def x(course_id: int, user=Depends(require_course_role("teacher", "assistant")), db=...):
            ...
    """
    roles = required or ("student",)

    def checker(course_id: int, user: m.User = Depends(current_user),
                db: OrmSession = Depends(get_db)) -> m.User:
        if user.role == "admin":
            return user
        role = course_role(user.id, course_id, db)
        ok = any(_at_least(role, r) for r in roles)
        if not ok:
            raise HTTPException(status_code=403, detail="无权访问该课程")
        return user

    return checker