"""答疑接口：创建会话 + SSE 流式答疑（RAG + 多轮）。"""
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as OrmSession

from app.agents.orchestrator import Orchestrator
from app.agents.tutor_agent import TutorAgent
from app.core.database import get_db
from app.core.deps import current_user
from app.kb.knowledge_base import KnowledgeBase
from app.models import models as m
from app.schemas.schemas import ChatIn

router = APIRouter(prefix="/api", tags=["智能答疑"])
orchestrator = Orchestrator()


@router.get("/sessions")
def list_sessions(request: Request, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(current_user)):
    sessions = (
        db.query(m.Session)
        .filter(m.Session.user_id == user.id, m.Session.is_deleted == 0)
        .order_by(m.Session.created_at.desc())
        .all()
    )
    return [{"id": s.id, "title": s.title, "course_id": s.course_id,
             "created_at": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else None}
            for s in sessions]


@router.get("/sessions/deleted")
def list_deleted_sessions(request: Request, db: OrmSession = Depends(get_db),
                          user: m.User = Depends(current_user)):
    """回收站：当前用户已删除的会话（软删除）。"""
    sessions = (
        db.query(m.Session)
        .filter(m.Session.user_id == user.id, m.Session.is_deleted == 1)
        .order_by(m.Session.deleted_at.desc())
        .all()
    )
    return [{"id": s.id, "title": s.title, "course_id": s.course_id,
             "deleted_at": s.deleted_at.strftime("%Y-%m-%d %H:%M") if s.deleted_at else None}
            for s in sessions]


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, request: Request, permanent: int = 0,
                   db: OrmSession = Depends(get_db),
                   user: m.User = Depends(current_user)):
    """删除一个会话。默认软删除（进回收站），?permanent=1 则彻底删除。"""
    sess = db.get(m.Session, session_id)
    if not sess or sess.user_id != user.id:
        raise HTTPException(status_code=404, detail="会话不存在")
    from datetime import datetime

    from app.utils.logging import write_log

    if permanent:
        title = sess.title or f"会话#{sess.id}"
        db.delete(sess)
        db.commit()
        write_log(user.id, "DELETE_SESSION", f"彻底删除会话：{title}", request)
        return {"msg": "已彻底删除", "id": session_id}
    sess.is_deleted = 1
    sess.deleted_at = datetime.now()
    db.commit()
    write_log(user.id, "DELETE_SESSION", f"删除会话：{sess.title or ('会话#' + str(sess.id))}", request)
    return {"msg": "已移入回收站", "id": session_id}


@router.delete("/sessions")
def batch_delete_sessions(ids: str, request: Request, db: OrmSession = Depends(get_db),
                          user: m.User = Depends(current_user)):
    """批量软删除会话，?ids=1,2,3。"""
    from datetime import datetime

    id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="未指定会话")
    rows = db.query(m.Session).filter(
        m.Session.user_id == user.id, m.Session.id.in_(id_list)).all()
    for r in rows:
        r.is_deleted = 1
        r.deleted_at = datetime.now()
    db.commit()
    from app.utils.logging import write_log

    write_log(user.id, "BATCH_DELETE_SESSION", f"批量删除会话 {len(rows)} 个", request)
    return {"msg": f"已移入回收站 {len(rows)} 个"}


@router.post("/sessions/{session_id}/restore")
def restore_session(session_id: int, request: Request, db: OrmSession = Depends(get_db),
                    user: m.User = Depends(current_user)):
    """从回收站恢复会话。"""
    sess = db.get(m.Session, session_id)
    if not sess or sess.user_id != user.id:
        raise HTTPException(status_code=404, detail="会话不存在")
    sess.is_deleted = 0
    sess.deleted_at = None
    db.commit()
    return {"msg": "已恢复", "id": session_id}


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: int, db: OrmSession = Depends(get_db),
                 user: m.User = Depends(current_user)):
    sess = db.get(m.Session, session_id)
    if not sess or sess.user_id != user.id:
        raise HTTPException(status_code=404, detail="会话不存在")
    msgs = (
        db.query(m.Message)
        .filter(m.Message.session_id == session_id)
        .order_by(m.Message.id.asc())
        .all()
    )
    return [
        {"role": x.role, "content": x.content, "sources": x.sources,
         "attachment": x.attachment}
        for x in msgs
    ]


_CHAT_UPLOAD_EXTS = {"txt", "md", "markdown", "pdf", "docx", "py", "png", "jpg", "jpeg"}


@router.post("/sessions/upload")
async def upload_chat_file(
    request: Request,
    file: UploadFile = File(...),
    user: m.User = Depends(current_user),
):
    """学生/教师向答疑上传附件。文件落盘 data/uploads/chat/，返回存储的相对文件名。"""
    from app.core.config import settings

    fname = (file.filename or "").strip()
    if not fname:
        raise HTTPException(status_code=400, detail="文件名为空")
    ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
    if ext not in _CHAT_UPLOAD_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：.{ext}")
    data = file.file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件不能超过 20MB")

    import uuid

    dest_dir = settings.UPLOAD_DIR / "chat"
    dest_dir.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    (dest_dir / stored).write_bytes(data)
    return {"code": 0, "name": fname, "path": f"chat/{stored}", "size": len(data)}


@router.post("/chat/stream")
async def chat_stream(body: ChatIn, request: Request, db: OrmSession = Depends(get_db),
                      user: m.User = Depends(current_user)):
    """SSE 流式答疑。首次提问需带上 course_id + 知识库。"""
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 选定课程：未指定则默认该用户第一门选修课
    if body.course_id:
        course = db.get(m.Course, body.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        course_id = course.id
    else:
        enr = db.query(m.Enrollment).filter(m.Enrollment.student_id == user.id).first()
        course_id = enr.course_id if enr else None
    if not course_id:
        raise HTTPException(status_code=400, detail="请先在教师端上传知识库并选课")

    # 会话（若未指定则创建）
    if body.session_id:
        sess = db.get(m.Session, body.session_id)
        if not sess or sess.user_id != user.id or sess.is_deleted:
            raise HTTPException(status_code=404, detail="会话不存在")
        sess_id = int(sess.id)
    else:
        sess = m.Session(user_id=user.id, course_id=course_id, title=question[:20])
        db.add(sess)
        db.commit()
        db.refresh(sess)
        sess_id = int(sess.id)

    # 读取历史（供多轮上下文）
    history = [
        {"role": x.role, "content": x.content}
        for x in db.query(m.Message)
        .filter(m.Message.session_id == sess_id)
        .order_by(m.Message.id.asc())
        .all()
    ]

    # 路由 + 答疑 Agent
    kb = KnowledgeBase(course_id)
    agent = TutorAgent(kb, course_id)
    db.add(m.Message(session_id=sess_id, role="user", content=question,
                     attachment=body.attachment))
    db.commit()

    # 附件摘要（用于提示词上下文，不改变功能逻辑）
    if body.attachment:
        try:
            att = json.loads(body.attachment)
            question = f"{question}\n[附件：{att.get('name', '未知文件')}]"
        except Exception:
            pass

    def _gen():
        full = ""
        final_sources = []
        final_text = ""
        _sent_session_id = False
        _it = agent.stream(question, history)
        while True:
            try:
                token = next(_it)
            except StopIteration:
                break
            except Exception as _e:
                # 若 LLM 流中途抛错，回退为通用错误信息
                yield f"data: {json.dumps({'token': f'（答疑出现异常：{_e}）'}, ensure_ascii=False)}\n\n"
                break
            # 首帧：回传 session_id 供前端绑定多轮上下文
            if not _sent_session_id:
                _sent_session_id = True
                yield f"data: {json.dumps({'session_id': sess_id}, ensure_ascii=False)}\n\n"
            # 末尾元数据帧：以特殊前缀标记，避免与正文 token 冲突
            if token.startswith("__META__"):
                try:
                    meta = json.loads(token[len("__META__"):])
                    final_sources = meta.get("sources", [])
                    final_text = meta.get("text", "")
                    # 生成器会在请求结束后运行，需自行开一个会话落库
                    from app.core.database import SessionLocal as _SL
                    _write_db = _SL()
                    try:
                        _write_db.add(m.Message(session_id=sess_id, role="assistant",
                                                content=final_text or full,
                                                sources=json.dumps(final_sources, ensure_ascii=False)))
                        _write_db.commit()
                    except Exception as _db_ex:
                        _write_db.rollback()
                    finally:
                        _write_db.close()
                    yield f"data: {json.dumps({'sources': final_sources, 'text': final_text or full}, ensure_ascii=False)}\n\n"
                except Exception:
                    pass
                continue
            full += token
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )