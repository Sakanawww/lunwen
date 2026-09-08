# Agent 提示词集合

> 用于指导 AI Agent 完成课程助教系统的各项开发任务  
> 使用方法：复制对应提示词 → 发送给 Agent → 执行开发

---

## 📋 目录

| 模块 | 提示词 | 适用场景 |
|------|--------|----------|
| 数据库 | [数据库迁移](#1-数据库迁移) | 多课程架构改造 |
| 权限 | [权限系统](#2-权限系统) | RBAC 权限控制 |
| 课程 | [课程管理](#3-课程管理 API) | CRUD 接口 |
| Agent | [Agent 配置](#4-agent-配置页面) | 多 AI 服务商 |
| 删除 | [删除功能](#5-删除功能) | 聊天/题目删除 |
| 答题 | [答题页面](#6-答题页面) | 洛谷风格 |
| 图谱 | [知识图谱](#7-知识图谱) | ECharts 可视化 |
| 日志 | [日志系统](#8-日志系统) | 操作审计 |
| UI | [UI 优化](#9-ui-优化) | 移除蓝点/背景 |

---

## 1. 数据库迁移

### 提示词

```
请完成课程助教系统的数据库架构改造，支持多课程管理。

【任务目标】
1. 创建课程表（courses）和课程用户关联表（course_users）
2. 为现有表添加 course_id 外键（questions, chat_sessions, knowledge_fragments, assignments, submissions）
3. 编写数据迁移脚本，将现有数据迁移到新架构

【技术要求】
- 使用 SQLAlchemy Alembic 进行迁移
- 外键约束：ON DELETE CASCADE
- 索引优化：course_id, user_id 复合索引
- 默认课程处理：创建"默认课程"，将孤儿数据关联

【输出内容】
1. models/course.py - 课程模型
2. models/course_user.py - 课程用户关联模型
3. alembic/versions/xxx_add_course_support.py - 迁移脚本
4. scripts/migrate_default_course.py - 数据迁移脚本

【验收标准】
- 迁移可回滚（downgrade）
- 外键约束生效
- 现有数据不丢失
```

---

## 2. 权限系统

### 提示词

```
请实现基于角色的课程权限系统（RBAC）。

【需求说明】
1. 四种角色：owner（所有者）| teacher（教师）| assistant（助教）| student（学生）
2. 权限矩阵：
   - owner: 所有权限（包括删除课程）
   - teacher: 查看/编辑/批改/聊天/RAG
   - assistant: 查看/批改/聊天
   - student: 查看/聊天/提交作业

【实现内容】
1. 权限检查装饰器
```python
@require_course_permission(['owner', 'teacher'])
async def some_api(course_id: int, ...):
    ...
```

2. 权限检查函数
```python
async def check_course_permission(db, course_id, user_id, required_roles)
```

3. 单元测试（跨课程访问测试）

【安全要求】
- 所有课程相关 API 必须通过权限检查
- 禁止通过 course_id 遍历访问
- 记录越权访问日志

【输出文件】
- app/utils/permissions.py - 权限工具
- app/api/middleware.py - 权限中间件
- tests/test_permissions.py - 权限测试
```

---

## 3. 课程管理 API

### 提示词

```
请实现课程管理的完整 API 接口。

【API 列表】
GET    /api/courses              # 获取我的课程列表
POST   /api/courses              # 创建课程
GET    /api/courses/{id}         # 课程详情
PUT    /api/courses/{id}         # 更新课程
DELETE /api/courses/{id}         # 删除课程（软删除）

POST   /api/courses/{id}/users   # 添加课程用户
GET    /api/courses/{id}/users   # 获取课程用户列表
DELETE /api/courses/{id}/users/{user_id} # 移除用户

【响应格式】
{
  "id": 1,
  "name": "数据结构",
  "code": "CS101",
  "teacher_name": "张老师",
  "user_role": "teacher",
  "student_count": 45,
  "created_at": "2025-01-01T00:00:00"
}

【业务规则】
- 创建课程时自动成为 owner
- 删除课程需检查是否有活跃学生
- 用户只能看到自己有权限的课程

【输出文件】
- app/api/courses.py - 课程 API
- app/schemas/course.py - Pydantic 模型
- tests/test_courses.py - API 测试
```

---

## 4. Agent 配置页面

### 提示词

```
请实现 AI 服务商配置页面，支持多模型接入。

【功能需求】
1. 服务商管理
   - 添加/编辑/删除 AI 服务商
   - API Key 加密存储（Fernet）
   - 连接测试功能

2. 支持的服务商
   - DeepSeek (deepseek-chat)
   - 通义千问 (qwen-plus)
   - ChatGLM (glm-4)
   - 自定义 OpenAI 兼容接口

3. 配置项
   - 服务商名称
   - API Key（前端脱敏显示 sk-****abcd）
   - Base URL
   - 模型名称
   - 额度限制
   - 是否默认

【前端要求】
- 服务商卡片网格布局
- 测试连接按钮（实时反馈）
- 剩余额度显示
- 默认服务商标识

【安全要求】
- API Key 后端加密存储
- 前端不传输明文 Key
- 操作日志记录

【输出文件】
- app/api/agents.py - Agent 配置 API
- app/templates/agent_settings.html - 配置页面
- app/static/js/agents.js - 前端逻辑
- app/models/ai_provider.py - 数据模型
```

---

## 5. 删除功能

### 提示词

```
请实现聊天记录和题目的删除功能（软删除 + 回收站）。

【功能需求】
1. 聊天记录删除
   - 单条删除：DELETE /api/chat/sessions/{id}
   - 批量删除：DELETE /api/chat/sessions?ids=1,2,3
   - 回收站：GET /api/chat/sessions/deleted
   - 恢复：POST /api/chat/sessions/{id}/restore

2. 题目删除
   - 检查引用（是否被作业使用）
   - 软删除标记 is_deleted
   - 回收站列表
   - 恢复功能

【前端交互】
- 删除前二次确认弹窗
- 删除后 Toast 提示 + 可撤销（3 秒）
- 回收站页面（查看/恢复/彻底删除）

【数据库变更】
ALTER TABLE chat_sessions ADD COLUMN (
  is_deleted BOOLEAN DEFAULT FALSE,
  deleted_at DATETIME,
  deleted_by INT
);

【输出文件】
- app/api/chat.py - 聊天删除 API
- app/api/questions.py - 题目删除 API
- app/templates/chat_deleted.html - 回收站页面
- app/static/js/chat_delete.js - 删除逻辑
```

---

## 6. 答题页面

### 提示词

```
请实现学生答题页面（参考洛谷风格）。

【页面布局】
┌─────────────────────────────────────────┐
│  题目描述（左）    │  答题区（右）       │
│  - 题目内容        │  - 代码编辑器       │
│  - 输入输出格式    │  - 语言选择         │
│  - 样例            │  - 提交按钮         │
├─────────────────────────────────────────┤
│  测试结果（提交后显示）                 │
│  - 测试点 1: ✅ AC 12ms 256KB          │
│  - 测试点 2: ❌ WA                     │
└─────────────────────────────────────────┘

【功能需求】
1. 代码编辑器（Monaco Editor / CodeMirror）
2. 语言选择（Python / C++ / Java）
3. 实时提交 + 判题
4. 草稿自动保存（localStorage）
5. 测试结果轮询显示

【判题逻辑】
- 客观题：直接对比答案
- 编程题：调用判题沙箱（或第三方 API）
- 主观题：AI 辅助批改

【API 接口】
POST   /api/submissions         # 提交答案
GET    /api/submissions/{id}    # 获取提交状态
GET    /api/submissions/my      # 我的提交记录

【输出文件】
- app/templates/answer.html - 答题页面
- app/api/submissions.py - 提交 API
- app/services/judge.py - 判题服务
- app/static/js/answer.js - 前端逻辑
```

---

## 7. 知识图谱

### 提示词

```
请实现知识图谱可视化页面（ECharts Graph）。

【功能需求】
1. 力导向图展示知识点关系
2. 节点支持拖拽、缩放
3. 点击节点显示详情
4. 搜索高亮路径
5. 关系类型区分（前置/相似/引用）

【API 接口】
GET /api/knowledge/{course_id}/graph
响应：
{
  "nodes": [
    {"id": 1, "name": "二叉树", "value": 10, "symbolSize": 50, "category": 0}
  ],
  "links": [
    {"source": 1, "target": 2, "relation_type": "prerequisite", "value": 0.9}
  ],
  "categories": [{"name": "数据结构"}, {"name": "算法"}]
}

【ECharts 配置要点】
- layout: 'force'（力导向）
- roam: true（缩放平移）
- draggable: true（节点拖拽）
- emphasis: {focus: 'adjacency'}（高亮邻接）
- force: {repulsion: 200, gravity: 0.1}

【前端交互】
- 点击节点 → 显示知识片段详情
- 双击节点 → 编辑知识点
- 搜索框 → 高亮匹配节点
- 图例 → 筛选关系类型

【输出文件】
- app/api/knowledge_graph.py - 图谱 API
- app/templates/knowledge_graph.html - 图谱页面
- app/static/js/knowledge_graph.js - ECharts 配置
- app/services/graph_builder.py - 图数据构建
```

---

## 8. 日志系统

### 提示词

```
请实现系统操作日志功能。

【日志模型】
CREATE TABLE operation_logs (
  id INT PRIMARY KEY,
  user_id INT,
  action VARCHAR(50),        -- LOGIN, DELETE_QUESTION, SUBMIT_ASSIGNMENT
  resource_type VARCHAR(50), -- question, assignment, chat
  resource_id INT,
  ip_address VARCHAR(45),
  request_method VARCHAR(10),
  request_path VARCHAR(200),
  old_value JSON,
  new_value JSON,
  status ENUM('success', 'failed', 'error'),
  error_message TEXT,
  duration_ms INT,
  created_at DATETIME
);

【实现内容】
1. 日志装饰器
```python
@log_operation(action='DELETE_QUESTION', resource_type='question')
async def delete_question(...):
    ...
```

2. 日志查询 API
```
GET /api/logs/operations      # 日志列表
GET /api/logs/statistics      # 统计分析
```

3. 日志查看页面
- 时间范围筛选
- 操作类型筛选
- 用户筛选
- 导出 CSV

【性能优化】
- 异步写入（不阻塞主流程）
- 90 天自动归档
- 单表超过 100 万条自动分区

【输出文件】
- app/utils/logging.py - 日志工具
- app/api/logs.py - 日志 API
- app/templates/logs.html - 日志页面
- app/models/operation_log.py - 日志模型
```

---

## 9. UI 优化

### 提示词 9.1：移除难度小蓝点

```
请移除题目卡片上的 5 个难度小蓝点指示器。

【查找范围】
grep -r "difficulty-dots" app/templates/
grep -r "question-dots" app/templates/
grep -r "<span class=\"dot" app/templates/

【修改内容】
1. HTML：删除难度指示器 HTML 结构
2. CSS：注释或删除相关样式
3. JS：移除难度相关逻辑

【文件列表】
- app/templates/components/question_card.html
- app/templates/questions.html
- app/templates/grading.html
- app/static/css/questions.css

【验收标准】
- 题目列表页无蓝点
- 题目卡片无蓝点
- 筛选器无难度选项
- 数据库 difficulty 字段保留（不删除）
```

### 提示词 9.2：注册页背景优化

```
请优化注册页面和登录页面的背景。

【设计要求】
- 浅色主题（与整体一致）
- 抽象几何图形
- 渐变蓝色调
- 轻量 SVG（<50KB）

【实现方案】
方案 A：CSS 渐变
background: 
  linear-gradient(135deg, rgba(91,127,255,0.1), rgba(139,92,246,0.1)),
  url('/static/images/bg-geometric.svg');

方案 B：纯 CSS 几何
::before {
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(91,127,255,0.15)),
    radial-gradient(circle at 80% 70%, rgba(139,92,246,0.15));
}

【输出文件】
- app/static/images/bg-geometric.svg - 背景图
- app/static/css/auth.css - 更新样式
- app/templates/register.html - 应用新背景
- app/templates/login.html - 同步更新
```

---

## 🔧 通用提示词模板

### 新建 API 模块

```
请创建 [模块名称] 的 API 接口。

【业务需求】
[描述业务逻辑]

【API 列表】
GET    /api/[resource]          # 列表
POST   /api/[resource]          # 创建
GET    /api/[resource]/{id}     # 详情
PUT    /api/[resource]/{id}     # 更新
DELETE /api/[resource]/{id}     # 删除

【数据模型】
[Pydantic Schema 定义]

【权限要求】
[需要何种权限检查]

【输出文件】
- app/api/[module].py
- app/schemas/[module].py
- app/models/[module].py
- tests/test_[module].py
```

### 新建前端页面

```
请创建 [页面名称] 页面。

【页面布局】
[ASCII 布局图或参考截图]

【功能需求】
1. [功能 1]
2. [功能 2]
3. [功能 3]

【API 接口】
[需要调用的后端 API]

【UI 规范】
- 遵循现有设计系统
- 使用 Remix Icon 图标
- 响应式适配移动端

【输出文件】
- app/templates/[page].html
- app/static/js/[page].js
- app/static/css/[page].css
```

### 数据库迁移

```
请编写数据库迁移脚本。

【变更内容】
1. 新建表：[表名]
2. 修改表：[表名] 添加 [字段]
3. 数据迁移：[迁移逻辑]

【要求】
- 支持 upgrade 和 downgrade
- 保留现有数据
- 添加外键约束
- 创建必要索引

【输出文件】
- alembic/versions/[版本号]_[描述].py
- scripts/[迁移脚本].py
```

---

## 📦 批量任务提示词

### 全栈开发任务

```
请完成以下全栈功能开发：[功能名称]

【后端任务】
1. 数据模型设计（models/）
2. API 接口实现（api/）
3. Pydantic Schema（schemas/）
4. 单元测试（tests/）

【前端任务】
1. 页面模板（templates/）
2. 交互逻辑（static/js/）
3. 样式文件（static/css/）
4. 组件复用（components/）

【联调要求】
1. API 文档（Swagger/OpenAPI）
2. 前后端接口对齐
3. 错误处理一致
4. 加载状态处理

【输出清单】
- [ ] 数据库迁移
- [ ] 后端 API
- [ ] 前端页面
- [ ] 单元测试
- [ ] API 文档
```

---

## 🎯 提示词使用技巧

### 1. 明确上下文
```
【项目背景】
基于 FastAPI 的课程助教系统，已有用户系统/认证系统

【当前任务】
在现有架构上添加 [新功能]

【技术约束】
- Python 3.11
- FastAPI + SQLAlchemy
- Jinja2 模板
- 原生 JS（无 Vue/React）
```

### 2. 指定输出格式
```
【输出要求】
1. 完整代码（可复制运行）
2. 关键代码注释
3. 文件路径标注
4. 依赖说明
```

### 3. 分阶段验证
```
【验收步骤】
1. 先输出数据模型 → 我确认
2. 再输出 API 接口 → 我确认
3. 最后输出前端页面 → 我确认

每阶段完成后等待我的反馈再继续。
```

### 4. 错误处理要求
```
【异常处理】
- 404：资源不存在
- 403：权限不足
- 400：参数错误
- 500：服务器错误（记录日志）

所有 API 必须统一错误响应格式：
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "资源不存在",
    "details": {...}
  }
}
```

---

## 📋 快速索引

| 任务类型 | 提示词位置 |
|----------|------------|
| 数据库迁移 | [数据库迁移](#1-数据库迁移) |
| 权限控制 | [权限系统](#2-权限系统) |
| CRUD API | [课程管理](#3-课程管理-api) |
| AI 配置 | [Agent 配置](#4-agent-配置页面) |
| 删除功能 | [删除功能](#5-删除功能) |
| 答题页面 | [答题页面](#6-答题页面) |
| 可视化 | [知识图谱](#7-知识图谱) |
| 审计日志 | [日志系统](#8-日志系统) |
| UI 优化 | [UI 优化](#9-ui-优化) |

---

> **使用建议**：
> 1. 复制对应提示词 → 根据实际情况修改参数 → 发送给 Agent
> 2. 复杂任务分阶段验证（模型 → API → 前端）
> 3. 保留验收标准用于代码审查
> 4. 所有代码提交前运行测试
