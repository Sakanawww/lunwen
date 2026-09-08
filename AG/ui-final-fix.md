# UI 最终修复提示词 —— 浅色主题 + 核心布局重构

> 基于用户反馈的精准修复，**必须逐项完成**

---

## 🎨 一、主题切换：深色 → 浅色

### 当前问题
- 深蓝色背景压抑、文字对比度不足
- 不符合教育类产品的清新感
- 长时间使用眼睛疲劳

### 新配色方案（浅色主题）

```css
:root {
  /* ===== 背景色 ===== */
  --bg-page: #F8FAFC;           /* 页面背景：浅灰蓝 */
  --bg-card: #FFFFFF;           /* 卡片背景：纯白 */
  --bg-sidebar: #FFFFFF;        /* 侧栏背景：纯白 */
  --bg-input: #FFFFFF;          /* 输入框背景：纯白 */
  --bg-hover: #F1F5F9;          /* 悬停背景：浅灰 */
  
  /* ===== 文字色 ===== */
  --text-primary: #1E293B;      /* 主文字：深灰蓝 */
  --text-secondary: #64748B;    /* 次要文字：中灰 */
  --text-muted: #94A3B8;        /* 弱化文字：浅灰 */
  
  /* ===== 强调色 ===== */
  --primary: #3B82F6;           /* 主色：科技蓝 */
  --primary-hover: #2563EB;     /* 悬停：深蓝 */
  --primary-light: rgba(59, 130, 246, 0.1);  /* 浅色背景 */
  
  /* ===== 功能色 ===== */
  --success: #10B981;           /* 成功：绿色 */
  --warning: #F59E0B;           /* 警告：黄色 */
  --danger: #EF4444;            /* 错误：红色 */
  
  /* ===== 边框 ===== */
  --border-light: #E2E8F0;      /* 细边框 */
  --border-medium: #CBD5E1;     /* 中等边框 */
  
  /* ===== 阴影 ===== */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.2);
  
  /* ===== 圆角 ===== */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;
}
```

### 全局样式

```css
body {
  font-family: 'Inter', -apple-system, 'Microsoft YaHei', sans-serif;
  background: var(--bg-page);
  color: var(--text-primary);
  line-height: 1.6;
}

/* 卡片统一样式 */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
}

/* 按钮统一样式 */
.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: var(--bg-hover);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}
```

---

## 🔴 二、智能答疑页重构（P0 核心）

### 当前问题
- 一堆标签堆在顶部，像表单不是聊天
- 没有对话气泡
- 没有左右分栏

### 目标布局（必须实现）

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 顶部导航栏 (白色背景，60px 高，底部细边框)                               │
│ [Logo] 课程助教系统           [知识库] [作业批改] [试题生成] [用户] [退出]│
├──────────┬──────────────────────────────────────────────┬───────────────┤
│ 会话列表  │              对话主区域                      │   (可选)     │
│ (280px)  │              (自适应)                        │              │
│          │                                              │              │
│ [+新建]  │  ┌────────────────────────────────────────┐ │              │
│ ───────  │  │  🤖 你好！我是课程答疑助手             │ │              │
│          │  │  基于课程知识库回答问题，附带引用来源   │ │              │
│ 今天     │  │                                        │ │              │
│ 二叉树   │  └────────────────────────────────────────┘ │              │
│ 10:30    │                                            │              │
│          │            ┌─────────────────────────────┐ │              │
│ 昨天     │            │ 什么是二叉树的前序遍历？     │ │              │
│ 链表     │            │                      (右对齐)│ │              │
│ 15:20    │  ┌────────────────────────────────────┐  │              │
│          │  │ 🤖 二叉树的前序遍历顺序是：根→左→右  │  │              │
│          │  │    ┌─────────────────────────────┐ │  │              │
│          │  │    │ 📎 引用来源                  │ │  │              │
│          │  │    │ 1.《数据结构》第 3 章 片段 2    │ │  │              │
│          │  │    └─────────────────────────────┘ │  │              │
│          │  └────────────────────────────────────┘  │              │
│          │                                            │              │
│          │  ┌─────────────────────────────────────┐  │              │
│          │  │ [输入问题...]                       │  │              │
│          │  └─────────────────────────────────────┘  │              │
└──────────┴──────────────────────────────────────────────┴──────────────┘
```

### 完整 HTML 模板（chat.html）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>智能答疑 - 课程助教系统</title>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        /* CSS 变量见上文 */
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, 'Microsoft YaHei', sans-serif;
            background: var(--bg-page);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* ===== 顶部导航 ===== */
        .navbar {
            height: 60px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-light);
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        
        .nav-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 600;
            font-size: 1rem;
        }
        
        .nav-logo {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--primary) 0%, #8B5CF6 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.25rem;
        }
        
        .nav-right {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.875rem;
            transition: color 0.2s;
        }
        
        .nav-link:hover {
            color: var(--primary);
        }
        
        .nav-link.active {
            color: var(--primary);
            font-weight: 500;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--bg-hover);
            border-radius: var(--radius-md);
            font-size: 0.875rem;
        }
        
        /* ===== 主布局 ===== */
        .chat-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        /* 左侧会话列表 */
        .sidebar {
            width: 280px;
            background: var(--bg-card);
            border-right: 1px solid var(--border-light);
            padding: 1rem;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .new-chat-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: var(--radius-md);
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            transition: all 0.2s;
            margin-bottom: 1rem;
        }
        
        .new-chat-btn:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
        }
        
        .session-group-title {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 500;
            margin: 1rem 0 0.5rem 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .session-item {
            padding: 0.75rem;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 0.25rem;
        }
        
        .session-item:hover {
            background: var(--bg-hover);
        }
        
        .session-item.active {
            background: var(--primary-light);
            border-left: 3px solid var(--primary);
        }
        
        .session-title {
            font-size: 0.875rem;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .session-time {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }
        
        /* 主对话区 */
        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .messages-wrapper {
            flex: 1;
            overflow-y: auto;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        /* 欢迎状态 */
        .welcome-card {
            max-width: 600px;
            margin: 4rem auto;
            text-align: center;
        }
        
        .welcome-icon {
            width: 64px;
            height: 64px;
            margin: 0 auto 1.5rem;
            background: linear-gradient(135deg, var(--primary) 0%, #8B5CF6 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
        }
        
        .welcome-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }
        
        .welcome-desc {
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }
        
        .suggestions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.75rem;
            margin-top: 1.5rem;
        }
        
        .suggestion-card {
            background: var(--bg-card);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 1rem;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
        }
        
        .suggestion-card:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .suggestion-card i {
            color: var(--primary);
            margin-right: 0.5rem;
        }
        
        .suggestion-card p {
            font-size: 0.875rem;
            color: var(--text-primary);
        }
        
        /* 消息气泡 */
        .message-row {
            display: flex;
            gap: 1rem;
            max-width: 70%;
        }
        
        .message-row.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 1.25rem;
        }
        
        .message-avatar.ai {
            background: linear-gradient(135deg, var(--primary) 0%, #8B5CF6 100%);
        }
        
        .message-avatar.user {
            background: var(--bg-hover);
        }
        
        .message-bubble {
            background: var(--bg-card);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-lg);
            padding: 1rem 1.25rem;
            line-height: 1.6;
            box-shadow: var(--shadow-sm);
        }
        
        .message-row.user .message-bubble {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
        }
        
        .message-row.ai .message-bubble {
            border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px;
        }
        
        /* 引用卡片 */
        .sources-section {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-light);
        }
        
        .sources-header {
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }
        
        .source-item {
            background: var(--bg-hover);
            border-radius: var(--radius-sm);
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            font-size: 0.8125rem;
            color: var(--text-secondary);
        }
        
        .source-item strong {
            color: var(--text-primary);
        }
        
        /* 输入区域 */
        .input-section {
            padding: 1.5rem 2rem;
            background: var(--bg-card);
            border-top: 1px solid var(--border-light);
        }
        
        .input-box {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
        }
        
        .message-textarea {
            width: 100%;
            background: var(--bg-input);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-lg);
            padding: 1rem 3.5rem 1rem 1.25rem;
            font-family: inherit;
            font-size: 0.9375rem;
            color: var(--text-primary);
            resize: none;
            min-height: 56px;
            max-height: 200px;
            transition: all 0.2s;
        }
        
        .message-textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
        }
        
        .message-textarea::placeholder {
            color: var(--text-muted);
        }
        
        .send-btn {
            position: absolute;
            right: 0.75rem;
            bottom: 0.75rem;
            width: 40px;
            height: 40px;
            background: var(--primary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .send-btn:hover {
            background: var(--primary-hover);
            transform: scale(1.05);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .input-hint {
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.75rem;
        }
        
        .input-hint kbd {
            background: var(--bg-hover);
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.6875rem;
        }
    </style>
</head>
<body>
    <!-- 顶部导航 -->
    <nav class="navbar">
        <div class="nav-left">
            <div class="nav-logo">📚</div>
            <span>课程助教系统</span>
        </div>
        <div class="nav-right">
            <a href="/kb" class="nav-link">知识库</a>
            <a href="/grading" class="nav-link">作业批改</a>
            <a href="/questions" class="nav-link">试题生成</a>
            <div class="user-info">
                <i class="ri-user-smile-line"></i>
                <span>{{ current_user.username }} · {{ current_user.role }}</span>
            </div>
            <a href="/logout" class="nav-link" style="color: var(--danger);">
                <i class="ri-logout-circle-line"></i> 退出
            </a>
        </div>
    </nav>
    
    <!-- 主容器 -->
    <div class="chat-container">
        <!-- 左侧会话列表 -->
        <aside class="sidebar">
            <button class="new-chat-btn">
                <i class="ri-add-line"></i> 新建对话
            </button>
            
            <div class="session-group-title">最近会话</div>
            
            <div class="session-list">
                <!-- Jinja2 循环渲染 -->
                {% for session in sessions %}
                <div class="session-item {% if session.id == current_session_id %}active{% endif %}">
                    <div class="session-title">{{ session.title }}</div>
                    <div class="session-time">{{ session.created_at|time_ago }}</div>
                </div>
                {% endfor %}
            </div>
        </aside>
        
        <!-- 主对话区 -->
        <main class="chat-main">
            <div class="messages-wrapper">
                <!-- 欢迎状态（无消息时） -->
                <div class="welcome-card">
                    <div class="welcome-icon">🤖</div>
                    <h1 class="welcome-title">智能答疑助手</h1>
                    <p class="welcome-desc">基于 RAG 知识库的课程问答，回答附带可靠来源引用</p>
                    
                    <div class="suggestions">
                        <div class="suggestion-card" data-question="什么是二叉树的前序遍历？">
                            <i class="ri-question-line"></i>
                            <p>什么是二叉树的前序遍历？</p>
                        </div>
                        <div class="suggestion-card" data-question="链表和数组有什么区别？">
                            <i class="ri-question-line"></i>
                            <p>链表和数组有什么区别？</p>
                        </div>
                        <div class="suggestion-card" data-question="如何计算算法的时间复杂度？">
                            <i class="ri-question-line"></i>
                            <p>如何计算算法的时间复杂度？</p>
                        </div>
                        <div class="suggestion-card" data-question="请解释一下动态规划的思想">
                            <i class="ri-question-line"></i>
                            <p>请解释一下动态规划的思想</p>
                        </div>
                    </div>
                </div>
                
                <!-- 有消息时的结构（示例）
                <div class="message-row ai">
                    <div class="message-avatar">🤖</div>
                    <div class="message-bubble">
                        <p>你好！我是课程答疑助手...</p>
                        <div class="sources-section">
                            <div class="sources-header">📎 引用来源</div>
                            <div class="source-item">
                                <strong>《数据结构》第 3 章</strong> - 片段 2
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="message-row user">
                    <div class="message-avatar">👤</div>
                    <div class="message-bubble">
                        什么是二叉树的前序遍历？
                    </div>
                </div>
                -->
            </div>
            
            <!-- 输入区域 -->
            <div class="input-section">
                <div class="input-box">
                    <textarea 
                        class="message-textarea"
                        placeholder="输入你的问题..."
                        rows="1"
                    ></textarea>
                    <button class="send-btn" title="发送">
                        <i class="ri-send-plane-fill"></i>
                    </button>
                </div>
                <div class="input-hint">
                    <kbd>Enter</kbd> 发送 · <kbd>Shift+Enter</kbd> 换行 · 回答将引用课程知识库来源
                </div>
            </div>
        </main>
    </div>
    
    <script>
        // 自动调整输入框高度
        const textarea = document.querySelector('.message-textarea');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        // 点击建议问题
        document.querySelectorAll('.suggestion-card').forEach(card => {
            card.addEventListener('click', function() {
                const question = this.dataset.question;
                textarea.value = question;
                textarea.focus();
            });
        });
    </script>
</body>
</html>
```

---

## 🟠 三、下拉框样式修复

### 问题
- 展开时灰色背景溢出
- 选项样式简陋

### 修复代码

```css
/* 自定义下拉框 */
select {
    appearance: none;
    -webkit-appearance: none;
    background: var(--bg-input);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 0.625rem 2.5rem 0.625rem 1rem;
    font-size: 0.9375rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s;
    
    /* 自定义箭头 */
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 16px;
}

select:hover {
    border-color: var(--primary);
}

select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: var(--shadow-glow);
}

/* 下拉选项样式（需配合 JS 自定义下拉） */
option {
    background: var(--bg-card);
    color: var(--text-primary);
    padding: 0.5rem;
}
```

---

## 🟡 四、图标统一（Remix Icon）

### 全局图标映射

```html
<!-- 导航栏 -->
<i class="ri-book-open-line"></i>      <!-- Logo -->
<i class="ri-folder-cloud-line"></i>   <!-- 知识库 -->
<i class="ri-checkbox-circle-line"></i> <!-- 作业批改 -->
<i class="ri-edit-circle-line"></i>    <!-- 试题生成 -->
<i class="ri-dashboard-line"></i>      <!-- 学情看板 -->
<i class="ri-user-smile-line"></i>     <!-- 用户 -->
<i class="ri-logout-circle-line"></i>  <!-- 退出 -->

<!-- 答疑页 -->
<i class="ri-add-line"></i>            <!-- 新建对话 -->
<i class="ri-question-line"></i>       <!-- 建议问题 -->
<i class="ri-send-plane-fill"></i>     <!-- 发送 -->
<i class="ri-attachment-2"></i>        <!-- 附件 -->
<i class="ri-file-text-line"></i>      <!-- 文档 -->

<!-- 表格 -->
<i class="ri-search-line"></i>         <!-- 搜索 -->
<i class="ri-settings-4-line"></i>     <!-- 设置 -->
<i class="ri-refresh-line"></i>        <!-- 刷新 -->
<i class="ri-delete-bin-line"></i>     <!-- 删除 -->
```

---

## 🟢 五、空状态设计

### 通用空状态组件

```html
<div class="empty-state">
    <div class="empty-icon">
        <i class="ri-inbox-line"></i>
    </div>
    <h3 class="empty-title">暂无数据</h3>
    <p class="empty-desc">相关内容将显示在这里</p>
</div>

<style>
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
}

.empty-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 1.5rem;
    background: var(--bg-hover);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    color: var(--text-muted);
}

.empty-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.empty-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
}
</style>
```

---

## 📋 六、Agent 设置页优化

### 问题
- 页面空荡荡
- 没有实际配置项

### 修复方案

```html
<!-- Agent 配置卡片 -->
<div class="agent-config-card">
    <div class="agent-header">
        <div class="agent-icon">🤖</div>
        <div class="agent-info">
            <h4>答疑 Agent</h4>
            <p>面向学生，基于 RAG 课程知识库进行多轮答疑并溯源引用</p>
        </div>
        <div class="agent-status">
            <span class="status-badge active">● 启用</span>
        </div>
    </div>
    
    <div class="agent-details">
        <div class="config-row">
            <label>模型</label>
            <span>qwen-plus</span>
        </div>
        <div class="config-row">
            <label>路由关键词</label>
            <div class="tags">
                <span class="tag">答疑</span>
                <span class="tag">问题</span>
                <span class="tag">不会</span>
                <span class="tag">+3</span>
            </div>
        </div>
        <div class="config-row">
            <label>操作</label>
            <button class="btn-secondary btn-sm">编辑配置</button>
        </div>
    </div>
</div>

<style>
.agent-config-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.agent-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-light);
    margin-bottom: 1rem;
}

.agent-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary) 0%, #8B5CF6 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.agent-info h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.agent-info p {
    font-size: 0.8125rem;
    color: var(--text-secondary);
}

.status-badge {
    font-size: 0.8125rem;
    color: var(--success);
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.config-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 0;
}

.config-row label {
    width: 100px;
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.tag {
    background: var(--bg-hover);
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    color: var(--text-secondary);
}
</style>
```

---

## ✅ 输出要求

1. **必须实现**：
   - [ ] 浅色主题（白色背景 + 蓝色强调）
   - [ ] 智能答疑页三栏布局（左侧会话 + 中间对话 + 右侧可选）
   - [ ] 对话气泡样式（用户右对齐蓝色，AI 左对齐白色）
   - [ ] 下拉框样式修复
   - [ ] 统一 Remix Icon 图标
   - [ ] 空状态组件

2. **保持**：
   - Jinja2 模板语法
   - 现有 API 接口不变
   - 响应式设计

3. **优先顺序**：
   1. 智能答疑页（chat.html）
   2. 全局 CSS 变量文件
   3. 其他页面适配浅色主题

---

> 请先输出完整的 `chat.html` 和 `static/css/variables.css`，确认效果后再修复其他页面。
