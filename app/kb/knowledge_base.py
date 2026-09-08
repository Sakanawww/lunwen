"""知识库解析、切分与向量化管理（基于 FAISS + Qwen Embedding）。"""
import json
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session as OrmSession

from app.core.config import settings
from app.models.models import KnowledgeChunk, KnowledgeDoc
from app.services import llm
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


class KnowledgeBase:
    """把一个课程的知识块向量化并持久化到 FAISS，支持相似度检索。"""

    def __init__(self, course_id: int):
        self.course_id = course_id
        index_dir = settings.FAISS_INDEX_DIR / f"course_{course_id}"
        self._index_path: Path = index_dir
        self._store: FAISS | None = None
        self._load()

    # ---- 索引目录与持久化 ----
    def _load(self):
        """若已存在该课程的索引则加载，否则置空。"""
        path = settings.FAISS_INDEX_DIR / f"course_{self.course_id}"
        self._index_path = path
        try:
            if (path / "index.faiss").exists() or (path / "index.pkl").exists():
                self._store = FAISS.load_local(
                    str(path), llm.embeddings, allow_dangerous_deserialization=True
                )
        except Exception:  # 索引损坏则不加载
            self._store = None

    @property
    def store(self) -> FAISS | None:
        return self._store

    # ---- 文档切分与入库 ----
    @staticmethod
    def split_text(text: str, source: str | None = None) -> List[Document]:
        """将长文本切分为适合检索的文本块。"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", ";", "，", " "],
        )
        docs = splitter.create_documents([text], metadatas=[{"source": source or ""}])
        return docs

    def add_document(self, text: str, source: str | None = None) -> List[Document]:
        """对一段文本切块并追加到向量索引（若首次则新建并持久化）。"""
        docs = self.split_text(text, source)
        if docs:
            if self._store is None:
                self._store = FAISS.from_documents(docs, llm.embeddings)
            else:
                self._store.add_documents(docs)
            self.save()
        return docs

    def save(self):
        """持久化 FAISS 索引目录。"""
        if self._store is not None:
            self._index_path.mkdir(parents=True, exist_ok=True)
            self._store.save_local(str(self._index_path))

    # ---- 检索 ----
    def retrieve(self, query: str, k: int = 5) -> List[tuple[Document, float]]:
        """返回与 query 最相似的 k 个文本块（含相似度分值）。"""
        if self._store is None:
            return []
        docs_with_scores = self._store.similarity_search_with_score(query, k=k)
        return docs_with_scores


# ---------------------------------------------------------------------------
# 业务封装：解析上传文件 → 入库 → 落库元数据
# ---------------------------------------------------------------------------
SUPPORTED_EXTS = {".txt", ".md"}


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        for enc in ("utf-8", "gbk"):
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            parts = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(parts)
        except Exception as exc:
            raise ValueError(f"PDF 解析失败：{exc}") from exc
    raise ValueError(f"暂不支持的文件类型：{suffix}，当前支持 {sorted(SUPPORTED_EXTS)} 及 .pdf")


def ingest_file(path: Path, db: OrmSession, course_id: int, upload_by: int | None) -> dict:
    """文件入库：切块 → 向量化 → 写 knowledge_docs / knowledge_chunks。"""
    text = _read_file(path)
    docs = KnowledgeBase.split_text(text, source=path.name)

    doc_row = KnowledgeDoc(
        course_id=course_id,
        title=path.stem,
        file_name=path.name,
        chunk_num=len(docs),
        upload_by=upload_by,
    )
    db.add(doc_row)
    db.flush()  # 取得 doc_row.id

    for i, d in enumerate(docs):
        db.add(
            KnowledgeChunk(
                doc_id=doc_row.id,
                seq=i,
                content=d.page_content,
                source=d.metadata.get("source"),
            )
        )

    # 构建/更新向量索引
    kb = KnowledgeBase(course_id)
    for d in docs:
        kb.add_document(d.page_content, source=d.metadata.get("source"))

    db.commit()
    return {"doc_id": doc_row.id, "title": doc_row.title, "chunk_num": len(docs)}


def query_sources(query: str, kb: KnowledgeBase, k: int = 5) -> tuple[str, List[dict]]:
    """检索并返回（拼接后的上下文, 溯源来源列表），供答疑 Agent 使用。"""
    if kb.store is None:
        return "", []
    hits = kb.retrieve(query, k=k)
    if not hits:
        return "", []
    context_parts = []
    sources = []
    for i, (doc, score) in enumerate(hits, start=1):
        context_parts.append(f"[片段{i}] {doc.page_content}")
        sources.append({
            "source": doc.metadata.get("source", ""),
            "score": round(float(score), 4),
        })
    return "\n\n".join(context_parts), sources