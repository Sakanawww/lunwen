"""答疑 Agent：基于 RAG 课程知识库的多轮智能答疑，带溯源引用。"""
import html
import json
import re
from typing import List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.kb.knowledge_base import query_sources
from app.services import llm

SYSTEM_PROMPT = (
    "你是一名严谨的《数据结构》课程助教。请根据下方【参考资料】回答问题。\n"
    "要求：\n"
    "1. 当【参考资料】能覆盖答案时，优先依据参考资料作答；\n"
    "2. 回答末尾另起一行输出「参考来源」，格式例：参考来源：数据结构讲义.docx·片段3；\n"
    "3. 当参考答案不足以回答时，用你自己的知识补充，并在首行注明「(参考资料有限，以下为补充解释)」；\n"
    "4. 作答清晰、分点、结合例子，使用简练的中文。\n"
)


def _build_prompt(context: str) -> list:
    """根据检索上下文组装消息，无检索结果时仍可回答。"""
    msgs: list = [SystemMessage(content=SYSTEM_PROMPT)]
    if context:
        msgs.append(HumanMessage(content=f"【参考资料】\n{context}"))
    return msgs


def _extract_sources(answer: str) -> tuple[str, List[str]]:
    """从回答中剥离「参考来源」行并返回澄清后的正文与来源列表。"""
    lines = answer.splitlines()
    source_lines = [ln for ln in lines if ln.strip().startswith(("参考来源", "来源", "参考"))]
    if source_lines:
        answer = "\n".join(
            ln for ln in lines if not ln.strip().startswith(("参考来源", "来源", "参考"))
        ).strip()
    sources = []
    for sl in source_lines:
        # 形如：参考来源：文档A·片段3；文档B·片段2
        content = re.sub(r"^(参考来源|来源|参考)\s*[:：]\s*", "", sl.strip())
        for part in content.split("；"):
            part = part.strip()
            if part:
                sources.append(part)
    return answer, sources


def format_message(html_text: str) -> str:
    """将模型输出的文本转换为可在页面安全展示的 HTML。"""
    if not html_text:
        return ""
    cleaned = html.escape(html_text)
    # 以换行分段、空行为段，简单转换行、加粗(*xxx*)等
    cleaned = cleaned.replace("\n", "<br>")
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", cleaned)
    cleaned = re.sub(r"`(.+?)`", r"<code>\1</code>", cleaned)
    return cleaned


class TutorAgent:
    """答疑 Agent：封装「检索 → 组装 → 调用 LLM(stram) → 溯源」链路。"""

    def __init__(self, kb, course_id: int):
        self.kb = kb
        self.course_id = course_id

    def answer(self, question: str, history: List[dict] | None = None) -> str:
        context, _ = query_sources(question, self.kb, k=5)
        msgs = _build_prompt(context)
        # 多轮会话历史（仅保留最近 N 条，作为上下文补充）
        msgs.extend(_to_role_messages(history or []))
        msgs.append(HumanMessage(content=question))
        model = llm.get_chat_model()
        resp = model.invoke(msgs)
        content = resp.content if hasattr(resp, "content") else str(resp)
        return content

    def answer_with_sources(self, question: str, history: List[dict] | None = None):
        """返回 (正文, 来源列表)。供 LangGraph 答疑节点使用。"""
        answer = self.answer(question, history)
        clean, src_list = _extract_sources(answer)
        return clean, src_list

    def stream(self, question: str, history: List[dict] | None = None):
        """流式输出，逐步 yield 文本片段，结束时 yield JSON 溯源信息。"""
        context, sources = query_sources(question, self.kb, k=5)
        msgs = _build_prompt(context)
        # 多轮会话历史（仅保留最近 N 条，作为上下文补充）
        msgs.extend(_to_role_messages(history or []))
        msgs.append(HumanMessage(content=question))
        model = llm.get_chat_model()
        full = []
        for chunk in model.stream(msgs):
            token = chunk.content
            if token:
                full.append(token)
                yield token
        answer = "".join(full)
        # 剥离「参考来源」行，得到最终正文与溯源列表
        clean, src_list = _extract_sources(answer)
        # 用不可出现在正文中的前缀标记最终 JSON，便于前端与 SSE 切分识别
        yield "__META__" + json.dumps(
            {"text": clean, "sources": src_list or sources}, ensure_ascii=False
        )


def _to_role_messages(history: List[dict]) -> List[HumanMessage | SystemMessage]:
    """把历史消息转为 LangChain 消息对象（演示仅取最近 8 条）。"""
    out: list = []
    for m in history[-8:]:
        role = m.get("role")
        content = m.get("content")
        if not content:
            continue
        out.append(HumanMessage(content=f"{role}: {content}", ) if role == "user"
                   else SystemMessage(content=content))
    return out