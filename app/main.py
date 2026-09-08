"""FastAPI 应用入口：注册路由、模板与页面渲染。"""
import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as OrmSession

from app.api import accounts, agents, auth, chat, courses, dashboard, grading, knowledge, logs, practice, question
from app.core import session as sstore
from app.core.config import settings
from app.core.course_deps import course_role
from app.core.database import get_db
from app.kb.knowledge_base import ingest_file
from app.models import models as m

app = FastAPI(title="基于 Agent 的课程助教系统", version="0.1.0")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
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
    return templates.TemplateResponse("login.html", _ctx(request))


@app.post("/login")
def login_page(request: Request, username: str = Form(...), password: str = Form(...),
               db: OrmSession = Depends(get_db)):
    from app.utils.helpers import hash_password

    user = db.query(m.User).filter(m.User.username == username).first()
    if not user or user.password_hash != hash_password(password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "username": username, "error": "用户名或密码错误", "user": None},
        )
    token = sstore.create_session(user.id, user.real_name, user.role)
    from app.utils.logging import write_log

    write_log(user.id, "LOGIN", f"用户登录：{user.username}（{user.role}）", request)
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie("token", token, httponly=True, max_age=28800)
    return resp


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", _ctx(request))


@app.post("/register")
def register_page_post(request: Request, username: str = Form(...), real_name: str = Form(...),
                       password: str = Form(...), role: str = Form(...),
                       db: OrmSession = Depends(get_db)):
    from app.utils.helpers import hash_password

    if db.query(m.User).filter(m.User.username == username).first():
        return templates.TemplateResponse("register.html",
                                          {**_ctx(request), "error": "用户名已存在"})
    user = m.User(username=username, password_hash=hash_password(password),
                  real_name=real_name, role=role)
    db.add(user)
    db.flush()
    if role == "student":
        db.add(m.Student(user_id=user.id, student_no=username))
    elif role == "teacher":
        db.add(m.Teacher(user_id=user.id, teacher_no=username))
    db.commit()
    return templates.TemplateResponse("login.html", {**_ctx(request), "msg": "注册成功，请登录"})


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
    ctx = _ctx(request)
    user = ctx["user"]
    if not user:
        return RedirectResponse("/", status_code=303)
    if user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/chat", status_code=303)

    # 课程范围：管理员看全部，教师看其 owner/teacher/assistant 的课程
    if user["role"] == "admin":
        courses = db.query(m.Course).all()
    else:
        courses = _visible_courses(db, user["id"])
    active_course = course_id or (courses[0].id if courses else None)

    if user["role"] == "admin":
        agents = db.query(m.AgentConfig).order_by(m.AgentConfig.sort_order).all()
        logs = db.query(m.SystemLog).order_by(m.SystemLog.id.desc()).limit(20).all()
        account_count = db.query(m.User).count()
        return templates.TemplateResponse(
            "admin.html", {**ctx, "agents": agents, "logs": logs, "courses": courses,
                           "account_count": account_count})

    stats = dashboard.course_stats(active_course, db, user)
    return templates.TemplateResponse(
        "dashboard.html",
        {**ctx, "courses": courses, "active_course": active_course, "stats": stats})


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


@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request, db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] != "student":
        return RedirectResponse("/dashboard", status_code=303)
    courses = db.query(m.Enrollment).filter(m.Enrollment.student_id == user["id"]).all()
    course_ids = [e.course_id for e in courses]
    course_rows = [db.get(m.Course, cid) for cid in course_ids if cid]
    sessions = (db.query(m.Session).filter(m.Session.user_id == user["id"])
                .order_by(m.Session.created_at.desc()).all())
    active_course = course_rows[0].id if course_rows else None
    return templates.TemplateResponse(
        "chat.html", {**ctx, "courses": course_rows, "sessions": sessions, "active_course": active_course})


@app.get("/courses", response_class=HTMLResponse)
def courses_page(request: Request, db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("courses.html", ctx)


@app.get("/chat/deleted", response_class=HTMLResponse)
def chat_deleted_page(request: Request, db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] != "student":
        return RedirectResponse("/dashboard", status_code=303)
    sessions = (db.query(m.Session).filter(m.Session.user_id == user["id"],
                                           m.Session.is_deleted == 1)
                .order_by(m.Session.deleted_at.desc()).all())
    return templates.TemplateResponse("chat_deleted.html", {**ctx, "sessions": sessions})


@app.get("/kb", response_class=HTMLResponse)
def kb_page(request: Request, course_id: int | None = None, db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    active = course_id or (courses[0].id if courses else None)
    docs = db.query(m.KnowledgeDoc).filter(m.KnowledgeDoc.course_id == active).all() if active else []
    return templates.TemplateResponse(
        "kb.html", {**ctx, "courses": courses, "docs": docs, "active_course": active})


@app.post("/kb/upload")
async def kb_upload(request: Request, course_id: int = Form(...),
                    file: UploadFile = File(...), db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    # RBAC：仅课程 owner/teacher/assistant 可上传
    role = course_role(user["id"], course_id, db)
    if user["role"] == "admin":
        role = "admin"
    if role not in ("admin", "owner", "teacher", "assistant"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    try:
        dest = settings.UPLOAD_DIR / file.filename
        with dest.open("wb") as f:
            f.write(await file.read())
        result = ingest_file(dest, db, course_id=course_id, upload_by=user["id"])
        docs = db.query(m.KnowledgeDoc).filter(m.KnowledgeDoc.course_id == course_id).all()
        msg = f"上传成功：{result['title']}，切分为 {result['chunk_num']} 个知识块已向量化。"
        from app.utils.logging import write_log

        write_log(user["id"], "UPLOAD_KB", f"上传知识库文档：{result['title']} ({result['chunk_num']}块)", request)
        return templates.TemplateResponse(
            "kb.html", {**ctx, "courses": courses, "docs": docs, "msg": msg})
    except Exception as exc:
        return templates.TemplateResponse(
            "kb.html", {**ctx, "courses": courses, "err": str(exc)})


@app.get("/grading", response_class=HTMLResponse)
def grading_page(request: Request, course_id: int | None = None,
                 db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    active = course_id or (courses[0].id if courses else None)
    subs = grading.get_submissions(active, db, user)
    return templates.TemplateResponse(
        "grading.html", {**ctx, "courses": courses, "active_course": active, "subs": subs})


@app.get("/questions", response_class=HTMLResponse)
def questions_page(request: Request, course_id: int | None = None,
                   db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    active = course_id or (courses[0].id if courses else None)
    qs = (db.query(m.Question)
          .filter(m.Question.course_id == active, m.Question.is_deleted == 0)
          .order_by(m.Question.id.desc()).limit(50).all()) if active else []
    return templates.TemplateResponse(
        "questions.html", {**ctx, "courses": courses, "questions": qs, "active_course": active})


@app.get("/dashboard/hot-questions", response_class=HTMLResponse)
def dashboard_hot_questions_page(request: Request, course_id: int | None = None,
                                 db: OrmSession = Depends(get_db)):
    """热门问题二级页：查看指定课程的全部提问（按次数倒序）。"""
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    active = course_id or (courses[0].id if courses else None)
    return templates.TemplateResponse(
        "dashboard_hot_questions.html",
        {**ctx, "courses": courses, "active_course": active})


@app.get("/dashboard/students", response_class=HTMLResponse)
def dashboard_students_page(request: Request, course_id: int | None = None,
                            db: OrmSession = Depends(get_db)):
    """选课学生二级页：查看指定课程的全部学生明细。"""
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    active = course_id or (courses[0].id if courses else None)
    return templates.TemplateResponse(
        "dashboard_students.html",
        {**ctx, "courses": courses, "active_course": active})


@app.get("/questions/recycle", response_class=HTMLResponse)
def questions_recycle_page(request: Request, course_id: int | None = None,
                           db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] not in ("teacher", "admin"):
        return RedirectResponse("/dashboard", status_code=303)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    active = course_id or (courses[0].id if courses else None)
    qs = (db.query(m.Question).filter(m.Question.course_id == active,
                                      m.Question.is_deleted == 1)
          .order_by(m.Question.id.desc()).all()) if active else []
    return templates.TemplateResponse(
        "recycle_bin.html", {**ctx, "courses": courses, "questions": qs, "active_course": active})


@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request, db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("logs.html", ctx)


@app.get("/agents", response_class=HTMLResponse)
def agents_page(request: Request, db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user or user["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("agent_settings.html", ctx)




@app.post("/questions/generate")
async def questions_gen(request: Request, course_id: int = Form(...),
                        topic: str = Form(...), num: int = Form(3),
                        difficulty: int = Form(3), db: OrmSession = Depends(get_db)):
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
                          difficulty=int(q.get("difficulty", difficulty)),
                          created_by=user["id"], source="ai"))
    db.commit()
    write_log(user["id"], "CREATE_QUESTION", f"AI 生成试题：{topic}({len(qs)}题, 难度{difficulty})", request)
    courses = _visible_courses(db, user["id"]) if user["role"] != "admin" else db.query(m.Course).all()
    all_qs = db.query(m.Question).filter(m.Question.course_id == course_id).order_by(m.Question.id.desc()).limit(50).all()
    return templates.TemplateResponse(
        "questions.html", {**ctx, "courses": courses, "questions": all_qs,
                           "msg": f"已生成 {len(qs)} 道试题"})


@app.get("/practice", response_class=HTMLResponse)
def practice_page(request: Request, course_id: int | None = None,
                  db: OrmSession = Depends(get_db)):
    ctx = _ctx(request)
    user = ctx["user"]
    if not user:
        return RedirectResponse("/", status_code=303)
    if user["role"] == "student":
        # 学生：可答题的课程 = 其 course_users / enrollments 中的课程
        allowed = {cu.course_id for cu in db.query(m.CourseUser).filter(m.CourseUser.user_id == user["id"]).all()}
        allowed |= {e.course_id for e in db.query(m.Enrollment).filter(m.Enrollment.student_id == user["id"]).all()}
    else:
        allowed = [c.id for c in _visible_courses(db, user["id"])]
    courses = db.query(m.Course).all()
    course_list = [c for c in courses if c.id in allowed]
    active = course_id or (course_list[0].id if course_list else None)
    questions = (db.query(m.Question).filter(m.Question.course_id == active)
                 .order_by(m.Question.id.asc()).all()) if active else []

    from app.agents.question_agent import format_options

    questions_json = json.dumps([
        {
            "id": q.id,
            "type": q.type,
            "stem": q.stem,
            "difficulty": q.difficulty,
            "options": format_options(q.options),
        }
        for q in questions
    ], ensure_ascii=False)
    return templates.TemplateResponse(
        "practice.html",
        {**ctx, "courses": course_list, "questions": questions,
         "active_course": active, "questions_json": questions_json})


@app.get("/health")
def health():
    return {"status": "ok", "system": "course-ta"}