"""Pydantic 数据模型（请求/响应结构）。"""
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------- 用户 / 认证 ----------
class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    role: str

    class Config:
        from_attributes = True


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    token: str
    user: UserOut


class RegisterIn(BaseModel):
    username: str
    password: str
    real_name: str
    role: str = Field(pattern="^(student|teacher)$")


# ---------- 会话 / 消息 ----------
class SessionOut(BaseModel):
    id: int
    course_id: Optional[int] = None
    title: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class CreateSessionIn(BaseModel):
    course_id: Optional[int] = None
    title: Optional[str] = "新会话"


class ChatIn(BaseModel):
    session_id: Optional[int] = None
    course_id: Optional[int] = None
    question: str
    attachment: Optional[str] = None  # 附件描述（JSON: 原文件名/存储路径/大小）


# ---------- 知识库 ----------
class UploadResult(BaseModel):
    doc_id: int
    title: str
    chunk_num: int


class KbStatus(BaseModel):
    msg: str


# ---------- 作业 / 批改 ----------
class GradeIn(BaseModel):
    submission_id: int


class QuestionGenIn(BaseModel):
    course_id: int
    topic: str
    num: int = Field(3, ge=1, le=10)
    difficulty: int = Field(3, ge=1, le=5)


# ---------- 课程 / 课程成员 (模块3) ----------
class CourseIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = Field(None, max_length=2000)


class CourseOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    teacher_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class CourseEnrollIn(BaseModel):
    """选课 / 移除选课（学生加入课程）。undo=True 表示退课。"""
    course_id: int
    undo: bool = False


class CourseMemberIn(BaseModel):
    """教师为学生在某课程内分配角色。"""
    user_id: int
    role: str = Field(..., pattern="^(owner|teacher|assistant|student)$")


# ---------- 作业 / 提交 ----------
class AssignmentCreateIn(BaseModel):
    course_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    deadline: Optional[str] = None


class SubmissionCreateIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=20000)