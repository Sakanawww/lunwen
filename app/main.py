"""FastAPI 应用入口：注册路由与 API 接口。"""
import json
import logging
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session as OrmSession

from app.api import accounts, agents, auth, chat, courses, dashboard, grading, knowledge, logs, practice, question
from app.core import session as sstore
from app.core.config import settings
from app.core.course_deps import course_role
from app.core.database import get_db
from app.core.security import security_headers_middleware
from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.kb.knowledge_base import ingest_file
from app.models import models as m

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="基于 Agent 的课程助教系统", version="0.1.0")

# 注册中间件 - CORS 必须在最前面
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册中间件 - 安全头在 CORS 之后执行
app.middleware("http")(security_headers_middleware)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 静态目录：前端样式 / 脚本 / 图片统一放 app/static，通过 /static 访问
_STATIC_DIR = Path(__file__).parent / "static"
_STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")

# 注册接口路由
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(grading.router)
app.include_router(question.router)
app.include_router(dashboard.router)
app.include_router(logs.router)
app.include_router(practice.router)
app.include_router(agents.router)
app.include_router(courses.router)
app.include_router(accounts.router)


# ---- 用户注入模板上下文 ----
def _ctx(request: Request):
    user = None
    token = request.cookies.get("token") or ""
    sess = sstore.get_session(token)
    if sess:
        user = {"id": sess["user_id"], "real_name": sess["real_name"], "role": sess["role"]}
    return {"request": request, "user": user, "current_user_id": sess["user_id"] if sess else None}


def _require(db: OrmSession, user: dict, *roles: str):
    if not user or user["role"] not in roles:
        return None
    return True


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if _ctx(request)["user"]:
        return RedirectResponse("/dashboard")
    # 直接跳转到 Vue 前端登录页
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page_redirect(request: Request):
    """登录页重定向到 Vue 前端"""
    return RedirectResponse("/", status_code=303)


@app.get("/register", response_class=HTMLResponse)
def register_page_redirect(request: Request):
    """注册页重定向到 Vue 前端"""
    return RedirectResponse("/register", status_code=303)


@app.post("/register", response_class=HTMLResponse)
def register_page_post_redirect(request: Request):
    """注册 POST 重定向到 Vue 前端"""
    return RedirectResponse("/register", status_code=303)


@app.get("/auth/logout")
def logout_page(request: Request):
    token = request.cookies.get("token") or ""
    sstore.destroy_session(token)
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("token")
    return resp


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, course_id: int | None = None,
                   db: OrmSession = Depends(get_db)):
    """Dashboard 页面已迁移到 Vue 前端，直接重定向"""
    return RedirectResponse("/dashboard", status_code=303)


def _visible_courses(db: OrmSession, user_id: int):
    """教师/助教可见的课程：course_users 中的 owner/teacher/assistant，
    以及 courses.teacher_id 指向该用户的课程（旧数据兼容）。"""
    ids = {c.course_id for c in db.query(m.CourseUser).filter(m.CourseUser.user_id == user_id).all()}
    ids |= {c.id for c in db.query(m.Course).filter(m.Course.teacher_id == user_id).all()}
    rows = []
    for cid in sorted(ids):
        row = db.get(m.Course, cid)
        if row:
            rows.append(row)
    return rows


# 以下页面已迁移到 Vue 前端，保留路由用于向后兼容，重定向到 Vue 前端
@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request, db: OrmSession = Depends(get_db)):
    """Chat 页面已迁移到 Vue 前端"""
    return RedirectResponse("/chat", status_code=303)


@app.get("/courses", response_class=HTMLResponse)
def courses_page(request: Request, db: OrmSession = Depends(get_db)):
    """Courses 页面已迁移到 Vue 前端"""
    return RedirectResponse("/courses", status_code=303)


@app.get("/chat/deleted", response_class=HTMLResponse)
def chat_deleted_page(request: Request, db: OrmSession = Depends(get_db)):
    """Chat Deleted 页面已迁移到 Vue 前端"""
    return RedirectResponse("/chat/deleted", status_code=303)


@app.get("/kb", response_class=HTMLResponse)
def kb_page(request: Request, course_id: int | None = None, db: OrmSession = Depends(get_db)):
    """Knowledge Base 页面已迁移到 Vue 前端"""
    return RedirectResponse("/knowledge", status_code=303)


@app.post("/kb/upload")
async def kb_upload(request: Request, course_id: int = Form(...),
                    file: UploadFile = File(...), db: OrmSession = Depends(get_db)):
    """知识库上传已迁移到 Vue 前端"""
    return RedirectResponse("/knowledge", status_code=303)


@app.get("/grading", response_class=HTMLResponse)
def grading_page(request: Request, course_id: int | None = None,
                 db: OrmSession = Depends(get_db)):
    """Grading 页面已迁移到 Vue 前端"""
    return RedirectResponse("/grading", status_code=303)


@app.get("/questions", response_class=HTMLResponse)
def questions_page(request: Request, course_id: int | None = None,
                   db: OrmSession = Depends(get_db)):
    """Questions 页面已迁移到 Vue 前端"""
    return RedirectResponse("/questions", status_code=303)


@app.get("/dashboard/hot-questions", response_class=HTMLResponse)
def dashboard_hot_questions_page(request: Request, course_id: int | None = None,
                                 db: OrmSession = Depends(get_db)):
    """热门问题页面已迁移到 Vue 前端"""
    return RedirectResponse("/dashboard/hot-questions", status_code=303)


@app.get("/dashboard/students", response_class=HTMLResponse)
def dashboard_students_page(request: Request, course_id: int | None = None,
                            db: OrmSession = Depends(get_db)):
    """学生名单页面已迁移到 Vue 前端"""
    return RedirectResponse("/dashboard/students", status_code=303)


@app.get("/questions/recycle", response_class=HTMLResponse)
def questions_recycle_page(request: Request, course_id: int | None = None,
                           db: OrmSession = Depends(get_db)):
    """试题回收站页面已迁移到 Vue 前端"""
    return RedirectResponse("/questions/recycle", status_code=303)


@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request, db: OrmSession = Depends(get_db)):
    """Logs 页面已迁移到 Vue 前端"""
    return RedirectResponse("/admin", status_code=303)


@app.get("/agents", response_class=HTMLResponse)
def agents_page(request: Request, db: OrmSession = Depends(get_db)):
    """Agents 配置页面已迁移到 Vue 前端"""
    return RedirectResponse("/admin", status_code=303)


@app.post("/questions/generate")
async def questions_gen(request: Request, course_id: int = Form(...),
                        topic: str = Form(...), num: int = Form(3),
                        difficulty: int = Form(3), db: OrmSession = Depends(get_db)):
    """试题生成 API - 保留用于向后兼容"""
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    # RBAC：仅课程 owner/teacher/assistant 可出题
    role = course_role(user["id"], course_id, db)
    if user["role"] == "admin":
        role = "admin"
    if role not in ("admin", "owner", "teacher", "assistant"):
        return RedirectResponse("/dashboard", status_code=303)
    course = db.get(m.Course, course_id)
    from app.agents.question_agent import generate_questions
    from app.utils.logging import write_log

    qs = generate_questions(topic, num, difficulty, course_name=course.name if course else "")
    for q in qs:
        db.add(m.Question(course_id=course_id, type=q.get("type", "short"),
                          stem=q.get("stem", ""), options=q.get("options", ""),
                          answer=q.get("answer", ""),
                          difficulty=q.get("difficulty", 3), source="ai"))
    db.commit()
    write_log(user["id"], "GEN_QUESTION", f"AI 生成 {len(qs)} 道试题：{topic}", request)
    return RedirectResponse(f"/questions?course_id={course_id}", status_code=303)


@app.get("/practice", response_class=HTMLResponse)
def practice_page(request: Request, db: OrmSession = Depends(get_db)):
    """Practice 页面已迁移到 Vue 前端"""
    return RedirectResponse("/practice", status_code=303)
