"""多 Agent 编排器：依据用户意图（关键词）路由到五个 Agent（答疑/批改/出题/考勤预警/学情分析）。"""
from typing import Literal

from app.agents import grader_agent, question_agent, tutor_agent
from app.kb.knowledge_base import KnowledgeBase

# 关键词 → Agent 名称 的路由表（与 agent_configs.route_keywords 对应，便于论文对照）
ROUTE_KEYWORDS = {
    "答疑Agent": ["答疑", "问题", "不会", "讲解", "概念", "含义", "为什么", "是什么", "什么意思"],
    "批改Agent": ["批改", "评分", "作业", "评语", "打分", "分数"],
    "出题Agent": ["出题", "试题", "测验", "题目", "组卷", "练习题"],
    "考勤预警Agent": ["缺勤", "旷课", "考勤", "出勤率", "预警", "提醒", "出勤"],
    "学情分析Agent": ["学情", "表现", "诊断", "平时分", "建议", "分析报告", "学习情况"],
}


class Orchestrator:
    """统一编排五个核心 Agent，实现「问答 → 行动」的闭环。"""

    def route(self, question: str) -> Literal["答疑Agent", "批改Agent", "出题Agent",
                                               "考勤预警Agent", "学情分析Agent"]:
        """根据问题关键词决定交由哪个 Agent 处理，默认交由答疑 Agent。"""
        for agent_name, keywords in ROUTE_KEYWORDS.items():
            for kw in keywords:
                if kw in question:
                    return agent_name
        return "答疑Agent"