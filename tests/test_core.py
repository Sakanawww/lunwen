"""核心单元测试：不依赖外部 LLM/MySQL，验证纯逻辑模块。

运行：
    .venv/Scripts/python.exe -m pytest tests/ -q
"""
import json

import pytest

from app.agents.tutor_agent import _extract_sources, format_message
from app.kb.knowledge_base import KnowledgeBase


# ---------------------------------------------------------------------------
# 答疑 Agent：参考来源解析
# ---------------------------------------------------------------------------
class TestExtractSources:
    def test_strip_source_line_and_collect(self):
        answer = (
            "栈是一种后进先出的线性表。\n"
            "参考来源：数据结构讲义.docx·片段1；笔记.docx·片段2"
        )
        clean, sources = _extract_sources(answer)
        assert "参考来源" not in clean
        assert "栈是一种" in clean
        assert sources == ["数据结构讲义.docx·片段1", "笔记.docx·片段2"]

    def test_no_source_line(self):
        clean, sources = _extract_sources("仅仅是一句回答")
        assert clean == "仅仅是一句回答"
        assert sources == []

    def test_chinese_colon_variant(self):
        clean, sources = _extract_sources("正文\n来源：课件·第3讲")
        assert sources == ["课件·第3讲"]
        assert "来源" not in clean


# ---------------------------------------------------------------------------
# 答疑 Agent：消息格式化（XSS 转义、换行分段、加粗/代码）
# ---------------------------------------------------------------------------
class TestFormatMessage:
    def test_escapes_html(self):
        out = format_message("<script>alert('x')</script>")
        assert "<script>" not in out
        assert "&lt;script&gt;" in out

    def test_bold_and_code(self):
        out = format_message("**重要**\n使用`push`操作。")
        assert "<strong>重要</strong>" in out
        assert "<code>push</code>" in out
        assert "<br>" in out


# ---------------------------------------------------------------------------
# 知识库：文本切分
# ---------------------------------------------------------------------------
class TestKnowledgeBase:
    def test_split_text(self):
        # 用足够长的多段文本，确保跨硬分隔符被切成多块
        paragraph = "哈希函数把关键字直接映射到表中地址。"
        text = "\n\n".join([paragraph * 12] * 3)
        docs = KnowledgeBase.split_text(text, source="test.md")
        assert len(docs) >= 2
        assert all(d.metadata.get("source") == "test.md" for d in docs)

    def test_mock_retrieve_without_store(self):
        # store 为空时不应返回结果（避免 None 崩溃）
        from unittest.mock import MagicMock

        kb = MagicMock()
        kb.store = None
        from app.kb.knowledge_base import query_sources

        context, sources = query_sources("任意问题", kb)
        assert context == ""
        assert sources == []


# ---------------------------------------------------------------------------
# 出题 Agent：选项解析
# ---------------------------------------------------------------------------
class TestQuestionFormat:
    def test_format_options(self):
        from app.agents.question_agent import format_options

        options = format_options("A.数组；B.链表；C.队列；D.栈")
        assert options == ["A.数组", "B.链表", "C.队列", "D.栈"]

    def test_format_options_empty(self):
        from app.agents.question_agent import format_options

        assert format_options("") == []


# ---------------------------------------------------------------------------
# 多 Agent 编排：路由
# ---------------------------------------------------------------------------
class TestOrchestrator:
    def test_route_all_agents(self):
        from app.agents.graph import router_node

        cases = [
            ("请答疑一下栈的用法", "答疑Agent"),
            ("帮我批改这段作业", "批改Agent"),
            ("生成一份测验", "出题Agent"),
        ]
        for q, expect in cases:
            state = {
                "question": q,
                "history": [],
                "messages": [],
                "intent": "",
                "result": {},
                "kb": None,
            }
            out = router_node(state)
            assert out["intent"] == expect, f"{q} 应路由到 {expect}"

    def test_route_default_tutor(self):
        from app.agents.graph import ROUTE_KEYWORDS, router_node

        state = {"question": "完全无关的句子", "intent": "", "result": {}}
        assert router_node(state)["intent"] == "答疑Agent"
        assert "答疑Agent" in ROUTE_KEYWORDS