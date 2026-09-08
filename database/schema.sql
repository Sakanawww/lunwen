-- =====================================================================
-- 基于 Agent 的课程助教系统 —— 数据库建表脚本
-- MySQL 8.0 / 字符集 utf8mb4
-- 数据库：course_ta
-- =====================================================================
CREATE DATABASE IF NOT EXISTS course_ta
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE course_ta;

-- ---------------------------------------------------------------------
-- 1. 用户表（含学生、教师、管理员三类角色，统一账号体系）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
  username      VARCHAR(50)  NOT NULL UNIQUE COMMENT '登录用户名',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希（SHA-256）',
  real_name     VARCHAR(50)  NOT NULL COMMENT '真实姓名',
  role          ENUM('student','teacher','admin') NOT NULL COMMENT '角色：学生/教师/管理员',
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB COMMENT='用户表';

-- ---------------------------------------------------------------------
-- 2. 学生表（扩展学生角色信息）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS students;
CREATE TABLE students (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '学生ID',
  user_id     BIGINT UNSIGNED NOT NULL COMMENT '对应用户ID',
  student_no  VARCHAR(20) NOT NULL UNIQUE COMMENT '学号',
  class_name  VARCHAR(50) COMMENT '班级',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='学生表';

-- ---------------------------------------------------------------------
-- 3. 教师表（扩展教师角色信息）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS teachers;
CREATE TABLE teachers (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '教师ID',
  user_id     BIGINT UNSIGNED NOT NULL COMMENT '对应用户ID',
  teacher_no  VARCHAR(20) NOT NULL UNIQUE COMMENT '工号',
  department  VARCHAR(50) COMMENT '所属院系',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='教师表';

-- ---------------------------------------------------------------------
-- 4. 课程表
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '课程ID',
  name         VARCHAR(100) NOT NULL COMMENT '课程名称',
  code         VARCHAR(30)  COMMENT '课程编号',
  teacher_id   BIGINT UNSIGNED COMMENT '授课教师(users.id)',
  description  TEXT COMMENT '课程简介',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='课程表';

-- ---------------------------------------------------------------------
-- 5. 选课表（学生与课程的多对多关系）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS enrollments;
CREATE TABLE enrollments (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
  student_id BIGINT UNSIGNED NOT NULL COMMENT '学生(users.id)',
  course_id  BIGINT UNSIGNED NOT NULL COMMENT '课程(courses.id)',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
  UNIQUE KEY uk_enroll (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id)  REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='选课表';

-- ---------------------------------------------------------------------
-- 6. 知识库文档表（RAG 源文件）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS knowledge_docs;
CREATE TABLE knowledge_docs (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '文档ID',
  course_id  BIGINT UNSIGNED NOT NULL COMMENT '所属课程',
  title      VARCHAR(200) NOT NULL COMMENT '文档标题',
  file_name  VARCHAR(255) COMMENT '原始文件名',
  chunk_num  INT    NOT NULL DEFAULT 0 COMMENT '切分得到的知识块数量',
  upload_by  BIGINT UNSIGNED COMMENT '上传教师(users.id)',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='知识库文档表';

-- ---------------------------------------------------------------------
-- 7. 知识块表（RAG 检索单元：文本块，含来源文档与位置）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS knowledge_chunks;
CREATE TABLE knowledge_chunks (
  id      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '知识块ID',
  doc_id  BIGINT UNSIGNED NOT NULL COMMENT '所属文档(knowledge_docs.id)',
  seq     INT  NOT NULL COMMENT '块在文档中的序号',
  content TEXT NOT NULL COMMENT '文本内容',
  source  VARCHAR(255) COMMENT '来源标注（用于溯源引用）',
  FOREIGN KEY (doc_id) REFERENCES knowledge_docs(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='知识块表';

-- ---------------------------------------------------------------------
-- 8. 会话表（学生与答疑 Agent 的多轮对话会话）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '会话ID',
  user_id    BIGINT UNSIGNED NOT NULL COMMENT '所属用户(users.id)',
  course_id  BIGINT UNSIGNED COMMENT '会话关联课程',
  title      VARCHAR(120) COMMENT '会话标题',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='会话表';

-- ---------------------------------------------------------------------
-- 9. 消息表（会话内的 Q/A 消息，含溯源来源）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
  session_id BIGINT UNSIGNED NOT NULL COMMENT '所属会话(sessions.id)',
  role       ENUM('user','assistant','agent') NOT NULL COMMENT '消息角色',
  content    TEXT NOT NULL COMMENT '消息内容',
  sources    TEXT COMMENT '溯源来源（JSON: 文档标题+块序号）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='消息表';

-- ---------------------------------------------------------------------
-- 10. 作业表
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS assignments;
CREATE TABLE assignments (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '作业ID',
  course_id   BIGINT UNSIGNED NOT NULL COMMENT '所属课程',
  title       VARCHAR(200) NOT NULL COMMENT '作业标题',
  description TEXT COMMENT '作业要求',
  deadline    DATETIME COMMENT '截止时间',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业表';

-- ---------------------------------------------------------------------
-- 11. 作业提交表（学生提交的作业答案）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '提交ID',
  assignment_id BIGINT UNSIGNED NOT NULL COMMENT '所属作业(assignments.id)',
  student_id    BIGINT UNSIGNED NOT NULL COMMENT '提交学生(users.id)',
  content       TEXT NOT NULL COMMENT '作业答案内容',
  status        ENUM('pending','graded') NOT NULL DEFAULT 'pending' COMMENT '批改状态',
  submitted_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  UNIQUE KEY uk_sub (assignment_id, student_id),
  FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
  FOREIGN KEY (student_id)    REFERENCES users(id)     ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业提交表';

-- ---------------------------------------------------------------------
-- 12. 批改记录表（AI 辅助批改结果）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS grading_records;
CREATE TABLE grading_records (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '批改ID',
  submission_id BIGINT UNSIGNED NOT NULL COMMENT '对应提交(submissions.id)',
  score         DECIMAL(5,2) COMMENT '得分',
  feedback      TEXT COMMENT '评语/批改意见',
  grade_by      ENUM('ai','teacher') NOT NULL DEFAULT 'ai' COMMENT '批改来源：AI 或教师',
  graded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '批改时间',
  FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='批改记录表';

-- ---------------------------------------------------------------------
-- 13. 试题表（AI 生成 / 教师录入）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS questions;
CREATE TABLE questions (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '试题ID',
  course_id   BIGINT UNSIGNED NOT NULL COMMENT '所属课程',
  type        ENUM('choice','fill','short') NOT NULL COMMENT '题型：选择/填空/简答',
  stem        TEXT NOT NULL COMMENT '题干',
  options     TEXT COMMENT '选项（选择题，JSON 或分号分隔）',
  answer      TEXT COMMENT '参考答案',
  difficulty  TINYINT COMMENT '难度（1-5）',
  created_by  BIGINT UNSIGNED COMMENT '创建者(users.id)',
  source      ENUM('ai','manual') NOT NULL DEFAULT 'manual' COMMENT '来源：AI 生成或手工录入',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='试题表';

-- ---------------------------------------------------------------------
-- 14. 学情记录表（学生自测答题记录，用于学情看板）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS learning_records;
CREATE TABLE learning_records (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
  student_id  BIGINT UNSIGNED NOT NULL COMMENT '学生(users.id)',
  course_id   BIGINT UNSIGNED NOT NULL COMMENT '课程(courses.id)',
  question_id BIGINT UNSIGNED COMMENT '作答试题(questions.id)',
  is_correct  TINYINT(1) COMMENT '是否答对',
  score       DECIMAL(5,2) COMMENT '本次得分',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作答时间',
  FOREIGN KEY (student_id)  REFERENCES users(id)       ON DELETE CASCADE,
  FOREIGN KEY (course_id)   REFERENCES courses(id)     ON DELETE CASCADE,
  FOREIGN KEY (question_id) REFERENCES questions(id)   ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='学情记录表';

-- ---------------------------------------------------------------------
-- 15. Agent 配置表（管理员端：Agent 注册与编排配置）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS agent_configs;
CREATE TABLE agent_configs (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT 'AgentID',
  name         VARCHAR(50) NOT NULL UNIQUE COMMENT 'Agent 名称（答疑/批改/出题）',
  role_desc    VARCHAR(255) COMMENT '角色职责描述',
  model        VARCHAR(100) COMMENT '使用的模型',
  enabled      TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  route_keywords VARCHAR(255) COMMENT '编排路由关键词（逗号分隔）',
  sort_order   INT NOT NULL DEFAULT 0 COMMENT '调度顺序',
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB COMMENT='Agent配置表';

-- ---------------------------------------------------------------------
-- 16. 系统日志表（管理员端审计日志）
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS system_logs;
CREATE TABLE system_logs (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
  user_id    BIGINT UNSIGNED COMMENT '操作用户(users.id)',
  action     VARCHAR(100) NOT NULL COMMENT '操作动作',
  detail     TEXT COMMENT '操作详情',
  ip         VARCHAR(45) COMMENT '来源IP',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='系统日志表';