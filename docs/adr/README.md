# 架构决策记录 (ADR) 索引

本目录包含课程助教系统的关键架构决策记录。

## ADR 列表

| 编号 | 标题 | 状态 |
|------|------|------|
| [ADR-001](001-use-langgraph-for-agent-orchestration.md) | 使用 LangGraph 而非纯 LangChain | 已采纳 |
| [ADR-002](002-use-faiss-for-vector-storage.md) | 使用 FAISS 而非 Chroma | 已采纳 |
| [ADR-003](003-use-jinja2-for-frontend.md) | 使用 Jinja2 而非 Vue/React | 已采纳 |
| [ADR-004](004-in-memory-session-storage.md) | 使用内存态会话而非 Redis | 已采纳 |
| [ADR-005](005-multi-course-architecture.md) | 使用多课程架构支持 RBAC 权限 | 已采纳 |
| [ADR-006](006-use-qwen-api.md) | 使用阿里云百炼 Qwen API | 已采纳 |

## 背景

本项目是《基于 Agent 的课程助教系统设计与实现》毕业设计的演示系统，实现基于多 Agent 协作的课程助教功能，完成**答疑/批改/出题**闭环。

## 技术栈总览

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | FastAPI | 异步 Web 框架 |
| ORM | SQLAlchemy | 数据库对象映射 |
| 数据库 | MySQL 8.0 | 关系型数据存储 |
| Agent 框架 | LangChain + LangGraph | 多 Agent 编排 |
| 向量库 | FAISS | 相似度检索 |
| Embedding | Qwen-Embedding | 文本向量化 |
| 大模型 | Qwen-Plus (阿里云百炼) | 云端 API |
| 前端 | Jinja2 + 原生 JS | 模板渲染 |
| 会话 | 内存态 (可选 Redis) | 用户会话管理 |

## 使用说明

ADR 采用标准格式，包含以下部分：

- **状态**：提议/已采纳/已废弃/已替换
- **上下文**：决策背景和问题描述
- **决策**：选定的方案
- **理由**：选择该方案的原因
- **后果**：正面影响和负面影响
- **相关文档**：代码位置和参考文档

## 相关文档

- `框架说明文档.md` - 完整的技术架构说明
- `README.md` - 项目概述和运行指南
