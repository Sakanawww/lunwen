"""账号管理接口：管理员对全系统用户/角色的增删查改。"""
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models import models as m
from app.models.models import Student, Teacher, User
from app.utils.helpers import hash_password

router = APIRouter(prefix="/api/accounts", tags=["账号管理"])

_ROLE_SET = {"admin", "teacher", "student"}


class AccountCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=100)
    real_name: str = Field(min_length=1, max_length=50)
    role: str = Field(pattern="^(admin|teacher|student)$")


class AccountUpdate(BaseModel):
    real_name: str | None = None
    role: str | None = Field(default=None, pattern="^(admin|teacher|student)$")
    password: str | None = Field(default=None, max_length=100)


def _get_user(db: OrmSession, user_id: int) -> User:
    user = db.get(m.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def _sync_profile(db: OrmSession, user: User, role: str):
    """保证 users/students/teachers 三表一致（换角色时同步迁移档案）。"""
    existing_student = db.query(m.Student).filter(m.Student.user_id == user.id).first()
    existing_teacher = db.query(m.Teacher).filter(m.Teacher.user_id == user.id).first()
    if role == "student":
        if existing_teacher:
            db.delete(existing_teacher)
            db.flush()
        if not existing_student:
            db.add(m.Student(user_id=user.id, student_no=user.username))
    elif role == "teacher":
        if existing_student:
            db.delete(existing_student)
            db.flush()
        if not existing_teacher:
            db.add(m.Teacher(user_id=user.id, teacher_no=user.username))


@router.get("")
@router.get("/")
def list_accounts(db: OrmSession = Depends(get_db),
                  _: m.User = Depends(require_role("admin"))):
    """列出全部账号（含角色档案信息）。"""
    users = db.query(m.User).order_by(m.User.id).all()
    students = {
        s.user_id: s for s in db.query(m.Student).all()
    }
    teachers = {
        t.user_id: t for t in db.query(m.Teacher).all()
    }
    rows = []
    for u in users:
        row = {
            "id": u.id,
            "username": u.username,
            "real_name": u.real_name,
            "role": u.role,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "",
        }
        if u.role == "student" and u.id in students:
            row["student_no"] = students[u.id].student_no
            row["class_name"] = students[u.id].class_name
        if u.role == "teacher" and u.id in teachers:
            row["teacher_no"] = teachers[u.id].teacher_no
            row["department"] = teachers[u.id].department
        rows.append(row)
    return {"accounts": rows}


@router.post("")
@router.post("/")
def create_account(body: AccountCreate, db: OrmSession = Depends(get_db),
                   _: m.User = Depends(require_role("admin"))):
    """新建账号。"""
    if db.query(m.User).filter(m.User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = m.User(username=body.username, password_hash=hash_password(body.password),
                  real_name=body.real_name, role=body.role)
    db.add(user)
    db.flush()
    _sync_profile(db, user, body.role)
    db.commit()
    return {"msg": "创建成功", "id": user.id}


@router.put("/{user_id}")
def update_account(user_id: int, body: AccountUpdate, db: OrmSession = Depends(get_db),
                   admin: m.User = Depends(require_role("admin"))):
    """编辑账号：改姓名/角色/密码。"""
    user = _get_user(db, user_id)
    if user.id == admin.id and body.role and body.role != "admin":
        raise HTTPException(status_code=400, detail="不能降级自己的管理员权限")
    if body.real_name in (None, "") or body.real_name is not None:
        if body.real_name:
            user.real_name = body.real_name
    if body.password:
        user.password_hash = hash_password(body.password)
    if body.role and body.role != user.role:
        user.role = body.role
        _sync_profile(db, user, body.role)
    db.commit()
    return {"msg": "更新成功"}


@router.delete("/{user_id}")
def delete_account(user_id: int, db: OrmSession = Depends(get_db),
                   admin: m.User = Depends(require_role("admin"))):
    """删除账号。"""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员账号")
    user = _get_user(db, user_id)
    db.delete(user)  # students/teachers/course_users/sessions 均级联删除
    db.commit()
    return {"msg": "删除成功"}