"""答题接口：学生自测答题、客观题即时判题、查看我的答题记录。"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.deps import current_user
from app.models import models as m

router = APIRouter(prefix="/api/practice", tags=["答题练习"])


class SubmitIn(BaseModel):
    question_id: int
    answer: str


def _judge(question: m.Question, answer: str) -> dict:
    """客观题判题：选择题对比选项 key（A/B/C/D），填空/简答题对比参考答案。"""
    ans = (answer or "").strip()
    qa = (question.answer or "").strip()
    if question.type == "choice":
        # 选择题：作答为单个选项字母
        correct = (ans.upper() == qa.upper()[:1]) and len(ans.upper()) == 1
        return {"correct": correct, "expected": qa, "is_key": True}
    # 填空/简答：精确/包含宽松匹配
    if not qa:
        return {"correct": False, "expected": "（未提供参考答案）", "is_key": True}
    correct = ans == qa or (len(ans) > 1 and qa in ans)
    return {"correct": correct, "expected": qa, "is_key": False}


@router.post("/submit")
def submit(body: SubmitIn, request: Request, db: OrmSession = Depends(get_db),
           user: m.User = Depends(current_user)):
    """提交一题答案并判题，写入学情记录。"""
    q = db.get(m.Question, body.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    verdict = _judge(q, body.answer)
    db.add(m.LearningRecord(
        student_id=user.id,
        course_id=q.course_id,
        question_id=q.id,
        is_correct=1 if verdict["correct"] else 0,
        score=100 if verdict["correct"] else 0,
    ))
    db.commit()
    from app.utils.logging import write_log

    write_log(user.id, "SUBMIT_ANSWER", f"自测答题：题目#{q.id} {'答对' if verdict['correct'] else '答错'}", request)
    return {"correct": verdict["correct"], "expected": verdict["expected"], "mechanism": verdict["is_key"]}


@router.get("/my")
def my_records(db: OrmSession = Depends(get_db),
               user: m.User = Depends(current_user)):
    """我的答题记录（近 50 条，含题目与对错）。"""
    rows = (
        db.query(m.LearningRecord)
        .filter(m.LearningRecord.student_id == user.id)
        .order_by(m.LearningRecord.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "question_id": r.question_id,
            "course_id": r.course_id,
            "is_correct": bool(r.is_correct),
            "score": float(r.score) if r.score is not None else None,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
        }
        for r in rows
    ]