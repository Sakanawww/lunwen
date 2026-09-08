# 《基于 Agent 的课程助教系统设计与实现》—— 项目交接说明文档

> 本文件用于把当前已实现的系统完整、忠实地交付给另一位 Agent / 协作同学。
> 请严格依据本文件（及其中引用的源码路径）工作，**不要臆造代码、数据、截图与文献**。
> 论文正文尚未撰写；本文件是"系统的实现与验证现状"记录，亦是后续撰写论文的素材基础。

---

## 0. 一次性重要约定（来自任务书，必须遵守）

1. **大模型为云端 API**，必须由使用者自行注册并填入 Key（`D:\Demo\.env` 中的 `QWEN_API_KEY`）。
   系统**绝不编造**问答结果、批改评分、试题、截图或测试数据。
2. **前端禁止使用 Vue**，一律用 **Jinja2 模板 + 少量原生 JS**。
3. **致谢不写指导老师真名**。
4. **密钥不进代码仓库、不进论文**，统一走 `.env`（已有 `.env.example` 与 `.gitignore`）。
5. **论文中的核心代码必须与实际源码一致**，不得改写伪造。

---

## 1. 项目概览

- **题目**：基于 Agent 的课程助教系统设计与实现
- **学校/专业**：成都文理学院 · 人工智能与大数据学院 · 计算机科学与技术
- **核心能力**：三个协作 Agent 完成 **答疑 / 批改 / 出题**；基于 RAG 课程知识库并带**引用溯源**
- **技术栈（固定，不可换）**：
  - 后端：`Python 3.11` + `FastAPI` + `SQLAlchemy` + `MySQL 8`
  - 智能体：`LangChain` + `LangGraph`（多 Agent 有状态编排）+ **Function Calling（工具调用）**
  - 检索：`FAISS` + Qwen `text-embedding-v4`（维度 1024）
  - 大模型：阿里云百炼 `qwen-plus`（OpenAI 兼容接口）
  - 前端：`Jinja2` + 原生 JS（禁用 Vue）
  - 会话：内存态（`app/core/session.py`），Redis 可选降级
- **依赖**：见 `requirements.txt`（已验证可安装运行）
- **启动方式**：
  ```bash
  .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```
  浏览器访问 `http://127.0.0.1:8000`。
- **演示账号**（`database/seed.sql`）：`admin` / `teacher` / `student`，密码均为 `123456`（SHA-256）

---

## 2. 目录结构

```
D:\Demo\
├─ .env.example      # 环境变量模板（无真实密钥）
├─ .gitignore        # 屏蔽 .env / 上传文件 / 向量索引 / 日志
├─ README.md         # 精简运行说明
├─ requirements.txt  # 依赖清单（已固定版本）
├─ start_server.sh   # 干净启动脚本（先清理残留 python 再以 venv 启动单实例）
├─ database\
│  ├─ schema.sql     # 建库建表（16 张表）
│  └─ seed.sql       # 演示数据（用户/课程/选课/知识文档 etc.）
├─ data\
│  ├─ seed_kb\       # 演示用《数据结构》讲义
│  ├─ faiss_index\   # FAISS 向量索引（运行时生成）
│  └─ uploads\       # 知识库上传文件（运行时生成）
├─ app\
│  ├─ main.py        # FastAPI 入口：页面路由 + 渲染
│  ├─ api\           # 认证 / 答疑 / 知识库 / 批改 / 出题 / 学情看板接口
│  ├─ agents\        # 答疑 / 批改 / 出题 + LangGraph 编排图 graph.py + orchestrator
│  ├─ kb\            # 知识库：切分、向量化、FAISS 检索、溯源
│  ├─ services\      # 大模型封装 llm.py
│  ├─ models\        # SQLAlchemy ORM（16 张表）
│  ├─ schemas\       # Pydantic 请求/响应模型
│  ├─ core\          # config / database / session / deps
│  └─ templates\     # Jinja2 页面
└─ tests\            # pytest 单元测试
```

---

## 3. 架构与核心流程

### 3.1 整体分层

```
浏览器 (Jinja2 页面 + SSE)
      │  HTTP / SSE
      ▼
FastAPI 应用 (app/main.py + app/api/*)
      │
      ├── 认证层  app/core/deps.py (Cookie token → current_user / require_role)
      ├── 业务层  app/agents/*  (三 Agent)
      │            └── LangGraph 编排 app/agents/graph.py
      ├── 检索层  app/kb/knowledge_base.py  (FAISS + Embedding)
      └── 持久层  SQLAlchemy ORM → MySQL (16 表)
```

### 3.2 三 Agent 编排（LangGraph）

- **编排图**：`app/agents/graph.py`
  - 定义 `AgentState`（`question` / `history` / `messages` / `intent` / `result` / `kb`）
  - 节点：`router`（关键词路由）、`答疑Agent`、`批改Agent`、`出题Agent`、`retrieval_tool`（RAG 检索工具）
  - 条件边：按 `intent` 分流到对应 Agent 节点，答疑占位节点后接检索工具节点再 `END`
- **关键词路由表**（与 `agent_configs.route_keywords` 对应，方便论文对照）：
  - 答疑：答疑、问题、不会、讲解、概念、含义、为什么、是什么、什么意思
  - 批改：批改、评分、作业、评语、打分、分数
  - 出题：出题、试题、测验、题目、组卷、练习题
- **Function Calling 演示**：`graph.py` 中 `@tool` 声明的 `example_generator` / `question_adjuster`
  两个工具，验证模型 `bind_tools` 后能自主发起工具调用（已在 Qwen 上实测通过）。
  答疑节点的 RAG 检索被封装为一次工具往返：`AIMessage(tool_calls=…) → ToolMessage`。

### 3.3 答疑 Agent（RAG + 溯源）

- **文件**：`app/agents/tutor_agent.py`
- 流程：
  1. `query_sources(question, kb, k=5)` 从 FAISS 检索相似知识块；
  2. 拼接参考资料 + 系统提示（要求"参考来源：文档·片段N"）调用 `qwen-plus`；
  3. `_extract_sources` 从回答末尾剥离来源行，得到正文与来源列表；
  4. `stream()` 逐步 `yield` 文本 token，结束帧以 `__META__{json}` 前缀携带最终**正文 + sources**。
- **SSE 端**：`app/api/chat.py` 的 `/api/chat/stream`
  - 解析 `data:` 帧中的 `token`/`sources`/`text`；
  - 将用户提问与助教回答**落库**到 `messages` 表（注意：流结束时 FastAPI 请求的 `db` 会话已关闭，
    所以在生成器内用 `SessionLocal` 自开新会话写库，并提前 `sess_id = int(sess.id)` 保存会话 ID；
    否则会报 `DetachedInstanceError`）。

---

## 4. 数据库设计（16 张表）

见 `database/schema.sql` 与 `app/models/models.py`（两者一致）。按功能归类：

| 分组 | 表名 | 作用 |
| --- | --- | --- |
| 用户体系 | users / students / teachers | 统一账号 + 角色扩展 |
| 课程 | courses / enrollments | 课程信息、学生选课 |
| 知识库(RAG) | knowledge_docs / knowledge_chunks | 文档元数据 + 文本块（检索单元） |
| 答疑 | sessions / messages | 多轮会话 + Q/A 消息（含 sources 溯源 JSON） |
| 作业 | assignments / submissions / grading_records | 作业、提交、AI批改结果 |
| 出题/自测 | questions / learning_records | AI 试题、学生答题记录 |
| 系统管理 | agent_configs / system_logs | Agent 配置、审计日志 |

关键约束：`messages.role ∈ (user, assistant, agent)`；`submissions(status=pending|graded)`；
`grading_records.grade_by ∈ (ai, teacher)`；`questions.source ∈ (ai, manual)`。

---

## 5. 各接口层实现要点

### 5.1 认证：`app/api/auth.py`
- `POST /auth/register`、`POST /auth/login`、`POST /auth/logout`
- 登录后写入 HttpOnly Cookie `token`，会话存内存 `app/core/session.py`
- 密码：SHA-256（演示用途），见 `app/utils/helpers.py`

### 5.2 答疑：`app/api/chat.py`
- `GET /api/sessions`、`GET /api/sessions/{id}/messages`
- `POST /api/chat/stream`（SSE）：未指定 `course_id` 时取该学生第一门选修课；未指定会话则新建。
- 页面 `/chat`：`chat.html` 通过 `EventSource` 流式接收，并在回答末尾渲染"📎 来源：…"。

### 5.3 知识库：`app/api/knowledge.py`
- `POST /api/kb/upload`（教师/管理员）：保存文件 → `ingest_file(...)` 切块向量化 → 元数据落库。
- `GET /api/kb/docs/{course_id}`：列出该课程已入库文档及块数。

### 5.4 批改：`app/api/grading.py`
- `GET /api/grade/submissions/{course_id}`：列出作业提交与批改状态。
- `POST /api/grade/{submission_id}`：调用批改 Agent 返回 `{score, feedback}`，写入 `grading_records`
  并把 `submission.status` 置为 `graded`。

### 5.5 出题：`app/api/question.py`
- `POST /api/question/generate`（教师/管理员）：按知识点/数量/难度生成并入库。
- `GET /api/question/list/{course_id}`：列出试题。

### 5.6 学情看板：`app/api/dashboard.py`
- `GET /api/dashboard/course/{course_id}`：统计选课人数、提交/已批改数、平均分、试题/文档/消息数。

### 5.7 大模型封装：`app/services/llm.py`
- `get_chat_model()` / `LLMFactory.chat_model()`：每次返回新的 `ChatOpenAI` 实例（Qwen），
  避免实例跨请求复用问题。
- `LLMFactory.embeddings()`：`text-embedding-v4`（1024 维）。

### 5.8 知识库核心：`app/kb/knowledge_base.py`
- `KnowledgeBase(course_id)`：按课程加载/保存 FAISS 索引目录 `data/faiss_index/course_{id}`
- `split_text`：`RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`，分隔符含中文句号
- `ingest_file`：支持 txt/md（utf-8/gbk 回退）与 pdf（pypdf），切块 → 向量化 → 写库
- `query_sources`：检索并返回 `(拼接上下文, 溯源来源列表)`；若 `kb.store is None` 返回空而非崩溃

---

## 6. 已完成并验证的功能清单（真实运行结果，非编造）

| # | 功能 | 验证方式 | 结果 |
| --- | --- | --- | --- |
| 1 | 依赖可安装 | `.venv` 全量 import | ✅ |
| 2 | 单 Agent + RAG 答疑（SSE 流式 + 溯源） | HTTP 客户端逐帧解析 | ✅ 流式 token + 末尾 sources 帧 |
| 3 | 答疑回答落库（`messages.role='assistant'`） | SQL 查询 | ✅ COUNT 正确 | 
| 4 | LangGraph 三 Agent 节点路由 | `graph.invoke()` 单测 | ✅ 答疑/批改/出题 intent 均命中 |
| 5 | Function Calling 工具绑定 | Qwen `bind_tools` 实测 | ✅ 模型返回 tool_calls |
| 6 | 批改 Agent | 教师端触发批改 | ✅ score=85 + 详细评语落库 |
| 7 | 出题 Agent | 教师端生成 | ✅ 生成 2 道《数据结构》试题入库 |
| 8 | 三端页面渲染 | 浏览器 + HTTP 状态码 | ✅ 三角色入口/权限隔离正常 |
| 9 | 浏览器实测答疑全流程 | 登录→提问→流式回答→来源展示 | ✅ 前端正确渲染回答与"来源：数据结构讲义·片段1" |
| 10 | 单元测试 | `pytest tests/` | ✅ 11 项通过 |

> 截图已拍摄多张（答疑流式、看板等），原始 PNG 位于 `C:\Users\sakana\.zcode\cli\artifacts\...`，
> 尚未归档到论文。如需使用请据实引用，**不可伪造"程序运行界面"图片**。

---

## 7. 已知事项与后续工作

### 7.1 已知技术注意点（写论文/改代码时勿踩坑）
1. **SSE 落库**：流结束必须**另开 SessionLocal 写库** + 提前保存 `sess_id`，否则 `DetachedInstanceError`。
2. **模型实例**：用 `llm.get_chat_model()`（工厂方法每次新建），勿缓存单例跨请求。
3. **双进程问题**：Windows 下用 base Python 与 venv Python 各自起服务会端口冲突且可能跑旧代码；
   务必用 `start_server.sh` 先清残留再以 **venv 解释器** 起单实例。
4. **中文文件名 / 中文 JSON**：上传/回复均用 UTF-8；API 侧 `json.dumps(..., ensure_ascii=False)`。
5. **导入路径**：单测/脚本需设 `PYTHONPATH=/d/Demo` 或从项目根运行。

### 7.2 尚未完成
- **{论文正文}**：需学校 Word 模板 / 任务书 / 开题报告对齐格式后撰写（核心内容见本文件）。
- 演示截图归档到论文附录。
- （可选）LangGraph 答疑节点当前采用"先检索注入 + 工具往返演示"，如需严格 tool 循环可进一步用
  `create_react_agent`，但受 Qwen tool 参数兼容性影响，现阶段以"检索工具封装"满足 溯源 + Function Calling 两点即可。

### 7.3 若要继续，建议顺序
1. 你提供学校模板/任务书 → 我按格式写论文正文。
2. 论文中插入真实架构图（基于第 3 节流程，用真实类名/表名绘制）。
3. 归档截图，整理演示稿。