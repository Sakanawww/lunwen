"""考勤预警 Agent：对连续缺勤学生生成自然语言提醒文案。

输入：某课程下连续缺勤超过阈值的学生名单及其考勤明细。
输出：LLM 生成的自然语言预警提醒（供教师确认后入库/展示）。

设计要点（论文对照）：
- 复用现有 LLM 工厂（app.services.llm），不引入新的模型依赖；
- Prompt 注入学生姓名、缺勤次数、缺勤日期，让模型生成有针对性的提醒；
- 无 LLM 可用时（无 API Key）回退为模板文案，保证演示可用。
"""
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.services import llm

SYSTEM_PROMPT = (
    "你是一名课程助教系统的考勤预警助手。教师会提供连续缺勤学生的信息，"
    "请为每名学生生成一段简短、关切的提醒文案（中文，50字以内），"
    "语气温和但严肃，提醒学生注意出勤，并建议联系老师沟通。"
    "输出格式：每行一条，格式为「学生姓名：提醒文案」。"
)


def _fallback_warnings(students: List[dict]) -> str:
    """无 LLM 时的模板回退。"""
    lines = []
    for s in students:
        name = s.get("real_name", s.get("username", "同学"))
        count = s.get("absent_count", 0)
        lines.append(f"{name}：您已连续缺勤{count}次，请尽快联系老师说明情况并注意按时出勤。")
    return "\n".join(lines)


def generate_warnings(students: List[dict]) -> str:
    """为连续缺勤学生生成预警提醒。

    Args:
        students: [{"user_id", "real_name", "username", "absent_count",
                    "absent_dates": ["2026-09-01", ...]}, ...]

    Returns:
        多行文本，每行一条提醒。
    """
    if not students:
        return "本次无需预警的学生。"

    # 组装输入描述
    info_lines = []
    for s in students:
        name = s.get("real_name") or s.get("username") or "同学"
        count = s.get("absent_count", 0)
        dates = s.get("absent_dates", [])
        dates_str = "、".join(dates[:5])
        info_lines.append(f"- {name}：连续缺勤{count}次，缺勤日期：{dates_str}")
    info_text = "\n".join(info_lines)

    try:
        model = llm.get_chat_model()
        msgs = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"以下是需要预警的学生信息：\n{info_text}\n\n请生成提醒文案。"),
        ]
        resp = model.invoke(msgs)
        content = resp.content if hasattr(resp, "content") else str(resp)
        return content.strip() if content else _fallback_warnings(students)
    except Exception:
        return _fallback_warnings(students)


def generate_warning_stream(students: List[dict]):
    """流式输出预警提醒，逐步 yield 文本片段。

    无 LLM 时一次性回退为模板文案。
    """
    if not students:
        yield "本次无需预警的学生。"
        return

    info_lines = []
    for s in students:
        name = s.get("real_name") or s.get("username") or "同学"
        count = s.get("absent_count", 0)
        dates = s.get("absent_dates", [])
        dates_str = "、".join(dates[:5])
        info_lines.append(f"- {name}：连续缺勤{count}次，缺勤日期：{dates_str}")
    info_text = "\n".join(info_lines)

    try:
        model = llm.get_chat_model()
        msgs = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"以下是需要预警的学生信息：\n{info_text}\n\n请生成提醒文案。"),
        ]
        has_token = False
        for chunk in model.stream(msgs):
            token = chunk.content
            if token:
                has_token = True
                yield token
        if not has_token:
            yield _fallback_warnings(students)
    except Exception:
        yield _fallback_warnings(students)
