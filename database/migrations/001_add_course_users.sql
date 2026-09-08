-- =====================================================================
-- 迁移：模块1 RBAC 多课程成员体系 —— 新增 course_users 表
-- 兼容旧数据并回填：
--   * courses.teacher_id   → course_users.role = 'owner'（授课教师→课程 owner）
--   * enrollments(student) → course_users.role = 'student'
-- 幂等：使用 CREATE TABLE IF NOT EXISTS 与 INSERT IGNORE，可重复执行。
-- =====================================================================
USE course_ta;

CREATE TABLE IF NOT EXISTS course_users (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '成员ID',
  course_id  BIGINT UNSIGNED NOT NULL COMMENT '课程(courses.id)',
  user_id    BIGINT UNSIGNED NOT NULL COMMENT '用户(users.id)',
  role       ENUM('owner','teacher','assistant','student') NOT NULL COMMENT '课程内角色',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  UNIQUE KEY uk_course_user (course_id, user_id),
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='课程成员表(RBAC)';

-- 回填：授课教师对应课程 → owner
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT id, teacher_id, 'owner'
FROM courses
WHERE teacher_id IS NOT NULL;

-- 回填：选课记录 → student
INSERT IGNORE INTO course_users (course_id, user_id, role)
SELECT course_id, student_id, 'student'
FROM enrollments;

-- 便于作为脚本文件执行时输出成功标记
SELECT 'migration ok' AS result;