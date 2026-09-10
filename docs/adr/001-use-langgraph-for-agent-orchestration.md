# ADR-001: 使用 LangGraph 而非纯 LangChain

## 状态

已采纳

## 上下文

在构建多 Agent 协作的课程助教系统时，需要选择一个合适的 Agent 编排框架。系统需要支持三个 Agent（答疑 Agent、批改 Agent、出题 Agent）的协同工作，并且需要实现有状态的工作流。

## 决策

选择使用 **LangGraph** 作为 Agent 编排框架，而非纯 LangChain。

## 理由

1. **有状态工作流支持**：LangGraph 提供了基于图的状态机模型，可以清晰地定义 Agent 之间的状态转换和数据流。

2. **条件边支持**：LangGraph 支持条件边（conditional edges），可以根据用户意图动态路由到不同的 Agent 节点。

3. **可视化编排**：图结构更直观地展示了多 Agent 协作的流程，便于调试和维护。

4. **循环和迭代**：LangGraph 原生支持循环和迭代模式，适合需要多轮对话的答疑场景。

## 架构示意

```
router → 条件边 → 答疑 Agent/批改 Agent/出题 Agent → END
```

## 后果

### 正面影响

- Agent 路由逻辑清晰，易于扩展新 Agent
- 状态管理集中，便于调试和追踪
- 支持复杂的多轮对话场景

### 负面影响

- 增加了 LangGraph 依赖
- 学习曲线略高于纯 LangChain

## 相关文档

- `app/agents/graph.py` - LangGraph 编排图实现
- `框架说明文档.md` - 第 5 节 数据流设计
