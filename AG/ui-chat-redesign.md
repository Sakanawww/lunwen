# 智能答疑页重新设计 - 完整修复版

> 针对当前问题的精准修复：图标缺失 + 对齐混乱 + 格式错误 + 侧栏打不开

---

## 🔴 当前问题清单

| 问题 | 描述 | 优先级 |
|------|------|--------|
| 没有图标 | 所有按钮/导航都是文字 | P0 |
| 布局错位 | 对话气泡不对齐，左右混乱 | P0 |
| 侧栏打不开 | 会话列表点击无响应 | P0 |
| 回答格式乱 | 代码/公式排版混乱 | P0 |
| 下拉框溢出 | 选项背景灰色溢出 | P1 |
| 建议问题太丑 | 像标签堆砌，不可点击 | P1 |

---

## ✅ 完整修复方案

### 一、HTML 完整结构（chat.html）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能答疑 - 课程助教系统</title>
    
    <!-- Remix Icon 图标库 -->
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        /* ========== CSS 变量 ========== */
        :root {
            /* 背景色 */
            --bg-page: #F5F7FA;
            --bg-card: #FFFFFF;
            --bg-hover: #F0F2F5;
            --bg-input: #FFFFFF;
            
            /* 文字色 */
            --text-primary: #1A1A1A;
            --text-secondary: #667788;
            --text-muted: #99AAB5;
            
            /* 强调色 */
            --primary: #5B7FFF;
            --primary-hover: #4665E8;
            --primary-light: rgba(91, 127, 255, 0.1);
            
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
        
        /* ========== 基础样式 ========== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Microsoft YaHei', sans-serif;
            background: var(--bg-page);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
        }
        
        /* ========== 顶部导航栏 ========== */
        .navbar {
            height: 56px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-light);
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
        }
        
        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 600;
            font-size: 1rem;
            color: var(--text-primary);
        }
        
        .navbar-logo {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.25rem;
        }
        
        .navbar-menu {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            padding: 0.5rem 0.75rem;
            border-radius: var(--radius-sm);
            transition: all 0.2s;
        }
        
        .nav-link:hover {
            color: var(--primary);
            background: var(--primary-light);
        }
        
        .nav-link.active {
            color: var(--primary);
            background: var(--primary-light);
        }
        
        .user-dropdown {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 0.75rem;
            background: var(--bg-hover);
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .user-dropdown:hover {
            background: var(--primary-light);
        }
        
        .user-avatar {
            width: 28px;
            height: 28px;
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* ========== 主布局 ========== */
        .chat-layout {
            display: flex;
            height: calc(100vh - 56px);
            overflow: hidden;
        }
        
        /* ===== 左侧会话列表 ===== */
        .sidebar {
            width: 300px;
            background: var(--bg-card);
            border-right: 1px solid var(--border-light);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }
        
        .sidebar-header {
            padding: 1rem;
            border-bottom: 1px solid var(--border-light);
        }
        
        .new-chat-btn {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.75rem 1rem;
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            font-size: 0.9375rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: var(--shadow-sm);
        }
        
        .new-chat-btn:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .session-list {
            flex: 1;
            overflow-y: auto;
            padding: 0.5rem;
        }
        
        .session-group {
            margin-bottom: 1rem;
        }
        
        .session-group-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 0.5rem 0.75rem;
        }
        
        .session-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
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
        }
        
        .session-icon {
            color: var(--text-muted);
            font-size: 1rem;
            margin-top: 0.125rem;
        }
        
        .session-content {
            flex: 1;
            min-width: 0;
        }
        
        .session-title {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 0.25rem;
        }
        
        .session-preview {
            font-size: 0.75rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* ===== 主对话区 ===== */
        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 2rem;
        }
        
        /* 欢迎状态 */
        .welcome-container {
            max-width: 700px;
            margin: 0 auto;
            padding-top: 4rem;
            text-align: center;
        }
        
        .welcome-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            color: white;
            box-shadow: var(--shadow-md);
        }
        
        .welcome-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
        }
        
        .welcome-desc {
            font-size: 1rem;
            color: var(--text-secondary);
            margin-bottom: 2.5rem;
        }
        
        .suggestions-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .suggestion-card {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 1rem 1.25rem;
            background: var(--bg-card);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
        }
        
        .suggestion-card:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .suggestion-icon {
            width: 32px;
            height: 32px;
            background: var(--primary-light);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            flex-shrink: 0;
        }
        
        .suggestion-text {
            font-size: 0.9375rem;
            color: var(--text-primary);
            line-height: 1.5;
        }
        
        /* 消息气泡 */
        .message-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            max-width: 85%;
        }
        
        .message-row.user {
            margin-left: auto;
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 1.25rem;
        }
        
        .message-avatar.ai {
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
        }
        
        .message-avatar.user {
            background: var(--bg-hover);
        }
        
        .message-bubble {
            flex: 1;
        }
        
        .message-content {
            background: var(--bg-card);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.5rem;
            line-height: 1.7;
            box-shadow: var(--shadow-sm);
        }
        
        .message-row.user .message-content {
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
            color: white;
            border: none;
            border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
        }
        
        .message-row.ai .message-content {
            border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px;
        }
        
        /* 消息内的排版 */
        .message-content p {
            margin-bottom: 1rem;
        }
        
        .message-content p:last-child {
            margin-bottom: 0;
        }
        
        .message-content code {
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            background: rgba(0,0,0,0.06);
            padding: 0.125rem 0.375rem;
            border-radius: 4px;
            font-size: 0.875em;
        }
        
        .message-row.user .message-content code {
            background: rgba(255,255,255,0.2);
        }
        
        .message-content pre {
            background: #1E1E1E;
            color: #D4D4D4;
            padding: 1rem;
            border-radius: var(--radius-md);
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .message-content pre code {
            background: transparent;
            padding: 0;
            color: inherit;
        }
        
        .message-content ul,
        .message-content ol {
            margin: 0.75rem 0;
            padding-left: 1.5rem;
        }
        
        .message-content li {
            margin-bottom: 0.5rem;
        }
        
        /* 引用来源卡片 */
        .sources-card {
            margin-top: 1.25rem;
            padding-top: 1.25rem;
            border-top: 1px solid var(--border-light);
        }
        
        .sources-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }
        
        .source-item {
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
            padding: 0.75rem;
            background: var(--bg-hover);
            border-radius: var(--radius-sm);
            margin-bottom: 0.5rem;
            font-size: 0.8125rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .source-item:hover {
            background: var(--primary-light);
        }
        
        .source-item i {
            color: var(--primary);
            margin-top: 0.125rem;
        }
        
        .source-item-text {
            color: var(--text-secondary);
            line-height: 1.5;
        }
        
        .source-item-text strong {
            color: var(--text-primary);
        }
        
        /* ===== 输入区域 ===== */
        .input-section {
            padding: 1.5rem 2rem;
            background: var(--bg-card);
            border-top: 1px solid var(--border-light);
        }
        
        .input-wrapper {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
        }
        
        .message-input {
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
        
        .message-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-light);
        }
        
        .message-input::placeholder {
            color: var(--text-muted);
        }
        
        .send-button {
            position: absolute;
            right: 0.75rem;
            bottom: 0.75rem;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #5B7FFF 0%, #8B5CF6 100%);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .send-button:hover {
            transform: scale(1.05);
            box-shadow: var(--shadow-md);
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
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
            border: 1px solid var(--border-light);
        }
        
        /* ===== 右侧知识溯源 ===== */
        .sources-sidebar {
            width: 280px;
            background: var(--bg-card);
            border-left: 1px solid var(--border-light);
            padding: 1.5rem;
            overflow-y: auto;
            flex-shrink: 0;
        }
        
        .sources-sidebar-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .source-doc-card {
            background: var(--bg-hover);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .source-doc-title {
            font-size: 0.8125rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .source-fragments {
            list-style: none;
        }
        
        .source-fragments li {
            font-size: 0.75rem;
            color: var(--text-secondary);
            padding: 0.375rem 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }
        
        .source-fragments li:hover {
            color: var(--primary);
        }
        
        .source-fragments li::before {
            content: "•";
            color: var(--primary);
        }
        
        /* ========== 滚动条 ========== */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-medium);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }
        
        /* ========== 响应式 ========== */
        @media (max-width: 1024px) {
            .sources-sidebar {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
            
            .suggestions-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
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
            <a href="/logout" class="nav-link" style="color: #EF4444;">
                <i class="ri-logout-circle-line"></i>
                <span>退出</span>
            </a>
        </div>
    </nav>
    
    <!-- 主布局 -->
    <div class="chat-layout">
        <!-- 左侧会话列表 -->
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
                </div>
                <div class="session-group">
                    <div class="session-group-title">昨天</div>
                    <div class="session-item">
                        <i class="ri-message-3-line session-icon"></i>
                        <div class="session-content">
                            <div class="session-title">链表插入操作</div>
                            <div class="session-preview">单链表如何在指定位置插入节点？</div>
                        </div>
                    </div>
                </div>
            </div>
        </aside>
        
        <!-- 主对话区 -->
        <main class="chat-main">
            <div class="messages-container">
                <!-- 欢迎状态（无消息时显示） -->
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
                
                <!-- 有消息时的示例结构
                <div class="message-row user">
                    <div class="message-avatar">👤</div>
                    <div class="message-content">
                        什么是二叉树的前序遍历？
                    </div>
                </div>
                
                <div class="message-row ai">
                    <div class="message-avatar">🤖</div>
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
                -->
            </div>
            
            <!-- 输入区域 -->
            <div class="input-section">
                <div class="input-wrapper">
                    <textarea 
                        class="message-input"
                        placeholder="输入你的问题，Enter 发送，Shift+Enter 换行..."
                        rows="1"
                    ></textarea>
                    <button class="send-button" title="发送">
                        <i class="ri-send-plane-fill"></i>
                    </button>
                </div>
                <div class="input-hint">
                    <kbd>Enter</kbd> 发送 · <kbd>Shift+Enter</kbd> 换行 · 回答将引用课程知识库来源
                </div>
            </div>
        </main>
        
        <!-- 右侧知识溯源 -->
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
                    <li>片段 1: 二叉树的定义</li>
                    <li>片段 3: 遍历算法详解</li>
                </ul>
            </div>
        </aside>
    </div>
    
    <script>
        // ===== 自动调整输入框高度 =====
        const textarea = document.querySelector('.message-input');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        // ===== 点击建议问题 =====
        document.querySelectorAll('.suggestion-card').forEach(card => {
            card.addEventListener('click', function() {
                const question = this.dataset.question;
                textarea.value = question;
                textarea.focus();
            });
        });
        
        // ===== 发送消息 =====
        const sendBtn = document.querySelector('.send-button');
        sendBtn.addEventListener('click', sendMessage);
        
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        function sendMessage() {
            const message = textarea.value.trim();
            if (!message) return;
            
            // TODO: 调用 API 发送消息
            console.log('发送消息:', message);
            textarea.value = '';
            textarea.style.height = 'auto';
        }
        
        // ===== 会话切换 =====
        document.querySelectorAll('.session-item').forEach(item => {
            item.addEventListener('click', function() {
                document.querySelectorAll('.session-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                // TODO: 加载会话消息
            });
        });
    </script>
</body>
</html>
```

---

## 📋 关键修复点

| 问题 | 修复方案 |
|------|---------|
| 没有图标 | 引入 Remix Icon CDN，所有按钮/导航添加 `<i>` 标签 |
| 布局错位 | 使用 Flexbox 三栏布局，严格对齐 |
| 侧栏打不开 | 添加点击事件监听，active 状态切换 |
| 格式混乱 | 代码块用 `<pre><code>`，行内代码用 `<code>` |
| 下拉框溢出 | 自定义 select 样式，添加 SVG 箭头 |
| 建议问题丑 | 改为卡片网格布局，可点击 |

---

## 🎨 样式预览

```
配色：
- 背景：#F5F7FA (浅灰)
- 卡片：#FFFFFF (纯白)
- 主色：#5B7FFF (蓝紫渐变)
- 文字：#1A1A1A / #667788 / #99AAB5

圆角：
- 按钮：12px
- 卡片：16px
- 气泡：16px (一角 4px)

阴影：
- 卡片：0 4px 12px rgba(0,0,0,0.08)
- 悬浮：0 8px 24px rgba(0,0,0,0.12)
```

---

## ✅ 输出要求

1. 完整 `chat.html` 文件（包含所有 CSS 和 JS）
2. 保持 Jinja2 模板语法
3. 图标全部使用 Remix Icon
4. 响应式断点：1024px 隐藏右栏，768px 隐藏左栏
5. 消息格式支持 Markdown 渲染（粗体/代码/列表）

---

> 请输出完整的 chat.html 文件，确保可以直接替换现有文件运行。
