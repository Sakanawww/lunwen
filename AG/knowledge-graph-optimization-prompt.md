# 知识图谱优化 + 多课程扩展 - 执行提示词

> 直接复制本提示词给执行 Agent，无需修改

---

## 📋 任务概述

基于现有知识图谱页面进行优化，并扩展多课程内容。

**参考截图**: 用户提供的知识图谱界面（浅色主题，力导向图）

---

## 🎯 核心需求

### 1. 知识图谱连线优化

**当前问题**: 知识点之间没有连线，显示为离散的点

**需求**:
- [ ] 知识点之间用**有向线段**连接（表示依赖/前置关系）
- [ ] 连线样式：浅蓝色 `#a8d5e2`，宽度 2px，带箭头
- [ ] 连线动画：从父节点流向子节点的流动效果（0.5s 循环）
- [ ] 点击连线高亮显示关联关系

**ECharts 配置**:
```javascript
series: [{
  type: 'graph',
  layout: 'force',
  force: {
    repulsion: 800,
    edgeLength: 150,
    gravity: 0.1
  },
  edges: [
    { source: '数据结构', target: '链表', label: { show: true, text: '包含' } },
    { source: '链表', target: '单链表', label: { show: true, text: '细分' } }
  ],
  lineStyle: {
    color: '#a8d5e2',
    width: 2,
    curveness: 0.1
  }
}]
```

---

### 2. 知识点展开动画

**需求**:
- [ ] 鼠标悬停知识点 → 停留 **0.2 秒** 后展开详细信息
- [ ] 展开效果：淡入 + 轻微放大（scale 1.0 → 1.05）
- [ ] 展开内容：知识点名称 + 关联题目数 + 掌握率
- [ ] 移开鼠标 → 0.15 秒后收起

**CSS 动画**:
```css
.knowledge-node {
  transition: all 0.2s ease;
}

.knowledge-node.expanded {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(41, 121, 255, 0.3);
}

.knowledge-node-tooltip {
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
```

**JavaScript 延迟逻辑**:
```javascript
let hoverTimer = null;

node.on('mouseover', () => {
  hoverTimer = setTimeout(() => {
    showTooltip(node);
  }, 200); // 0.2 秒延迟
});

node.on('mouseout', () => {
  clearTimeout(hoverTimer);
  setTimeout(() => hideTooltip(node), 150);
});
```

---

### 3. 建立知识树结构

**需求**:
- [ ] 左侧增加**知识树面板**（可折叠，宽度 280px）
- [ ] 树形结构展示课程知识体系
- [ ] 支持点击树节点定位到图谱对应位置
- [ ] 树节点显示：✅ 已掌握 / ⚠️ 学习中 / ⚪ 未开始

**知识树 HTML 结构**:
```html
<div class="knowledge-tree-panel">
  <div class="tree-header">
    <h3>📚 知识树</h3>
    <button class="toggle-btn">折叠</button>
  </div>
  <div class="tree-content">
    <ul class="tree-root">
      <li class="tree-node expanded">
        <span class="node-icon">📖</span>
        <span class="node-name">数据结构</span>
        <span class="node-progress">65%</span>
        <ul class="tree-children">
          <li class="tree-node mastered">
            <span class="node-icon">✅</span>
            <span class="node-name">线性表</span>
          </li>
          <li class="tree-node learning">
            <span class="node-icon">⚠️</span>
            <span class="node-name">树和二叉树</span>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</div>
```

---

### 4. 去掉难度框后面的五个小框

**当前问题**: 题目难度显示为 5 个小蓝点（●●●○○）

**需求**:
- [ ] 移除所有难度点显示
- [ ] 改为**文字标签**: 🟢 简单 / 🟡 中等 / 🔴 困难
- [ ] 位置：题目卡片右上角

**修改前**:
```html
<div class="difficulty-dots">
  <span class="dot filled"></span>
  <span class="dot filled"></span>
  <span class="dot filled"></span>
  <span class="dot"></span>
  <span class="dot"></span>
</div>
```

**修改后**:
```html
<span class="difficulty-label easy">🟢 简单</span>
<span class="difficulty-label medium">🟡 中等</span>
<span class="difficulty-label hard">🔴 困难</span>
```

**CSS**:
```css
.difficulty-label {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.difficulty-label.easy {
  background: #e8f5e9;
  color: #2e7d32;
}

.difficulty-label.medium {
  background: #fff8e1;
  color: #f57f17;
}

.difficulty-label.hard {
  background: #ffebee;
  color: #c62828;
}
```

---

### 5. 新增课程内容

**需求**: 在现有《数据结构》基础上，增加 3 门新课程

#### 课程列表:

| 课程名 | 课程代码 | 知识点数 | 题目数 | 封面色 |
|--------|----------|----------|--------|--------|
| 数据结构 | CS101 | 40 | 120 | #2563eb |
| **操作系统** | CS201 | 50 | 150 | #7c3aed |
| **计算机网络** | CS301 | 45 | 130 | #059669 |
| **计算机基础原理** | CS401 | 35 | 100 | #dc2626 |

**数据库插入语句**:
```sql
-- 操作系统
INSERT INTO courses (course_code, course_name, description, owner_id, color)
VALUES ('CS201', '操作系统', '进程管理、内存管理、文件系统等核心概念', 1, '#7c3aed');

-- 计算机网络
INSERT INTO courses (course_code, course_name, description, owner_id, color)
VALUES ('CS301', '计算机网络', 'OSI 七层模型、TCP/IP 协议栈、网络编程', 1, '#059669');

-- 计算机基础原理
INSERT INTO courses (course_code, course_name, description, owner_id, color)
VALUES ('CS401', '计算机基础原理', '数字逻辑、计算机组成、指令系统', 1, '#dc2626');
```

**知识图谱课程切换**:
```html
<div class="course-selector">
  <select id="course-select">
    <option value="CS101">数据结构</option>
    <option value="CS201">操作系统</option>
    <option value="CS301">计算机网络</option>
    <option value="CS401">计算机基础原理</option>
  </select>
</div>
```

---

### 6. 新增多个学生账号

**需求**: 在现有数据库中加入 10 个学生账号

**学生账号列表**:
```sql
INSERT INTO users (username, email, password_hash, role, student_id)
VALUES 
('student001', 'student001@demo.com', '$2b$12$...', 'student', '2021001'),
('student002', 'student002@demo.com', '$2b$12$...', 'student', '2021002'),
('student003', 'student003@demo.com', '$2b$12$...', 'student', '2021003'),
('student004', 'student004@demo.com', '$2b$12$...', 'student', '2021004'),
('student005', 'student005@demo.com', '$2b$12$...', 'student', '2021005'),
('student006', 'student006@demo.com', '$2b$12$...', 'student', '2021006'),
('student007', 'student007@demo.com', '$2b$12$...', 'student', '2021007'),
('student008', 'student008@demo.com', '$2b$12$...', 'student', '2021008'),
('student009', 'student009@demo.com', '$2b$12$...', 'student', '2021009'),
('student010', 'student010@demo.com', '$2b$12$...', 'student', '2021010');

-- 初始密码统一为：123456
```

**学生 - 课程关联**:
```sql
-- 每个学生选修 2-3 门课程
INSERT INTO course_enrollments (user_id, course_id, role, enrolled_at)
VALUES 
(2, 1, 'student', NOW()),  -- student001 选修数据结构
(2, 2, 'student', NOW()),  -- student001 选修操作系统
(3, 1, 'student', NOW()),  -- student002 选修数据结构
(3, 3, 'student', NOW()),  -- student002 选修计算机网络
-- ... 更多关联
```

---

### 7. 新增 3 个老师账号

**需求**: 在现有 1 个老师基础上，增加 2 个老师，共 3 个老师

**老师账号列表**:
```sql
INSERT INTO users (username, email, password_hash, role, teacher_id, department)
VALUES 
('王老师', 'wang@demo.com', '$2b$12$...', 'teacher', 'T001', '计算机学院'),
('李老师', 'li@demo.com', '$2b$12$...', 'teacher', 'T002', '计算机学院'),
('张老师', 'zhang@demo.com', '$2b$12$...', 'teacher', 'T003', '软件学院');

-- 老师 - 课程关联
INSERT INTO course_teachers (course_id, user_id, role)
VALUES 
(1, 1, 'owner'),    -- 王老师 - 数据结构（拥有者）
(2, 2, 'owner'),    -- 李老师 - 操作系统（拥有者）
(3, 3, 'owner'),    -- 张老师 - 计算机网络（拥有者）
(1, 2, 'teacher'),  -- 李老师 - 数据结构（协教）
(4, 1, 'owner');    -- 王老师 - 计算机基础（拥有者）
```

---

## 📁 输出文件清单

### 后端文件
- [ ] `app/models/knowledge_graph.py` - 知识图谱数据模型
- [ ] `app/api/knowledge_graph.py` - 知识图谱 API 接口
- [ ] `app/api/courses.py` - 课程管理 API（扩展）
- [ ] `alembic/versions/00X_add_courses.py` - 课程迁移脚本
- [ ] `alembic/versions/00Y_add_users.py` - 用户数据迁移

### 前端文件
- [ ] `app/templates/knowledge_graph.html` - 知识图谱页面（优化连线 + 动画）
- [ ] `app/static/js/knowledge-graph.js` - 图谱交互逻辑（ECharts 配置）
- [ ] `app/static/css/knowledge-graph.css` - 图谱样式（动画 + 布局）
- [ ] `app/static/css/components/difficulty-label.css` - 难度标签样式
- [ ] `app/templates/components/course_selector.html` - 课程切换组件

### 数据文件
- [ ] `data/seed_courses.sql` - 课程种子数据
- [ ] `data/seed_users.sql` - 用户种子数据（3 老师 + 10 学生）
- [ ] `data/seed_knowledge_points.sql` - 知识点关系数据

---

## ✅ 验收标准

### 功能验收
- [ ] 知识点之间有清晰的连线（带箭头）
- [ ] 鼠标悬停知识点 → 0.2 秒延迟后展开详细信息
- [ ] 左侧知识树可折叠，点击节点定位到图谱
- [ ] 课程切换下拉框可切换 4 门课程
- [ ] 难度显示为文字标签（🟢 简单/🟡 中等/🔴 困难）
- [ ] 3 个老师账号可登录，各自管理对应课程
- [ ] 10 个学生账号可登录，查看已选修课程

### 视觉验收
- [ ] 连线颜色：#a8d5e2（浅蓝色）
- [ ] 节点展开动画：0.2s ease
- [ ] 知识树面板：280px 宽，可折叠
- [ ] 难度标签：圆角 4px，带图标
- [ ] 整体风格：浅色主题，DeepSeek HARNESS 参考

### 性能验收
- [ ] 图谱加载时间 < 1.5s（40 个知识点）
- [ ] 课程切换响应 < 300ms
- [ ] 知识树展开/收起 < 150ms

---

## 🔧 技术实现要点

### ECharts 图谱配置
```javascript
const chartOption = {
  series: [{
    type: 'graph',
    layout: 'force',
    force: {
      repulsion: 800,
      edgeLength: 150,
      gravity: 0.1
    },
    emphasis: {
      focus: 'adjacency',
      lineStyle: {
        width: 4,
        color: '#2563eb'
      }
    },
    edgeSymbol: ['none', 'arrow'],
    edgeSymbolSize: 8
  }]
};
```

### 0.2 秒延迟展开实现
```javascript
class KnowledgeGraph {
  constructor() {
    this.hoverDelay = 200; // 200ms = 0.2s
    this.hoverTimer = null;
  }
  
  bindNodeEvents(nodeElement) {
    nodeElement.addEventListener('mouseenter', (e) => {
      this.hoverTimer = setTimeout(() => {
        this.showNodeDetail(e.target);
      }, this.hoverDelay);
    });
    
    nodeElement.addEventListener('mouseleave', () => {
      clearTimeout(this.hoverTimer);
      setTimeout(() => this.hideNodeDetail(), 150);
    });
  }
}
```

---

## 🚀 执行步骤

1. **第 1 步**: 运行数据库迁移（新增课程 + 用户）
2. **第 2 步**: 修改知识图谱页面（连线 + 动画）
3. **第 3 步**: 实现知识树面板
4. **第 4 步**: 修改难度显示为文字标签
5. **第 5 步**: 测试课程切换功能
6. **第 6 步**: 验证所有账号登录

---

**提示词结束** - 直接复制给执行 Agent 使用
