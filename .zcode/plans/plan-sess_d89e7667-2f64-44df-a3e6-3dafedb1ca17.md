# 实施计划：弹窗→二级页面 + 后端越权漏洞修复

## 一、后端越权漏洞修复（10+ 接口）

**根因**：项目有完善的 `require_course_role()` (`app/core/course_deps.py:62`) 用于课程级 RBAC，但新增的 8 个功能模块全部只用 `require_role()` (系统角色) 或 `current_user` (仅认证)，导致任意教师可访问/修改其他课程的数据，甚至学生也能读取他人数 submissions。

### 1.1 高危：无任何权限校验的接口

| 文件 | 接口 | 修复 |
|------|------|------|
| `app/api/grading.py:42` `get_submissions` | 任何登录用户可读所有课程的作业提交(含 content/score/feedback) | 加 `require_course_role("teacher","assistant")` |
| `app/api/dashboard.py:116` `course_stats` | 任何登录用户可读任意课程统计 | 加 `require_course_role("teacher","assistant")` |

### 1.2 中危：有角色校验但无课程归属校验（跨教师越权）

| 文件 | 接口 | 修复 |
|------|------|------|
| `app/api/grading.py:14` `grade_submission` | 任意教师可批改任意课程作业 | 先从 submission→assignment→course_id，再校验归属 |
| `app/api/dashboard.py:20` `course_students` | 任意教师可拉取其他课程学生 PII | `_is_allowed` 加 `require_course_role` |
| `app/api/dashboard.py:261` `dashboard_overview` | 跨课程看板 | 同上 |
| `app/api/dashboard.py:447` `hot_questions` | 跨课程热门问题 | 同上 |
| `app/api/announcements.py` 全部接口 | 任意教师可发/删任意课程公告 | 加 `require_course_role("teacher","assistant")` |
| `app/api/knowledge.py` upload/list/preview/delete | 跨课程知识库 | 加 `require_course_role("teacher","assistant")` |
| `app/api/question.py` gen/list/delete/restore | 跨课程试题 | 加 `require_course_role("teacher","assistant")` |
| `app/api/performance.py` diagnose | 教师 AI 诊断无归属校验 | 加 `require_course_role("teacher","assistant")` |
| `app/api/attendance.py` 所有教师端接口 | 跨课程考勤 | 加 `require_course_role("teacher","assistant")` |

### 1.3 低危：学生端接口缺选课校验

| 文件 | 接口 | 修复 |
|------|------|------|
| `app/api/practice.py:33` `submit` | 未选课用户可答题 | 加 `require_course_role("student")` |
| `app/api/attendance.py:136` `sign_in` | 未选课可签到 | 加 `require_course_role("student")` |
| `app/api/attendance.py:175` `session_records` | 任意用户可读考勤记录 | 加 `require_course_role` |

**统一改法**：将各端点的 `user: m.User = Depends(current_user)` 替换为 `user: m.User = Depends(require_course_role("teacher", "assistant"))`（教师端）或 `Depends(require_course_role("student"))`（学生端），admin 自动通过。对于无 course_id 参数的端点（如 grade_submission），先查询获取 course_id 再校验。

## 二、弹窗/Alert → 二级页面（8 处）

### 2.1 新增路由（`router/index.ts`）

```
dashboard/students/:id          → StudentDetailView.vue    (teacher,admin)
attendance/sessions/:id         → AttendanceSessionView.vue (teacher,admin)  
knowledge/:docId                → KnowledgeDocView.vue      (teacher,admin)
practice/:questionId            → PracticeQuestionView.vue  (student,teacher,admin)
performance/diagnose/:studentId → PerformanceDiagnoseView.vue (teacher,admin)
```

### 2.2 新建页面文件

**① StudentDetailView.vue** (`/dashboard/students/:id`)
- 替代 StudentsView 的 `alert()` `viewDetail()`
- 展示学生完整信息：基本信息(姓名/学号/班级/邮箱)、作业提交记录+均分、练习记录+正确率、答疑提问数、平时分四维得分
- 需新增后端 `GET /api/dashboard/students/:student_id/detail` 接口（聚合 Submission+GradingRecord+LearningRecord+Message+PerformanceScore）
- "返回"按钮回 `/dashboard/students`

**② AttendanceSessionView.vue** (`/attendance/sessions/:id`)
- 替代 AttendanceView 的 `showRecordsModal` modal
- 展示某次考勤的完整签到记录表格，支持内联编辑签到状态(present/late/leave/absent)
- 复用现有 `GET /api/attendance/sessions/:sid/records` 和 `PUT /api/attendance/records` 接口
- "返回"按钮回 `/attendance`

**③ KnowledgeDocView.vue** (`/knowledge/:docId`)
- 替代 KnowledgeView 的 `showPreviewModal` modal
- 展示文档所有分块内容，带分页/搜索
- 复用现有 `GET /api/kb/preview/:doc_id` 接口
- "返回"按钮回 `/knowledge`

**④ PracticeQuestionView.vue** (`/practice/:questionId`)
- 替代 PracticeView 的 `showPracticeModal` + `showResultModal` 两个 modal
- 展示题目+选项/填空，提交后内联显示结果(正确/错误+答案)
- 复用现有 `POST /api/practice/submit` 接口和 `GET /api/question/list/:cid`
- "返回"按钮回 `/practice`

**⑤ PerformanceDiagnoseView.vue** (`/performance/diagnose/:studentId`)
- 替代 PerformanceView 的 `showDiagnose` slide-up panel
- 展示学生四维得分卡片 + SSE AI 诊断报告流式输出
- 复用现有 `POST /api/performance/diagnose` 接口
- 需从 courseStore 读 currentCourseId
- "返回"按钮回 `/performance`

### 2.3 修改现有页面（移除 modal/alert，改为 router.push）

| 文件 | 改动 |
|------|------|
| `StudentsView.vue` | `viewDetail()` 从 `alert()` 改为 `router.push({name:'StudentDetail',params:{id}})` |
| `AttendanceView.vue` | `viewRecords()` 从 `showRecordsModal=true` 改为 `router.push`；删除 modal 模板和 CSS |
| `KnowledgeView.vue` | `openPreview()` 从 `showPreviewModal=true` 改为 `router.push`；删除 modal 模板和 CSS |
| `PracticeView.vue` | `startPractice()` 从 `showPracticeModal=true` 改为 `router.push`；删除两个 modal 模板和 CSS |
| `PerformanceView.vue` | `diagnose()` 从 `showDiagnose=true` 改为 `router.push`；删除 diagnose-panel 模板和 CSS |

### 2.4 MyPerformanceView 诊断面板

`MyPerformanceView.vue` 的 `showDiagnose` panel 是学生自己的诊断，不需要单独路由（学生已经在自己的页面），改为内联展开/折叠而非 `position:fixed` 覆盖层。

## 三、alert/confirm → Toast 通知组件

### 3.1 新建 `useToast` composable

创建 `frontend/src/composables/useToast.ts`，提供 `toast.success(msg)` / `toast.error(msg)` 方法，在页面右上角显示自动消失的通知卡片。

### 3.2 替换所有 alert() 调用

16 处 `alert()` 替换为 `toast.success()` / `toast.error()`：
- DashboardView(1)、AttendanceView(2)、CoursesView(3)、AdminView(4)、GradingView(1)、PracticeView(1)、ChatView(4)

### 3.3 替换所有 confirm() 调用

13 处 `confirm()` 替换为统一的 `ConfirmDialog` 组件（小型 modal，保留确认语义但用项目设计风格）：
- AnnouncementsView(1)、AdminView(1)、ChatView(3)、KnowledgeView(1)、CoursesView(2)、AssignmentsView(1)、AttendanceView(1)、QuestionsView(1)、RecycleBinView(2)

## 四、其他逻辑漏洞修复

| 问题 | 修复 |
|------|------|
| AdminView 系统状态卡片是硬编码 mock | 标注为"演示数据"或接入真实 `/api/health` |
| AdminView LLM/系统配置表单是 dead UI | 改为只读展示 .env 配置说明，移除"保存"按钮 |
| AdminView 用户状态全是"正常" | 移除状态列或接入真实状态 |
| KnowledgeView onMounted 不 fetchCourses | 补上 `await courseStore.fetchCourses()` |
| 多处 catch 吞错误无用户反馈 | 改为 `toast.error()` |
| MyPerformanceView signPresent 无 try/catch | 补上错误处理 |

## 五、执行顺序

1. **后端越权修复**（最优先，安全问题）→ 逐文件改 `current_user` → `require_course_role`
2. **新增后端学生详情接口** `GET /api/dashboard/students/:id/detail`
3. **新建 5 个二级页面 .vue 文件**
4. **路由注册** 5 条新路由
5. **修改 5 个现有页面** 移除 modal/alert，改 router.push
6. **创建 Toast + ConfirmDialog 组件**，替换全局 alert/confirm
7. **修复其他逻辑漏洞**（AdminView mock、KnowledgeView onMounted 等）
8. **浏览器全量验证**