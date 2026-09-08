# 功能需求分析与可行性评估

> 评估日期：2025 年  
> 项目：基于 Agent 的课程助教系统  
> 评估维度：用户价值 / 技术可行性 / 实现成本 / 优先级

---

## 📊 需求总览

| 序号 | 需求名称 | 类型 | 优先级 | 复杂度 | 建议周期 |
|------|----------|------|--------|--------|----------|
| 1 | Q&A 聊天记录删除 | 功能优化 | P1 | 低 | 0.5 天 |
| 2 | 多课程管理 | 核心功能 | P0 | 中 | 2 天 |
| 3 | 多老师学生关系 | 核心功能 | P0 | 中 | 3 天 |
| 4 | Agent 配置页面 | 功能增强 | P1 | 中 | 2 天 |
| 5 | RAG 知识预览 | 可视化 | P2 | 高 | 4 天 |
| 6 | 学生答题页面 | 新功能 | P1 | 高 | 5 天 |
| 7 | 移除难度评级 | 简化 | P2 | 低 | 0.5 天 |
| 8 | 题目删除功能 | 功能优化 | P1 | 低 | 0.5 天 |
| 9 | 注册页背景优化 | UI 优化 | P3 | 低 | 0.5 天 |
| 10 | 日志系统 | 基础设施 | P1 | 中 | 2 天 |

---

## 🔍 逐项分析

### 1️⃣ Q&A 历史聊天记录删除

**用户意图：**
- 学生/老师希望清理聊天历史（隐私保护）
- 删除单条或批量删除会话记录
- 可能包含"清空全部"需求

**技术方案：**
```python
# API 设计
DELETE /api/chat/history/{session_id}     # 删除单条会话
DELETE /api/chat/history?course_id={id}   # 删除课程全部会话
DELETE /api/chat/history/all              # 清空全部

# 数据库操作
DELETE FROM chat_sessions WHERE user_id = ? AND session_id = ?
DELETE FROM chat_messages WHERE session_id = ?
```

**可行性：** ✅ 高
- 技术难度：低（标准 CRUD 操作）
- 数据影响：级联删除消息记录
- 风险点：误删恢复（建议增加软删除/回收站）

**实现建议：**
```
前端：
- 会话列表添加删除按钮（hover 显示）
- 批量选择 + 批量删除
- 删除前二次确认弹窗
- 删除后 Toast 提示 + 可撤销（3 秒）

后端：
- 软删除标记 is_deleted
- 定时任务清理 30 天前软删除记录
- 操作日志记录（谁删除了什么）
```

**优先级：** P1 - 用户隐私需求，影响体验

---

### 2️⃣ 准备多门课

**用户意图：**
- 一个老师可以教授多门课程
- 学生可以选修多门课程
- 需要课程切换/管理入口

**技术方案：**
```python
# 现有模型扩展
class Course(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey('users.id'))  # 主讲老师
    co_teacher_ids = Column(JSON)  # 协作老师 [id1, id2]
    students = relationship('User', secondary='course_enrollments')

class CourseEnrollment(Base):
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    role = Column(String)  # 'teacher' | 'student' | 'assistant'
    enrolled_at = Column(DateTime)
```

**可行性：** ✅ 高
- 技术难度：中（需要重构部分关联）
- 数据影响：需要迁移现有数据
- 风险点：权限边界（跨课程数据隔离）

**实现建议：**
```
数据库变更：
1. courses 表添加 teacher_id 字段
2. 新增 course_enrollments 关联表
3. 迁移现有数据（默认课程 → 新结构）

API 变更：
GET /api/courses              # 获取用户所有课程（根据角色过滤）
GET /api/courses/{id}         # 课程详情
POST /api/courses             # 创建课程（老师）
PUT /api/courses/{id}         # 更新课程
DELETE /api/courses/{id}      # 删除课程

UI 变更：
- 顶部导航添加课程切换下拉框
- 课程管理页面（老师可见）
- 我的课程列表（学生可见）
```

**优先级：** P0 - 核心功能，必须实现

---

### 3️⃣ 多老师学生关系（各自对应课程）

**用户意图：**
```
老师 A → 课程 A → 学生群体 A
老师 B → 课程 B → 学生群体 B
学生 X 可以选修 课程 A + 课程 B
```

**技术方案：**
```python
# RBAC 权限模型扩展
class UserRole(Base):
    __tablename__ = 'user_roles'
    
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    role = Column(String)  # 'owner' | 'teacher' | 'student' | 'assistant'
    
    # 权限矩阵
    permissions = {
        'owner': ['all'],
        'teacher': ['view', 'edit', 'grade', 'chat', 'rag'],
        'student': ['view', 'chat', 'submit']
    }

# API 权限装饰器
def require_course_role(required_roles):
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            course_id = kwargs.get('course_id')
            user_id = current_user.id
            
            # 查询用户在当前课程的角色
            role = await get_user_course_role(user_id, course_id)
            
            if role not in required_roles:
                raise HTTPException(403, "权限不足")
            
            return await f(*args, **kwargs)
        return wrapped
    return decorator
```

**可行性：** ✅ 高
- 技术难度：中（权限系统重构）
- 数据影响：需要角色关联表
- 风险点：历史数据权限映射

**实现建议：**
```
权限检查点：
- 聊天页面：只允许查看本课程聊天记录
- 作业批改：只能批改本课程作业
- 试题生成：只能访问本课程题库
- RAG 知识库：课程隔离

UI 体现：
- 课程卡片显示角色标签（老师/学生）
- 不同角色显示不同功能入口
- 老师可见"课程管理"，学生可见"我的学习"
```

**优先级：** P0 - 核心权限模型，必须实现

---

### 4️⃣ Agent 设置页面（多 AI 模型配置）

**用户意图：**
- 支持配置多个 AI 服务商（DeepSeek / Qwen / ChatGLM 等）
- 每个课程可独立选择 AI 模型
- API Key 安全管理

**技术方案：**
```python
# 配置模型
class AIProvider(Base):
    __tablename__ = 'ai_providers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)  # 'DeepSeek' | 'Qwen' | 'ChatGLM'
    api_key = Column(EncryptedString)  # 加密存储
    base_url = Column(String)
    model_name = Column(String)  # 'deepseek-chat' | 'qwen-plus'
    is_active = Column(Boolean)
    course_id = Column(Integer, ForeignKey('courses.id'))

# 配置页面数据结构
{
  "providers": [
    {
      "id": 1,
      "name": "DeepSeek",
      "api_key": "sk-****",  # 前端脱敏显示
      "model": "deepseek-chat",
      "is_default": true,
      "quota_remaining": 8500  # 剩余额度
    },
    {
      "id": 2,
      "name": "通义千问",
      "api_key": "sk-****",
      "model": "qwen-plus",
      "is_default": false
    }
  ]
}
```

**可行性：** ✅ 高
- 技术难度：中（加密存储 + 多服务商适配）
- 数据安全：API Key 需要加密存储
- 风险点：Key 泄露风险

**实现建议：**
```
安全要求：
- API Key 使用 Fernet 加密存储
- 前端只显示后 4 位（sk-****abcd）
- 支持 Key 有效性测试（点击"测试连接"）
- 使用量统计（Token 消耗 / 剩余额度）

UI 设计：
┌─────────────────────────────────────────┐
│  AI 模型配置                              │
├─────────────────────────────────────────┤
│  + 添加服务商                            │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │ DeepSeek Chat              ✅   │    │
│  │ sk-****abcd        [编辑][删除] │    │
│  │ 剩余额度：8500 Token            │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ 通义千问 Qwen              ⭕   │    │
│  │ sk-****efgh        [编辑][删除] │    │
│  │ 剩余额度：未知                  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

Agent 切换逻辑：
- 默认使用第一个启用的服务商
- 失败时自动切换到备用服务商
- 记录每次请求使用的服务商（用于统计）
```

**优先级：** P1 - 增强系统灵活性

---

### 5️⃣ RAG 知识预览（离散图可视化）

**用户意图：**
- 查看已上传的知识文档
- 知识点之间的关系可视化
- 知识图谱/离散图展示

**技术方案：**
```python
# 知识片段关系
class KnowledgeFragment(Base):
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    course_id = Column(Integer, ForeignKey('courses.id'))
    document_id = Column(Integer, ForeignKey('documents.id'))
    
    # 向量嵌入
    embedding = Column(ARRAY(Float))  # FAISS 索引
    
    # 关系（可选，用于知识图谱）
    related_fragments = relationship(
        'KnowledgeFragment',
        secondary='fragment_relations',
        backref='related_to'
    )

class FragmentRelation(Base):
    __tablename__ = 'fragment_relations'
    
    source_id = Column(Integer, ForeignKey('knowledge_fragments.id'))
    target_id = Column(Integer, ForeignKey('knowledge_fragments.id'))
    relation_type = Column(String)  # 'prerequisite' | 'similar' | 'reference'
    confidence = Column(Float)  # 关系置信度
```

**可行性：** ⚠️ 中
- 技术难度：高（图可视化 + 关系提取）
- 前端库：ECharts Graph / D3.js / G6
- 风险点：大数据量渲染性能

**实现建议：**
```
方案 A - 简单版（推荐 MVP）
- 列表展示知识片段
- 搜索 + 标签过滤
- 点击展开详情（来源文档 + 向量相似度）

方案 B - 进阶版
- 力导向图展示知识点关系
- 节点大小 = 被引用次数
- 边颜色 = 关系类型
- 支持缩放/拖拽/搜索

ECharts Graph 配置示例：
option = {
  series: [{
    type: 'graph',
    layout: 'force',
    data: [
      { name: '二叉树', value: 10, symbolSize: 50 },
      { name: '遍历算法', value: 8, symbolSize: 40 },
      { name: '时间复杂度', value: 6, symbolSize: 30 }
    ],
    links: [
      { source: '二叉树', target: '遍历算法' },
      { source: '遍历算法', target: '时间复杂度' }
    ],
    roam: true,  // 支持缩放平移
    label: { show: true, position: 'right' }
  }]
}

实现路径：
1. 后端提供知识片段 API（含相似度）
2. 前端用 ECharts Graph 渲染
3. 点击节点显示片段详情
4. 支持搜索高亮路径
```

**优先级：** P2 - 锦上添花功能

---

### 6️⃣ 学生答题页面（参考洛谷）

**用户意图：**
- 在线编程/答题界面
- 实时提交 + 自动判分
- 题目描述 + 代码编辑器 + 测试结果

**技术方案：**
```python
# 答题记录模型
class Submission(Base):
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    
    # 提交内容
    code = Column(Text)  # 学生代码
    language = Column(String)  # 'python' | 'cpp' | 'java'
    
    # 判分结果
    status = Column(String)  # 'AC' | 'WA' | 'TLE' | 'MLE' | 'RE' | 'CE'
    score = Column(Integer)
    execution_time = Column(Integer)  # ms
    memory_usage = Column(Integer)  # KB
    error_message = Column(Text)
    
    # 判题详情
    test_cases = Column(JSON)  # [{id, input, expected, actual, passed}]
    
    submitted_at = Column(DateTime)
    judged_at = Column(DateTime)
```

**可行性：** ⚠️ 中
- 技术难度：高（代码沙箱 + 安全执行）
- 安全要求：代码执行隔离（Docker 容器）
- 风险点：恶意代码执行风险

**实现建议：**
```
判题系统架构：
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  学生提交代码  │ -> │  判题队列    │ -> │  Docker 沙箱   │
│  (前端)      │    │  (Redis)    │    │  (隔离执行)   │
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                                              v
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  返回结果    │ <- │  结果存储    │ <- │  测试用例对比 │
│  (前端)      │    │  (MySQL)    │    │  (判分逻辑)   │
└──────────────┘    └──────────────┘    └──────────────┘

UI 布局（参考洛谷）：
┌─────────────────────────────────────────────────────┐
│  题目：线性表的实现                    [提交代码]    │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │                 │  │  题目描述               │  │
│  │   代码编辑器     │  │  - 问题说明             │  │
│  │   (Monaco)      │  │  - 输入格式             │  │
│  │                 │  │  - 输出格式             │  │
│  │                 │  │  - 样例                 │  │
│  │                 │  │  - 提示                 │  │
│  └─────────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  测试结果                                            │
│  ┌──────────────────────────────────────────────┐  │
│  │ 测试点 | 状态 | 耗时 | 内存 | 得分           │  │
│  ├──────────────────────────────────────────────┤  │
│  │ #1     | ✅ AC | 12ms | 256KB | 10          │  │
│  │ #2     | ✅ AC | 15ms | 260KB | 10          │  │
│  │ #3     | ❌ WA | 8ms  | 248KB | 0           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

安全方案：
- 使用 Docker 容器隔离代码执行
- 限制 CPU/内存/执行时间
- 禁用网络访问
- 白名单系统调用
- 超时自动终止

MVP 方案（简化）：
- 先支持客观题（选择/填空）自动判分
- 编程题使用预定义测试用例对比
- 暂不实现代码沙箱，使用 API 调用第三方判题服务
```

**优先级：** P1 - 核心学习功能，但实现复杂度高

---

### 7️⃣ 去掉难度评级（5 个小蓝点）

**用户意图：**
- 移除题目列表/卡片上的 **5 个小蓝点难度指示器**
- 纯 UI 层面隐藏，不影响数据库字段
- 简化视觉干扰

**技术方案：**
```css
/* 需要隐藏的元素 */
.question-dots,
.difficulty-indicator,
.difficulty-dots {
  display: none !important;
}

/* 或者移除生成逻辑 */
<!-- 删除前 -->
<div class="question-dots">
  <span class="dot active"></span>
  <span class="dot active"></span>
  <span class="dot active"></span>
  <span class="dot"></span>
  <span class="dot"></span>
</div>

<!-- 删除后 -->
<!-- 直接移除整段 -->
```

**可行性：** ✅ 高
- 技术难度：极低（CSS 隐藏 or HTML 移除）
- 数据影响：无（difficulty 字段保留，仅不显示）
- 风险点：无

**实现建议：**
```
需要修改的文件（搜索 "difficulty" 或 "dot"）：
- app/templates/questions.html      - 题目列表页
- app/templates/grading.html        - 批改页面
- app/templates/components/question-card.html - 题目卡片组件
- app/static/css/questions.css      - 相关样式可保留或删除

查找关键词：
grep -r "difficulty-dots" app/templates/
grep -r "question-dots" app/templates/
grep -r "<span class=\"dot" app/templates/
```

**优先级：** P2 - 纯 UI 优化，10 分钟可完成

---

### 8️⃣ 题目可以删除

**用户意图：**
- 老师可以删除自己创建的题目
- 软删除（防止误删）

**技术方案：**
```python
# 软删除字段
class Question(Base):
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey('users.id'))

# API
DELETE /api/questions/{id}  # 软删除
POST /api/questions/{id}/restore  # 恢复

# 查询过滤
questions = session.query(Question).filter(
    Question.is_deleted == False
)
```

**可行性：** ✅ 高
- 技术难度：低（标准软删除模式）
- 数据影响：需要添加字段
- 风险点：被引用的题目（作业/考试）需要处理

**实现建议：**
```
删除前检查：
- 题目是否被作业引用？
- 题目是否被考试引用？
- 有引用时提示"无法删除，已被使用"或"删除后相关作业将跳过此题"

UI 交互：
- 题目列表每行添加删除按钮（红色）
- 点击后弹出确认框
- 删除后显示"已删除"Toast
- 回收站页面（可选，查看/恢复已删除）
```

**优先级：** P1 - 基本 CRUD 需求

---

### 9️⃣ 注册页面背景图修改

**用户意图：**
- 优化注册页视觉体验
- 更换背景图（更专业/美观）

**技术方案：**
```css
/* 现有 */
.register-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 建议替换为 */
.register-page {
  background: 
    linear-gradient(135deg, rgba(91, 127, 255, 0.9) 0%, rgba(139, 92, 246, 0.9) 100%),
    url('/static/images/bg-abstract.svg');
  background-size: cover;
  background-position: center;
}
```

**可行性：** ✅ 高
- 技术难度：低（CSS 变更）
- 设计建议：使用浅色抽象几何图形（与整体主题一致）
- 风险点：无

**实现建议：**
```
推荐方案：
- 使用 SVG 抽象几何背景（轻量）
- 或渐变色 + 粒子动画（动态效果）
- 保持与登录页一致风格

资源位置：
- app/static/images/register-bg.svg
- app/static/css/auth.css
```

**优先级：** P3 - 视觉优化，不影响功能

---

### 🔟 日志系统导入

**用户意图：**
- 系统操作日志记录
- 用户行为追踪
- 异常日志收集

**技术方案：**
```python
# 日志模型
class OperationLog(Base):
    __tablename__ = 'operation_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String)  # 'LOGIN' | 'DELETE_QUESTION' | 'SUBMIT_ASSIGNMENT'
    resource_type = Column(String)  # 'question' | 'assignment' | 'chat'
    resource_id = Column(Integer)
    
    # 请求信息
    ip_address = Column(String)
    user_agent = Column(String)
    request_method = Column(String)
    request_path = Column(String)
    
    # 操作详情
    old_value = Column(JSON)  # 修改前的值
    new_value = Column(JSON)  # 修改后的值
    
    # 结果
    status = Column(String)  # 'SUCCESS' | 'FAILED'
    error_message = Column(Text)
    
    created_at = Column(DateTime)

# 日志装饰器
def log_operation(action: str, resource_type: str = None):
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            start_time = time.time()
            try:
                result = await f(*args, **kwargs)
                
                # 记录成功日志
                await create_log(
                    action=action,
                    status='SUCCESS',
                    duration=time.time() - start_time
                )
                return result
            except Exception as e:
                # 记录失败日志
                await create_log(
                    action=action,
                    status='FAILED',
                    error_message=str(e)
                )
                raise
        return wrapped
    return decorator

# 使用示例
@log_operation(action='DELETE_QUESTION', resource_type='question')
async def delete_question(question_id: int):
    ...
```

**可行性：** ✅ 高
- 技术难度：中（日志切面 + 存储优化）
- 存储方案：MySQL（结构化）+ 文件日志（原始日志）
- 风险点：日志量过大（需要定期清理）

**实现建议：**
```
日志级别：
- INFO: 常规操作（登录/提交作业/聊天）
- WARNING: 异常操作（权限不足/重复提交）
- ERROR: 系统错误（API 失败/数据库异常）

日志查看页面：
┌─────────────────────────────────────────────────────┐
│  系统日志                              [导出] [清理] │
├─────────────────────────────────────────────────────┤
│  时间范围：[最近 7 天 ▼]  操作类型：[全部 ▼]  用户：[__] │
├─────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐  │
│  │ 时间       | 用户   | 操作        | 状态     │  │
│  ├──────────────────────────────────────────────┤  │
│  │ 10:30:25  | 张三  | 删除题目    | ✅ 成功  │  │
│  │ 10:28:12  | 李四  | 提交作业    | ✅ 成功  │  │
│  │ 10:25:08  | 系统  | API 错误     | ❌ 失败  │  │
│  └──────────────────────────────────────────────┘  │
│  共 1256 条记录                    [1] [2] [3] ...  │
└─────────────────────────────────────────────────────┘

配置建议：
- 日志保留 90 天
- 单表超过 100 万条自动归档
- 敏感操作（删除/修改）必须记录
```

**优先级：** P1 - 运维和审计必需

---

## 📋 实施建议

### 阶段一：核心功能（2 周）
| 需求 | 工时 | 依赖 |
|------|------|------|
| 2. 多课程管理 | 2 天 | - |
| 3. 多老师学生关系 | 3 天 | 2 |
| 10. 日志系统 | 2 天 | - |
| 1. 聊天记录删除 | 0.5 天 | - |
| 8. 题目删除 | 0.5 天 | - |

### 阶段二：功能增强（2 周）
| 需求 | 工时 | 依赖 |
|------|------|------|
| 4. Agent 配置页面 | 2 天 | 2 |
| 6. 学生答题页面 | 5 天 | 2, 3 |
| 7. 移除难度评级 | 0.5 天 | - |
| 9. 注册页背景 | 0.5 天 | - |

### 阶段三：可视化（2 周）
| 需求 | 工时 | 依赖 |
|------|------|------|
| 5. RAG 知识预览 | 4 天 | 2 |
| 6. 答题页面判题系统 | 3 天 | 6 |

---

## ⚠️ 风险提示

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 多课程数据隔离 | 高 | 严格测试权限边界 |
| 代码沙箱安全 | 高 | 使用 Docker 隔离 + 资源限制 |
| API Key 安全 | 中 | 加密存储 + 访问审计 |
| 知识图谱性能 | 中 | 限制节点数量 + 分页加载 |
| 日志存储膨胀 | 低 | 定期归档 + 压缩 |

---

## ✅ 推荐优先级排序

```
P0（必须实现）：
├─ 2. 多课程管理
└─ 3. 多老师学生关系

P1（重要功能）：
├─ 10. 日志系统
├─ 4. Agent 配置页面
├─ 6. 学生答题页面（MVP 版）
├─ 1. 聊天记录删除
└─ 8. 题目删除

P2（锦上添花）：
├─ 5. RAG 知识预览
└─ 7. 移除难度评级

P3（视觉优化）：
└─ 9. 注册页背景修改
```

---

> **总体评估：** 需求合理，技术可行，建议分三阶段实施  
> **预计总工时：** 约 15-20 人天  
> **关键路径：** 多课程管理 → 权限系统 → 答题页面
