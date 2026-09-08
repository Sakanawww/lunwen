-- =====================================================================
-- 002_add_demo_courses_users.sql
-- 知识图谱多课程扩展：新增 3 门课程、2 位老师、10 位学生的演示数据。
-- 依赖：001_add_course_users.sql（course_users 表）已执行。
-- 幂等：INSERT ... 使用唯一键 / ON DUPLICATE KEY 忽略重复。
-- =====================================================================
USE course_ta;

-- ---- 1. 新增 2 位老师（密码均为 123456 的 SHA-256） ----
-- 123456 的 SHA-256 = 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
INSERT IGNORE INTO users (username, password_hash, real_name, role)
SELECT 'teacher2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '李老师', 'teacher';

INSERT IGNORE INTO users (username, password_hash, real_name, role)
SELECT 'teacher3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '张老师', 'teacher';

INSERT INTO teachers (user_id, teacher_no, department)
SELECT id, 'T2026002', '人工智能与大数据学院' FROM users WHERE username = 'teacher2'
  AND NOT EXISTS (SELECT 1 FROM teachers WHERE teacher_no = 'T2026002');

INSERT INTO teachers (user_id, teacher_no, department)
SELECT id, 'T2026003', '软件学院' FROM users WHERE username = 'teacher3'
  AND NOT EXISTS (SELECT 1 FROM teachers WHERE teacher_no = 'T2026003');

-- ---- 2. 新增 10 位学生（密码均为 123456） ----
INSERT IGNORE INTO users (username, password_hash, real_name, role) VALUES
('student001', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生甲', 'student'),
('student002', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生乙', 'student'),
('student003', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生丙', 'student'),
('student004', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生丁', 'student'),
('student005', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生戊', 'student'),
('student006', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生己', 'student'),
('student007', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生庚', 'student'),
('student008', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生辛', 'student'),
('student009', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生壬', 'student'),
('student010', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '学生癸', 'student');

INSERT INTO students (user_id, student_no, class_name)
SELECT u.id, u.username, '计算机科学与技术1班' FROM users u WHERE u.username IN ('student001','student002','student003','student004','student005','student006','student007','student008','student009','student010')
  AND NOT EXISTS (SELECT 1 FROM students s WHERE s.student_no = u.username);

-- ---- 3. 新增 3 门课程（数据结构已存在；幂等：仅当 code 不存在时插入） ----
-- 操作系统 → 李老师(teacher2)；计算机网络 → 张老师(teacher3)；计算机基础原理 → 李老师
-- 说明：course.code 未声明唯一，故幂等依赖 Nonexistent 检查；已加唯一索引 uk_courses_code 兜底。
INSERT INTO courses (name, code, teacher_id, description)
SELECT '操作系统', 'CS201', t.user_id, '进程管理、内存管理、文件系统等核心概念'
FROM teachers t WHERE t.teacher_no = 'T2026002'
  AND NOT EXISTS (SELECT 1 FROM courses WHERE code = 'CS201');

INSERT INTO courses (name, code, teacher_id, description)
SELECT '计算机网络', 'CS301', t.user_id, 'OSI 参考模型、TCP/IP 协议栈、网络编程'
FROM teachers t WHERE t.teacher_no = 'T2026003'
  AND NOT EXISTS (SELECT 1 FROM courses WHERE code = 'CS301');

INSERT INTO courses (name, code, teacher_id, description)
SELECT '计算机基础原理', 'CS401', t.user_id, '数字逻辑、计算机组成、指令系统'
FROM teachers t WHERE t.teacher_no = 'T2026002'
  AND NOT EXISTS (SELECT 1 FROM courses WHERE code = 'CS401');

-- ---- 4. course_users：课程归属（owner）----
-- 数据结构(id=1) owner = 王老师(teacher, username='teacher')
-- 操作系统(id=2) owner = 李老师(teacher2)
-- 计算机网络(id=3) owner = 张老师(teacher3)
-- 计算机基础原理(id=4) owner = 李老师(teacher2)
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'owner'
FROM courses c JOIN users u ON (c.code='CS2001' AND u.username='teacher')
WHERE c.code='CS2001';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'owner'
FROM courses c JOIN users u ON (c.code='CS201' AND u.username='teacher2')
WHERE c.code='CS201';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'owner'
FROM courses c JOIN users u ON (c.code='CS301' AND u.username='teacher3')
WHERE c.code='CS301';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'owner'
FROM courses c JOIN users u ON (c.code='CS401' AND u.username='teacher2')
WHERE c.code='CS401';

-- ---- 5. 学生选课（course_users + enrollments 保持一致）----
-- student001..010 每生选 2-3 门课
-- student001: 数据结构 + 操作系统
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS2001' AND u.username='student001';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS201' AND u.username='student001';
-- student002: 数据结构 + 计算机网络
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS2001' AND u.username='student002';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS301' AND u.username='student002';
-- student003: 操作系统 + 计算机基础
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS201' AND u.username='student003';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS401' AND u.username='student003';
-- student004: 计算机网络
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS301' AND u.username='student004';
-- student005: 数据结构 + 操作系统
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS2001' AND u.username='student005';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS201' AND u.username='student005';
-- student006: 计算机基础 + 计算机网络
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS401' AND u.username='student006';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS301' AND u.username='student006';
-- student007: 数据结构
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS2001' AND u.username='student007';
-- student008: 操作系统 + 计算机网络
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS201' AND u.username='student008';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS301' AND u.username='student008';
-- student009: 计算机基础
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS401' AND u.username='student009';
-- student010: 数据结构 + 计算机基础
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS2001' AND u.username='student010';
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT c.id, u.id, 'student' FROM courses c, users u WHERE c.code='CS401' AND u.username='student010';

-- 同步 enrollments（保持与 course_users 的学生关系一致，避免重复）
INSERT IGNORE INTO enrollments (student_id, course_id)
SELECT cu.user_id, cu.course_id FROM course_users cu WHERE cu.role = 'student';