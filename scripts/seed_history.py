"""回填近 90 天的历史演示数据，让学情看板的时间范围切换（7/30/90 天）有真实差异。

- 回填内容：答疑会话+消息（is_deleted=1，不进入答疑侧栏但计入看板）、
  历史作业+提交+批改、自测练习记录。
- 幂等：检测到该课程已有超过 15 天前的答疑消息即跳过，可重复执行。
- 用法：
    .venv/Scripts/python.exe scripts/seed_history.py [course_id]   # 默认课程 1
  也可被 seed_demo.py 以 backfill_course(db, course_id) 复用。
"""
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import models as m

QUESTIONS = [
    "什么是栈？", "什么是队列？", "栈和队列有什么区别？", "什么是链表？",
    "链表和数组有什么区别？", "什么是二叉树？", "什么是二叉树的前序遍历？",
    "二叉树的中序遍历和后序遍历有什么区别？", "什么是哈希表？", "哈希冲突怎么解决？",
    "什么是时间复杂度？", "如何计算算法的时间复杂度？", "什么是空间复杂度？",
    "什么是快速排序？", "快速排序的时间复杂度是多少？", "什么是归并排序？",
    "冒泡排序和选择排序的区别？", "什么是堆？", "什么是图的深度优先搜索？",
    "什么是图的广度优先搜索？", "什么是递归？", "什么是动态规划？",
    "解释一下动态规划的思想", "什么是贪心算法？", "什么是邻接矩阵？",
    "什么是最小生成树？", "什么是拓扑排序？", "什么是串的模式匹配？",
    "转置矩阵的实现要点？", "什么是循环链表？",
]

ANSWER_TMPL = (
    "（历史演示数据）关于「{q}」的要点：\n"
    "1. 先掌握定义与基本术语；\n"
    "2. 理解典型操作及其时间复杂度；\n"
    "3. 结合课件例题练习巩固。"
)


def backfill_course(db, course_id: int, course_name: str | None = None) -> str:
    """向单个课程回填历史数据。不提交事务（由调用方决定）；返回摘要文本。"""
    rng = random.Random(20260912 + course_id)
    name = course_name or f"课程{course_id}"
    now = datetime.now()

    has_history = (
        db.query(m.Message.id)
        .join(m.Session, m.Message.session_id == m.Session.id)
        .filter(m.Session.course_id == course_id,
                m.Message.created_at < now - timedelta(days=15))
        .first()
    )
    if has_history:
        return "已有历史数据，跳过"

    students = [r[0] for r in db.query(m.Enrollment.student_id)
                .filter(m.Enrollment.course_id == course_id).all() if r[0]]
    if not students:
        students = [r[0] for r in db.query(m.CourseUser.user_id)
                    .filter(m.CourseUser.course_id == course_id,
                            m.CourseUser.role == "student").all() if r[0]]
    if not students:
        return "该课程没有学生，跳过"

    n_sessions = n_messages = 0
    for d in range(89, 8, -1):
        base_day = now - timedelta(days=d)
        for _ in range(rng.randint(2, 6)):
            q = rng.choice(QUESTIONS)
            stu = rng.choice(students)
            ts = base_day.replace(hour=rng.randint(8, 21),
                                  minute=rng.randint(0, 59),
                                  second=rng.randint(0, 59),
                                  microsecond=0)
            sess = m.Session(user_id=stu, course_id=course_id,
                             title=q[:60], is_deleted=1, created_at=ts)
            db.add(sess)
            db.flush()
            db.add(m.Message(session_id=sess.id, role="user",
                             content=q, created_at=ts))
            db.add(m.Message(session_id=sess.id, role="assistant",
                             content=ANSWER_TMPL.format(q=q),
                             created_at=ts + timedelta(minutes=1)))
            n_sessions += 1
            n_messages += 2

    a1 = m.Assignment(course_id=course_id, title="第2章 线性表小测（历史演示）",
                      description="基础测验（历史演示数据）",
                      deadline=now - timedelta(days=75),
                      created_at=now - timedelta(days=80))
    a2 = m.Assignment(course_id=course_id, title="第3章 综合小测（历史演示）",
                      description="综合应用测验（历史演示数据）",
                      deadline=now - timedelta(days=45),
                      created_at=now - timedelta(days=50))
    db.add_all([a1, a2])
    db.flush()

    n_sub = n_graded = 0
    for a, span_days, n in ((a1, 70, 8), (a2, 40, 10)):
        picked = rng.sample(students, min(len(students), n))
        for stu in picked:
            ts = now - timedelta(days=rng.randint(1, span_days))
            sub = m.Submission(assignment_id=a.id, student_id=stu,
                               content="（历史演示数据）完成本章练习题并附解题思路。",
                               status="graded", submitted_at=ts)
            db.add(sub)
            db.flush()
            n_sub += 1
            if rng.random() < 0.8:
                db.add(m.GradingRecord(
                    submission_id=sub.id,
                    score=rng.randint(65, 100),
                    feedback="（历史演示数据）整体思路正确，注意边界条件与复杂度分析。",
                    grade_by="teacher",
                    graded_at=ts + timedelta(days=1)))
                n_graded += 1

    qids = [r[0] for r in db.query(m.Question.id)
            .filter(m.Question.course_id == course_id).all()]
    n_lr = 0
    if qids:
        for d in range(89, 8, -1):
            if rng.random() < 0.5:
                continue
            base_day = now - timedelta(days=d)
            for _ in range(rng.randint(1, 3)):
                ts = base_day.replace(hour=rng.randint(8, 21),
                                      minute=rng.randint(0, 59),
                                      second=rng.randint(0, 59),
                                      microsecond=0)
                db.add(m.LearningRecord(
                    student_id=rng.choice(students), course_id=course_id,
                    question_id=rng.choice(qids),
                    is_correct=1 if rng.random() < 0.7 else 0,
                    created_at=ts))
                n_lr += 1

    return (f"历史会话 {n_sessions}（侧栏不可见）、消息 {n_messages}、"
            f"提交 {n_sub}、批改 {n_graded}、练习记录 {n_lr}")


def main() -> None:
    course_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    db = SessionLocal()
    try:
        msg = backfill_course(db, course_id)
        db.commit()
        print(f"课程 {course_id}：{msg}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
