# 基于 Agent 的课程助教系统（演示实现）

本项目是《基于 Agent 的课程助教系统设计与实现》毕业设计的可运行演示系统。
三个智能体协作完成**答疑 / 批改 / 出题**闭环，基于 RAG 课程知识库并带**引用溯源**，
使用云端大模型 API + Function Calling 工具调用。

## 技术栈

- 后端：Python 3.11 · FastAPI · SQLAlchemy · MySQL
- 智能体：LangChain + ReAct + **LangGraph**（多 Agent 有状态编排）+ Function Calling
- 检索：FAISS 向量库 + Qwen Embedding（RAG 溯源）
- 前端：**Vue 3 + Vite + TypeScript + Pinia + Vue Router**（shadcn/ui 风格设计）
- 会话：**Redis Session**（不可用时自动降级为内存态，仅限开发）

## 快速部署（从 GitHub 拉取到本地运行）

### 0. 环境要求

| 依赖 | 版本要求 | 说明 |
| --- | --- | --- |
| Python | 3.11（勿用 3.13+，LangChain 生态暂不兼容） | 后端 |
| Node.js | ≥ 18 | 前端构建 |
| MySQL | 8.x | 需知道 root 密码（或专用账号） |
| Redis | 任意（可选） | 未安装时自动降级为内存会话，仅限开发 |

### 1. 拉取代码并安装依赖

```bash
git clone https://github.com/Sakanawww/lunwen.git course-ta
cd course-ta

python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      # Windows
# .venv/bin/pip install -r requirements.txt        # Linux / Mac

cd frontend && npm install && cd ..
```

### 2. 配置 `.env`

复制 `.env.example` 为 `.env`，填入你的真实值：

```ini
QWEN_API_KEY=sk-你的百炼Key          # 答疑/批改/出题/知识库向量化必需
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_CHAT_MODEL=qwen-plus
QWEN_EMBEDDING_MODEL=text-embedding-v4

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DB=course_ta                   # 数据库需预先创建：CREATE DATABASE course_ta;
```

> ⚠️ 大模型为**云端 API**（阿里云百炼），需自行注册并填入 Key。
> 没有 Key 时系统仍可启动、浏览页面与看板演示数据，但答疑/批改/出题/知识库向量化无法调用模型。

### 3. 一键初始化演示数据

```bash
.venv\Scripts\python scripts\seed_demo.py
```

脚本会自动：建表 → 创建演示账号与 4 门课程 → 导入 4 份课程讲义入知识库
（配置了 QWEN_API_KEY 时同时生成 FAISS 向量索引）→ 布置作业与题库 →
回填近 90 天的学习行为数据（答疑/提交/练习历史，供学情看板展示）。

需要重置为初始演示状态时：`.venv\Scripts\python scripts\seed_demo.py --force`（清空重灌）。

### 4. 启动服务

```bash
python scripts/start.py start      # 一键启动前后端（后端 :8000 · 前端 :5173）
python scripts/start.py status     # 查看服务状态
python scripts/start.py stop       # 停止服务
python scripts/start.py restart    # 重启服务
python scripts/start.py logs       # 查看日志（-f 跟踪）
```

启动后访问 http://localhost:5173 （接口文档 http://localhost:8000/docs ）。

### 演示账号（密码均为 `123456`）

| 角色 | 账号 | 说明 |
| --- | --- | --- |
| 管理员 | `admin` | 全部功能 + 用户管理与日志审计 |
| 教师 | `teacher` | 数据结构课程（看板/知识库/作业/批改/出题） |
| 教师 | `teacher02` / `teacher03` | 操作系统 / 计算机网络、计算机基础原理 |
| 学生 | `student`（及 student01~09） | 答疑、自测练习、我的作业 |

## 功能特点

- **作业全链路闭环**：教师发布作业 → 学生在线提交 → AI 自动批改 → 学情看板统计。
- **课程全生命周期管理**：课程创建/编辑/删除，学生选课/退课，课程成员角色（owner/teacher/assistant/student）。
- **知识库管理**：上传讲义自动切分向量化；删除文档同步清理文本块并重建 FAISS 索引。
- **多课程数据隔离**：课程/时间范围切换后，看板与试题库按所选课程与范围实时刷新（趋势图按日/周/月自适应聚合）。
- **对话记录管理**：答疑会话软删除、恢复与彻底删除。
- **试题回收站**：已删除试题可搜索、批量恢复或彻底删除。
- **AI 出题自动入库**：出题 Agent 生成的题目写入题库并实时展示。
- **答题历史与正确率**：学生自测记录与正确率统计。
- **全角色页面真实数据**：所有页面接入后端真实 API，无 mock 占位数据。
- **多轮对话上下文**：SSE 流式答疑带引用溯源，支持连续多轮对话。

## 功能入口

| 角色 | 入口 | 能力 |
| --- | --- | --- |
| 学生 | /chat、/practice、/my-assignments、/courses | SSE 流式答疑（带引用溯源 + 多轮上下文）、自测练习（真实判题落库 + 答题历史）、查看/提交作业、课程选择/退课 |
| 教师 | /dashboard、/knowledge、/assignments、/grading、/questions、/courses | 学情看板、上传/删除知识库、发布/删除作业、AI 批改、AI 出题、试题管理（含回收站）、课程创建/编辑/删除 |
| 管理员 | /dashboard、/knowledge、/assignments、/grading、/questions、/admin、/courses | 教师全部能力 + 用户管理（增删改）、系统概览、操作日志审计 |

## 目录结构

```
app/
  agents/        # 答疑/批改/出题三个 Agent + 多 Agent 编排 + LangGraph 图 graph.py
  kb/            # 知识库切分、向量化、FAISS 检索、溯源
  api/           # FastAPI 接口（认证/答疑/知识库/批改/出题/看板/课程管理/作业管理/会话删除）
  models/        # SQLAlchemy ORM
  schemas/       # Pydantic 请求/响应模型
  core/          # 配置、数据库、会话（Redis）、依赖
  services/      # 大模型封装
frontend/        # Vue3 前端
database/        # schema.sql（DDL 参考）/ migrations
scripts/         # start.py 统一启动脚本；seed_demo.py 一键演示数据；seed_history.py 历史回填；rebuild_kb_index.py 重建向量索引
data/seed_kb/    # 4 门课程的演示讲义（知识库初始语料）
tests/           # 单元测试（pytest）
```

> `data/uploads/`（上传文件）与 `data/faiss_index/`（向量索引）为运行时数据，不入仓库。

## 常见问题

- **端口被占用**：后端固定使用 8000、前端 5173。若启动失败提示端口占用，
  先结束占用进程（`netstat -ano | findstr :8000`），再 `python scripts/start.py start`。
- **没有 Redis？** `.env` 保留 Redis 配置即可，未安装时后端自动使用内存会话（fakeredis），重启后需重新登录。
- **知识库检索为空 / 报向量化错误**：多为未配置 `QWEN_API_KEY`。配置后执行
  `.venv\Scripts\python scripts\rebuild_kb_index.py` 即可用已入库的讲义文本块重建索引
  （或在「知识库」页重新上传 `data/seed_kb/` 中的讲义）。
- **看板没有数据**：请确认已执行 `scripts/seed_demo.py`；时间范围切换 7/30/90 天
  依赖回填的历史行为数据。

## 测试

```bash
.venv\Scripts\python -m pytest tests/ -q
```
