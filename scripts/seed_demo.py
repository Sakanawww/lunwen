"""一键初始化演示数据：让老师 clone 仓库后执行一条命令即可获得完整可演示的系统。

包含：演示账号（admin/teacher/student）、4 门课程、选课关系、知识库（含向量索引）、
作业、题库、以及近 90 天的学习行为数据（复用 seed_history.py）。

用法：
    python scripts/seed_demo.py             # 首次初始化（已有数据时自动跳过）
    python scripts/seed_demo.py --force     # 清空全部数据并重新初始化（慎用）

说明：
- 需先复制 .env.example 为 .env 并配置 MySQL；表结构由本脚本自动创建。
- 知识库向量索引需要 QWEN_API_KEY；未配置时仅入库文本块，可稍后在
  「知识库」页重新上传讲义（data/seed_kb/）生成索引。
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine
from app.models import models as m
from app.utils.helpers import hash_password

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "data" / "seed_kb"

DEMO_PASSWORD = "123456"

# 班级定义：(名称, 年级, 专业)
CLASSES = [
    ("计科2601班", "2026级", "计算机科学与技术"),
    ("计科2602班", "2026级", "计算机科学与技术"),
]

# 每个学生分配到的班级索引（与 STUDENTS 列表对齐）
STUDENT_CLASS_MAP = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

# (课程名, 课程代码, 讲义文件, 授课教师用户名)
COURSES = [
    ("数据结构", "CS202", "数据结构讲义.txt", "teacher"),
    ("操作系统", "OS301", "操作系统讲义.txt", "teacher02"),
    ("计算机网络", "NET401", "计算机网络讲义.txt", "teacher03"),
    ("计算机基础原理", "CS101", "计算机基础原理讲义.txt", "teacher03"),
]

TEACHERS = [
    ("teacher", "王老师", "T1001", "计算机学院"),
    ("teacher02", "李老师", "T1002", "计算机学院"),
    ("teacher03", "张老师", "T1003", "软件学院"),
]

STUDENTS = [
    ("student", "陈同学"),
    ("student01", "张伟"),
    ("student02", "李娜"),
    ("student03", "王强"),
    ("student04", "刘洋"),
    ("student05", "陈静"),
    ("student06", "赵磊"),
    ("student07", "孙悦"),
    ("student08", "周涛"),
    ("student09", "吴敏"),
]

# 每门课程的示例题目：(题型, 题干, 选项, 答案, 难度)
def _questions_for(course_name: str):
    return [
        ("choice", f"【{course_name}】下列关于本课程核心概念的说法正确的是？",
         "A. 概念A正确；B. 概念B错误；C. 概念C错误；D. 概念D错误", "A", 2),
        ("choice", f"【{course_name}】以下哪项属于{course_name}课程的典型应用场景？",
         "A. 场景一；B. 场景二；C. 场景三；D. 以上都是", "D", 3),
        ("fill", f"【{course_name}】请写出本课程中一个核心术语的英文名称。", None, "见讲义词汇表", 2),
        ("short", f"【{course_name}】简述本课程一个核心知识点的要点与应用。", None,
         "要点覆盖定义、典型操作与复杂度/流程分析即可。", 3),
    ]


def ensure_tables(force: bool) -> None:
    if force:
        Base.metadata.drop_all(engine)
        print("已清空全部表（--force）。")
    Base.metadata.create_all(engine)


def seed_users(db: SessionLocal) -> dict:
    """返回 username -> user_id 映射。"""
    ids = {}
    admin = m.User(username="admin", password_hash=hash_password(DEMO_PASSWORD),
                   real_name="系统管理员", role="admin")
    db.add(admin)
    db.flush()
    ids["admin"] = admin.id

    for username, real_name, role in [(t[0], t[1], "teacher") for t in TEACHERS] + \
                                     [(s[0], s[1], "student") for s in STUDENTS]:
        u = m.User(username=username, password_hash=hash_password(DEMO_PASSWORD),
                   real_name=real_name, role=role)
        db.add(u)
        db.flush()
        ids[username] = u.id

    # 教师档案
    for username, _, tno, dept in TEACHERS:
        db.add(m.Teacher(user_id=ids[username], teacher_no=tno, department=dept))
    # 班级实体
    class_ids = []
    for name, grade, major in CLASSES:
        cls = m.Class(name=name, grade=grade, major=major)
        db.add(cls)
        db.flush()
        class_ids.append(cls.id)
    # 学生档案（关联班级 class_id）
    for i, (username, _) in enumerate(STUDENTS):
        cls_idx = STUDENT_CLASS_MAP[i] if i < len(STUDENT_CLASS_MAP) else 0
        db.add(m.Student(user_id=ids[username],
                         student_no=f"S2026{i + 1:03d}",
                         class_name=CLASSES[cls_idx][0],
                         class_id=class_ids[cls_idx]))
    return ids


def seed_courses(db: SessionLocal, user_ids: dict) -> dict:
    """返回 course_name -> (course_id, teacher_user_id)。"""
    result = {}
    for name, code, _, teacher_username in COURSES:
        c = m.Course(name=name, code=code, teacher_id=user_ids[teacher_username],
                     description=f"{name}课程演示数据（含讲义知识库与作业）")
        db.add(c)
        db.flush()
        result[name] = (c.id, user_ids[teacher_username])
        db.add(m.CourseUser(course_id=c.id, user_id=user_ids[teacher_username], role="owner"))
        for username, _ in STUDENTS:
            db.add(m.CourseUser(course_id=c.id, user_id=user_ids[username], role="student"))
            db.add(m.Enrollment(student_id=user_ids[username], course_id=c.id))
    return result


def seed_knowledge(db: SessionLocal, courses: dict, uploader_id: int) -> None:
    """从 data/seed_kb/ 导入讲义：文本块入库；向量索引在配置了 QWEN_API_KEY 时生成。"""
    from app.kb.knowledge_base import KnowledgeBase

    for name, _, kb_file, _ in COURSES:
        path = KB_DIR / kb_file
        if not path.exists():
            print(f"  [跳过] 未找到讲义文件 {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs = KnowledgeBase.split_text(text, source=path.name)
        course_id = courses[name][0]

        doc_row = m.KnowledgeDoc(course_id=course_id, title=path.stem,
                                 file_name=path.name, chunk_num=len(docs),
                                 upload_by=uploader_id)
        db.add(doc_row)
        db.flush()
        for i, d in enumerate(docs):
            db.add(m.KnowledgeChunk(doc_id=doc_row.id, seq=i,
                                    content=d.page_content, source=path.name))
        try:
            kb = KnowledgeBase(course_id)
            for d in docs:
                kb.add_document(d.page_content, source=path.name)
            print(f"  [知识库] {name}：{len(docs)} 个文本块 + 向量索引")
        except Exception as exc:
            print(f"  [知识库] {name}：文本块已入库，但向量索引生成失败（{exc}）。"
                  f"配置 QWEN_API_KEY 后可在知识库页重新上传讲义生成。")


def seed_assignments(db: SessionLocal, courses: dict) -> None:
    now = datetime.now()
    for name, _, _, _ in COURSES:
        course_id, _teacher_id = courses[name]
        db.add(m.Assignment(course_id=course_id,
                            title=f"{name}·第1章基础练习",
                            description=f"完成{name}第1章课后习题 1-5 题。",
                            deadline=now + timedelta(days=7),
                            created_at=now - timedelta(days=3)))
        db.add(m.Assignment(course_id=course_id,
                            title=f"{name}·第2章综合应用",
                            description=f"结合{name}第2章内容完成综合设计题。",
                            deadline=now + timedelta(days=14),
                            created_at=now - timedelta(days=1)))


def seed_questions(db: SessionLocal, courses: dict) -> None:
    for name, _, _, _ in COURSES:
        course_id, teacher_id = courses[name]
        for qtype, stem, options, answer, diff in _questions_for(name):
            db.add(m.Question(course_id=course_id, type=qtype, stem=stem,
                              options=options, answer=answer, difficulty=diff,
                              created_by=teacher_id, source="manual"))


def seed_attendance(db: SessionLocal, courses: dict, user_ids: dict) -> None:
    """回填近 90 天考勤数据：每门课 8 次考勤课次 + 随机签到明细。"""
    import random
    rng = random.Random(20260914)
    now = datetime.now()
    student_ids = [user_ids[u] for u, _ in STUDENTS]

    for name, _, _, _ in COURSES:
        course_id, teacher_id = courses[name]
        # 8 次考勤，分布在近 90 天内
        for k in range(8):
            days_ago = int(rng.uniform(2, 88))
            sess_date = (now - timedelta(days=days_ago)).date()
            status = "open" if k == 0 else "closed"
            sess = m.AttendanceSession(course_id=course_id, session_date=sess_date,
                                       status=status, created_by=teacher_id,
                                       created_at=now - timedelta(days=days_ago))
            db.add(sess)
            db.flush()
            # 为每个学生生成签到状态
            for sid in student_ids:
                r = rng.random()
                if r < 0.82:
                    st = "present"
                elif r < 0.90:
                    st = "late"
                elif r < 0.95:
                    st = "leave"
                else:
                    st = "absent"
                # 个别学生连续缺勤（用于预警演示）
                if k >= 5 and student_ids.index(sid) == 3 and days_ago < 30:
                    st = "absent"
                signed_at = (now - timedelta(days=days_ago, hours=rng.uniform(0, 2))
                             ) if st in ("present", "late") else None
                db.add(m.AttendanceRecord(session_id=sess.id, student_id=sid,
                                          status=st, signed_at=signed_at))


def seed_announcements(db: SessionLocal, courses: dict, user_ids: dict) -> None:
    """为每门课创建 2-3 条演示公告。"""
    now = datetime.now()
    templates = [
        ("关于第3章课后作业的说明", "第3章课后习题1-5题需在下周日前提交，请注意截止时间。"),
        ("期中复习安排", "本周五将进行期中复习答疑，请同学们提前准备问题。"),
        ("课堂纪律提醒", "请同学们按时出勤，连续缺勤将影响平时成绩。"),
    ]
    for name, _, _, teacher_username in COURSES:
        course_id, _ = courses[name]
        teacher_id = user_ids[teacher_username]
        for i, (title, content) in enumerate(templates[:2]):
            db.add(m.Announcement(course_id=course_id, title=title, content=content,
                                  created_by=teacher_id,
                                  created_at=now - timedelta(days=i * 3 + 1)))


def main() -> None:
    force = "--force" in sys.argv
    ensure_tables(force)

    db = SessionLocal()
    try:
        if not force and db.query(m.User).first():
            print("数据库已初始化过，跳过。如需重灌请执行：python scripts/seed_demo.py --force")
            return

        print("初始化演示数据…")
        user_ids = seed_users(db)
        courses = seed_courses(db, user_ids)
        seed_knowledge(db, courses, user_ids["admin"])
        seed_assignments(db, courses)
        seed_questions(db, courses)
        seed_attendance(db, courses, user_ids)
        seed_announcements(db, courses, user_ids)

        # 近 90 天学习行为数据（答疑/作业/练习历史）
        from seed_history import backfill_course
        for name, _, _, _ in COURSES:
            msg = backfill_course(db, courses[name][0], course_name=name)
            print(f"  [历史数据] {name}：{msg}")

        db.commit()
        print("\n✅ 初始化完成！演示账号（密码均为 123456）：")
        print("   管理员  admin")
        print("   教师    teacher（数据结构）/ teacher02（操作系统）/ teacher03（计算机网络、计算机基础原理）")
        print("   学生    student（及 student01~student09）")
        print("\n启动系统：python scripts/start.py start   # 或分别启动前后端，见 README")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
