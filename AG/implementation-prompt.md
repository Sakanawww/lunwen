# 课程助教系统功能实现 - 完整提示词

> 项目：基于 Agent 的课程助教系统  
> 技术栈：FastAPI + SQLAlchemy + MySQL + Jinja2 + 原生 JS  
> 实现周期：4-6 周  
> 文档版本：v1.0

---

## 📋 需求总览

| 序号 | 功能模块 | 优先级 | 预估工时 | 依赖关系 |
|------|----------|--------|----------|----------|
| 1 | Q&A 聊天记录删除 | P1 | 4 小时 | - |
| 2 | 多课程管理 | P0 | 3 天 | - |
| 3 | 多老师学生权限 | P0 | 3 天 | 2 |
| 4 | Agent 配置页面 | P1 | 2 天 | 2,3 |
| 5 | RAG 知识网状关系图 | P2 | 4 天 | 2 |
| 6 | 学生答题页面 | P1 | 5 天 | 2,3 |
| 7 | 移除难度 5 个小蓝点 | P3 | 30 分钟 | - |
| 8 | 题目删除功能 | P1 | 4 小时 | - |
| 9 | 注册页背景优化 | P3 | 2 小时 | - |
| 10 | 日志系统 | P1 | 2 天 | - |

---

## 🎯 一、数据库架构设计

### 1.1 核心表结构变更

```sql
-- ============================================
-- 2. 多课程管理 + 3. 多老师学生权限
-- ============================================

-- 课程表（新增）
CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL COMMENT '课程名称',
    code VARCHAR(50) UNIQUE COMMENT '课程代码',
    description TEXT COMMENT '课程描述',
    teacher_id INT NOT NULL COMMENT '主讲老师 ID',
    semester VARCHAR(50) COMMENT '学期',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 课程用户关联表（核心权限表）
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

-- 现有表添加 course_id 外键
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

-- ============================================
-- 4. Agent 配置表
-- ============================================

CREATE TABLE ai_providers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    name VARCHAR(50) NOT NULL COMMENT '服务商名称',
    api_key_encrypted TEXT NOT NULL COMMENT '加密的 API Key',
    base_url VARCHAR(200) COMMENT 'API 基础 URL',
    model_name VARCHAR(100) COMMENT '模型名称',
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    quota_limit INT COMMENT '额度限制',
    quota_used INT DEFAULT 0 COMMENT '已用额度',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 5. 知识片段关系表（网状图）
-- ============================================

CREATE TABLE knowledge_relations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    source_fragment_id INT NOT NULL,
    target_fragment_id INT NOT NULL,
    relation_type ENUM('prerequisite', 'similar', 'reference', 'parent_child') NOT NULL,
    confidence FLOAT DEFAULT 1.0 COMMENT '关系置信度',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_relation (source_fragment_id, target_fragment_id, relation_type),
    FOREIGN KEY (source_fragment_id) REFERENCES knowledge_fragments(id) ON DELETE CASCADE,
    FOREIGN KEY (target_fragment_id) REFERENCES knowledge_fragments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 6. 答题页面相关表
-- ============================================

CREATE TABLE submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    course_id INT NOT NULL,
    assignment_id INT,
    
    -- 提交内容
    answer_text TEXT COMMENT '主观题答案',
    code_content TEXT COMMENT '编程题代码',
    language VARCHAR(20) COMMENT '编程语言',
    
    -- 判分结果
    status ENUM('pending', 'graded', 'reviewing') DEFAULT 'pending',
    score DECIMAL(5,2),
    max_score INT DEFAULT 100,
    feedback TEXT COMMENT '批改反馈',
    
    -- 执行信息（编程题）
    execution_time INT COMMENT '执行时间 ms',
    memory_usage INT COMMENT '内存使用 KB',
    test_cases_passed INT,
    test_cases_total INT,
    
    -- 时间戳
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    graded_at DATETIME,
    graded_by INT,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 10. 日志系统表
-- ============================================

CREATE TABLE operation_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id INT COMMENT '资源 ID',
    
    -- 请求信息
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path VARCHAR(200),
    
    -- 操作详情
    old_value JSON COMMENT '修改前的值',
    new_value JSON COMMENT '修改后的值',
    
    -- 结果
    status ENUM('success', 'failed', 'error') DEFAULT 'success',
    error_message TEXT,
    duration_ms INT COMMENT '执行耗时 ms',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_action (user_id, action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 🔧 二、后端 API 实现

### 2.1 课程管理 API

```python
# app/api/courses.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/courses", tags=["课程管理"])

# ============ 课程 CRUD ============

@router.get("", response_model=List[CourseResponse])
async def get_my_courses(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有课程
    - 老师：看到自己教授的课程
    - 学生：看到自己选修的课程
    """
    query = db.query(Course).join(CourseUser).filter(
        CourseUser.user_id == current_user.id
    )
    
    courses = query.offset(skip).limit(limit).all()
    return courses

@router.post("", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新课程（创建者自动成为 owner）
    """
    db_course = Course(
        name=course.name,
        code=course.code,
        description=course.description,
        teacher_id=current_user.id,
        semester=course.semester
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    # 创建者自动成为 owner
    course_user = CourseUser(
        course_id=db_course.id,
        user_id=current_user.id,
        role='owner'
    )
    db.add(course_user)
    db.commit()
    
    # 记录日志
    await create_operation_log(
        action='CREATE_COURSE',
        resource_type='course',
        resource_id=db_course.id,
        status='success'
    )
    
    return db_course

@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取课程详情（含用户角色）
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, "课程不存在")
    
    # 检查权限
    course_user = db.query(CourseUser).filter(
        CourseUser.course_id == course_id,
        CourseUser.user_id == current_user.id
    ).first()
    
    if not course_user:
        raise HTTPException(403, "无权访问该课程")
    
    return {
        **course.__dict__,
        'user_role': course_user.role,
        'teacher_name': course.teacher.username
    }

@router.put("/{course_id}")
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新课程信息（需要 teacher+ 权限）
    """
    # 权限检查
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher'])
    
    # 更新逻辑...
    pass

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除课程（软删除，仅 owner 可操作）
    """
    await check_course_permission(db, course_id, current_user.id, ['owner'])
    
    course = db.query(Course).filter(Course.id == course_id).first()
    course.is_active = False
    db.commit()
    
    await create_operation_log(
        action='DELETE_COURSE',
        resource_type='course',
        resource_id=course_id,
        status='success'
    )
    
    return {"message": "课程已删除"}

# ============ 课程用户管理 ============

@router.post("/{course_id}/users")
async def add_course_user(
    course_id: int,
    user_data: CourseUserAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加课程用户（老师添加学生/助教）
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher'])
    
    course_user = CourseUser(
        course_id=course_id,
        user_id=user_data.user_id,
        role=user_data.role
    )
    db.add(course_user)
    db.commit()
    
    return {"message": "用户已添加"}

@router.get("/{course_id}/users")
async def get_course_users(
    course_id: int,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取课程用户列表
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher', 'assistant'])
    
    query = db.query(CourseUser).filter(CourseUser.course_id == course_id)
    if role:
        query = query.filter(CourseUser.role == role)
    
    users = query.all()
    return users

@router.delete("/{course_id}/users/{user_id}")
async def remove_course_user(
    course_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    移除课程用户
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher'])
    
    course_user = db.query(CourseUser).filter(
        CourseUser.course_id == course_id,
        CourseUser.user_id == user_id
    ).first()
    
    if course_user:
        db.delete(course_user)
        db.commit()
    
    return {"message": "用户已移除"}

# ============ 权限检查装饰器 ============

async def check_course_permission(
    db: Session,
    course_id: int,
    user_id: int,
    required_roles: List[str]
):
    """
    检查用户在指定课程的权限
    """
    course_user = db.query(CourseUser).filter(
        CourseUser.course_id == course_id,
        CourseUser.user_id == user_id
    ).first()
    
    if not course_user:
        raise HTTPException(403, "无权访问该课程")
    
    if course_user.role not in required_roles:
        raise HTTPException(403, f"权限不足，需要：{required_roles}")
    
    return course_user
```

---

### 2.2 聊天记录删除 API

```python
# app/api/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/api/chat", tags=["聊天"])

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除聊天会话（软删除）
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(404, "会话不存在")
    
    # 软删除标记
    session.is_deleted = True
    session.deleted_at = datetime.now()
    db.commit()
    
    await create_operation_log(
        action='DELETE_CHAT_SESSION',
        resource_type='chat_session',
        resource_id=session_id,
        status='success'
    )
    
    return {"message": "会话已删除"}

@router.delete("/sessions")
async def batch_delete_sessions(
    session_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量删除聊天会话
    """
    db.query(ChatSession).filter(
        ChatSession.id.in_(session_ids),
        ChatSession.user_id == current_user.id
    ).update({
        "is_deleted": True,
        "deleted_at": datetime.now()
    })
    db.commit()
    
    return {"message": f"已删除 {len(session_ids)} 个会话"}

@router.post("/sessions/{session_id}/restore")
async def restore_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    恢复已删除的会话（回收站功能）
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.is_deleted == True
    ).first()
    
    if not session:
        raise HTTPException(404, "会话不存在或未被删除")
    
    session.is_deleted = False
    session.deleted_at = None
    db.commit()
    
    return {"message": "会话已恢复"}

@router.get("/sessions/deleted")
async def get_deleted_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取已删除的会话列表（回收站）
    """
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_deleted == True
    ).order_by(ChatSession.deleted_at.desc()).all()
    
    return sessions
```

---

### 2.3 Agent 配置 API

```python
# app/api/agents.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import os

router = APIRouter(prefix="/api/agents", tags=["Agent 配置"])

# 加密密钥（应从环境变量读取）
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)

@router.get("/providers")
async def get_ai_providers(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取课程的 AI 服务商配置（API Key 脱敏）
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher'])
    
    providers = db.query(AIProvider).filter(
        AIProvider.course_id == course_id,
        AIProvider.is_active == True
    ).all()
    
    # 脱敏返回
    result = []
    for p in providers:
        result.append({
            "id": p.id,
            "name": p.name,
            "model_name": p.model_name,
            "api_key_masked": f"sk-****{p.api_key_encrypted[-4:]}",
            "base_url": p.base_url,
            "is_default": p.is_default,
            "quota_limit": p.quota_limit,
            "quota_used": p.quota_used,
            "quota_remaining": p.quota_limit - p.quota_used if p.quota_limit else None
        })
    
    return result

@router.post("/providers")
async def create_ai_provider(
    provider: AIProviderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加 AI 服务商配置
    """
    await check_course_permission(db, provider.course_id, current_user.id, ['owner', 'teacher'])
    
    # 加密 API Key
    encrypted_key = cipher.encrypt(provider.api_key.encode())
    
    db_provider = AIProvider(
        course_id=provider.course_id,
        name=provider.name,
        api_key_encrypted=encrypted_key.decode(),
        base_url=provider.base_url,
        model_name=provider.model_name,
        is_default=provider.is_default
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    
    return db_provider

@router.put("/providers/{provider_id}")
async def update_ai_provider(
    provider_id: int,
    provider_update: AIProviderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新 AI 服务商配置
    """
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(404, "服务商不存在")
    
    await check_course_permission(db, db_provider.course_id, current_user.id, ['owner', 'teacher'])
    
    # 更新字段
    if provider_update.name:
        db_provider.name = provider_update.name
    if provider_update.api_key:
        db_provider.api_key_encrypted = cipher.encrypt(provider_update.api_key.encode()).decode()
    if provider_update.model_name:
        db_provider.model_name = provider_update.model_name
    if provider_update.is_default is not None:
        db_provider.is_default = provider_update.is_default
    
    db.commit()
    db.refresh(db_provider)
    
    return db_provider

@router.delete("/providers/{provider_id}")
async def delete_ai_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除 AI 服务商配置
    """
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(404, "服务商不存在")
    
    await check_course_permission(db, db_provider.course_id, current_user.id, ['owner', 'teacher'])
    
    db.delete(db_provider)
    db.commit()
    
    return {"message": "服务商已删除"}

@router.post("/providers/{provider_id}/test")
async def test_ai_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试 AI 服务商连接
    """
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(404, "服务商不存在")
    
    # 解密 API Key
    api_key = cipher.decrypt(db_provider.api_key_encrypted.encode()).decode()
    
    # 调用测试接口
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{db_provider.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": db_provider.model_name,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10.0
            )
            response.raise_for_status()
        
        return {"status": "success", "message": "连接测试成功"}
    except Exception as e:
        return {"status": "failed", "message": f"连接失败：{str(e)}"}
```

---

### 2.4 题目管理 API（含删除）

```python
# app/api/questions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/questions", tags=["题目管理"])

@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除题目（软删除，检查引用）
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(404, "题目不存在")
    
    # 检查是否被作业引用
    from sqlalchemy import exists
    
    has_assignment = db.query(exists().where(
        AssignmentQuestion.question_id == question_id
    )).scalar()
    
    if has_assignment:
        raise HTTPException(
            400, 
            "该题目已被作业引用，无法删除。请先从作业中移除。"
        )
    
    # 软删除
    question.is_deleted = True
    question.deleted_at = datetime.now()
    question.deleted_by = current_user.id
    db.commit()
    
    await create_operation_log(
        action='DELETE_QUESTION',
        resource_type='question',
        resource_id=question_id,
        status='success'
    )
    
    return {"message": "题目已删除"}

@router.post("/{question_id}/restore")
async def restore_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    恢复已删除的题目
    """
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.is_deleted == True
    ).first()
    
    if not question:
        raise HTTPException(404, "题目不存在或未被删除")
    
    question.is_deleted = False
    question.deleted_at = None
    question.deleted_by = None
    db.commit()
    
    return {"message": "题目已恢复"}

@router.get("/deleted")
async def get_deleted_questions(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取已删除的题目列表（回收站）
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher'])
    
    questions = db.query(Question).filter(
        Question.course_id == course_id,
        Question.is_deleted == True
    ).order_by(Question.deleted_at.desc()).all()
    
    return questions
```

---

### 2.5 日志系统 API

```python
# app/api/logs.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/logs", tags=["系统日志"])

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
    """
    获取操作日志列表（管理员）
    """
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
    
    # 分页
    total = query.count()
    logs = query.order_by(OperationLog.created_at.desc())\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": logs
    }

@router.get("/statistics")
async def get_log_statistics(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取日志统计信息
    """
    if current_user.role not in ['admin', 'owner']:
        raise HTTPException(403, "无权访问日志")
    
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
    ).filter(
        OperationLog.created_at >= start_date
    ).group_by(OperationLog.status).all()
    
    # 活跃用户统计
    user_stats = db.query(
        User.username,
        func.count(OperationLog.id).label('count')
    ).join(OperationLog, OperationLog.user_id == User.id).filter(
        OperationLog.created_at >= start_date
    ).group_by(User.username).order_by(func.count(OperationLog.id).desc()).limit(10).all()
    
    return {
        "period_days": days,
        "action_statistics": [{"action": s[0], "count": s[1]} for s in action_stats],
        "status_statistics": [{"status": s[0], "count": s[1]} for s in status_stats],
        "top_users": [{"username": s[0], "count": s[1]} for s in user_stats]
    }
```

---

### 2.6 答题提交 API

```python
# app/api/submissions.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/api/submissions", tags=["答题提交"])

@router.post("")
async def create_submission(
    submission: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交答案（支持文本答案和代码）
    """
    # 检查题目是否存在
    question = db.query(Question).filter(Question.id == submission.question_id).first()
    if not question:
        raise HTTPException(404, "题目不存在")
    
    # 创建提交记录
    db_submission = Submission(
        user_id=current_user.id,
        question_id=submission.question_id,
        course_id=submission.course_id,
        assignment_id=submission.assignment_id,
        answer_text=submission.answer_text,
        code_content=submission.code_content,
        language=submission.language,
        status='pending'
    )
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    # 异步判题（客观题/编程题）
    if question.question_type in ['objective', 'programming']:
        await grade_submission.delay(db_submission.id)
    
    return db_submission

@router.get("/{submission_id}")
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取提交详情
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(404, "提交记录不存在")
    
    # 权限检查
    if submission.user_id != current_user.id:
        await check_course_permission(db, submission.course_id, current_user.id, ['owner', 'teacher'])
    
    return submission

@router.get("/my")
async def get_my_submissions(
    course_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取我的提交记录
    """
    query = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.course_id == course_id
    )
    
    if status:
        query = query.filter(Submission.status == status)
    
    total = query.count()
    submissions = query.order_by(Submission.submitted_at.desc())\
                        .offset((page - 1) * page_size)\
                        .limit(page_size)\
                        .all()
    
    return {
        "total": total,
        "page": page,
        "data": submissions
    }
```

---

### 2.7 知识图谱 API

```python
# app/api/knowledge_graph.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

router = APIRouter(prefix="/api/knowledge", tags=["知识图谱"])

@router.get("/{course_id}/graph")
async def get_knowledge_graph(
    course_id: int,
    max_nodes: int = Query(100, ge=10, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取知识图谱数据（网状关系）
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher', 'assistant', 'student'])
    
    # 查询知识片段
    fragments = db.query(KnowledgeFragment).filter(
        KnowledgeFragment.course_id == course_id,
        KnowledgeFragment.is_deleted == False
    ).limit(max_nodes).all()
    
    # 查询关系
    relations = db.query(KnowledgeRelation).join(
        KnowledgeFragment, KnowledgeRelation.source_fragment_id == KnowledgeFragment.id
    ).filter(
        KnowledgeFragment.course_id == course_id
    ).all()
    
    # 构建图数据
    nodes = []
    for f in fragments:
        nodes.append({
            "id": f.id,
            "name": f.title[:20] + "..." if len(f.title) > 20 else f.title,
            "value": f.vector_norm if hasattr(f, 'vector_norm') else 1,
            "category": f.category_id or 0,
            "symbolSize": min(50, 10 + (f.vector_norm or 1) * 10),
            "draggable": True
        })
    
    links = []
    for r in relations:
        links.append({
            "source": r.source_fragment_id,
            "target": r.target_fragment_id,
            "relation_type": r.relation_type,
            "value": r.confidence
        })
    
    # 分类
    categories = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.course_id == course_id
    ).all()
    
    return {
        "nodes": nodes,
        "links": links,
        "categories": [{"name": c.name} for c in categories]
    }

@router.get("/{course_id}/fragments")
async def get_knowledge_fragments(
    course_id: int,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取知识片段列表（支持搜索）
    """
    await check_course_permission(db, course_id, current_user.id, ['owner', 'teacher', 'assistant', 'student'])
    
    query = db.query(KnowledgeFragment).filter(
        KnowledgeFragment.course_id == course_id,
        KnowledgeFragment.is_deleted == False
    )
    
    if search:
        query = query.filter(KnowledgeFragment.content.like(f"%{search}%"))
    if category_id:
        query = query.filter(KnowledgeFragment.category_id == category_id)
    
    total = query.count()
    fragments = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "data": fragments
    }
```

---

## 🎨 三、前端页面实现

### 3.1 课程选择下拉框（全局导航）

```html
<!-- app/templates/components/course_selector.html -->

<div class="course-selector" id="courseSelector">
  <div class="course-trigger" tabindex="0">
    <i class="ri-book-open-line"></i>
    <span class="course-name" id="currentCourseName">数据结构</span>
    <i class="ri-arrow-down-s-line"></i>
  </div>
  
  <div class="course-dropdown">
    <div class="dropdown-search">
      <i class="ri-search-line"></i>
      <input type="text" placeholder="搜索课程..." id="courseSearch" />
    </div>
    
    <ul class="course-list" id="courseList">
      <!-- 动态加载 -->
    </ul>
    
    <div class="dropdown-footer">
      <a href="/courses/manage" class="manage-link">
        <i class="ri-settings-4-line"></i>
        <span>课程管理</span>
      </a>
    </div>
  </div>
</div>

<script>
// 课程选择器逻辑
async function loadCourses() {
  const response = await fetch('/api/courses');
  const courses = await response.json();
  
  const list = document.getElementById('courseList');
  list.innerHTML = courses.map(course => `
    <li class="course-item ${course.id === currentCourseId ? 'active' : ''}" 
        data-id="${course.id}" 
        data-role="${course.user_role}">
      <i class="ri-book-open-line"></i>
      <span class="course-name">${course.name}</span>
      <span class="course-role-badge">${getRoleBadge(course.user_role)}</span>
      ${course.id === currentCourseId ? '<i class="ri-check-line"></i>' : ''}
    </li>
  `).join('');
}

// 点击切换课程
document.querySelectorAll('.course-item').forEach(item => {
  item.addEventListener('click', async function() {
    const courseId = this.dataset.id;
    const role = this.dataset.role;
    
    // 切换到新课程
    localStorage.setItem('currentCourseId', courseId);
    localStorage.setItem('currentCourseRole', role);
    
    // 刷新页面或更新状态
    window.location.reload();
  });
});
</script>

<style>
.course-selector {
  position: relative;
  display: inline-block;
}

.course-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.course-trigger:hover {
  border-color: #5B7FFF;
  background: #F8FAFF;
}

.course-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  min-width: 240px;
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-8px);
  transition: all 0.2s;
  z-index: 1000;
}

.course-selector.active .course-dropdown {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}

.course-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 6px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.course-item:hover {
  background: #F0F2F5;
}

.course-item.active {
  background: rgba(91, 127, 255, 0.1);
  color: #5B7FFF;
}

.course-role-badge {
  margin-left: auto;
  padding: 2px 8px;
  background: #F0F2F5;
  border-radius: 4px;
  font-size: 12px;
  color: #667788;
}
</style>
```

---

### 3.2 聊天记录删除功能

```html
<!-- app/templates/components/chat_session_list.html -->

<div class="chat-session-list">
  <div class="session-header">
    <h3>历史会话</h3>
    <div class="session-actions">
      <button class="btn-text" id="batchDeleteBtn">
        <i class="ri-delete-bin-line"></i>
        <span>批量删除</span>
      </button>
    </div>
  </div>
  
  <ul class="session-items" id="sessionList">
    <!-- 会话项 -->
    <li class="session-item" data-session-id="123">
      <input type="checkbox" class="session-checkbox" />
      <div class="session-content">
        <div class="session-title">关于二叉树的问题</div>
        <div class="session-meta">
          <span class="session-time">2 小时前</span>
          <span class="session-count">15 条消息</span>
        </div>
      </div>
      <div class="session-operations">
        <button class="btn-icon btn-sm" title="删除" onclick="deleteSession(123)">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    </li>
  </ul>
  
  <!-- 回收站入口 -->
  <div class="trash-bin-link">
    <a href="/chat/deleted">
      <i class="ri-delete-bin-2-line"></i>
      <span>回收站</span>
    </a>
  </div>
</div>

<script>
// 删除会话
async function deleteSession(sessionId) {
  if (!confirm('确定要删除这个会话吗？删除后可在回收站恢复。')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/chat/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      // 从列表中移除
      const item = document.querySelector(`[data-session-id="${sessionId}"]`);
      item.style.transition = 'all 0.3s';
      item.style.opacity = '0';
      item.style.transform = 'translateX(-20px)';
      setTimeout(() => item.remove(), 300);
      
      showToast('会话已删除', 'success');
    }
  } catch (error) {
    showToast('删除失败', 'error');
  }
}

// 批量删除
async function batchDeleteSessions() {
  const checkboxes = document.querySelectorAll('.session-checkbox:checked');
  const sessionIds = Array.from(checkboxes).map(cb => 
    cb.closest('.session-item').dataset.sessionId
  );
  
  if (sessionIds.length === 0) {
    showToast('请选择要删除的会话', 'warning');
    return;
  }
  
  if (!confirm(`确定要删除选中的 ${sessionIds.length} 个会话吗？`)) {
    return;
  }
  
  try {
    const response = await fetch('/api/chat/sessions', {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session_ids: sessionIds})
    });
    
    if (response.ok) {
      sessionIds.forEach(id => {
        const item = document.querySelector(`[data-session-id="${id}"]`);
        item.remove();
      });
      showToast(`已删除 ${sessionIds.length} 个会话`, 'success');
    }
  } catch (error) {
    showToast('批量删除失败', 'error');
  }
}
</script>
```

---

### 3.3 Agent 配置页面

```html
<!-- app/templates/agent_settings.html -->

{% extends "base.html" %}

{% block title %}Agent 配置{% endblock %}

{% block content %}
<div class="page-container">
  <div class="page-header">
    <h1>
      <i class="ri-robot-line"></i>
      <span>AI 模型配置</span>
    </h1>
    <button class="btn-primary" onclick="showAddProviderModal()">
      <i class="ri-add-line"></i>
      <span>添加服务商</span>
    </button>
  </div>
  
  <!-- 服务商列表 -->
  <div class="provider-grid" id="providerList">
    <!-- 动态加载 -->
  </div>
</div>

<!-- 添加/编辑弹窗 -->
<div class="modal" id="providerModal">
  <div class="modal-content">
    <div class="modal-header">
      <h2>添加 AI 服务商</h2>
      <button class="modal-close" onclick="closeModal()">
        <i class="ri-close-line"></i>
      </button>
    </div>
    
    <form id="providerForm">
      <div class="form-group">
        <label>服务商名称</label>
        <input type="text" name="name" placeholder="如：DeepSeek / 通义千问" required />
      </div>
      
      <div class="form-group">
        <label>API Key</label>
        <input type="password" name="api_key" placeholder="sk-..." required />
        <small>API Key 将加密存储</small>
      </div>
      
      <div class="form-group">
        <label>API 基础 URL</label>
        <input type="url" name="base_url" placeholder="https://api.deepseek.com" />
      </div>
      
      <div class="form-group">
        <label>模型名称</label>
        <input type="text" name="model_name" placeholder="deepseek-chat" required />
      </div>
      
      <div class="form-group">
        <label>额度限制（可选）</label>
        <input type="number" name="quota_limit" placeholder="如：10000" />
      </div>
      
      <div class="form-group">
        <label class="checkbox-label">
          <input type="checkbox" name="is_default" />
          <span>设为默认服务商</span>
        </label>
      </div>
    </form>
    
    <div class="modal-footer">
      <button class="btn-secondary" onclick="closeModal()">取消</button>
      <button class="btn-primary" onclick="saveProvider()">保存</button>
    </div>
  </div>
</div>

<script>
// 加载服务商列表
async function loadProviders() {
  const courseId = getCurrentCourseId();
  const response = await fetch(`/api/agents/providers?course_id=${courseId}`);
  const providers = await response.json();
  
  const list = document.getElementById('providerList');
  list.innerHTML = providers.map(p => `
    <div class="provider-card ${p.is_default ? 'default' : ''}">
      <div class="provider-header">
        <h3>${p.name}</h3>
        ${p.is_default ? '<span class="default-badge">默认</span>' : ''}
      </div>
      
      <div class="provider-info">
        <div class="info-row">
          <span class="label">模型</span>
          <span class="value">${p.model_name}</span>
        </div>
        <div class="info-row">
          <span class="label">API Key</span>
          <span class="value">${p.api_key_masked}</span>
        </div>
        <div class="info-row">
          <span class="label">剩余额度</span>
          <span class="value">${p.quota_remaining || '无限制'}</span>
        </div>
      </div>
      
      <div class="provider-actions">
        <button class="btn-text" onclick="testProvider(${p.id})">
          <i class="ri-flashlight-line"></i>
          测试连接
        </button>
        <button class="btn-text" onclick="editProvider(${p.id})">
          <i class="ri-edit-line"></i>
          编辑
        </button>
        <button class="btn-text danger" onclick="deleteProvider(${p.id})">
          <i class="ri-delete-bin-line"></i>
          删除
        </button>
      </div>
    </div>
  `).join('');
}

// 测试连接
async function testProvider(providerId) {
  const btn = event.target.closest('button');
  btn.classList.add('loading');
  
  try {
    const response = await fetch(`/api/agents/providers/${providerId}/test`, {
      method: 'POST'
    });
    const result = await response.json();
    
    if (result.status === 'success') {
      showToast('连接测试成功', 'success');
    } else {
      showToast(`连接失败：${result.message}`, 'error');
    }
  } catch (error) {
    showToast('测试失败', 'error');
  } finally {
    btn.classList.remove('loading');
  }
}
</script>

<style>
.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.provider-card {
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.provider-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  border-color: #5B7FFF;
}

.provider-card.default {
  border-color: #5B7FFF;
  background: linear-gradient(135deg, #F8FAFF, #FFFFFF);
}

.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.provider-header h3 {
  font-size: 18px;
  color: #1A1A1A;
  margin: 0;
}

.default-badge {
  padding: 4px 10px;
  background: #5B7FFF;
  color: #FFFFFF;
  border-radius: 12px;
  font-size: 12px;
}

.provider-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #F0F2F5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: #667788;
  font-size: 14px;
}

.info-row .value {
  color: #1A1A1A;
  font-weight: 500;
}

.provider-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #E8ECF0;
}

.provider-actions .btn-text {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
}

.provider-actions .btn-text.danger {
  color: #EF4444;
}
</style>
{% endblock %}
```

---

### 3.4 移除难度 5 个小蓝点

```css
/* app/static/css/questions.css - 找到并删除/注释以下代码 */

/* ===== 删除前 ===== */
.question-dots {
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
}

/* ===== 删除后 ===== */
/* 难度指示器已移除 - 2025 */
/* .question-dots { ... } */
```

```html
<!-- app/templates/components/question_card.html -->

<!-- 删除前 -->
<div class="question-card">
  <h3 class="question-title">{{ question.title }}</h3>
  <div class="question-meta">
    <span class="question-type">{{ question.question_type }}</span>
    <div class="question-dots">
      <span class="dot active"></span>
      <span class="dot active"></span>
      <span class="dot active"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
  </div>
</div>

<!-- 删除后 -->
<div class="question-card">
  <h3 class="question-title">{{ question.title }}</h3>
  <div class="question-meta">
    <span class="question-type">{{ question.question_type }}</span>
    <!-- 难度指示器已移除 -->
  </div>
</div>
```

---

### 3.5 知识图谱可视化（ECharts Graph）

```html
<!-- app/templates/knowledge_graph.html -->

<div class="graph-container" id="knowledgeGraph"></div>

<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
// 初始化知识图谱
async function initKnowledgeGraph() {
  const courseId = getCurrentCourseId();
  const response = await fetch(`/api/knowledge/${courseId}/graph`);
  const graphData = await response.json();
  
  const chart = echarts.init(document.getElementById('knowledgeGraph'));
  
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
          return `<strong>${params.name}</strong><br/>关联知识点：${params.data.links || 0} 个`;
        }
        return `${params.data.source} → ${params.data.target}<br/>类型：${params.data.relation_type}`;
      }
    },
    legend: [{
      data: graphData.categories.map(c => c.name),
      bottom: 10,
      left: 'center'
    }],
    series: [{
      type: 'graph',
      layout: 'force',
      data: graphData.nodes,
      links: graphData.links,
      categories: graphData.categories,
      roam: true,  // 支持缩放平移
      draggable: true,
      
      // 节点样式
      symbol: 'circle',
      symbolSize: function(val, params) {
        return params.data.symbolSize || 30;
      },
      label: {
        show: true,
        position: 'right',
        color: '#1A1A1A',
        fontSize: 12
      },
      
      // 连线样式
      lineStyle: {
        color: 'source',
        curveness: 0.3,
        width: 1.5,
        opacity: 0.7
      },
      
      // 高亮样式
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 3
        }
      },
      
      // 力导向布局配置
      force: {
        repulsion: 200,  // 节点斥力
        gravity: 0.1,    // 引力
        edgeLength: [50, 200],  // 边长范围
        layoutAnimation: true
      }
    }],
    
    // 交互
    animationDuration: 1500,
    animationThreshold: 500
  };
  
  chart.setOption(option);
  
  // 点击节点事件
  chart.on('click', function(params) {
    if (params.dataType === 'node') {
      showFragmentDetail(params.data.id);
    }
  });
  
  // 窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize();
  });
}

// 显示知识点详情
function showFragmentDetail(fragmentId) {
  // 实现详情弹窗
}

// 搜索过滤
function filterGraph(keyword) {
  // 高亮匹配节点
}

initKnowledgeGraph();
</script>

<style>
.graph-container {
  width: 100%;
  height: 600px;
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 12px;
}
</style>
```

---

### 3.6 学生答题页面（参考洛谷）

```html
<!-- app/templates/answer.html -->

{% extends "base.html" %}

{% block title %}答题 - {{ question.title }}{% endblock %}

{% block content %}
<div class="answer-page">
  <div class="page-header">
    <h1>{{ question.title }}</h1>
    <div class="question-meta">
      <span class="meta-item">
        <i class="ri-time-line"></i>
        <span>限时 {{ question.time_limit }} 分钟</span>
      </span>
      <span class="meta-item">
        <i class="ri-star-line"></i>
        <span>满分 {{ question.max_score }} 分</span>
      </span>
    </div>
  </div>
  
  <div class="answer-layout">
    <!-- 左侧：题目描述 -->
    <div class="question-panel">
      <div class="panel-header">
        <h2>题目描述</h2>
      </div>
      <div class="panel-content">
        <div class="question-description">
          {{ question.description | safe }}
        </div>
        
        {% if question.input_format %}
        <div class="format-section">
          <h3>输入格式</h3>
          <pre>{{ question.input_format }}</pre>
        </div>
        {% endif %}
        
        {% if question.output_format %}
        <div class="format-section">
          <h3>输出格式</h3>
          <pre>{{ question.output_format }}</pre>
        </div>
        {% endif %}
        
        {% if question.sample_input %}
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
        {% endif %}
      </div>
    </div>
    
    <!-- 右侧：答题区 -->
    <div class="answer-panel">
      <div class="panel-header">
        <h2>作答</h2>
      </div>
      <div class="panel-content">
        <form id="answerForm">
          {% if question.question_type == 'programming' %}
          <!-- 编程题：代码编辑器 -->
          <div class="code-editor-wrapper">
            <div class="editor-toolbar">
              <select id="languageSelect">
                <option value="python">Python 3</option>
                <option value="cpp">C++ 17</option>
                <option value="java">Java 11</option>
              </select>
              <button type="button" class="btn-text" onclick="insertTemplate()">
                <i class="ri-file-code-line"></i>
                模板
              </button>
            </div>
            <textarea id="codeEditor" class="code-editor" placeholder="在此编写代码..."></textarea>
          </div>
          
          {% elif question.question_type == 'subjective' %}
          <!-- 主观题：文本框 -->
          <textarea id="answerText" class="answer-textarea" 
                    placeholder="请输入你的答案..."></textarea>
          
          {% else %}
          <!-- 客观题：选项 -->
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
          
          <div class="form-actions">
            <button type="button" class="btn-secondary" onclick="saveDraft()">
              <i class="ri-save-line"></i>
              保存草稿
            </button>
            <button type="submit" class="btn-primary">
              <i class="ri-submit-line"></i>
              提交答案
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- 提交结果弹窗 -->
<div class="modal" id="resultModal">
  <div class="modal-content result-content">
    <div class="result-header">
      <h2>提交结果</h2>
    </div>
    <div class="result-body">
      <div class="result-status" id="resultStatus">
        <i class="ri-loader-4-line"></i>
        <span>判题中...</span>
      </div>
      
      <div class="test-cases" id="testCases">
        <!-- 测试点详情 -->
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-primary" onclick="closeResultModal()">关闭</button>
    </div>
  </div>
</div>

<script>
// 提交答案
document.getElementById('answerForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const questionId = {{ question.id }};
  const courseId = getCurrentCourseId();
  
  let submissionData = {
    question_id: questionId,
    course_id: courseId,
    language: document.getElementById('languageSelect')?.value || null
  };
  
  // 根据题型收集答案
  {% if question.question_type == 'programming' %}
  submissionData.code_content = document.getElementById('codeEditor').value;
  {% elif question.question_type == 'subjective' %}
  submissionData.answer_text = document.getElementById('answerText').value;
  {% else %}
  const selected = document.querySelector('input[name="answer"]:checked');
  if (!selected) {
    showToast('请选择答案', 'warning');
    return;
  }
  submissionData.answer_text = selected.value;
  {% endif %}
  
  // 提交
  const btn = e.target.querySelector('button[type="submit"]');
  btn.classList.add('loading');
  
  try {
    const response = await fetch('/api/submissions', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(submissionData)
    });
    
    const result = await response.json();
    
    // 显示结果
    showResult(result);
  } catch (error) {
    showToast('提交失败', 'error');
  } finally {
    btn.classList.remove('loading');
  }
});

// 显示判题结果
function showResult(submission) {
  const modal = document.getElementById('resultModal');
  const statusEl = document.getElementById('resultStatus');
  
  modal.classList.add('show');
  
  // 轮询判题状态
  async function pollResult() {
    const response = await fetch(`/api/submissions/${submission.id}`);
    const data = await response.json();
    
    if (data.status === 'graded') {
      // 判题完成
      statusEl.className = `result-status ${data.score > 0 ? 'success' : 'failed'}`;
      statusEl.innerHTML = `
        <i class="ri-${data.score > 0 ? 'check' : 'close'}-circle-line"></i>
        <span>${data.score > 0 ? '通过' : '未通过'}</span>
        <span class="score">${data.score} / {{ question.max_score }} 分</span>
      `;
      
      // 显示测试点详情
      showTestCases(data.test_cases);
    } else {
      // 继续轮询
      setTimeout(pollResult, 1000);
    }
  }
  
  pollResult();
}

// 保存草稿
function saveDraft() {
  const content = document.getElementById('codeEditor')?.value || 
                  document.getElementById('answerText')?.value;
  localStorage.setItem(`draft_${questionId}`, content);
  showToast('草稿已保存', 'success');
}

// 加载草稿
function loadDraft() {
  const draft = localStorage.getItem(`draft_${questionId}`);
  if (draft) {
    const editor = document.getElementById('codeEditor') || document.getElementById('answerText');
    if (editor) editor.value = draft;
  }
}

// 页面加载时
loadDraft();
</script>

<style>
.answer-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.answer-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 24px;
}

.question-panel, .answer-panel {
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 12px;
  overflow: hidden;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #E8ECF0;
  background: #F8FAFF;
}

.panel-header h2 {
  font-size: 16px;
  margin: 0;
  color: #1A1A1A;
}

.panel-content {
  padding: 20px;
}

.question-description {
  line-height: 1.8;
  color: #333;
}

.format-section, .sample-section {
  margin-top: 24px;
}

.format-section h3, .sample-section h3 {
  font-size: 14px;
  color: #667788;
  margin-bottom: 8px;
}

.format-section pre, .sample-section pre {
  background: #F5F7FA;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  overflow-x: auto;
}

.sample-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.sample-box {
  background: #F5F7FA;
  padding: 12px;
  border-radius: 6px;
}

.sample-title {
  font-size: 12px;
  color: #99AAB5;
  margin-bottom: 8px;
}

/* 代码编辑器 */
.code-editor-wrapper {
  margin-bottom: 16px;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.code-editor {
  width: 100%;
  height: 300px;
  padding: 12px;
  border: 1px solid #E8ECF0;
  border-radius: 6px;
  font-family: 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
}

.answer-textarea {
  width: 100%;
  min-height: 200px;
  padding: 12px;
  border: 1px solid #E8ECF0;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.8;
  resize: vertical;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid #E8ECF0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #5B7FFF;
  background: #F8FAFF;
}

.option-item input[type="radio"]:checked + .option-key + .option-content {
  color: #5B7FFF;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #E8ECF0;
}

/* 结果弹窗 */
.result-content {
  max-width: 600px;
}

.result-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px;
  justify-content: center;
  font-size: 18px;
}

.result-status.success {
  color: #10B981;
}

.result-status.failed {
  color: #EF4444;
}

.score {
  margin-left: 16px;
  font-size: 24px;
  font-weight: 600;
}

.test-cases {
  margin-top: 24px;
  border-top: 1px solid #E8ECF0;
  padding-top: 16px;
}

.test-case-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.test-case-item.passed {
  background: rgba(16, 185, 129, 0.1);
}

.test-case-item.failed {
  background: rgba(239, 68, 68, 0.1);
}
</style>
{% endblock %}
```

---

### 3.7 注册页背景优化

```css
/* app/static/css/auth.css */

/* ===== 注册页背景优化 ===== */

.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* 新背景：浅色渐变 + 抽象几何 */
  background: 
    linear-gradient(135deg, rgba(91, 127, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%),
    url('/static/images/bg-geometric.svg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

/* 或者使用纯 CSS 几何背景 */
.register-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(91, 127, 255, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
  pointer-events: none;
  z-index: -1;
}

/* 登录页同步更新 */
.login-page {
  /* 同样应用新背景 */
}
```

```svg
<!-- app/static/images/bg-geometric.svg -->

<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#5B7FFF;stop-opacity:0.1" />
      <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:0.1" />
    </linearGradient>
  </defs>
  
  <!-- 背景 -->
  <rect width="1920" height="1080" fill="#F5F7FA"/>
  
  <!-- 几何图形 -->
  <circle cx="200" cy="150" r="100" fill="url(#grad1)" opacity="0.5"/>
  <circle cx="1700" cy="900" r="150" fill="url(#grad1)" opacity="0.5"/>
  <circle cx="960" cy="540" r="200" fill="url(#grad1)" opacity="0.3"/>
  
  <!-- 三角形 -->
  <polygon points="400,800 500,600 600,800" fill="rgba(91,127,255,0.08)"/>
  <polygon points="1400,300 1500,100 1600,300" fill="rgba(139,92,246,0.08)"/>
  
  <!-- 线条装饰 -->
  <line x1="0" y1="200" x2="1920" y2="200" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
  <line x1="0" y1="400" x2="1920" y2="400" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
  <line x1="0" y1="600" x2="1920" y2="600" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
  <line x1="0" y1="800" x2="1920" y2="800" stroke="rgba(91,127,255,0.05)" stroke-width="1"/>
</svg>
```

---

## 📝 四、日志系统实现

### 4.1 日志装饰器

```python
# app/utils/logging.py

from functools import wraps
from datetime import datetime
import json
import time

def log_operation(action: str, resource_type: str = None, log_request: bool = True):
    """
    操作日志装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            request = kwargs.get('request') or next((arg for arg in args if hasattr(arg, 'headers')), None)
            
            log_data = {
                'action': action,
                'resource_type': resource_type,
                'user_id': None,
                'ip_address': None,
                'request_method': None,
                'request_path': None,
                'status': 'success',
                'old_value': None,
                'new_value': None
            }
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 记录成功日志
                log_data['status'] = 'success'
                log_data['new_value'] = result if isinstance(result, dict) else None
                
                return result
                
            except Exception as e:
                # 记录失败日志
                log_data['status'] = 'failed'
                log_data['error_message'] = str(e)
                raise
            finally:
                # 补充公共信息
                if request:
                    log_data['ip_address'] = request.client.host
                    log_data['request_method'] = request.method
                    log_data['request_path'] = request.url.path
                
                log_data['duration_ms'] = int((time.time() - start_time) * 1000)
                
                # 异步写入日志（不阻塞主流程）
                asyncio.create_task(write_operation_log(log_data))
        
        return wrapper
    return decorator

async def write_operation_log(log_data: dict):
    """
    写入操作日志
    """
    try:
        from app.models import OperationLog
        from app.database import get_db_session
        
        db = next(get_db_session())
        
        log = OperationLog(**log_data)
        db.add(log)
        db.commit()
    except Exception as e:
        # 日志写入失败不影响主流程
        print(f"日志写入失败：{e}")
    finally:
        db.close()
```

### 4.2 使用示例

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

---

## ✅ 五、实现检查清单

### 阶段一：核心架构（第 1-2 周）

- [ ] 数据库表结构变更（courses, course_users）
- [ ] 课程管理 API（CRUD）
- [ ] 权限检查装饰器
- [ ] 全局课程选择器组件
- [ ] 现有数据迁移脚本

### 阶段二：功能完善（第 3-4 周）

- [ ] 聊天记录删除功能
- [ ] 题目删除功能（含回收站）
- [ ] Agent 配置页面
- [ ] 日志系统基础
- [ ] 移除难度小蓝点
- [ ] 注册页背景更新

### 阶段三：可视化与答题（第 5-6 周）

- [ ] 知识图谱 ECharts 可视化
- [ ] 学生答题页面
- [ ] 判题逻辑（客观题）
- [ ] 日志查看页面
- [ ] 性能优化与测试

---

## 🚨 六、风险提示

| 风险点 | 影响 | 缓解措施 |
|--------|------|----------|
| 多课程数据隔离 | 高 | 严格测试权限边界，编写跨课程访问测试用例 |
| API Key 安全 | 高 | Fernet 加密存储，操作审计日志 |
| 判题沙箱安全 | 高 | MVP 阶段用第三方 API，后期自建 Docker 沙箱 |
| 知识图谱性能 | 中 | 限制节点数 500，分页加载 |
| 日志存储膨胀 | 低 | 90 天自动归档，定期清理 |

---

## 📦 七、交付物清单

```
项目交付文件结构：

AG/
├── implementation-prompt.md      # 本提示词文档
├── feature-requests-analysis.md  # 需求分析文档
├── database-migration.sql        # 数据库迁移脚本
├── api-reference.md              # API 接口文档
└── ui-components.md              # UI 组件规范

app/
├── api/
│   ├── courses.py               # 课程管理 API
│   ├── agents.py                # Agent 配置 API
│   ├── submissions.py           # 答题提交 API
│   ├── knowledge_graph.py       # 知识图谱 API
│   └── logs.py                  # 日志系统 API
├── models/
│   ├── course.py                # 课程模型
│   ├── ai_provider.py           # AI 服务商模型
│   ├── submission.py            # 答题提交模型
│   └── operation_log.py         # 日志模型
├── templates/
│   ├── agent_settings.html      # Agent 配置页
│   ├── answer.html              # 答题页面
│   └── knowledge_graph.html     # 知识图谱页
└── static/
    ├── css/
    │   └── auth.css             # 注册页样式更新
    └── images/
        └── bg-geometric.svg     # 新背景图
```

---

> **文档版本**：v1.0  
> **最后更新**：2025 年  
> **适用项目**：基于 Agent 的课程助教系统  
> **技术栈**：FastAPI + SQLAlchemy + MySQL + Jinja2 + ECharts
