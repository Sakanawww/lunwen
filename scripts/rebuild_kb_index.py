"""从数据库中已有的文本块重建各课程的 FAISS 向量索引。

适用场景：
- 首次部署时只导入了文本块（未配置 QWEN_API_KEY），之后配置好 Key 用于生成索引；
- 索引文件损坏或与数据库不一致时重建。

用法：.venv/Scripts/python.exe scripts/rebuild_kb_index.py [course_id]
不带参数则重建全部课程的索引。需要 .env 中配置 QWEN_API_KEY。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import models as m
from app.kb.knowledge_base import KnowledgeBase


def rebuild(db, course_id: int) -> str:
    chunks = (
        db.query(m.KnowledgeChunk)
        .join(m.KnowledgeDoc, m.KnowledgeChunk.doc_id == m.KnowledgeDoc.id)
        .filter(m.KnowledgeDoc.course_id == course_id)
        .order_by(m.KnowledgeChunk.doc_id, m.KnowledgeChunk.seq)
        .all()
    )
    if not chunks:
        return f"课程 {course_id}：无文本块，跳过"
    kb = KnowledgeBase(course_id)
    kb.rebuild_from_chunks(chunks)
    return f"课程 {course_id}：已用 {len(chunks)} 个文本块重建向量索引"


def main() -> None:
    target = int(sys.argv[1]) if len(sys.argv) > 1 else None
    db = SessionLocal()
    try:
        if target is not None:
            course_ids = [target]
        else:
            course_ids = [r[0] for r in db.query(m.Course.id).all()]
        for cid in course_ids:
            print(rebuild(db, cid))
    finally:
        db.close()


if __name__ == "__main__":
    main()
