"""知识库接口：上传文档 → 切分 → 向量化入库。"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.deps import current_user, require_role
from app.kb.knowledge_base import ingest_file
from app.models import models as m

router = APIRouter(prefix="/api/kb", tags=["知识库"])


@router.post("/upload")
async def upload(
    request: Request,
    course_id: int = Form(...),
    file: UploadFile = File(...),
    db: OrmSession = Depends(get_db),
    user: m.User = Depends(require_role("teacher", "admin")),
):
    """教师上传课程资料（txt/md/pdf），切块并向量化，写入知识库。"""
    course = db.get(m.Course, course_id)
    if not course:
        return {"msg": "课程不存在", "code": 1}

    path = _save_upload(file)
    result = ingest_file(path, db, course_id=course_id, upload_by=user.id)
    return {"msg": "上传成功", "code": 0, "data": result}


def _save_upload(file: UploadFile):
    import os

    from app.core.config import settings

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    dest = settings.UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        f.write(file.file.read())
    return dest


@router.get("/docs/{course_id}")
def list_docs(course_id: int, db: OrmSession = Depends(get_db),
              user: m.User = Depends(current_user)):
    docs = db.query(m.KnowledgeDoc).filter(m.KnowledgeDoc.course_id == course_id).all()
    return [
        {"id": d.id, "title": d.title, "chunk_num": d.chunk_num,
         "created_at": d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else None}
        for d in docs
    ]


@router.get("/doc/{doc_id}/preview")
def preview_doc(doc_id: int, db: OrmSession = Depends(get_db),
                user: m.User = Depends(current_user)):
    """预览文档内容：按知识块顺序拼接文本供前端展示。"""
    doc = db.get(m.KnowledgeDoc, doc_id)
    if not doc:
        raise HTTPException(404, "文档不存在")
    chunks = (db.query(m.KnowledgeChunk)
              .filter(m.KnowledgeChunk.doc_id == doc_id)
              .order_by(m.KnowledgeChunk.seq.asc())
              .all())
    return {
        "id": doc.id,
        "title": doc.title,
        "file_name": doc.file_name,
        "chunk_num": doc.chunk_num,
        "created_at": doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else None,
        "chunks": [{"seq": c.seq, "content": c.content} for c in chunks],
    }