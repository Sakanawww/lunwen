"""基于 LangGraph 的多 Agent 编排图：将答疑/批改/出题三个 Agent 纳入有状态工作流。

设计要点（与论文架构对应）：
1. 状态定义（State）—— 用 LangGraph 的 TypedDict 描述流程共享的数据；
2. 节点（Node）—— 每个 Agent 是一个图节点；tool 节点用于把 Agent 请求的
   Function Calling 工具调用真正执行；
3. 条件边（Conditional Edge）—— 依据路由结果决定进入哪个 Agent 节点；
4. 工具调用（Function Calling）—— 答疑/出题 Agent 通过 bind_tools 声明工具，
   由大模型自主决定是否调用，tool 节点负责执行并把结果回填到消息历史。
"""
from typing import Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph

from app.services import llm


# ---------------------------------------------------------------------------
# 1. 状态定义
# ---------------------------------------------------------------------------
class AgentState(TypedDict, total=False):
    question: str
    history: list
    messages: list          # LangChain 消息历史（含 tool 往返）
    intent: str             # 路由结果
    result: dict
    kb: object              # 知识库句柄（RAG 上下文注入）


# ---------------------------------------------------------------------------
# 2. 业务工具（Function Calling 的可调用函数）
# 演示：答疑 Agent 可申请"据给定关键词扩展例题"，出题 Agent 可申请"调整题目数量"。
# ---------------------------------------------------------------------------
@tool
def example_generator(topic: str, count: int = 1) -> str:
    """为某个知识点生成 count 个进阶练习示例，供答疑时补充讲解。"""
    return f"（工具调用：为「{topic}」生成 {count} 个进阶练习示例）"


@tool
def question_adjuster(current_num: int, delta: int) -> str:
    """让出题 Agent 在生成前调整题目数量：current_num 为当前数量，delta 为增量。"""
    new_num = max(1, current_num + delta)
    return f"(工具调用：题目数量由 {current_num} 调整为 {new_num})"


TOOLS = [example_generator, question_adjuster]


# ---------------------------------------------------------------------------
# 3. 路由
# ---------------------------------------------------------------------------
ROUTE_KEYWORDS = {
    "答疑Agent": ["答疑", "问题", "不会", "讲解", "概念", "含义", "为什么", "是什么", "什么意思"],
    "批改Agent": ["批改", "评分", "作业", "评语", "打分", "分数"],
    "出题Agent": ["出题", "试题", "测验", "题目", "组卷", "练习题"],
}


def router_node(state: AgentState) -> AgentState:
    """路由节点：根据关键词把请求送到对应 Agent 节点。"""
    question = state["question"]
    intent = "答疑Agent"
    for agent_name, keywords in ROUTE_KEYWORDS.items():
        for kw in keywords:
            if kw in question:
                intent = agent_name
                break
        if intent != "答疑Agent":
            break
    return {**state, "intent": intent, "result": {}}


# ---------------------------------------------------------------------------
# 4. Agent 节点
# ---------------------------------------------------------------------------
def tutor_node(state: AgentState) -> AgentState:
    """答疑 Agent 节点：RAG 上下文由外部注入，这里演示工具调用闭环。"""
    from app.agents.tutor_agent import TutorAgent

    kb = state.get("kb")
    history = state.get("history") or []
    msgs = state.get("messages") or []
    agent = TutorAgent(kb, state.get("course_id"))
    answer, sources = agent.answer_with_sources(state["question"], history)
    return {**state, "result": {"text": answer, "sources": sources}}


def retrieval_tool_node(state: AgentState) -> AgentState:
    """答疑工具节点：把答疑请求中的"检索"封装为一次工具调用执行，
    演示 Function Calling 的"模型决策→执行→回填"闭环。"""
    from app.kb.knowledge_base import query_sources as _retrieve

    question = state["question"]
    kb = state.get("kb")
    context, sources = _retrieve(question, kb, k=5)
    messages = list(state.get("messages") or [])
    # 模拟模型发出的一次工具调用：检索知识库
    tool_name = "retrieve_knowledge"
    messages.append(
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": tool_name,
                    "args": {"query": question},
                    "id": "call_retrieve_1",
                }
            ],
        )
    )
    messages.append(ToolMessage(content=context or "（无可检索内容）", tool_call_id="call_retrieve_1"))
    return {**state, "messages": messages, "retrieved": {"sources": sources, "context": context}}


def grader_node(state: AgentState) -> AgentState:
    """批改 Agent 节点。"""
    from app.agents.grader_agent import grade

    return {**state, "result": grade(state["question"])}


def question_node(state: AgentState) -> AgentState:
    """出题 Agent 节点。"""
    from app.agents.question_agent import generate_questions

    return {**state, "result": {"questions": generate_questions(state["question"], 3, 3)}}


# ---------------------------------------------------------------------------
# 5. 条件边
# ---------------------------------------------------------------------------
def route_by_intent(state: AgentState) -> Literal["答疑Agent", "批改Agent", "出题Agent"]:
    return state["intent"]


# ---------------------------------------------------------------------------
# 6. 组装并编译图（模块级单例）
# ---------------------------------------------------------------------------
_builder = StateGraph(AgentState)

_builder.add_node("router", router_node)
_builder.add_node("答疑Agent", tutor_node)
_builder.add_node("批改Agent", grader_node)
_builder.add_node("出题Agent", question_node)
_builder.add_node("retrieval_tool", retrieval_tool_node)

_builder.set_entry_point("router")
_builder.add_conditional_edges(
    "router",
    route_by_intent,
    {
        "答疑Agent": "答疑Agent",
        "批改Agent": "批改Agent",
        "出题Agent": "出题Agent",
    },
)
_builder.add_edge("答疑Agent", "retrieval_tool")
_builder.add_edge("retrieval_tool", END)
_builder.add_edge("批改Agent", END)
_builder.add_edge("出题Agent", END)

graph = _builder.compile()