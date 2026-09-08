"""批改 Agent：对学生作业进行 AI 辅助批改、评分与评语生成。"""
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.services import llm

SYSTEM_PROMPT = (
    "你是一名严谨的《数据结构》课程助教，负责批改学生作业。\n"
    "请严格按照以下 JSON 结构输出（不要输出多余文字）：\n"
    "{\"score\": 得分(0-100数字), \"feedback\": \"针对知识点的具体评语、指出错误并给出改进建议\"}\n"
)


def grade(content: str) -> dict:
    """输入学生作业内容，返回 {\"score\": int, \"feedback\": str}。"""
    msgs = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"请批改以下学生作业：\n---\n{content}\n---"),
    ]
    model = llm.chat_model()
    resp = model.invoke(msgs)
    text = resp.content if hasattr(resp, "content") else str(resp)
    # 提取 JSON
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            import json

            data = json.loads(m.group(0))
            score = int(data.get("score", 0))
            feedback = str(data.get("feedback", "（未生成评语）"))
            return {"score": score, "feedback": feedback}
        except Exception:
            pass
    return {"score": 0, "feedback": text[:500]}