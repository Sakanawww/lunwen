"""认证相关接口：注册 / 登录 / 登出。"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session as OrmSession

from app.core import session as sstore
from app.core.database import get_db
from app.models import models as m
from app.models.models import Student, Teacher, User
from app.schemas.schemas import LoginIn, RegisterIn
from app.utils.helpers import hash_password

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
def register(body: RegisterIn, db: OrmSession = Depends(get_db)):
    """注册学生或教师账号。"""
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        real_name=body.real_name,
        role=body.role,
    )
    db.add(user)
    db.flush()
    if body.role == "student":
        db.add(Student(user_id=user.id, student_no=body.username))
    else:
        db.add(Teacher(user_id=user.id, teacher_no=body.username))
    db.commit()
    return {"msg": "注册成功"}


@router.post("/login")
def login(body: LoginIn, db: OrmSession = Depends(get_db)):
    """登录：校验后建立会话，返回 token 和用户信息。"""
    user = db.query(User).filter(User.username == body.username).first()
    if not user or user.password_hash != hash_password(body.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token_value = sstore.create_session(user.id, user.real_name, user.role)
    return {"token": token_value, "user": {"id": user.id, "username": user.username, "real_name": user.real_name, "email": "", "role": user.role}}


@router.post("/logout")
def logout(request: Request):
    """登出：清除会话并删除 Cookie。"""
    token = request.cookies.get("token") or ""
    sstore.destroy_session(token)
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("token")
    return resp