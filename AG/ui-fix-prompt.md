# UI 修复提示词 —— 针对当前问题逐项修复

> 基于已实现的深色主题进行精准修复，重点解决智能答疑页布局问题

---

## 🚨 问题优先级

| 优先级 | 页面 | 问题 |
|--------|------|------|
| 🔴 P0 | 智能答疑 | 没有对话气泡布局，完全不像聊天界面 |
| 🟠 P1 | 知识库 | 下拉框样式崩坏，文件上传按钮太丑 |
| 🟡 P2 | 管理员控制台 | Tab 按钮看不清，空状态简陋 |
| 🟢 P3 | 全局 | 缺少悬停动效，对比度不足 |

---

## 🔴 P0：智能答疑页重构（核心！）

### 当前问题截图
用户看到的是一堆标签 + 大空白，完全不是聊天界面。

### 目标布局（三栏式）

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 顶部导航栏 (60px, #1E293B)                                              │
│ [Logo] 课程助教系统                    [用户信息] [知识库] [作业批改] [退出]│
├──────────┬──────────────────────────────────────────────┬───────────────┤
│ 会话列表  │              对话主区域                      │   知识溯源    │
│ (260px)  │              (自适应，居中)                  │   (280px)    │
│          │                                              │              │
│ [+新建]  │  ┌────────────────────────────────────────┐ │  📚 引用来源  │
│ ───────  │  │  欢迎使用智能答疑助手                  │ │  ─────────── │
│          │  │                                        │ │              │
│ 最近会话 │  │  💬 你可以问我：                       │ │  📄 文档 1   │
│ 二叉树   │  │  • 什么是二叉树的前序遍历？            │ │    ├─ 片段 1 │
│ 链表     │  │  • 链表和数组有什么区别？              │ │    └─ 片段 2 │
│ 图论     │  │  • 如何计算时间复杂度？                │ │              │
│          │  │                                        │ │  📄 文档 2   │
│          │  └────────────────────────────────────────┘ │    └─ 片段 1 │
│          │                                              │              │
│          │  ┌────────────────────────────────────────┐ │              │
│          │  │ [输入你的问题...                       ]│ │              │
│          │  │                                        │ │              │
│          │  └────────────────────────────────────────┘ │              │
│          │       [📎] [📷]              [✨优化] [➤发送]│              │
└──────────┴──────────────────────────────────────────────┴──────────────┘
```

### 对话气泡样式（有消息时）

```
对话区域（有消息时）：
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  🤖 你好！我是课程答疑助手，基于 RAG 知识库回答问题。       │
│     我可以帮你解答课程相关疑问，回答会附带引用来源。         │
│                                                             │
│  👤 什么是二叉树的前序遍历？                        (右对齐)│
│                                                             │
│  🤖 二叉树的前序遍历顺序是：根→左→右。具体来说...           │
│     ┌─────────────────────────────────────────────────────┐│
│     │ 📎 引用来源                                          ││
│     │ 1. 《数据结构讲义》第 3 章 - 片段 2                   ││
│     │    "前序遍历首先访问根节点，然后递归遍历左子树..."   ││
│     └─────────────────────────────────────────────────────┘│
│                                                             │
│  👤 那中序遍历呢？                                  (右对齐)│
│                                                             │
│  🤖 中序遍历顺序是：左→根→右。...                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 完整 HTML 结构（chat.html 重构）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能答疑 - 课程助教系统</title>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        /* ============ CSS 变量 ============ */
        :root {
            --bg-page: #0F172A;
            --bg-sidebar: #1E293B;
            --bg-card: #1E293B;
            --bg-input: #334155;
            --bg-hover: #334155;
            
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            
            --accent-blue: #3B82F6;
            --accent-purple: #8B5CF6;
            --accent-green: #10B981;
            
            --gradient-primary: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
            --border-subtle: rgba(148, 163, 184, 0.1);
            --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
            
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --radius-xl: 24px;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, 'Microsoft YaHei', sans-serif;
            background: var(--bg-page);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
        }
        
        /* ============ 三栏布局 ============ */
        .chat-layout {
            display: grid;
            grid-template-columns: 260px 1fr 280px;
            height: 100vh;
        }
        
        /* ============ 左侧会话列表 ============ */
        .sidebar-left {
            background: var(--bg-sidebar);
            border-right: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            padding: 1rem;
        }
        
        .new-chat-btn {
            background: var(--gradient-primary);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: var(--radius-md);
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .new-chat-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-glow);
        }
        
        .session-list {
            margin-top: 1rem;
            overflow-y: auto;
            flex: 1;
        }
        
        .session-item {
            padding: 0.75rem;
            border-radius: var(--radius-sm);
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .session-item:hover {
            background: var(--bg-hover);
        }
        
        .session-item.active {
            background: rgba(59, 130, 246, 0.15);
            border-left: 3px solid var(--accent-blue);
        }
        
        .session-title {
            font-size: 0.875rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .session-time {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }
        
        /* ============ 中间对话区 ============ */
        .chat-main {
            display: flex;
            flex-direction: column;
            background: var(--bg-page);
            position: relative;
        }
        
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        /* 欢迎状态 */
        .welcome-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
        }
        
        .welcome-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .welcome-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .welcome-suggestions {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin-top: 2rem;
            max-width: 600px;
        }
        
        .suggestion-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .suggestion-tag {
            background: var(--bg-input);
            padding: 0.5rem 1rem;
            border-radius: var(--radius-md);
            font-size: 0.875rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .suggestion-tag:hover {
            background: var(--accent-blue);
        }
        
        /* 消息气泡 */
        .message {
            display: flex;
            gap: 1rem;
            max-width: 80%;
            animation: fadeIn 0.3s ease;
        }
        
        .message.user {
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
        }
        
        .message.ai .message-avatar {
            background: var(--gradient-primary);
        }
        
        .message.user .message-avatar {
            background: var(--bg-input);
        }
        
        .message-content {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1rem 1.25rem;
            line-height: 1.6;
        }
        
        .message.user .message-content {
            background: var(--gradient-primary);
            border: none;
            border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
        }
        
        .message.ai .message-content {
            border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px;
        }
        
        /* 引用卡片 */
        .sources-card {
            background: var(--bg-input);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-top: 1rem;
        }
        
        .sources-title {
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .source-item {
            font-size: 0.8125rem;
            color: var(--text-secondary);
            padding: 0.5rem;
            background: var(--bg-page);
            border-radius: var(--radius-sm);
            margin-top: 0.5rem;
        }
        
        /* 输入区域 */
        .input-area {
            padding: 1.5rem;
            background: var(--bg-page);
            border-top: 1px solid var(--border-subtle);
        }
        
        .input-wrapper {
            display: flex;
            gap: 1rem;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .input-container {
            flex: 1;
            position: relative;
        }
        
        .message-input {
            width: 100%;
            background: var(--bg-input);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1rem 1.25rem;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.9375rem;
            resize: none;
            min-height: 56px;
            max-height: 200px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        .message-input:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: var(--shadow-glow);
        }
        
        .input-actions {
            display: flex;
            gap: 0.5rem;
            align-items: flex-end;
        }
        
        .action-btn {
            width: 48px;
            height: 48px;
            border-radius: var(--radius-md);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background 0.2s;
        }
        
        .action-btn.secondary {
            background: var(--bg-input);
            color: var(--text-secondary);
        }
        
        .action-btn.primary {
            background: var(--gradient-primary);
            color: white;
        }
        
        .action-btn:hover {
            transform: scale(1.05);
        }
        
        /* ============ 右侧知识溯源 ============ */
        .sidebar-right {
            background: var(--bg-sidebar);
            border-left: 1px solid var(--border-subtle);
            padding: 1.5rem;
            overflow-y: auto;
        }
        
        .sources-panel-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .source-doc {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .source-doc-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .source-fragments {
            list-style: none;
            padding-left: 1.5rem;
        }
        
        .source-fragments li {
            font-size: 0.8125rem;
            color: var(--text-secondary);
            padding: 0.25rem 0;
            cursor: pointer;
        }
        
        .source-fragments li:hover {
            color: var(--accent-blue);
        }
        
        /* ============ 动画 ============ */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading-pulse {
            animation: pulse 1.5s infinite;
        }
        
        /* ============ 响应式 ============ */
        @media (max-width: 1024px) {
            .chat-layout {
                grid-template-columns: 260px 1fr;
            }
            .sidebar-right {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .chat-layout {
                grid-template-columns: 1fr;
            }
            .sidebar-left {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="chat-layout">
        <!-- 左侧会话列表 -->
        <aside class="sidebar-left">
            <button class="new-chat-btn">
                <i class="ri-add-line"></i> 新建对话
            </button>
            <div class="session-list">
                <div class="session-item active">
                    <div class="session-title">二叉树的前序遍历</div>
                    <div class="session-time">2 分钟前</div>
                </div>
                <div class="session-item">
                    <div class="session-title">链表插入操作</div>
                    <div class="session-time">1 小时前</div>
                </div>
            </div>
        </aside>
        
        <!-- 中间对话区 -->
        <main class="chat-main">
            <div class="messages-container">
                <!-- 欢迎状态（无消息时显示） -->
                <div class="welcome-state">
                    <div class="welcome-icon">🤖</div>
                    <h1 class="welcome-title">智能答疑助手</h1>
                    <p style="color: var(--text-secondary);">基于 RAG 知识库的课程问答，回答附带可靠来源引用</p>
                    
                    <div class="welcome-suggestions">
                        <p style="font-size: 0.875rem; color: var(--text-muted);">💡 你可以问我：</p>
                        <div class="suggestion-tags">
                            <span class="suggestion-tag">什么是二叉树的前序遍历？</span>
                            <span class="suggestion-tag">链表和数组有什么区别？</span>
                            <span class="suggestion-tag">如何计算算法的时间复杂度？</span>
                        </div>
                    </div>
                </div>
                
                <!-- 有消息时的结构（示例）
                <div class="message ai">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>你好！我是课程答疑助手...</p>
                        <div class="sources-card">
                            <div class="sources-title">📎 引用来源</div>
                            <div class="source-item">1. 《数据结构讲义》第 3 章 - 片段 2</div>
                        </div>
                    </div>
                </div>
                
                <div class="message user">
                    <div class="message-avatar">👤</div>
                    <div class="message-content">什么是二叉树的前序遍历？</div>
                </div>
                -->
            </div>
            
            <!-- 输入区域 -->
            <div class="input-area">
                <div class="input-wrapper">
                    <div class="input-container">
                        <textarea 
                            class="message-input" 
                            placeholder="输入你的问题，Enter 发送，Shift+Enter 换行..."
                            rows="1"
                        ></textarea>
                    </div>
                    <div class="input-actions">
                        <button class="action-btn secondary" title="上传附件">
                            <i class="ri-attachment-2"></i>
                        </button>
                        <button class="action-btn secondary" title="智能优化">
                            <i class="ri-sparkling-fill"></i>
                        </button>
                        <button class="action-btn primary" title="发送">
                            <i class="ri-send-plane-fill"></i>
                        </button>
                    </div>
                </div>
            </div>
        </main>
        
        <!-- 右侧知识溯源 -->
        <aside class="sidebar-right">
            <div class="sources-panel">
                <h3 class="sources-panel-title">📚 引用来源</h3>
                <div class="source-doc">
                    <div class="source-doc-title">📄 数据结构讲义</div>
                    <ul class="source-fragments">
                        <li>片段 1: 二叉树的定义</li>
                        <li>片段 3: 遍历算法详解</li>
                    </ul>
                </div>
            </div>
        </aside>
    </div>
    
    <script>
        // ============ 自动调整输入框高度 ============
        const textarea = document.querySelector('.message-input');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        // ============ 发送消息（示例）============
        // 实际项目中对接 SSE 流式接口
    </script>
</body>
</html>
```

---

## 🟠 P1：知识库页修复

### 问题清单

```
1. 下拉框展开时背景灰色溢出
2. "选择文件"按钮是原生样式，太丑
3. 缺少拖拽上传区域
4. 文档列表缺少删除操作
```

### 修复代码片段

```html
<!-- 上传区域重构 -->
<div class="upload-section">
    <label class="course-select">
        <span>选择课程</span>
        <select>
            <option>数据结构</option>
            <option>算法分析</option>
        </select>
    </label>
    
    <div class="upload-area" id="uploadArea">
        <input type="file" id="fileInput" hidden multiple accept=".txt,.md,.pdf">
        
        <div class="upload-placeholder">
            <i class="ri-upload-cloud-2-line" style="font-size: 2rem; color: var(--accent-blue);"></i>
            <p>拖拽文件到此处，或 <span class="upload-link">点击选择文件</span></p>
            <p class="upload-hint">支持 .txt / .md / .pdf 格式</p>
        </div>
        
        <button class="upload-btn">
            <i class="ri-upload-line"></i> 上传并向量化
        </button>
    </div>
</div>

<style>
.upload-area {
    border: 2px dashed var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 2rem;
    text-align: center;
    transition: border-color 0.2s, background 0.2s;
    cursor: pointer;
}

.upload-area:hover,
.upload-area.dragover {
    border-color: var(--accent-blue);
    background: rgba(59, 130, 246, 0.05);
}

.upload-btn {
    background: var(--gradient-primary);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    margin-top: 1rem;
}

.document-table .action-btn {
    color: #EF4444;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-sm);
    transition: background 0.2s;
}

.document-table .action-btn:hover {
    background: rgba(239, 68, 68, 0.1);
}
</style>
```

---

## 🟡 P2：管理员控制台优化

### Tab 按钮修复

```css
/* 当前问题：白色背景 + 白色文字看不清 */
.tab-btn {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-subtle);
}

.tab-btn.active {
    background: var(--accent-blue);
    color: white;
    border-color: var(--accent-blue);
}

.tab-btn:hover:not(.active) {
    background: var(--bg-hover);
}
```

### 空状态优化

```html
<div class="empty-state">
    <i class="ri-folder-receive-line" style="font-size: 3rem; color: var(--text-muted);"></i>
    <p style="margin-top: 1rem; color: var(--text-secondary);">暂无日志</p>
    <p style="font-size: 0.8125rem; color: var(--text-muted);">用户操作记录将显示在这里</p>
</div>
```

### 分页器按钮

```css
.pagination-btn {
    background: var(--bg-input);
    color: var(--text-primary);
    border: 1px solid var(--border-subtle);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
    background: var(--accent-blue);
    border-color: var(--accent-blue);
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
```

---

## 🟢 P3：全局动效增强

### 悬停反馈

```css
/* 所有可点击元素添加过渡 */
button, a, [role="button"], .session-item {
    transition: transform 0.2s, background 0.2s, box-shadow 0.2s;
}

button:hover, a:hover {
    transform: translateY(-2px);
}

/* 表格行悬停 */
tr:hover {
    background: rgba(59, 130, 246, 0.05);
}

/* 输入框 Focus 光晕 */
input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
```

### 加载动画

```css
@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-subtle);
    border-top-color: var(--accent-blue);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}
```

---

## 📦 输出要求

1. **优先修复智能答疑页**，输出完整 `chat.html` 模板
2. 保持 Jinja2 模板语法（`{{ }}`、`{% %}`）
3. CSS 变量统一管理，方便后续主题切换
4. 图标全部换为 Remix Icon
5. 响应式断点：1024px（隐藏右栏）、768px（隐藏左栏）

---

> 请先输出智能答疑页的完整代码，确认效果后再修复其他页面。
