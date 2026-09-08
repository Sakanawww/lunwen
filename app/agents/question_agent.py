"""出题 Agent：依据知识点、课程与难度批量生成试题。"""
import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.services import llm

SYSTEM_PROMPT = (
    "你是一名课程出题专家。请根据所选课程、指定数量、难度、覆盖给定知识点生成试题。\n"
    "题目内容必须严格贴合该门课程的知识范围，不要套用到其它课程；若知识点与该课程无关，"
    "也要尽量围绕该课程的相关章节来出题。\n"
    "请严格以 JSON 数组输出（数组内每个元素为一题，不要输出多余文字），结构如下：\n"
    "[{\"type\": \"choice|fill|short\", \"stem\": \"题干\", "
    "\"options\": \"选择题选项如 A.xxx；B.xxx；C.xxx；D.xxx（非选择题为空）\", "
    "\"answer\": \"参考答案\", \"difficulty\": 1-5}]\n"
)


def generate_questions(topic: str, num: int = 3, difficulty: int = 3,
                       course_name: str = "") -> list[dict]:
    """按知识点与课程生成试题，返回试题 dict 列表。"""
    msgs = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"课程：{course_name or '（未指定）'}。\n"
                f"请生成 {num} 道关于「{topic}」的该课程试题，"
                f"难度{int(difficulty)}级（1-5）。各题型尽量搭配。"
            )
        ),
    ]
    model = llm.chat_model()
    resp = model.invoke(msgs)
    text = resp.content if hasattr(resp, "content") else str(resp)
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except Exception:
        return []


def format_options(options: str) -> list[str]:
    """把选项字符串拆成可展示的列表（选择题）。"""
    if not options:
        return []
    return [o.strip() for o in re.split(r"[；;\n]", options) if o.strip()]