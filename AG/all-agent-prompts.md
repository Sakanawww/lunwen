# 课程助教系统 - 完整开发提示词集合

> 直接复制每个模块的提示词发送给执行 Agent  
> 共 10 个功能模块 + 通用模板

---

## 📋 使用说明

1. **选择模块** → 找到对应提示词
2. **完整复制** → 包含【】内所有要求
3. **发送给 Agent** → 开始执行
4. **验收代码** → 按验收标准检查

---

## 模块 1：数据库迁移（多课程架构）

```
请完成课程助教系统的数据库架构改造，支持多课程管理。

【项目背景】
- 现有单课程系统，需改造为多课程架构
- 技术栈：Python 3.11 + FastAPI + SQLAlchemy + MySQL 8
- 已有用户表 (users)，需添加课程关联

【任务目标】
1. 创建课程表（courses）
2. 创建课程用户关联表（course_users）- 实现 RBAC 权限
3. 为现有表添加 course_id 外键：
   - questions
   - chat_sessions
   - knowledge_fragments
   - assignments
   - submissions
4. 编写数据迁移脚本（将现有数据迁移到默认课程）

【数据模型要求】

1. courses 表：
```sql
CREATE TABLE courses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  code VARCHAR(50) UNIQUE,
  description TEXT,
  teacher_id INT NOT NULL,
  semester VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (teacher_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

2. course_users 表（核心权限表）：
```sql
CREATE TABLE course_users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  course_id INT NOT NULL,
  user_id INT NOT NULL,
  role ENUM('owner', 'teacher', 'assistant', 'student') NOT NULL,
  enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_course_user (course_id, user_id),
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

3. 现有表添加 course_id：
```sql
ALTER TABLE questions ADD COLUMN course_id INT;
ALTER TABLE questions ADD FOREIGN KEY (course_id) REFERENCES courses(id);

ALTER TABLE chat_sessions ADD COLUMN course_id INT;
ALTER TABLE chat_sessions ADD FOREIGN KEY (course_id) REFERENCES courses(id);

ALTER TABLE knowledge_fragments ADD COLUMN course_id INT;
ALTER TABLE knowledge_fragments ADD FOREIGN KEY (course_id) REFERENCES courses(id);

ALTER TABLE assignments ADD COLUMN course_id INT;
ALTER TABLE assignments ADD FOREIGN KEY (course_id) REFERENCES courses(id);

ALTER TABLE submissions ADD COLUMN course_id INT;
ALTER TABLE submissions ADD FOREIGN KEY (course_id) REFERENCES courses(id);
```

【输出文件清单】
1. app/models/course.py - 课程模型类
2. app/models/course_user.py - 课程用户关联模型
3. alembic/versions/[timestamp]_add_course_architecture.py - Alembic 迁移脚本
4. scripts/migrate_to_multi_course.py - 数据迁移脚本（现有数据→默认课程）
5. tests/test_models.py - 模型单元测试

【验收标准】
- [ ] 迁移可执行 upgrade 和 downgrade
- [ ] 外键约束生效（删除课程级联删除关联数据）
- [ ] 现有数据不丢失（全部迁移到默认课程）
- [ ] 创建索引（course_id, user_id 复合索引）
- [ ] 所有模型继承 Base 类，支持序列化

【注意事项】
- 使用 Alembic 进行迁移
- 迁移脚本必须有 downgrade 方法
- 默认课程 ID=1，名称"默认课程"
- 迁移前备份数据
```

---

## 模块 2：权限系统（RBAC）

```
请实现基于角色的课程权限系统（RBAC）。

【需求说明】
四种角色权限矩阵：
- owner: 所有权限（包括删除课程、转移所有权）
- teacher: 查看/编辑/批改/聊天/RAG/题目管理
- assistant: 查看/批改/聊天（不可删除）
- student: 查看/聊天/提交作业

【实现内容】

1. 权限检查装饰器：
```python
from functools import wraps
from fastapi import HTTPException, status

def require_course_permission(required_roles: list):
    """
    课程权限检查装饰器
    required_roles: ['owner', 'teacher'] 等
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数获取 db, course_id, current_user
            db = kwargs.get('db') or next(arg for arg in args if isinstance(arg, Session))
            course_id = kwargs.get('course_id') or next((arg for arg in args if isinstance(arg, int)), None)
            current_user = kwargs.get('current_user') or next((arg for arg in args if hasattr(arg, 'id')), None)
            
            # 检查权限
            from app.models.course_user import CourseUser
            course_user = db.query(CourseUser).filter(
                CourseUser.course_id == course_id,
                CourseUser.user_id == current_user.id
            ).first()
            
            if not course_user or course_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

2. 权限检查辅助函数：
```python
async def check_course_permission(
    db: Session,
    course_id: int,
    user_id: int,
    required_roles: list
) -> CourseUser:
    """
    检查用户在指定课程的权限
    返回：CourseUser 对象（包含角色信息）
    异常：403 权限不足
    """
```

3. 权限常量定义：
```python
# app/core/permissions.py

class Permission:
    # 课程权限
    VIEW_COURSE = 'view_course'
    EDIT_COURSE = 'edit_course'
    DELETE_COURSE = 'delete_course'
    
    # 题目权限
    VIEW_QUESTION = 'view_question'
    CREATE_QUESTION = 'create_question'
    EDIT_QUESTION = 'edit_question'
    DELETE_QUESTION = 'delete_question'
    
    # 作业权限
    VIEW_ASSIGNMENT = 'view_assignment'
    CREATE_ASSIGNMENT = 'create_assignment'
    GRADE_ASSIGNMENT = 'grade_assignment'
    
    # 聊天权限
    VIEW_CHAT = 'view_chat'
    SEND_MESSAGE = 'send_message'
    
    # RAG 权限
    VIEW_RAG = 'view_rag'
    UPLOAD_RAG = 'upload_rag'

# 角色权限映射
ROLE_PERMISSIONS = {
    'owner': [Permission.__dict__[p] for p in Permission.__dict__ if not p.startswith('_')],
    'teacher': [Permission.VIEW_COURSE, Permission.VIEW_QUESTION, Permission.CREATE_QUESTION, 
                Permission.GRADE_ASSIGNMENT, Permission.SEND_MESSAGE, Permission.VIEW_RAG, Permission.UPLOAD_RAG],
    'assistant': [Permission.VIEW_COURSE, Permission.VIEW_QUESTION, Permission.GRADE_ASSIGNMENT, 
                  Permission.SEND_MESSAGE, Permission.VIEW_RAG],
    'student': [Permission.VIEW_COURSE, Permission.VIEW_QUESTION, Permission.SEND_MESSAGE]
}
```

【单元测试要求】
```python
# tests/test_permissions.py

def test_owner_can_access_all():
    """owner 角色可以访问所有接口"""
    
def test_student_cannot_delete():
    """student 角色删除操作返回 403"""
    
def test_cross_course_access_forbidden():
    """跨课程访问被禁止（A 课程学生不能访问 B 课程数据）"""
    
def test_no_course_enrollment():
    """未加入课程的用户访问返回 403"""
```

【输出文件】
1. app/core/permissions.py - 权限定义和检查工具
2. app/api/middleware.py - 权限中间件
3. tests/test_permissions.py - 权限测试用例
4. docs/permission_matrix.md - 权限矩阵文档

【验收标准】
- [ ] 所有课程相关 API 必须通过权限检查
- [ ] 禁止通过遍历 course_id 访问其他课程数据
- [ ] 越权访问记录日志（warning 级别）
- [ ] 单元测试覆盖率 > 90%
```

---

## 模块 3：课程管理 API

```
请实现课程管理的完整 API 接口。

【API 列表】

1. 获取我的课程列表
GET /api/courses?skip=0&limit=50
响应：
{
  "total": 10,
  "data": [
    {
      "id": 1,
      "name": "数据结构",
      "code": "CS101",
      "description": "计算机核心课程",
      "teacher_name": "张老师",
      "user_role": "teacher",
      "student_count": 45,
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}

2. 创建课程
POST /api/courses
请求：
{
  "name": "算法分析",
  "code": "CS102",
  "description": "算法课程",
  "semester": "2025 春"
}

3. 课程详情
GET /api/courses/{id}

4. 更新课程
PUT /api/courses/{id}

5. 删除课程（软删除）
DELETE /api/courses/{id}

6. 添加课程用户
POST /api/courses/{id}/users
请求：
{
  "user_id": 123,
  "role": "student"  // owner|teacher|assistant|student
}

7. 获取课程用户列表
GET /api/courses/{id}/users?role=student

8. 移除课程用户
DELETE /api/courses/{id}/users/{user_id}

【业务规则】
1. 创建课程时，创建者自动成为 owner
2. 删除课程需检查是否有活跃学生（有学生时提示"请先移除所有学生"）
3. 只有 owner 可以删除课程
4. 只有 owner/teacher 可以添加/移除用户
5. 用户只能看到自己有权限的课程

【Pydantic Schema】
```python
# app/schemas/course.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    semester: Optional[str] = Field(None, max_length=50)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    teacher_name: str
    user_role: str  # 当前用户在课程中的角色
    student_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

【输出文件】
1. app/api/courses.py - 课程 API 实现
2. app/schemas/course.py - Pydantic 模型
3. tests/test_courses.py - API 测试
4. app/core/dependencies.py - 依赖注入（get_current_course）

【验收标准】
- [ ] 所有接口通过权限测试
- [ ] 课程列表按更新时间排序
- [ ] 软删除后数据不可见（is_active=False）
- [ ] 添加课程时自动创建 course_users 记录（owner 角色）
```

---

## 模块 4：Agent 配置页面（多 AI 服务商）

```
请实现 AI 服务商配置页面，支持多模型接入。

【功能需求】

1. 服务商管理
   - 添加 AI 服务商（DeepSeek / 通义千问 / ChatGLM / 自定义）
   - 编辑服务商配置
   - 删除服务商
   - 设置默认服务商

2. 配置项
   - 服务商名称（如：DeepSeek Chat）
   - API Key（加密存储，前端脱敏显示 sk-****abcd）
   - Base URL（如：https://api.deepseek.com）
   - 模型名称（如：deepseek-chat）
   - 额度限制（可选，用于统计）
   - 是否默认（boolean）

3. 连接测试
   - 点击"测试连接"按钮
   - 调用服务商 API 验证 Key 有效性
   - 显示测试结果（成功/失败 + 错误信息）

【安全要求】
1. API Key 使用 Fernet 加密存储
```python
from cryptography.fernet import Fernet
import os

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)

# 加密
encrypted_key = cipher.encrypt(api_key.encode())

# 解密
decrypted_key = cipher.decrypt(encrypted_key).decode()
```

2. 前端脱敏显示
```python
# API 返回时
api_key_masked = f"sk-****{original_key[-4:]}"
```

3. 操作日志记录（谁修改了 Key）

【API 接口】
GET    /api/agents/providers?course_id={id}  # 获取服务商列表
POST   /api/agents/providers                 # 添加服务商
PUT    /api/agents/providers/{id}            # 更新服务商
DELETE /api/agents/providers/{id}            # 删除服务商
POST   /api/agents/providers/{id}/test       # 测试连接

【前端页面要求】
1. 服务商卡片网格布局（响应式）
2. 默认服务商标识（蓝色徽章）
3. 测试连接按钮（实时反馈）
4. 剩余额度显示（如已配置）
5. 添加/编辑弹窗

【输出文件】
1. app/api/agents.py - Agent 配置 API
2. app/models/ai_provider.py - 数据模型
3. app/schemas/agent.py - Pydantic 模型
4. app/templates/agent_settings.html - 配置页面
5. app/static/js/agents.js - 前端交互逻辑
6. app/static/css/agents.css - 页面样式

【验收标准】
- [ ] API Key 加密存储（数据库不可明文）
- [ ] 前端不传输明文 Key（仅传输加密后的值）
- [ ] 测试连接功能正常（调用真实 API）
- [ ] 默认服务商切换正常
- [ ] 删除前检查是否被使用
```

---

## 模块 5：删除功能（聊天 + 题目）

```
请实现聊天记录和题目的删除功能（软删除 + 回收站）。

【功能 1：聊天记录删除】

API 接口：
1. 删除单条会话
DELETE /api/chat/sessions/{session_id}

2. 批量删除
DELETE /api/chat/sessions?ids=1,2,3

3. 获取已删除会话（回收站）
GET /api/chat/sessions/deleted

4. 恢复已删除会话
POST /api/chat/sessions/{session_id}/restore

数据库变更：
```sql
ALTER TABLE chat_sessions ADD COLUMN (
  is_deleted BOOLEAN DEFAULT FALSE,
  deleted_at DATETIME,
  deleted_by INT,
  FOREIGN KEY (deleted_by) REFERENCES users(id)
);
```

前端交互：
- 会话列表每行显示删除按钮（hover 显示）
- 点击删除 → 二次确认弹窗
- 删除后 Toast 提示 + 可撤销（3 秒内点击撤销）
- 回收站页面（查看/恢复/彻底删除）

【功能 2：题目删除】

API 接口：
1. 删除题目
DELETE /api/questions/{question_id}

2. 获取已删除题目
GET /api/questions/deleted?course_id={id}

3. 恢复题目
POST /api/questions/{question_id}/restore

业务规则：
1. 删除前检查引用（是否被作业使用）
```python
# 检查是否被作业引用
has_assignment = db.query(exists().where(
    assignment_questions.c.question_id == question_id
)).scalar()

if has_assignment:
    raise HTTPException(
        400, 
        "该题目已被作业引用，无法删除。请先从作业中移除。"
    )
```

2. 软删除标记
```sql
ALTER TABLE questions ADD COLUMN (
  is_deleted BOOLEAN DEFAULT FALSE,
  deleted_at DATETIME,
  deleted_by INT
);
```

3. 查询时过滤已删除
```python
questions = db.query(Question).filter(
    Question.is_deleted == False
)
```

【前端页面】
1. 回收站页面（/chat/deleted 和 /questions/deleted）
   - 列表显示已删除项目
   - 恢复按钮
   - 彻底删除按钮（二次确认）

2. 删除确认弹窗
```html
<div class="confirm-modal">
  <h3>确认删除</h3>
  <p>删除后可在回收站恢复，确定继续吗？</p>
  <div class="modal-actions">
    <button class="btn-secondary" onclick="closeModal()">取消</button>
    <button class="btn-danger" onclick="confirmDelete()">删除</button>
  </div>
</div>
```

【输出文件】
1. app/api/chat.py - 聊天删除 API
2. app/api/questions.py - 题目删除 API（更新）
3. app/templates/recycle_bin.html - 回收站页面
4. app/static/js/delete.js - 删除交互逻辑
5. alembic/versions/[timestamp]_add_soft_delete.py - 迁移脚本

【验收标准】
- [ ] 删除操作记录日志（谁删除了什么）
- [ ] 回收站支持分页
- [ ] 恢复功能正常
- [ ] 彻底删除后数据不可恢复
- [ ] 批量删除事务处理（要么全成功要么全失败）
```

---

## 模块 6：答题页面（洛谷风格）

```
请实现学生答题页面（参考洛谷风格）。

【页面布局】
┌─────────────────────────────────────────────────────┐
│  顶部导航                                           │
├─────────────────────────────────────────────────────┤
│  题目：[题目名称]                     [提交答案]    │
├──────────────────────┬──────────────────────────────┤
│  题目描述（左）       │  答题区（右）                │
│  - 题目内容          │  - 语言选择（编程题）        │
│  - 输入输出格式      │  - 代码编辑器                │
│  - 样例              │  - 选项（客观题）            │
│                      │  - 文本框（主观题）          │
├──────────────────────┴──────────────────────────────┤
│  测试结果（提交后显示）                              │
│  ┌────────────────────────────────────────────┐    │
│  │ 测试点 1: ✅ AC  12ms  256KB  得分 10     │    │
│  │ 测试点 2: ❌ WA   8ms  248KB  得分 0      │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘

【功能需求】

1. 题型支持
   - 客观题：单选/多选（点击选项）
   - 主观题：文本框作答
   - 编程题：代码编辑器 + 语言选择

2. 代码编辑器
   - 使用 Monaco Editor 或 CodeMirror
   - 语法高亮（Python/C++/Java）
   - 行号显示
   - 自动缩进

3. 提交判题
   - 实时提交（AJAX）
   - 判题状态轮询（pending → grading → graded）
   - 结果显示（AC/WA/TLE/MLE/RE）
   - 测试点详情展开

4. 草稿功能
   - 自动保存到 localStorage
   - 页面刷新不丢失
   - 提交后清空草稿

5. 倒计时提醒（限时作业）
   - 剩余时间显示
   - 最后 5 分钟提醒
   - 超时禁止提交

【API 接口】
POST   /api/submissions         # 提交答案
GET    /api/submissions/{id}    # 获取提交详情
GET    /api/submissions/my      # 我的提交记录
POST   /api/submissions/{id}/cancel  # 取消提交（判题中）

【判题逻辑】
```python
# app/services/judge.py

class JudgeService:
    async def judge_submission(self, submission_id: int):
        """
        判题服务
        1. 获取题目和提交
        2. 根据题型选择判题策略
        3. 返回判题结果
        """
        submission = db.query(Submission).get(submission_id)
        question = submission.question
        
        if question.question_type == 'objective':
            return self.judge_objective(submission, question)
        elif question.question_type == 'programming':
            return await self.judge_programming(submission, question)
        elif question.question_type == 'subjective':
            return await self.judge_subjective(submission, question)
    
    def judge_objective(self, submission, question):
        """客观题：直接对比答案"""
        is_correct = submission.answer_text == question.correct_answer
        return {'score': question.max_score if is_correct else 0}
    
    async def judge_programming(self, submission, question):
        """编程题：调用判题沙箱"""
        # 方案 A：自建 Docker 沙箱
        # 方案 B：调用第三方 API（如：Judge0）
        pass
    
    async def judge_subjective(self, submission, question):
        """主观题：AI 辅助批改"""
        # 调用 LLM 进行语义分析
        pass
```

【前端页面结构】
```html
<!-- app/templates/answer.html -->

<div class="answer-page">
  <!-- 题目信息 -->
  <div class="question-panel">
    <h1>{{ question.title }}</h1>
    <div class="question-meta">
      <span>满分：{{ question.max_score }}分</span>
      <span>限时：{{ question.time_limit }}分钟</span>
    </div>
    
    <!-- 题目描述 -->
    <div class="question-content">
      {{ question.description | safe }}
    </div>
    
    <!-- 输入输出格式 -->
    {% if question.input_format %}
    <div class="format-section">
      <h3>输入格式</h3>
      <pre>{{ question.input_format }}</pre>
    </div>
    {% endif %}
    
    <!-- 样例 -->
    <div class="sample-section">
      <h3>样例</h3>
      <div class="sample-grid">
        <div class="sample-box">
          <div class="sample-title">输入</div>
          <pre>{{ question.sample_input }}</pre>
        </div>
        <div class="sample-box">
          <div class="sample-title">输出</div>
          <pre>{{ question.sample_output }}</pre>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 答题区 -->
  <div class="answer-panel">
    <form id="answerForm">
      <!-- 编程题：代码编辑器 -->
      {% if question.question_type == 'programming' %}
      <div class="code-editor-wrapper">
        <select id="languageSelect">
          <option value="python">Python 3</option>
          <option value="cpp">C++ 17</option>
          <option value="java">Java 11</option>
        </select>
        <textarea id="codeEditor" class="code-editor"></textarea>
      </div>
      
      <!-- 主观题：文本框 -->
      {% elif question.question_type == 'subjective' %}
      <textarea id="answerText" class="answer-textarea"></textarea>
      
      <!-- 客观题：选项 -->
      {% else %}
      <div class="options-list">
        {% for option in question.options %}
        <label class="option-item">
          <input type="radio" name="answer" value="{{ option.key }}" />
          <span class="option-key">{{ option.key }}.</span>
          <span class="option-content">{{ option.content }}</span>
        </label>
        {% endfor %}
      </div>
      {% endif %}
      
      <!-- 提交按钮 -->
      <div class="form-actions">
        <button type="button" onclick="saveDraft()">保存草稿</button>
        <button type="submit">提交答案</button>
      </div>
    </form>
  </div>
</div>

<!-- 判题结果弹窗 -->
<div class="modal" id="resultModal">
  <div class="result-content">
    <div class="result-status">
      <i class="ri-loader-4-line spinning"></i>
      <span>判题中...</span>
    </div>
    <div class="test-cases"></div>
  </div>
</div>
```

【输出文件】
1. app/templates/answer.html - 答题页面模板
2. app/api/submissions.py - 提交 API
3. app/services/judge.py - 判题服务
4. app/models/submission.py - 提交记录模型
5. app/static/js/answer.js - 前端交互
6. app/static/css/answer.css - 页面样式
7. app/static/vendor/monaco/ - Monaco 编辑器（或 CDN）

【验收标准】
- [ ] 代码编辑器语法高亮正常
- [ ] 提交后轮询判题状态
- [ ] 测试点详情正确显示
- [ ] 草稿自动保存（刷新不丢失）
- [ ] 倒计时功能正常
- [ ] 移动端响应式适配
```

---

## 模块 7：知识图谱可视化

```
请实现知识图谱可视化页面（ECharts Graph）。

【功能需求】

1. 力导向图展示
   - 节点：知识片段（圆形，大小=重要性）
   - 边：知识点关系（不同颜色=不同关系类型）
   - 支持拖拽节点
   - 支持缩放平移

2. 关系类型
   - prerequisite（前置知识）：蓝色实线
   - similar（相似知识点）：绿色虚线
   - reference（参考资料）：灰色点线
   - parent_child（父子关系）：紫色实线

3. 交互功能
   - 点击节点 → 显示知识片段详情
   - 双击节点 → 编辑知识点
   - 悬停节点 → 高亮邻接节点和边
   - 搜索框 → 高亮匹配节点
   - 图例 → 筛选关系类型

【API 接口】
GET /api/knowledge/{course_id}/graph
响应：
{
  "nodes": [
    {
      "id": 1,
      "name": "二叉树",
      "value": 10,
      "symbolSize": 50,
      "category": 0,
      "draggable": true
    }
  ],
  "links": [
    {
      "source": 1,
      "target": 2,
      "relation_type": "prerequisite",
      "value": 0.9
    }
  ],
  "categories": [
    {"name": "数据结构"},
    {"name": "算法"}
  ]
}

【ECharts 配置】
```javascript
const option = {
  title: {
    text: '知识图谱',
    subtext: '展示知识点之间的关联关系',
    top: 'bottom',
    left: '20'
  },
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      if (params.dataType === 'node') {
        return `<strong>${params.name}</strong><br/>关联：${params.data.links || 0}个`;
      }
      return `${params.data.source} → ${params.data.target}<br/>类型：${params.data.relation_type}`;
    }
  },
  legend: [{
    data: categories.map(c => c.name),
    bottom: 10,
    left: 'center'
  }],
  series: [{
    type: 'graph',
    layout: 'force',
    data: nodes,
    links: links,
    categories: categories,
    roam: true,      // 缩放平移
    draggable: true, // 节点拖拽
    
    // 节点样式
    symbol: 'circle',
    symbolSize: function(val, params) {
      return params.data.symbolSize || 30;
    },
    label: {
      show: true,
      position: 'right',
      color: '#1A1A1A'
    },
    
    // 连线样式
    lineStyle: {
      color: 'source',
      curveness: 0.3,
      width: 1.5
    },
    
    // 高亮
    emphasis: {
      focus: 'adjacency',
      lineStyle: {
        width: 3
      }
    },
    
    // 力导向配置
    force: {
      repulsion: 200,   // 节点斥力
      gravity: 0.1,     // 引力
      edgeLength: [50, 200]
    },
    
    // 动画
    animationDuration: 1500,
    animationThreshold: 500
  }]
};
```

【前端页面】
```html
<!-- app/templates/knowledge_graph.html -->

<div class="graph-page">
  <div class="graph-header">
    <h1>知识图谱</h1>
    <div class="graph-controls">
      <input type="text" class="search-box" placeholder="搜索知识点..." />
      <select id="relationFilter">
        <option value="">全部关系</option>
        <option value="prerequisite">前置知识</option>
        <option value="similar">相似知识点</option>
        <option value="reference">参考资料</option>
      </select>
      <button onclick="resetGraph()">重置视图</button>
    </div>
  </div>
  
  <div class="graph-container" id="knowledgeGraph"></div>
  
  <!-- 节点详情弹窗 -->
  <div class="modal" id="nodeDetailModal">
    <div class="modal-content">
      <h3 id="nodeTitle"></h3>
      <div id="nodeContent"></div>
      <div class="modal-footer">
        <button onclick="closeModal()">关闭</button>
        <button onclick="editNode()">编辑</button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
const chart = echarts.init(document.getElementById('knowledgeGraph'));
chart.setOption(option);

// 点击节点
chart.on('click', function(params) {
  if (params.dataType === 'node') {
    showNodeDetail(params.data.id);
  }
});

// 搜索高亮
document.querySelector('.search-box').addEventListener('input', function(e) {
  const keyword = e.target.value;
  highlightNodes(keyword);
});
</script>
```

【输出文件】
1. app/api/knowledge_graph.py - 图谱 API
2. app/services/graph_builder.py - 图数据构建服务
3. app/templates/knowledge_graph.html - 图谱页面
4. app/static/js/knowledge_graph.js - ECharts 配置
5. app/static/css/knowledge_graph.css - 页面样式

【验收标准】
- [ ] 节点数 < 500 时流畅渲染
- [ ] 拖拽节点无卡顿
- [ ] 缩放平移流畅
- [ ] 点击节点显示详情
- [ ] 搜索高亮功能正常
- [ ] 移动端禁用拖拽（改为点击）
```

---

## 模块 8：日志系统

```
请实现系统操作日志功能。

【日志模型】
```sql
CREATE TABLE operation_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  action VARCHAR(50) NOT NULL,        -- LOGIN, DELETE_QUESTION, SUBMIT_ASSIGNMENT
  resource_type VARCHAR(50),          -- question, assignment, chat
  resource_id INT,
  ip_address VARCHAR(45),
  user_agent TEXT,
  request_method VARCHAR(10),
  request_path VARCHAR(200),
  old_value JSON,                     -- 修改前的值
  new_value JSON,                     -- 修改后的值
  status ENUM('success', 'failed', 'error') DEFAULT 'success',
  error_message TEXT,
  duration_ms INT,                    -- 执行耗时
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_user_action (user_id, action),
  INDEX idx_resource (resource_type, resource_id),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

【日志装饰器】
```python
# app/utils/logging.py

from functools import wraps
import time
from datetime import datetime

def log_operation(action: str, resource_type: str = None, log_request: bool = True):
    """
    操作日志装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 获取请求信息
            request = kwargs.get('request') or next(
                (arg for arg in args if hasattr(arg, 'headers')), 
                None
            )
            current_user = kwargs.get('current_user') or next(
                (arg for arg in args if hasattr(arg, 'id')),
                None
            )
            
            log_data = {
                'action': action,
                'resource_type': resource_type,
                'user_id': current_user.id if current_user else None,
                'ip_address': request.client.host if request else None,
                'request_method': request.method if request else None,
                'request_path': request.url.path if request else None,
                'status': 'success',
                'old_value': None,
                'new_value': None
            }
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 记录成功日志
                log_data['new_value'] = result if isinstance(result, dict) else None
                
                return result
                
            except Exception as e:
                # 记录失败日志
                log_data['status'] = 'failed'
                log_data['error_message'] = str(e)
                raise
            finally:
                # 补充公共信息
                log_data['duration_ms'] = int((time.time() - start_time) * 1000)
                
                # 异步写入日志（不阻塞主流程）
                asyncio.create_task(write_operation_log(log_data))
        
        return wrapper
    return decorator

async def write_operation_log(log_data: dict):
    """异步写入操作日志"""
    try:
        from app.models import OperationLog
        from app.database import get_db_session
        
        db = next(get_db_session())
        log = OperationLog(**log_data)
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"日志写入失败：{e}")
    finally:
        db.close()
```

【使用示例】
```python
# app/api/questions.py

from app.utils.logging import log_operation

@router.post("")
@log_operation(action='CREATE_QUESTION', resource_type='question')
async def create_question(
    question: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建题目（自动记录日志）"""
    # ...
    return db_question

@router.delete("/{question_id}")
@log_operation(action='DELETE_QUESTION', resource_type='question')
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除题目（自动记录日志）"""
    # ...
```

【日志查询 API】
```python
# app/api/logs.py

@router.get("/operations")
async def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取操作日志列表（管理员）"""
    # 权限检查
    if current_user.role not in ['admin', 'owner']:
        raise HTTPException(403, "无权访问日志")
    
    query = db.query(OperationLog)
    
    # 筛选条件
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if action:
        query = query.filter(OperationLog.action == action)
    if resource_type:
        query = query.filter(OperationLog.resource_type == resource_type)
    if status:
        query = query.filter(OperationLog.status == status)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)
    
    total = query.count()
    logs = query.order_by(OperationLog.created_at.desc())\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
    
    return {
        "total": total,
        "page": page,
        "data": logs
    }

@router.get("/statistics")
async def get_log_statistics(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日志统计信息"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 按操作类型统计
    action_stats = db.query(
        OperationLog.action,
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= start_date
    ).group_by(OperationLog.action).all()
    
    # 按状态统计
    status_stats = db.query(
        OperationLog.status,
        func.count(OperationLog.id).label('count')
    ).group_by(OperationLog.status).all()
    
    return {
        "period_days": days,
        "action_statistics": [{"action": s[0], "count": s[1]} for s in action_stats],
        "status_statistics": [{"status": s[0], "count": s[1]} for s in status_stats]
    }
```

【日志查看页面】
```html
<!-- app/templates/logs.html -->

<div class="logs-page">
  <div class="page-header">
    <h1>操作日志</h1>
    <div class="page-actions">
      <button onclick="exportLogs()">导出 CSV</button>
      <button onclick="clearLogs()">清理日志</button>
    </div>
  </div>
  
  <div class="filter-bar">
    <select id="userFilter">
      <option value="">全部用户</option>
      <!-- 动态加载用户列表 -->
    </select>
    <select id="actionFilter">
      <option value="">全部操作</option>
      <option value="LOGIN">登录</option>
      <option value="DELETE_QUESTION">删除题目</option>
      <option value="SUBMIT_ASSIGNMENT">提交作业</option>
    </select>
    <select id="statusFilter">
      <option value="">全部状态</option>
      <option value="success">成功</option>
      <option value="failed">失败</option>
      <option value="error">错误</option>
    </select>
    <input type="date" id="startDate" />
    <input type="date" id="endDate" />
    <button onclick="searchLogs()">查询</button>
  </div>
  
  <table class="data-table">
    <thead>
      <tr>
        <th>时间</th>
        <th>用户</th>
        <th>操作</th>
        <th>资源</th>
        <th>状态</th>
        <th>耗时</th>
        <th>IP</th>
      </tr>
    </thead>
    <tbody id="logsTableBody">
      <!-- 动态加载 -->
    </tbody>
  </table>
  
  <div class="pagination">
    <!-- 分页组件 -->
  </div>
</div>
```

【输出文件】
1. app/utils/logging.py - 日志工具（装饰器）
2. app/api/logs.py - 日志 API
3. app/models/operation_log.py - 日志模型
4. app/templates/logs.html - 日志页面
5. app/static/js/logs.js - 前端逻辑
6. alembic/versions/[timestamp]_add_operation_logs.py - 迁移脚本

【验收标准】
- [ ] 所有写操作自动记录日志（创建/更新/删除）
- [ ] 日志异步写入（不阻塞主流程）
- [ ] 日志查询支持多条件筛选
- [ ] 导出 CSV 功能正常
- [ ] 90 天自动归档（定时任务）
- [ ] 单表超过 100 万条自动分区
```

---

## 模块 9：UI 优化（移除蓝点 + 背景）

```
请完成两项 UI 优化。

【任务 1：移除题目难度 5 个小蓝点】

1. 查找难度指示器代码：
```bash
grep -r "difficulty-dots" app/templates/
grep -r "question-dots" app/templates/
grep -r "<span class=\"dot" app/templates/
```

2. 删除 HTML 结构：
```html
<!-- 删除前 -->
<div class="question-dots">
  <span class="dot active"></span>
  <span class="dot active"></span>
  <span class="dot active"></span>
  <span class="dot"></span>
  <span class="dot"></span>
</div>

<!-- 删除后 -->
<!-- 难度指示器已移除 -->
```

3. 删除 CSS 样式（或注释）：
```css
/* .question-dots {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.question-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #E0E8FF;
}

.question-dots .dot.active {
  background: #5B7FFF;
} */
```

4. 修改的文件：
- app/templates/components/question_card.html
- app/templates/questions.html
- app/templates/grading.html
- app/static/css/questions.css

【任务 2：注册页背景优化】

1. 创建新背景图（SVG）：
```xml
<!-- app/static/images/bg-geometric.svg -->
<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <rect width="1920" height="1080" fill="#F5F7FA"/>
  
  <!-- 渐变圆 -->
  <circle cx="200" cy="150" r="100" fill="rgba(91,127,255,0.1)"/>
  <circle cx="1700" cy="900" r="150" fill="rgba(139,92,246,0.1)"/>
  <circle cx="960" cy="540" r="200" fill="rgba(16,185,129,0.05)"/>
  
  <!-- 三角形 -->
  <polygon points="400,800 500,600 600,800" fill="rgba(91,127,255,0.08)"/>
  <polygon points="1400,300 1500,100 1600,300" fill="rgba(139,92,246,0.08)"/>
  
  <!-- 装饰线 -->
  <line x1="0" y1="200" x2="1920" y2="200" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
  <line x1="0" y1="400" x2="1920" y2="400" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
  <line x1="0" y1="600" x2="1920" y2="600" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
  <line x1="0" y1="800" x2="1920" y2="800" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
</svg>
```

2. 更新 CSS：
```css
/* app/static/css/auth.css */

.register-page, .login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  
  background: 
    linear-gradient(135deg, rgba(91,127,255,0.1) 0%, rgba(139,92,246,0.1) 100%),
    url('/static/images/bg-geometric.svg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

/* 或者纯 CSS 方案（无图片） */
.register-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(91,127,255,0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(139,92,246,0.15) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(16,185,129,0.1) 0%, transparent 70%);
  pointer-events: none;
  z-index: -1;
}
```

【输出文件】
1. app/static/images/bg-geometric.svg - 新背景图
2. app/static/css/auth.css - 更新样式
3. app/templates/register.html - 应用新背景
4. app/templates/login.html - 同步更新
5. 删除的难度指示器相关代码

【验收标准】
- [ ] 题目列表页无蓝点
- [ ] 题目卡片无蓝点
- [ ] 注册页背景为浅色几何渐变
- [ ] 登录页同步更新
- [ ] 移动端响应式正常
```

---

## 通用模板：新建 API 模块

```
请创建 [模块名称] 的 API 接口。

【项目背景】
基于 FastAPI 的课程助教系统，已有用户/认证系统

【技术栈】
- Python 3.11 + FastAPI + SQLAlchemy + MySQL 8
- Jinja2 模板 + 原生 JS
- 浅色主题 + Remix Icon

【业务需求】
[在此描述具体业务需求]

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
1. app/api/[module].py - API 实现
2. app/schemas/[module].py - Pydantic 模型
3. app/models/[module].py - 数据模型（如需要）
4. tests/test_[module].py - 单元测试

【验收标准】
- [ ] API 通过 Swagger 文档测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 错误处理统一（404/403/400）
- [ ] 日志记录完整
```

---

## 通用模板：新建前端页面

```
请创建 [页面名称] 页面。

【页面布局】
[ASCII 布局图或参考截图]

【功能需求】
1. [功能 1 描述]
2. [功能 2 描述]
3. [功能 3 描述]

【API 接口】
[需要调用的后端 API 列表]

【UI 规范】
- 遵循现有设计系统（浅色主题）
- 使用 Remix Icon 图标
- 响应式适配移动端（断点：1024px, 768px）
- 加载状态（骨架屏/Loading 动画）
- 错误状态（404/空数据）

【输出文件】
1. app/templates/[page].html - 页面模板
2. app/static/js/[page].js - 交互逻辑
3. app/static/css/[page].css - 页面样式
4. app/static/components/[component].html - 可复用组件（如有）

【验收标准】
- [ ] 页面加载时间 < 2 秒
- [ ] 移动端适配正常
- [ ] 所有按钮有 hover 状态
- [ ] 表单验证完整
- [ ] 错误提示友好
```

---

## 通用模板：数据库迁移

```
请编写数据库迁移脚本。

【变更内容】
1. 新建表：[表名和结构]
2. 修改表：[表名] 添加 [字段]
3. 数据迁移：[迁移逻辑]

【要求】
- 使用 Alembic 迁移
- 支持 upgrade 和 downgrade
- 保留现有数据
- 添加外键约束
- 创建必要索引

【输出文件】
1. alembic/versions/[timestamp]_[description].py - 迁移脚本
2. scripts/[migration_script].py - 数据迁移脚本（如需要）
3. tests/test_migration.py - 迁移测试

【验收标准】
- [ ] upgrade 执行成功
- [ ] downgrade 执行成功（回滚）
- [ ] 数据不丢失
- [ ] 外键约束生效
- [ ] 索引创建成功
```

---

## 📋 快速索引

| 模块 | 提示词位置 | 预计工时 |
|------|------------|----------|
| 1. 数据库迁移 | [模块 1](#模块 1 数据库迁移多课程架构) | 1 天 |
| 2. 权限系统 | [模块 2](#模块 2 权限系统 rbac) | 1 天 |
| 3. 课程 API | [模块 3](#模块 3 课程管理-api) | 1 天 |
| 4. Agent 配置 | [模块 4](#模块 4agent-配置页面多 ai 服务商) | 2 天 |
| 5. 删除功能 | [模块 5](#模块 5 删除功能聊天题目) | 0.5 天 |
| 6. 答题页面 | [模块 6](#模块 6 答题页面洛谷风格) | 3 天 |
| 7. 知识图谱 | [模块 7](#模块 7 知识图谱可视化) | 2 天 |
| 8. 日志系统 | [模块 8](#模块 8 日志系统) | 2 天 |
| 9. UI 优化 | [模块 9](#模块 9ui 优化移除蓝点背景) | 0.5 天 |

---

> **使用建议**：
> 1. 按顺序执行（1→9）- 后续模块依赖前面基础
> 2. 每完成一个模块 → 运行测试 → 提交代码
> 3. 复杂模块分阶段验收（模型→API→前端）
> 4. 所有提示词可直接复制发送给执行 Agent
