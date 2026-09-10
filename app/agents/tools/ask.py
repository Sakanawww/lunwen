"""Ask 工具：向用户提问以获取更多信息。"""
from typing import Optional


class AskTool:
    """Ask 工具类：向用户提问以获取澄清或额外信息。"""
    
    def __init__(self):
        self._pending_questions: list[dict] = []
        self._answers: dict[int, str] = {}
    
    def ask(self, question: str, context: Optional[str] = None) -> str:
        """向用户提问。
        
        Args:
            question: 要问的问题
            context: 问题上下文（可选）
            
        Returns:
            提示消息，表示正在等待用户回答
        """
        question_id = len(self._pending_questions) + 1
        self._pending_questions.append({
            "id": question_id,
            "question": question,
            "context": context,
            "answered": False
        })
        return f"[提问 #{question_id}] {question}"
    
    def submit_answer(self, question_id: int, answer: str) -> str:
        """提交对某个问题的回答。
        
        Args:
            question_id: 问题 ID
            answer: 用户的回答
            
        Returns:
            确认消息
        """
        for q in self._pending_questions:
            if q["id"] == question_id:
                q["answered"] = True
                self._answers[question_id] = answer
                return f"已记录对问题 #{question_id} 的回答"
        return f"未找到问题 #{question_id}"
    
    def get_pending_questions(self) -> str:
        """获取所有待回答的问题。
        
        Returns:
            待回答问题列表
        """
        pending = [q for q in self._pending_questions if not q["answered"]]
        if not pending:
            return "暂无待回答的问题"
        
        lines = ["待回答的问题："]
        for q in pending:
            lines.append(f"  #{q['id']}: {q['question']}")
        return "\n".join(lines)
    
    def get_answer(self, question_id: int) -> Optional[str]:
        """获取某个问题的回答。
        
        Args:
            question_id: 问题 ID
            
        Returns:
            用户的回答，若未回答则返回 None
        """
        return self._answers.get(question_id)
    
    def clear_answers(self):
        """清空所有回答记录。"""
        self._answers.clear()
        for q in self._pending_questions:
            q["answered"] = False


# 全局单例
_ask_tool: Optional[AskTool] = None


def get_ask_tool() -> AskTool:
    """获取 Ask 工具单例。"""
    global _ask_tool
    if _ask_tool is None:
        _ask_tool = AskTool()
    return _ask_tool
