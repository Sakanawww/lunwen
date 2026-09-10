"""FastAPI 应用入口：注册路由与 API 接口。

注意：前端已完全迁移到 Vue 3 SPA，后端仅提供 REST API，
不再渲染 HTML 模板。所有页面路由由 Vue Router 处理。
"""
import json
import logging
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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

# 注册接口路由（全部为 REST API）
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


# ---- 用户注入模板上下文（已废弃，仅保留向后兼容）----
def _ctx(request: Request):
    """已废弃：前端已迁移到 Vue，不再使用模板上下文。"""
    user = None
    token = request.cookies.get("token") or ""
    sess = sstore.get_session(token)
    if sess:
        user = {"id": sess["user_id"], "real_name": sess["real_name"], "role": sess["role"]}
    return {"request": request, "user": user, "current_user_id": sess["user_id"] if sess else None}


def _require(db: OrmSession, user: dict, *roles: str):
    """已废弃：前端已迁移到 Vue，不再使用模板权限检查。"""
    if not user or user["role"] not in roles:
        return None
    return True


# ============================================================================
# 以下路由已废弃，前端已完全迁移到 Vue 3 SPA
# 所有页面路由由 Vue Router 处理，后端仅提供 REST API
# ============================================================================

@app.get("/")
def index():
    """根路径：返回 API 信息。
    
    前端已迁移到 Vue 3 SPA，请访问 /api/docs 查看 API 文档。
    """
    return {
        "name": "课程助教系统 API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "note": "前端已迁移到 Vue 3 SPA，所有页面由前端路由处理"
    }


@app.get("/auth/logout")
def logout(request: Request):
    """登出：清除会话并删除 Cookie。"""
    token = request.cookies.get("token") or ""
    sstore.destroy_session(token)
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("token")
    return resp


# ============================================================================
# 已废弃的路由（保留用于向后兼容，返回 410 Gone 或重定向到前端）
# ============================================================================

@app.get("/login")
@app.get("/register")
@app.get("/dashboard")
@app.get("/chat")
@app.get("/courses")
@app.get("/kb")
@app.get("/grading")
@app.get("/questions")
@app.get("/practice")
@app.get("/admin")
@app.get("/logs")
def deprecated_routes():
    """这些路由已废弃，前端已迁移到 Vue 3 SPA。
    
    所有页面请求应由前端开发服务器（Vite）处理，
    或通过 API 端点 (/api/*) 访问后端服务。
    """
    return {
        "error": "Route deprecated",
        "message": "前端已迁移到 Vue 3 SPA，请通过前端开发服务器访问",
        "frontend": "http://localhost:5173",
        "api_docs": "/docs"
    }
