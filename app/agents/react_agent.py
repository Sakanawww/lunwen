"""ReAct 模式 Agent 编排：基于 ReAct（Reasoning + Acting）范式的智能Agent。

ReAct 模式核心：
1. Thought（思考）：分析当前状态，决定下一步行动
2. Action（行动）：调用工具执行具体任务
3. Observation（观察）：获取工具执行结果
4. 循环直到问题解决或达到最大迭代次数
"""
from typing import Any, Callable, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from app.services import llm


# ReAct 系统提示模板
REACT_SYSTEM_PROMPT = """你是一个智能助教，使用 ReAct（Reasoning + Acting）模式来解决问题。

工作流程：
1. 思考（Thought）：分析用户问题，思考需要什么信息
2. 行动（Action）：选择合适的工具来获取信息
3. 观察（Observation）：查看工具返回的结果
4. 重复以上步骤，直到能够完整回答问题

可用工具：
{tools_description}

回答格式：
Thought: [你的思考过程]
Action: [工具名称]
Action Input: {{工具参数}}
Observation: [工具返回结果]
...（重复直到得出结论）
Thought: 我现在有了足够的信息
Final Answer: [最终回答]

如果不需要使用工具，直接给出 Final Answer。"""


class ReActAgent:
    """ReAct 模式 Agent 类。"""
    
    def __init__(
        self,
        tools: list[BaseTool],
        model: Optional[ChatOpenAI] = None,
        max_iterations: int = 5,
    ):
        """初始化 ReAct Agent。
        
        Args:
            tools: 可用工具列表
            model: LLM 模型（默认使用配置中的模型）
            max_iterations: 最大迭代次数
        """
        self.tools = {tool.name: tool for tool in tools}
        self.model = model or llm.get_chat_model()
        self.max_iterations = max_iterations
        
        # 构建工具描述
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])
        self.system_prompt = REACT_SYSTEM_PROMPT.format(tools_description=tools_desc)
    
    def run(self, query: str, history: Optional[list] = None) -> str:
        """运行 ReAct 循环，返回最终答案。
        
        Args:
            query: 用户问题
            history: 历史对话记录
            
        Returns:
            最终回答
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=query),
        ]
        
        # 添加历史对话
        if history:
            for msg in history[-5:]:  # 只保留最近 5 条
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        iteration = 0
        thought_chain = []
        
        while iteration < self.max_iterations:
            # 获取模型响应
            response = self.model.invoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            
            # 检查是否包含工具调用
            if hasattr(response, "tool_calls") and response.tool_calls:
                # 处理工具调用
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})
                    
                    if tool_name in self.tools:
                        # 执行工具
                        tool = self.tools[tool_name]
                        try:
                            observation = tool.invoke(**tool_args)
                        except Exception as e:
                            observation = f"Error: {e}"
                        
                        # 添加到消息历史
                        messages.append(AIMessage(content="", tool_calls=[tool_call]))
                        messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call.get("id")))
                        
                        thought_chain.append(f"使用工具 {tool_name}: {observation}")
                    else:
                        thought_chain.append(f"未知工具：{tool_name}")
            else:
                # 没有工具调用，检查是否有最终答案
                if "Final Answer" in content or "最终答案" in content:
                    return content
                # 否则继续迭代
                messages.append(AIMessage(content=content))
            
            iteration += 1
        
        # 达到最大迭代次数，返回当前结果
        return f"达到最大迭代次数 ({self.max_iterations})。当前思考：{thought_chain[-1] if thought_chain else '无'}"


class TodoListReActAgent:
    """待办事项 ReAct Agent：使用 ReAct 模式管理待办事项。"""
    
    def __init__(self):
        from app.agents.tools.todo_list import get_todo_tool
        self.todo_tool = get_todo_tool()
    
    def run(self, query: str) -> str:
        """处理待办事项相关查询。
        
        Args:
            query: 用户查询
            
        Returns:
            处理结果
        """
        # 简单解析查询
        if "添加" in query or "创建" in query:
            # 提取待办内容
            content = query.replace("添加", "").replace("创建", "").strip()
            return self.todo_tool.add_todo(content)
        elif "完成" in query or "标记" in query:
            # 提取 ID
            import re
            match = re.search(r"#?(\d+)", query)
            if match:
                todo_id = int(match.group(1))
                return self.todo_tool.complete_todo(todo_id)
            return "请指定要完成的待办事项 ID"
        elif "删除" in query:
            import re
            match = re.search(r"#?(\d+)", query)
            if match:
                todo_id = int(match.group(1))
                return self.todo_tool.delete_todo(todo_id)
            return "请指定要删除的待办事项 ID"
        elif "列表" in query or "查看" in query:
            show_completed = "全部" in query or "所有" in query
            return self.todo_tool.list_todos(show_completed=show_completed)
        else:
            return self.todo_tool.list_todos()


class WebSearchReActAgent:
    """网络搜索 ReAct Agent：使用 ReAct 模式执行网络搜索。"""
    
    def __init__(self):
        from app.agents.tools.web_search import get_search_tool
        self.search_tool = get_search_tool()
    
    def run(self, query: str) -> str:
        """处理搜索相关查询。
        
        Args:
            query: 用户查询
            
        Returns:
            搜索结果
        """
        if "搜索" in query or "查找" in query:
            # 提取搜索关键词
            keywords = query.replace("搜索", "").replace("查找", "").strip()
            return self.search_tool.search(keywords)
        elif "历史" in query:
            return self.search_tool.get_search_history()
        else:
            return f"请明确搜索内容。示例：'搜索 Python 教程'"
