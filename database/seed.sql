-- =====================================================================
-- 基于 Agent 的课程助教系统 —— 初始数据
-- 依赖：schema.sql 已执行
--
-- 说明：
--   * 密码使用 SHA-256 存储（演示简化），初始账号密码见 README。
--   * 验证课程取《数据结构》，用于示例知识库 / 答疑 / 出题。
--   * admin / teacher / student 为三类内置演示账号。
-- =====================================================================
USE course_ta;

-- ---- 用户：admin / teacher / student（密码均为 123456 的 SHA-256） ----
-- 123456 的 SHA-256 = 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
INSERT INTO users (username, password_hash, real_name, role) VALUES
 ('admin',   '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '管理员', 'admin'),
 ('teacher', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '王老师', 'teacher'),
 ('student', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '李同学', 'student');

INSERT INTO teachers (user_id, teacher_no, department) VALUES
 (2, 'T2026001', '人工智能与大数据学院');

INSERT INTO students (user_id, student_no, class_name) VALUES
 (3, '2026001', '计算机科学与技术1班');

-- ---- 课程：数据结构（授课教师 = teacher, id=2） ----
INSERT INTO courses (name, code, teacher_id, description) VALUES
 ('数据结构', 'CS2001', 2, '本课程介绍线性表、栈、队列、树、图及查找与排序等基本数据结构与算法。');

INSERT INTO enrollments (student_id, course_id) VALUES (3, 1);

-- ---- 作业（用于演示 AI 辅助批改） ----
INSERT INTO assignments (course_id, title, description, deadline) VALUES
 (1, '线性表综合练习', '编写算法实现单链表的插入、删除与逆置，并说明时间/空间复杂度。',
  DATE_ADD(NOW(), INTERVAL 7 DAY)),
 (1, '二叉树遍历', '分别用递归与非递归方式实现二叉树的前序、中序、后序遍历。',
  DATE_ADD(NOW(), INTERVAL 14 DAY));

-- ---- 学生提交一份待批改作业 ----
INSERT INTO submissions (assignment_id, student_id, content, status) VALUES
 (1, 3, '单链表插入：先申请新结点，将新结点 next 指向当前结点的后继，再将当前结点 next 指向新结点，时间复杂度 O(1)。删除：将当前结点 next 指向后继的后继，释放结点，时间复杂度 O(1)。逆置：头插法依次插入，时间复杂度 O(n)。', 'pending');

-- ---- Agent 注册配置（答疑/批改/出题 三 Agent） ----
INSERT INTO agent_configs (name, role_desc, model, enabled, route_keywords, sort_order) VALUES
 ('答疑Agent',  '面向学生，基于 RAG 课程知识库进行多轮答疑并溯源引用。', 'qwen-plus', 1, '答疑,问题,不会,讲解,概念,含义', 1),
 ('批改Agent',  '面向教师，对学生作业进行 AI 辅助批改、评分并生成评语。', 'qwen-plus', 1, '批改,评分,作业,评语,打分', 2),
 ('出题Agent',  '面向教师，依据知识点与难度批量生成试题。',            'qwen-plus', 1, '出题,试题,测验,题目', 3);