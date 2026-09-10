# 基于 Agent 的课程助教系统（演示实现）

本项目是《基于 Agent 的课程助教系统设计与实现》毕业设计的可运行演示系统。
三个智能体协作完成**答疑 / 批改 / 出题**闭环，基于 RAG 课程知识库并带**引用溯源**，
使用云端大模型 API + Function Calling 工具调用。

## 技术栈

- 后端：Python 3.11 · FastAPI · SQLAlchemy · MySQL
- 智能体：LangChain + **LangGraph**（多 Agent 有状态编排）+ Function Calling
- 检索：FAISS 向量库 + Qwen Embedding（RAG 溯源）
- 前端：**Vue 3 + Vite + TypeScript + Pinia + Vue Router**（shadcn/ui 风格设计）
- 会话：内存态（Redis 可选降级）

## 运行前准备

1. **安装 Python 3.11**（LangChain 生态暂不兼容 3.13+）。
2. **创建虚拟环境并装依赖**：

   ```bash
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   cd frontend && npm install && cd ..
   ```

3. **配置 `.env`（需自行填写，勿提交仓库）**，参考 `.env.example`：

   ```ini
   # 阿里云百炼（Qwen）OpenAI 兼容接口
   QWEN_API_KEY=sk-你的Key
   QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_CHAT_MODEL=qwen-plus
   QWEN_EMBEDDING_MODEL=text-embedding-v4

   # MySQL
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=你的密码
   MYSQL_DB=course_ta
   ```

   > ⚠️ 大模型为**云端 API**，**必须自行注册百炼/DeepSeek 账号并填入 Key**，否则答疑/批改/出题无法运行。系统**不会编造**任何运行结果。

4. **初始化数据库**：

   ```bash
   mysql -uroot -p < database/schema.sql
   mysql -uroot -p < database/seed.sql
   ```

   > 种子账号：`admin` / `teacher` / `student`，密码均为 `123456`。

> 种子账号：`admin` / `teacher` / `student`，密码均为 `123456`。

5. **启动服务（推荐使用统一启动脚本）**：

   ```bash
   # 一键启动前后端（后端 :8000 · 前端 :5173 · Swagger 文档 :8000/docs）
   python scripts/start.py start

   # 其他常用命令
   python scripts/start.py status    # 查看服务状态
   python scripts/start.py stop      # 停止服务
   python scripts/start.py restart   # 重启服务
   python scripts/start.py logs      # 查看日志（-f 跟踪）
   python scripts/start.py daemon    # 守护进程模式（Linux/Mac）
   ```

   启动后浏览器访问 http://localhost:5173 进入系统（登录页 http://localhost:5173/login）。

## 功能入口

| 角色 | 入口 | 能力 |
| --- | --- | --- |
| 学生 | /chat | SSE 流式答疑（带引用溯源）、自测 |
| 教师 | /kb 、/grading、/questions | 上传知识库、AI 批改、AI 出题、学情看板 |
| 管理员 | /dashboard | Agent 配置与系统概览 |

## 目录结构

```
app/
  agents/        # 答疑/批改/出题三个 Agent + LangGraph 编排图 graph.py
  kb/            # 知识库切分、向量化、FAISS 检索、溯源
  api/           # FastAPI 接口（认证/答疑/知识库/批改/出题/看板）
  models/        # SQLAlchemy ORM
  schemas/       # Pydantic 请求/响应模型
  core/          # 配置、数据库、会话、依赖
  services/      # 大模型封装
frontend/        # Vue3 前端（src/views、src/stores、src/router 等）
database/        # schema.sql / seed.sql
scripts/         # 统一启动脚本 start.py、zh_tw/zh_cn 等
data/seed_kb/    # 演示用《数据结构》讲义
tests/           # 单元测试（pytest）
data/uploads/    # 运行时知识库上传文件（勿提交）
data/faiss_index/# 运行时向量索引（勿提交）
```

## 测试

```bash
.venv\Scripts\python -m pytest tests/ -q
```