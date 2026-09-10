# ADR-005: 使用多课程架构支持 RBAC 权限

## 状态

已采纳

## 上下文

系统初始设计为单课程架构，所有数据（题目、聊天记录、知识库等）都归属于单一课程。随着系统扩展，需要支持多课程管理，每个课程有独立的教师、学生和知识库，并且需要实现基于角色的访问控制（RBAC）。

## 决策

采用 **多课程架构**，通过 `courses` 表和 `course_users` 表实现课程管理和用户权限控制。

## 理由

1. **实际场景需求**：真实的教学场景中，一位教师可能教授多门课程，一位学生也可能选修多门课程。

2. **数据隔离**：不同课程的知识库、题目、聊天记录等数据需要隔离，避免混淆。

3. **权限细化**：通过 `course_users` 表实现课程级别的角色权限（owner/teacher/assistant/student）。

4. **扩展性**：为后续的课程间数据共享、跨课程统计等功能奠定基础。

## 架构设计

### 核心表结构

```sql
-- 课程表
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
);

-- 课程用户关联表（RBAC 核心）
CREATE TABLE course_users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  course_id INT NOT NULL,
  user_id INT NOT NULL,
  role ENUM('owner', 'teacher', 'assistant', 'student') NOT NULL,
  enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_course_user (course_id, user_id),
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 权限矩阵

| 角色 | 权限 |
|------|------|
| owner | 所有权限（包括删除课程、转移所有权） |
| teacher | 查看/编辑/批改/聊天/RAG/题目管理 |
| assistant | 查看/批改/聊天（不可删除） |
| student | 查看/聊天/提交作业 |

## 数据迁移

为现有表添加 `course_id` 外键：
- `questions`
- `chat_sessions`
- `knowledge_fragments`
- `assignments`
- `submissions`

## 后果

### 正面影响

- 支持多课程并行运行
- 数据隔离清晰
- 权限控制细粒度

### 负面影响

- 数据库迁移复杂度增加
- 所有查询需要增加 `course_id` 过滤
- API 需要增加权限检查中间件

## 相关文档

- `app/models/course.py` - 课程模型
- `app/models/course_user.py` - 课程用户关联模型
- `框架说明文档.md` - 第 4.5 节 数据模型
