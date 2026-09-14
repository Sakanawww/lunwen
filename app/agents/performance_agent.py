"""学情分析 Agent：基于学生多维学习数据生成自然语言诊断与改进建议。

输入：某学生在某课程的四维平时分数据（出勤/作业/练习/答疑）及学习行为明细。
输出：LLM 生成的自然语言学情诊断报告（含优势分析、薄弱项、改进建议）。

设计要点（论文对照）：
- 这是本系统对标学习通的差异化亮点：学习通只给数字不给诊断，
  本系统用 LLM 将多维数据转化为可理解的自然语言分析；
- 复用现有 LLM 工厂与 SSE 流式架构，与答疑 Agent 的 stream 模式一致；
- 无 API Key 时回退为基于规则的模板诊断，保证演示可用。
"""
import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.services import llm

SYSTEM_PROMPT = (
    "你是一名课程助教系统的学情分析专家。教师或学生会提供一名学生的多维学习数据，"
    "请生成一段自然语言的学情诊断报告。要求：\n"
    "1. 先总体评价该学生的学习状态；\n"
    "2. 分析优势维度与薄弱维度；\n"
    "3. 给出 2-3 条具体的改进建议；\n"
    "4. 语言简练、客观、有建设性，使用中文，控制在 300 字以内。"
)


def _build_student_info(data: dict) -> str:
    """把多维数据组装成 LLM 可读的描述。"""
    name = data.get("real_name") or data.get("username") or "该学生"
    course = data.get("course_name", "本课程")
    total = data.get("total_score", 0)
    att = data.get("attendance_score", 0)
    asg = data.get("assignment_score", 0)
    pra = data.get("practice_score", 0)
    eng = data.get("engagement_score", 0)

    lines = [
        f"学生：{name}（课程：{course}）",
        f"平时分总分：{total} / 100",
        f"  - 出勤维度：{att} / 100",
        f"  - 作业维度：{asg} / 100",
        f"  - 练习维度：{pra} / 100",
        f"  - 答疑活跃度：{eng} / 100",
    ]

    # 补充明细
    detail = data.get("detail", {})
    if detail:
        lines.append(f"  出勤率：{detail.get('attendance_rate', '—')}%")
        lines.append(f"  作业提交数：{detail.get('submission_count', 0)}")
        lines.append(f"  作业平均分：{detail.get('avg_score', '—')}")
        lines.append(f"  练习次数：{detail.get('practice_count', 0)}")
        lines.append(f"  练习正确率：{detail.get('accuracy', '—')}%")
        lines.append(f"  答疑提问数：{detail.get('question_count', 0)}")
        abs_count = detail.get("absent_count", 0)
        if abs_count > 0:
            lines.append(f"  缺勤次数：{abs_count}")

    return "\n".join(lines)


def _fallback_diagnosis(data: dict) -> str:
    """无 LLM 时的规则模板诊断。"""
    name = data.get("real_name") or data.get("username") or "该学生"
    total = float(data.get("total_score", 0))
    att = float(data.get("attendance_score", 0))
    asg = float(data.get("assignment_score", 0))
    pra = float(data.get("practice_score", 0))
    eng = float(data.get("engagement_score", 0))

    # 找最强和最弱维度
    dims = [("出勤", att), ("作业", asg), ("练习", pra), ("答疑", eng)]
    dims_sorted = sorted(dims, key=lambda x: x[1], reverse=True)
    strongest = dims_sorted[0]
    weakest = dims_sorted[-1]

    lines = [f"【学情诊断报告 - {name}】"]
    if total >= 85:
        lines.append(f"总体评价：学习状态优秀，平时分 {total} 分，各维度表现均衡。")
    elif total >= 70:
        lines.append(f"总体评价：学习状态良好，平时分 {total} 分，仍有提升空间。")
    elif total >= 60:
        lines.append(f"总体评价：学习状态一般，平时分 {total} 分，需要加强。")
    else:
        lines.append(f"总体评价：学习状态欠佳，平时分 {total} 分，需重点关注。")

    lines.append(f"优势维度：{strongest[0]}（{strongest[1]}分）。")
    lines.append(f"薄弱维度：{weakest[0]}（{weakest[1]}分），建议重点加强。")

    suggestions = []
    if weakest[0] == "出勤":
        suggestions.append("请保证按时出勤，减少缺勤次数。")
    elif weakest[0] == "作业":
        suggestions.append("建议按时完成并提交作业，遇到困难及时请教老师或同学。")
    elif weakest[0] == "练习":
        suggestions.append("建议增加课后练习频率，通过反复练习巩固知识点。")
    elif weakest[0] == "答疑":
        suggestions.append("建议多利用智能答疑功能，主动提问以加深理解。")
    suggestions.append("保持优势维度的良好表现，持续进步。")
    lines.append("改进建议：" + " ".join(suggestions))

    return "\n".join(lines)


def diagnose(data: dict) -> str:
    """同步生成学情诊断报告。"""
    info = _build_student_info(data)
    try:
        model = llm.get_chat_model()
        msgs = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"请根据以下学生数据生成学情诊断报告：\n\n{info}"),
        ]
        resp = model.invoke(msgs)
        content = resp.content if hasattr(resp, "content") else str(resp)
        return content.strip() if content else _fallback_diagnosis(data)
    except Exception:
        return _fallback_diagnosis(data)


def diagnose_stream(data: dict):
    """流式输出学情诊断，逐步 yield 文本片段。

    无 LLM 时一次性回退为模板诊断。
    """
    info = _build_student_info(data)
    try:
        model = llm.get_chat_model()
        msgs = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"请根据以下学生数据生成学情诊断报告：\n\n{info}"),
        ]
        has_token = False
        for chunk in model.stream(msgs):
            token = chunk.content
            if token:
                has_token = True
                yield token
        if not has_token:
            yield _fallback_diagnosis(data)
    except Exception:
        yield _fallback_diagnosis(data)
