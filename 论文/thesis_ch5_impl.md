# 5 系统实现

本章对系统的实现进行说明。首先介绍系统的开发与运行环境，随后按功能模块说明各模块的具体实现，最后阐述系统的测试方法与测试结果。

## 5.1 系统实现概述

### 5.1.1 系统开发环境

系统开发在 Windows 环境下进行，主要软件环境如下：

（1）操作系统：Windows 10/11（64 位）。

（2）开发语言与运行时：Python 3.11。系统使用虚拟环境隔离依赖，代码基于 Python 编写，利用类型注解与异步特性提升可维护性。

（3）开发工具：使用代码编辑器进行开发与调试，通过 Uvicorn 本地启动 FastAPI 应用进行联调测试。

（4）主要依赖框架及版本：FastAPI、LangChain、LangGraph、FAISS、SQLAlchemy、pymysql、Jinja2 等，具体版本在 requirements.txt 中固定。

### 5.1.2 系统运行环境

系统运行环境如下：

（1）服务器端：可采用普通个人计算机或云主机运行，需安装 Python 3.10/3.11 运行环境、MySQL 8 数据库，并配置大模型 API 的访问密钥。

（2）数据库：MySQL 8，使用 utf8mb4 字符集。

（3）大模型服务：阿里云百炼（通义千问）云端 API，通过 .env 环境变量配置 API Key、接口地址、对话模型与嵌入模型，不进入代码仓库。

（4）客户端：普通浏览器，支持 Server-Sent Events，无需额外插件。

## 5.2 系统实现

### 5.2.1 认证模块实现

系统在登录页面提供用户名与密码输入，登录接口进行身份校验后建立会话，并把令牌写入 HttpOnly Cookie。系统通过依赖注入（FastAPI Depends）实现认证与角色控制：`current_user` 依赖从 Cookie 解析令牌还原当前用户，`require_role` 依赖在 `current_user` 基础上进一步校验角色。核心实现示意如下：

```python
def current_user(request, db):          # 解析 Cookie token → 返回当前用户
    token = request.cookies.get("token") or ""
    sess = sstore.get_session(token)
    if not sess:
        raise HTTPException(401, "未登录或会话已过期")
    user = db.get(m.User, sess["user_id"])
    return user

def require_role(*roles):               # 角色校验
    def checker(user=Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "无权限执行该操作")
        return user
    return checker
```

用户登录界面如图 5.1 所示。系统根据登录角色跳转到对应的功能界面，学生端进入答疑界面，教师端进入学情与知识库等功能界面，管理员端进入后台管理界面。

【截图：图5.1 用户登录界面】

### 5.2.2 智能答疑模块实现

智能答疑模块是系统的核心，包含后端智能体与前端流式展示两部分。

后端部分，答疑 Agent 封装"检索—组装—调用—溯源"链路。学生提问后，系统构建该课程的知识库对象，通过 `query_sources` 从 FAISS 索引检索与问题相似的知识块，再将系统提示、检索上下文与学生问题组装为消息序列，调用大语言模型进行流式生成；模型逐段输出文本，答疑 Agent 逐段返回，在流式结束后解析回答末尾的"参考来源"行，得到清洁正文与来源列表。核心实现示意如下：

```python
class TutorAgent:
    def __init__(self, kb, course_id):
        self.kb = kb

    def stream(self, question, history):
        context, sources = query_sources(question, self.kb, k=5)   # FAISS 检索
        msgs = _build_prompt(context)                               # 组装提示
        msgs.extend(_to_role_messages(history))
        msgs.append(HumanMessage(content=question))
        model = llm.get_chat_model()                                # 云端大模型
        full = []
        for chunk in model.stream(msgs):                            # 流式生成
            yield chunk.content
            full.append(chunk.content)
        clean, src = _extract_sources("".join(full))                # 剥离来源行
        yield "__META__" + json.dumps({"text": clean, "sources": src or sources})
```

其中 `query_sources` 负责从 FAISS 索引检索并返回拼接后的上下文与来源列表，实现溯源所需的数据来源。接口层通过 SSE（Server-Sent Events）将答疑 Agent 的流式输出以 `data:` 帧的形式持续推送给前端，并以 `__META__` 为前缀的特有数据帧在流末尾发送最终正文与来源信息。学生答疑界面如图 5.2 所示，回答以流式方式逐段显示，并在末尾展示"参考来源：数据结构讲义.docx·片段3"等来源标注。

【截图：图5.2 学生答疑界面（流式回答 + 来源溯源）】

前端使用原生 JavaScript 的 EventSource 建立 SSE 连接，接收 token 帧并逐步追加文本，接收 sources 帧后渲染来源列表，实现流式对话的实时展示。这一方案在保证实时性的同时避免了轮询带来的额外开销。

### 5.2.3 知识库管理模块实现

知识库管理模块支持教师上传课程文档并自动入库。上传采用表单文件提交，后端保存文件后调用文档入库逻辑：根据文件后缀读取文本内容，使用文本切分器按 500 字符块大小、50 字符重叠对文本进行切分，得到若干知识块；随后将每个知识块向量化并入 FAISS 索引，同时把文档元数据与知识块写入 MySQL。核心实现示意如下：

```python
def ingest_file(path, db, course_id, upload_by):
    text = _read_file(path)                       # 读取 txt/md/pdf 文本
    docs = KnowledgeBase.split_text(text, source=path.name)   # 切分知识块
    # 写入 knowledge_docs / knowledge_chunks 元数据
    ...
    kb = KnowledgeBase(course_id)
    for d in docs:
        kb.add_document(d.page_content, source=d.metadata.get("source"))  # 向量化入索引
    return {"doc_id": doc_row.id, "chunk_num": len(docs)}
```

知识块切分参数可根据课程内容调整，重叠区间的设置保证了相邻知识块衔接的完整性，提升了检索召回效果。教师知识库管理界面如图 5.3 所示，可查看课程已入库文档及其知识块数量。

【截图：图5.3 知识库管理界面】

### 5.2.4 作业批改模块实现

作业批改模块面向教师，对学生作业进行 AI 辅助批改。系统以固定结构的系统提示引导批改 Agent，要求其对作业作答按照统一评分标准输出 JSON 结构：包含百分制得分（score）与针对知识点的评语（feedback）。批改完成后，系统创建批改记录写入数据库，并把作业提交状态置为"已批改"。核心实现示意如下：

```python
def grade(content):
    msgs = [SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"请批改以下学生作业：\n---\n{content}\n---")]
    model = llm.chat_model()
    resp = model.invoke(msgs)
    data = json.loads(re.search(r"\{.*\}", resp.content, re.S).group(0))
    return {"score": int(data.get("score", 0)),
            "feedback": str(data.get("feedback", ""))}
```

通过限定输出为 JSON 结构，系统能够稳定地从模型回复中解析出得分与评语，进而实现结构化的批改记录存储。教师批改界面如图 5.4 所示，可查看作业提交内容、AI 评分与评语。

【截图：图5.4 作业批改界面（含 AI 评分与评语）】

### 5.2.5 智能出题模块实现

智能出题模块面向教师，依据知识点、数量与难度批量生成试题。系统引导出题 Agent 以 JSON 数组形式生成结构化的试题，包含题型（选择、填空、简答）、题干、选项、参考答案与难度等级。生成结果通过正则从模型回复中提取 JSON 数组，逐条写入试题库。核心实现示意如下：

```python
def generate_questions(topic, num=3, difficulty=3):
    msgs = [SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"请生成 {num} 道关于「{topic}」的《数据结构》试题，难度{difficulty}级")]
    resp = llm.chat_model().invoke(msgs)
    data = json.loads(re.search(r"\[.*\]", resp.content, re.S).group(0))
    return data
```

教师出题界面如图 5.5 所示，教师设置课程、知识点、题量与难度后可批量生成试题，并查看试题库中的题干、题型与难度等信息。

【截图：图5.5 智能出题界面（含试题库展示）】

### 5.2.6 学情看板模块实现

学情看板模块面向教师与管理员，通过数据库聚合查询统计课程的整体学情。系统对选课人数、作业提交数量、已批改数量、平均得分、知识文档数量、试题数量与答疑消息数量等指标进行统计，并以看板形式呈现。核心实现示意如下：

```python
def course_stats(course_id, db, user):
    total_students = db.query(func.count(m.Enrollment.id)).filter(...).scalar()
    submission_count = db.query(func.count(m.Submission.id)).join(...).scalar()
    graded_count    = db.query(func.count(m.GradingRecord.id)).join(...).scalar()
    avg_score       = db.query(func.avg(m.GradingRecord.score)).join(...).scalar()
    return {"total_students": total_students, "submission_count": submission_count,
            "graded_count": graded_count, "avg_score": round(float(avg_score), 1),
            "question_count": ..., "doc_count": ..., "chat_count": ...}
```

学情看板界面如图 5.6 所示，集中展示课程的各项统计数据，帮助教师快速掌握课程整体教学与学习情况。

【截图：图5.6 学情看板界面】

## 5.3 系统测试

### 5.3.1 测试方法

系统测试主要采用黑盒测试与白盒测试相结合的方法。黑盒测试将程序视为黑盒，不考虑内部实现，通过给定的输入验证输出是否符合预期，重点覆盖各模块的功能点与边界情况。白盒测试在单元层面针对关键逻辑进行验证，例如来源解析、知识库切分、路由判断等函数。系统还编写了基于 pytest 的自动化单元测试，对核心逻辑进行回归保护。

### 5.3.2 功能测试

功能测试覆盖系统的主要功能点，包括身份认证、智能答疑、知识库入库、作业批改、智能出题与学情统计等。部分测试用例及结果如表 5.1 所示。

【表5.1 系统功能测试用例表】

测试覆盖了三类角色的关键流程，包括学生登录与答疑会话、教师上传知识库、AI 批改作业、批量生成试题、以及管理员查看看板与配置等，均验证通过。此外，自动化单元测试对来源解析函数、知识库切分方法、选项格式化函数、智能体路由函数等核心逻辑进行了验证，共 11 项测试全部通过。

## 5.4 本章小结

本章对系统的实现进行了说明。介绍了系统的开发环境与运行环境，按认证管理、智能答疑、知识库管理、作业批改、智能出题、学情看板等模块，结合页面与核心代码逻辑阐述了各功能的实现过程，最后介绍了系统的测试方法与功能测试结果。测试结果表明，系统各模块功能正确、流程完整，具备良好的可用性与稳定性。