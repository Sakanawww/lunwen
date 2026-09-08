# 智能答疑页面 - 完整功能规格说明书

> UI 风格参考：DeepSeek HARNESS / ChatGPT / Claude  
> 技术约束：Jinja2 模板 + 原生 JS + 浅色主题

---

## 📐 一、页面布局（DeepSeek HARNESS 风格）

### 1.1 整体结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 顶部导航栏 (56px, 白色背景，底部细边框 #E8ECF0)                          │
│ [📚 Logo] 课程助教系统    [知识库] [作业批改] [试题生成] [👤 用户] [退出] │
├──────────┬──────────────────────────────────────────────┬───────────────┤
│ 会话列表  │              对话主区域                      │  引用来源    │
│ (280px)  │              (自适应，最大 900px)            │  (280px)    │
│ 白色背景  │              浅灰背景 #F5F7FA                │  白色背景   │
│          │                                              │             │
│ [+新建]  │  ┌────────────────────────────────────────┐ │  📚 引用来源  │
│ ───────  │  │  欢迎卡片 (无消息时)                   │ │  ─────────  │
│          │  │  🤖 智能答疑助手                       │ │             │
│ 今天     │  │  基于 RAG 知识库的课程问答              │ │  📄 文档 1  │
│ • 二叉树  │  │  [建议问题卡片 2x2 网格]               │ │    ├─ 片段 1│
│ 10:30    │  └────────────────────────────────────────┘ │    └─ 片段 2│
│          │                                              │             │
│ 昨天     │  ┌────────────────────────────────────────┐ │  📄 文档 2  │
│ • 链表    │  │  💬 用户消息 (右对齐，蓝色气泡)        │ │    └─ 片段 1│
│ 15:20    │  │  🤖 AI 回复 (左对齐，白色卡片 + 引用)    │ │             │
│          │  └────────────────────────────────────────┘ │             │
│          │                                              │             │
│          │  ┌────────────────────────────────────────┐ │             │
│          │  │  [输入框............................] 🔵│ │             │
│          │  └────────────────────────────────────────┘ │             │
│          │     Enter 发送 · Shift+Enter 换行            │             │
└──────────┴──────────────────────────────────────────────┴─────────────┘
```

### 1.2 尺寸规范

| 区域 | 宽度 | 高度 | 说明 |
|------|------|------|------|
| 顶部导航 | 100% | 56px | 固定 |
| 左侧会话列表 | 280px | 100% | 可折叠（移动端隐藏） |
| 主对话区 | 自适应 (max 900px) | 100% | 内容居中 |
| 右侧引用 | 280px | 100% | 可折叠（<1024px 隐藏） |
| 输入区域 | 100% | 自动 | 固定在底部 |

---

## 🎨 二、视觉设计规范

### 2.1 配色方案（浅色主题）

```css
:root {
  /* 背景 */
  --bg-page: #F5F7FA;           /* 页面背景 */
  --bg-card: #FFFFFF;           /* 卡片/侧栏背景 */
  --bg-hover: #F0F2F5;          /* 悬停背景 */
  --bg-input: #FFFFFF;          /* 输入框背景 */
  
  /* 文字 */
  --text-primary: #1A1A1A;      /* 主标题/正文 */
  --text-secondary: #667788;    /* 次要文字 */
  --text-muted: #99AAB5;        /* 弱化文字 */
  
  /* 主色 */
  --primary: #5B7FFF;           /* 科技蓝 */
  --primary-hover: #4665E8;     /* 悬停深蓝 */
  --primary-light: rgba(91, 127, 255, 0.1);
  
  /* 渐变 */
  --gradient-primary: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
  
  /* 边框 */
  --border-light: #E8ECF0;
  --border-medium: #D0D7DE;
  
  /* 阴影 */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
  
  /* 圆角 */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```

### 2.2 字体规范

```css
/* 引入字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

--font-sans: 'Inter', -apple-system, 'Microsoft YaHei', sans-serif;
--font-mono: 'JetBrains Mono', 'Consolas', monospace;

/* 字号 */
--text-xs: 0.75rem;      /* 12px - 辅助文字 */
--text-sm: 0.8125rem;    /* 13px - 次要文字 */
--text-base: 0.9375rem;  /* 15px - 正文 */
--text-lg: 1rem;         /* 16px - 标题 */
--text-xl: 1.125rem;     /* 18px - 大标题 */
--text-2xl: 1.5rem;      /* 24px - 页面标题 */
```

### 2.3 图标规范（Remix Icon）

```html
<!-- 引入 -->
<link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">

<!-- 导航栏图标 -->
<i class="ri-folder-cloud-line"></i>      <!-- 知识库 -->
<i class="ri-checkbox-circle-line"></i>   <!-- 作业批改 -->
<i class="ri-edit-circle-line"></i>       <!-- 试题生成 -->
<i class="ri-dashboard-line"></i>         <!-- 学情看板 -->
<i class="ri-user-smile-line"></i>        <!-- 用户 -->
<i class="ri-logout-circle-line"></i>     <!-- 退出 -->

<!-- 会话列表 -->
<i class="ri-add-line"></i>               <!-- 新建对话 -->
<i class="ri-message-3-line"></i>         <!-- 会话图标 -->
<i class="ri-time-line"></i>              <!-- 最近 -->
<i class="ri-history-line"></i>           <!-- 历史 -->

<!-- 对话区 -->
<i class="ri-question-line"></i>          <!-- 建议问题 -->
<i class="ri-send-plane-fill"></i>        <!-- 发送按钮 -->
<i class="ri-attachment-2"></i>           <!-- 附件 -->
<i class="ri-sparkling-fill"></i>         <!-- 智能优化 -->

<!-- 消息内容 -->
<i class="ri-file-text-line"></i>         <!-- 文档引用 -->
<i class="ri-book-open-line"></i>         <!-- 知识库 -->
<i class="ri-check-line"></i>             <!-- 正确 -->
<i class="ri-error-warning-line"></i>     <!-- 警告 -->
```

---

## 🧩 三、核心功能模块

### 3.1 顶部导航栏

```html
<nav class="navbar">
  <div class="navbar-brand">
    <div class="navbar-logo">📚</div>
    <span>课程助教系统</span>
  </div>
  <div class="navbar-menu">
    <a href="/kb" class="nav-link">
      <i class="ri-folder-cloud-line"></i>
      <span>知识库</span>
    </a>
    <a href="/grading" class="nav-link">
      <i class="ri-checkbox-circle-line"></i>
      <span>作业批改</span>
    </a>
    <a href="/questions" class="nav-link">
      <i class="ri-edit-circle-line"></i>
      <span>试题生成</span>
    </a>
    <a href="/dashboard" class="nav-link">
      <i class="ri-dashboard-line"></i>
      <span>学情看板</span>
    </a>
    <div class="user-dropdown">
      <div class="user-avatar">李</div>
      <span>李同学</span>
      <i class="ri-arrow-down-s-line"></i>
    </div>
    <a href="/logout" class="nav-link logout">
      <i class="ri-logout-circle-line"></i>
      <span>退出</span>
    </a>
  </div>
</nav>
```

**样式要求：**
- 高度：56px
- 背景：白色 #FFFFFF
- 底部边框：1px solid #E8ECF0
- Logo：36x36px 渐变圆角方
- 导航项：悬停蓝色背景 + 文字变色
- 用户头像：圆形渐变背景 + 姓氏

---

### 3.2 左侧会话列表

```html
<aside class="sidebar">
  <div class="sidebar-header">
    <button class="new-chat-btn">
      <i class="ri-add-line"></i>
      <span>新建对话</span>
    </button>
  </div>
  
  <div class="session-list">
    <div class="session-group">
      <div class="session-group-title">今天</div>
      
      <div class="session-item active">
        <i class="ri-message-3-line session-icon"></i>
        <div class="session-content">
          <div class="session-title">二叉树的前序遍历</div>
          <div class="session-preview">什么是二叉树的前序遍历？</div>
        </div>
      </div>
      
      <div class="session-item">
        <i class="ri-message-3-line session-icon"></i>
        <div class="session-content">
          <div class="session-title">链表插入操作</div>
          <div class="session-preview">单链表如何在指定位置插入节点？</div>
        </div>
      </div>
    </div>
    
    <div class="session-group">
      <div class="session-group-title">昨天</div>
      <!-- 更多会话... -->
    </div>
  </div>
</aside>
```

**交互要求：**
- 点击会话项 → 加载该会话消息
- 当前会话：蓝色背景高亮 + 左侧 3px 蓝色边框
- 悬停：浅灰背景 #F0F2F5
- 标题超出：省略号截断
- 新建对话：渐变按钮，点击清空当前对话

---

### 3.3 欢迎状态（无消息时）

```html
<div class="welcome-container">
  <div class="welcome-icon">🤖</div>
  <h1 class="welcome-title">智能答疑助手</h1>
  <p class="welcome-desc">基于 RAG 知识库的课程问答，回答附带可靠来源引用</p>
  
  <div class="suggestions-grid">
    <div class="suggestion-card" data-question="什么是二叉树的前序遍历？">
      <div class="suggestion-icon">
        <i class="ri-question-line"></i>
      </div>
      <div class="suggestion-text">什么是二叉树的前序遍历？</div>
    </div>
    
    <div class="suggestion-card" data-question="链表和数组有什么区别？">
      <div class="suggestion-icon">
        <i class="ri-question-line"></i>
      </div>
      <div class="suggestion-text">链表和数组有什么区别？</div>
    </div>
    
    <div class="suggestion-card" data-question="如何计算算法的时间复杂度？">
      <div class="suggestion-icon">
        <i class="ri-question-line"></i>
      </div>
      <div class="suggestion-text">如何计算算法的时间复杂度？</div>
    </div>
    
    <div class="suggestion-card" data-question="请解释一下动态规划的思想">
      <div class="suggestion-icon">
        <i class="ri-question-line"></i>
      </div>
      <div class="suggestion-text">请解释一下动态规划的思想</div>
    </div>
  </div>
</div>
```

**样式要求：**
- 容器：最大宽度 700px，居中
- Logo：80x80px 渐变圆角，白色图标
- 标题：28px 粗体，深蓝 #1A1A1A
- 描述：16px 中灰 #667788
- 建议卡片：2x2 网格，白色背景 + 细边框
- 悬停：边框变蓝 + 轻微上浮 2px

---

### 3.4 对话气泡（核心）

#### 用户消息（右对齐）

```html
<div class="message-row user">
  <div class="message-avatar">👤</div>
  <div class="message-content">
    什么是二叉树的前序遍历？
  </div>
</div>
```

**样式：**
- 气泡背景：渐变蓝 #5B7FFF → #8B5CF6
- 文字：白色
- 圆角：左上 16px / 右上 16px / 左下 4px / 右下 16px
- 头像：右侧，灰色圆形背景
- 最大宽度：85%

#### AI 回复（左对齐）

```html
<div class="message-row ai">
  <div class="message-avatar ai">🤖</div>
  <div class="message-content">
    <p>二叉树的前序遍历是一种深度优先的遍历方式...</p>
    
    <div class="sources-card">
      <div class="sources-header">
        <i class="ri-attachment-line"></i>
        <span>引用来源</span>
      </div>
      
      <div class="source-item">
        <i class="ri-file-text-line"></i>
        <div class="source-item-text">
          <strong>《数据结构》第 3 章</strong> - 片段 2
        </div>
      </div>
    </div>
  </div>
</div>
```

**样式：**
- 气泡背景：白色 #FFFFFF
- 边框：1px solid #E8ECF0
- 圆角：左上 16px / 右上 16px / 左下 16px / 右下 4px
- 头像：左侧，渐变背景
- 引用卡片：浅灰背景，可展开/收起

---

### 3.5 消息内容排版（Markdown 渲染）

```css
/* 段落 */
.message-content p {
  margin-bottom: 1rem;
  line-height: 1.7;
}

/* 代码 - 行内 */
.message-content code {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(0,0,0,0.06);
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.875em;
}

/* 代码 - 代码块 */
.message-content pre {
  background: #1E1E1E;
  color: #D4D4D4;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
}

/* 列表 */
.message-content ul,
.message-content ol {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

/* 引用 */
.message-content blockquote {
  border-left: 3px solid var(--primary);
  padding-left: 1rem;
  color: var(--text-secondary);
  margin: 1rem 0;
}

/* 表格 */
.message-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.message-content th,
.message-content td {
  border: 1px solid var(--border-light);
  padding: 0.75rem;
  text-align: left;
}

.message-content th {
  background: var(--bg-hover);
  font-weight: 600;
}
```

---

### 3.6 输入区域

```html
<div class="input-section">
  <div class="input-wrapper">
    <textarea 
      class="message-input"
      placeholder="输入你的问题，Enter 发送，Shift+Enter 换行..."
      rows="1"
    ></textarea>
    
    <div class="input-actions">
      <button class="action-btn secondary" title="上传附件">
        <i class="ri-attachment-2"></i>
      </button>
      <button class="action-btn secondary" title="智能优化">
        <i class="ri-sparkling-fill"></i>
      </button>
    </div>
    
    <button class="send-button" title="发送">
      <i class="ri-send-plane-fill"></i>
    </button>
  </div>
  
  <div class="input-hint">
    <kbd>Enter</kbd> 发送 · <kbd>Shift+Enter</kbd> 换行 · 回答将引用课程知识库来源
  </div>
</div>
```

**样式要求：**
- 输入框：白色背景，圆角 16px，最小高度 56px
- Focus：蓝色边框 + 光晕阴影
- 发送按钮：渐变蓝，40x40px，右下角绝对定位
- 附件按钮：灰色，悬停变蓝
- 智能优化：渐变图标，点击触发 AI 润色
- 快捷键提示：居中，灰色小字

---

### 3.7 右侧引用来源

```html
<aside class="sources-sidebar">
  <h3 class="sources-sidebar-title">
    <i class="ri-book-open-line"></i>
    <span>引用来源</span>
  </h3>
  
  <div class="source-doc-card">
    <div class="source-doc-title">
      <i class="ri-file-text-line"></i>
      <span>数据结构讲义.docx</span>
    </div>
    <ul class="source-fragments">
      <li data-fragment="1">片段 1: 二叉树的定义</li>
      <li data-fragment="3">片段 3: 遍历算法详解</li>
    </ul>
  </div>
  
  <div class="source-doc-card">
    <div class="source-doc-title">
      <i class="ri-file-text-line"></i>
      <span>算法导论.pdf</span>
    </div>
    <ul class="source-fragments">
      <li data-fragment="5">片段 5: 时间复杂度分析</li>
    </ul>
  </div>
</aside>
```

**样式要求：**
- 背景：白色
- 左边框：1px solid #E8ECF0
- 文档卡片：浅灰背景，圆角 8px
- 片段列表：可点击，高亮对应引用
- 悬停：蓝色文字 + 背景

---

## ⚡ 四、交互功能

### 4.1 会话管理

```javascript
// 新建对话
document.querySelector('.new-chat-btn').addEventListener('click', async () => {
  const response = await fetch('/api/chat/sessions', { method: 'POST' });
  const session = await response.json();
  loadSession(session.id);
});

// 切换会话
document.querySelectorAll('.session-item').forEach(item => {
  item.addEventListener('click', async function() {
    const sessionId = this.dataset.sessionId;
    
    // 更新激活状态
    document.querySelectorAll('.session-item').forEach(i => i.classList.remove('active'));
    this.classList.add('active');
    
    // 加载消息
    await loadMessages(sessionId);
  });
});

// 删除会话（右键菜单）
document.querySelectorAll('.session-item').forEach(item => {
  item.addEventListener('contextmenu', async function(e) {
    e.preventDefault();
    const confirmed = confirm('确定删除此会话？');
    if (confirmed) {
      await fetch(`/api/chat/sessions/${this.dataset.sessionId}`, { method: 'DELETE' });
      this.remove();
    }
  });
});
```

### 4.2 消息发送

```javascript
const textarea = document.querySelector('.message-input');
const sendBtn = document.querySelector('.send-button');

// 发送消息
async function sendMessage() {
  const message = textarea.value.trim();
  if (!message) return;
  
  // 添加用户消息到界面
  appendMessage('user', message);
  textarea.value = '';
  textarea.style.height = 'auto';
  
  // 调用 API（SSE 流式）
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      message, 
      session_id: currentSessionId,
      course_id: selectedCourseId 
    })
  });
  
  // 流式接收
  const reader = response.body.getReader();
  const aiMessageEl = appendMessage('ai', '');
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = new TextDecoder().decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        if (data.type === 'token') {
          aiMessageEl.content += data.text;
        } else if (data.type === 'sources') {
          renderSources(aiMessageEl, data.sources);
        }
      }
    }
  }
}

// 键盘快捷键
textarea.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
```

### 4.3 建议问题点击

```javascript
document.querySelectorAll('.suggestion-card').forEach(card => {
  card.addEventListener('click', function() {
    const question = this.dataset.question;
    textarea.value = question;
    textarea.focus();
    sendMessage();
  });
});
```

### 4.4 输入框自动高度

```javascript
textarea.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});
```

---

## 📱 五、响应式断点

```css
/* 桌面端 (>1024px) - 三栏全显示 */

/* 平板 (768-1024px) - 隐藏右侧引用栏 */
@media (max-width: 1024px) {
  .sources-sidebar {
    display: none;
  }
  
  .chat-main {
    max-width: 100%;
  }
}

/* 手机 (<768px) - 隐藏左侧会话列表 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
  
  .message-row {
    max-width: 95%;
  }
  
  /* 移动端：添加汉堡菜单切换会话列表 */
  .mobile-menu-btn {
    display: block;
    position: fixed;
    top: 70px;
    left: 1rem;
    z-index: 100;
  }
}
```

---

## 🎬 六、动效规范

### 6.1 消息出现动画

```css
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.message-row.ai {
  animation: slideInLeft 0.4s ease-out;
}

.message-row.user {
  animation: slideInRight 0.4s ease-out;
}

.suggestion-card {
  animation: fadeIn 0.5s ease-out;
}
```

### 6.2 流式输出打字机效果

```css
@keyframes cursorBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.typing-cursor::after {
  content: '|';
  animation: cursorBlink 0.8s infinite;
  color: var(--primary);
}
```

### 6.3 按钮悬停反馈

```css
.btn, .action-btn {
  transition: all 0.2s ease;
}

.btn:hover, .action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(91, 127, 255, 0.3);
}

.btn:active, .action-btn:active {
  transform: translateY(0);
}
```

### 6.4 加载状态

```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-light);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading-pulse {
  animation: pulse 1.5s infinite;
}
```

---

## 🧪 七、功能测试清单

| 功能 | 测试步骤 | 预期结果 |
|------|---------|---------|
| 新建对话 | 点击"+新建对话"按钮 | 清空当前对话，创建新会话 |
| 切换会话 | 点击左侧会话列表项 | 加载对应历史消息 |
| 发送消息 | 输入文字 + Enter | 消息上屏，AI 开始流式回复 |
| 建议问题 | 点击欢迎页建议卡片 | 自动填充并发送 |
| 引用展开 | 点击右侧引用片段 | 高亮对应回答内容 |
| 代码渲染 | 发送含代码的问题 | 代码块语法高亮正确 |
| 换行 | Shift+Enter | 输入框换行，不发送 |
| 附件上传 | 点击附件按钮 | 弹出文件选择器 |
| 响应式 | 调整窗口宽度 | 侧栏按断点隐藏 |
| 移动端 | 手机浏览器访问 | 汉堡菜单切换会话 |

---

## 📦 八、输出文件结构

```
app/templates/
└── chat.html              # 智能答疑页完整模板

app/static/css/
├── variables.css          # CSS 变量定义
├── chat.css              # 答疑页专用样式
└── components.css         # 通用组件样式

app/static/js/
├── chat.js               # 答疑页交互逻辑
└── utils.js              # 工具函数

app/api/
└── chat.py               # 答疑接口（SSE 流式）
```

---

## ✅ 九、验收标准

### 视觉
- [ ] 浅色主题，白色背景 + 蓝色强调
- [ ] 所有图标使用 Remix Icon
- [ ] 对话气泡左右对齐正确
- [ ] 代码块/列表/表格渲染正确
- [ ] 引用来源卡片样式统一

### 交互
- [ ] 会话列表点击可切换
- [ ] 新建对话功能正常
- [ ] 发送消息 Enter/Shift+Enter 正确
- [ ] 建议问题点击可发送
- [ ] 流式输出打字机效果流畅

### 性能
- [ ] 首屏加载 <2 秒
- [ ] 消息滚动流畅 60fps
- [ ] SSE 连接稳定不断开
- [ ] 移动端响应式适配

### 可访问性
- [ ] 键盘导航完整（Tab 遍历）
- [ ] 焦点状态可见
- [ ] 对比度符合 WCAG AA
- [ ] 屏幕阅读器友好

---

> **最后更新**：2025 年  
> **参考产品**：DeepSeek HARNESS / ChatGPT / Claude / Notion AI  
> **适用项目**：《基于 Agent 的课程助教系统设计与实现》
