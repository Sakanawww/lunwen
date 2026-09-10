"""TodoList 工具：支持创建、查看、完成待办事项。"""
from typing import Optional
from pydantic import BaseModel, Field


class TodoItem(BaseModel):
    """待办事项项。"""
    id: int
    content: str
    completed: bool = False


class TodoListTool:
    """TodoList 工具类：管理待办事项列表。"""
    
    def __init__(self):
        self._todos: list[TodoItem] = []
        self._next_id = 1
    
    def add_todo(self, content: str) -> str:
        """添加一个待办事项。
        
        Args:
            content: 待办事项内容
            
        Returns:
            成功消息
        """
        item = TodoItem(id=self._next_id, content=content, completed=False)
        self._todos.append(item)
        self._next_id += 1
        return f"已添加待办事项 #{item.id}: {content}"
    
    def list_todos(self, show_completed: bool = True) -> str:
        """列出所有待办事项。
        
        Args:
            show_completed: 是否显示已完成的项
            
        Returns:
            格式化的待办列表
        """
        if not self._todos:
            return "暂无待办事项"
        
        lines = ["待办事项列表："]
        for item in self._todos:
            if not show_completed and item.completed:
                continue
            status = "✓" if item.completed else "○"
            lines.append(f"  [{status}] #{item.id}: {item.content}")
        
        return "\n".join(lines)
    
    def complete_todo(self, todo_id: int) -> str:
        """标记待办事项为已完成。
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            成功或错误消息
        """
        for item in self._todos:
            if item.id == todo_id:
                item.completed = True
                return f"已标记待办 #{todo_id} 为已完成"
        return f"未找到待办事项 #{todo_id}"
    
    def delete_todo(self, todo_id: int) -> str:
        """删除一个待办事项。
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            成功或错误消息
        """
        for i, item in enumerate(self._todos):
            if item.id == todo_id:
                self._todos.pop(i)
                return f"已删除待办 #{todo_id}"
        return f"未找到待办事项 #{todo_id}"
    
    def clear_completed(self) -> str:
        """清理所有已完成的待办事项。
        
        Returns:
            成功消息
        """
        count = sum(1 for item in self._todos if item.completed)
        self._todos = [item for item in self._todos if not item.completed]
        return f"已清理 {count} 个已完成的待办事项"


# 全局单例
_todo_tool: Optional[TodoListTool] = None


def get_todo_tool() -> TodoListTool:
    """获取 TodoList 工具单例。"""
    global _todo_tool
    if _todo_tool is None:
        _todo_tool = TodoListTool()
    return _todo_tool
