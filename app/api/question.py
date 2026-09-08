"""试题生成接口：AI 出题并保存到试题库。"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as OrmSession

from app.agents.question_agent import generate_questions
from app.core.database import get_db
from app.core.deps import current_user, require_role
from app.models import models as m
from app.schemas.schemas import QuestionGenIn

router = APIRouter(prefix="/api/question", tags=["试题生成"])


@router.post("/generate")
def gen_questions(body: QuestionGenIn, db: OrmSession = Depends(get_db),
                  user: m.User = Depends(require_role("teacher", "admin"))):
    """依据课程、知识点与难度批量生成试题并入库。"""
    course = db.get(m.Course, body.course_id)
    course_name = course.name if course else ""
    questions = generate_questions(body.topic, body.num, body.difficulty, course_name)
    saved = []
    for index, q in enumerate(questions, start=1):
        row = m.Question(
            course_id=body.course_id,
            type=q.get("type", "short"),
            stem=q.get("stem", ""),
            options=q.get("options", ""),
            answer=q.get("answer", ""),
            difficulty=int(q.get("difficulty", body.difficulty)),
            created_by=user.id,
            source="ai",
        )
        db.add(row)
        saved.append({"index": index, **q})
    db.commit()
    return {"count": len(saved), "questions": saved}


@router.get("/list/{course_id}")
def list_questions(course_id: int, db: OrmSession = Depends(get_db),
                   user: m.User = Depends(current_user)):
    qs = db.query(m.Question).filter(
        m.Question.course_id == course_id, m.Question.is_deleted == 0).all()
    return [
        {"id": q.id, "type": q.type, "stem": q.stem, "options": q.options,
         "difficulty": q.difficulty, "source": q.source}
        for q in qs
    ]


@router.get("/deleted/{course_id}")
def list_deleted_questions(course_id: int, db: OrmSession = Depends(get_db),
                           user: m.User = Depends(require_role("teacher", "admin"))):
    """回收站：指定课程已删除题目。"""
    qs = db.query(m.Question).filter(
        m.Question.course_id == course_id, m.Question.is_deleted == 1).all()
    return [
        {"id": q.id, "type": q.type, "stem": q.stem, "difficulty": q.difficulty,
         "deleted_at": q.deleted_at.strftime("%Y-%m-%d %H:%M") if q.deleted_at else None}
        for q in qs
    ]


@router.delete("/{question_id}")
def delete_question(question_id: int, request: Request, permanent: int = 0,
                    db: OrmSession = Depends(get_db),
                    user: m.User = Depends(require_role("teacher", "admin"))):
    """删除题目。默认软删除（进回收站），?permanent=1 则彻底删除。"""
    q = db.get(m.Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    from datetime import datetime

    from app.utils.logging import write_log

    if permanent:
        stem = q.stem[:30]
        db.delete(q)
        db.commit()
        write_log(user.id, "DELETE_QUESTION", f"彻底删除题目：{stem}", request)
        return {"msg": "已彻底删除", "id": question_id}
    q.is_deleted = 1
    q.deleted_at = datetime.now()
    db.commit()
    write_log(user.id, "DELETE_QUESTION", f"删除题目：{q.stem[:30]}", request)
    return {"msg": "已移入回收站", "id": question_id}


@router.post("/{question_id}/restore")
def restore_question(question_id: int, db: OrmSession = Depends(get_db),
                     user: m.User = Depends(require_role("teacher", "admin"))):
    """从回收站恢复题目。"""
    q = db.get(m.Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    q.is_deleted = 0
    q.deleted_at = None
    db.commit()
    return {"msg": "已恢复", "id": question_id}