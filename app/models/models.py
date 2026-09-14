"""ORM 模型 —— 与 database/schema.sql 对应（含功能扩展新增表）。"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    role = Column(Enum("student", "teacher", "admin"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Student(Base):
    __tablename__ = "students"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_no = Column(String(20), nullable=False, unique=True)
    class_name = Column(String(50))
    class_id = Column(BigInteger, ForeignKey("classes.id", ondelete="SET NULL"))


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teacher_no = Column(String(20), nullable=False, unique=True)
    department = Column(String(50))


class Course(Base):
    __tablename__ = "courses"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(30))
    teacher_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class CourseUser(Base):
    """课程成员（RBAC）：用户与课程的多对多，并标注其在课程内角色。

    角色：owner（创建者/授课教师）、teacher（协教）、assistant（助教）、
    student（学生）。兼容旧数据：courses.teacher_id 视为 teacher 成员；
    enrollments 视为 student 成员。
    """

    __tablename__ = "course_users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum("owner", "teacher", "assistant", "student"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (
        # 同一用户在同一门课程中只有一种角色
        UniqueConstraint("course_id", "user_id", name="uk_course_user"),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    file_name = Column(String(255))
    chunk_num = Column(Integer, nullable=False, default=0)
    upload_by = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_id = Column(BigInteger, ForeignKey("knowledge_docs.id", ondelete="CASCADE"), nullable=False)
    seq = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255))


class Session(Base):
    __tablename__ = "sessions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="SET NULL"))
    title = Column(String(120))
    is_deleted = Column(Integer, nullable=False, default=0)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum("user", "assistant", "agent"), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(Text)
    attachment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assignment_id = Column(BigInteger, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum("pending", "graded"), nullable=False, default="pending")
    submitted_at = Column(DateTime, server_default=func.now())


class GradingRecord(Base):
    __tablename__ = "grading_records"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    submission_id = Column(BigInteger, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    score = Column(DECIMAL(5, 2))
    feedback = Column(Text)
    grade_by = Column(Enum("ai", "teacher"), nullable=False, default="ai")
    graded_at = Column(DateTime, server_default=func.now())


class Question(Base):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum("choice", "fill", "short"), nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(Text)
    answer = Column(Text)
    difficulty = Column(Integer)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    source = Column(Enum("ai", "manual"), nullable=False, default="manual")
    is_deleted = Column(Integer, nullable=False, default=0)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="SET NULL"))
    is_correct = Column(Integer)
    score = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, server_default=func.now())


class AgentConfig(Base):
    __tablename__ = "agent_configs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    role_desc = Column(String(255))
    model = Column(String(100))
    enabled = Column(Integer, nullable=False, default=1)
    route_keywords = Column(String(255))
    sort_order = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    detail = Column(Text)
    status = Column(String(20), default="success")
    ip = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())


# ===== 功能扩展新增模型 =====


class Class(Base):
    """班级实体：独立于课程，学生归属班级，课程可关联授课班级。"""

    __tablename__ = "classes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="班级名称")
    grade = Column(String(20), comment="年级")
    major = Column(String(100), comment="专业")
    created_at = Column(DateTime, server_default=func.now())


class ClassCourse(Base):
    """班级 ↔ 课程多对多：标记某门课程面向哪些班级授课。"""

    __tablename__ = "class_courses"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    class_id = Column(BigInteger, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint("class_id", "course_id", name="uk_class_course"),)


class AttendanceSession(Base):
    """考勤课次：教师为某课程在某日发起的一次考勤。"""

    __tablename__ = "attendance_sessions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    session_date = Column(Date, nullable=False, comment="考勤日期")
    status = Column(Enum("open", "closed"), nullable=False, default="open", comment="签到状态")
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())


class AttendanceRecord(Base):
    """签到明细：每名学生在某次考勤课次中的出勤状态。"""

    __tablename__ = "attendance_records"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("present", "late", "leave", "absent"), nullable=False, default="absent",
                    comment="出勤/迟到/请假/旷课")
    signed_at = Column(DateTime)
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uk_attendance"),)


class PerformanceScore(Base):
    """平时分：四维子分 + 加权总分，物化存储便于历史对比与看板展示。"""

    __tablename__ = "performance_scores"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    attendance_score = Column(DECIMAL(5, 2), default=0, comment="出勤维度得分 0-100")
    assignment_score = Column(DECIMAL(5, 2), default=0, comment="作业维度得分 0-100")
    practice_score = Column(DECIMAL(5, 2), default=0, comment="练习维度得分 0-100")
    engagement_score = Column(DECIMAL(5, 2), default=0, comment="答疑活跃度得分 0-100")
    total_score = Column(DECIMAL(5, 2), default=0, comment="加权总分 0-100")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint("course_id", "student_id", name="uk_perf"),)


class Announcement(Base):
    """课程公告：教师发布，面向选课学生。"""

    __tablename__ = "announcements"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())