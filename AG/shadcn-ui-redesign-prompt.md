# 课程助教系统 - shadcn/ui 风格 UI 设计迭代提示词

> 直接复制本提示词给执行 Agent，无需修改

---

## 📋 设计目标

基于 **shadcn/ui** 设计系统，对当前课程助教系统进行全面的 UI 风格迭代。

**参考风格**:
- shadcn/ui - 简洁、专业、可访问性优先
- Vercel Design - 现代、极简、开发者友好
- Linear - 精致细节、流畅动画
- Raycast - 高效、美观、键盘优先

---

## 🎨 设计原则

### 1. 核心理念

```
功能优先 (Function First)
    ↓
视觉清晰 (Visual Clarity)
    ↓
细节精致 (Refined Details)
    ↓
一致体验 (Consistent Experience)
```

### 2. 设计价值观

| 价值观 | 描述 | 示例 |
|--------|------|------|
| **简洁** | 减少视觉噪音，突出核心内容 | 留白 > 装饰 |
| **一致** | 统一的间距、颜色、圆角 | 8px 网格系统 |
| **可访问** | 键盘导航、屏幕阅读器支持 | 焦点可见、对比度达标 |
| **响应式** | 移动优先，渐进增强 | 断点：sm→md→lg→xl→2xl |
| **性能** | 最小 CSS、按需加载 | Tailwind PurgeCSS |

---

## 🎨 设计令牌系统 (Design Tokens)

### 三层令牌架构

```
Primitive Tokens (原始值)
       ↓
Semantic Tokens (语义别名)
       ↓
Component Tokens (组件专用)
```

### 1. 原始令牌 (Primitive Tokens)

```css
/* 颜色 - HSL 格式，支持透明度 */
:root {
  --color-slate-50: 210 40% 98%;
  --color-slate-100: 210 40% 96.1%;
  --color-slate-200: 214.3 31.8% 91.4%;
  --color-slate-300: 212.7 26.8% 83.9%;
  --color-slate-400: 215 20.2% 65.1%;
  --color-slate-500: 215.4 16.3% 46.9%;
  --color-slate-600: 215.3 25% 36.5%;
  --color-slate-700: 215.3 31% 26.5%;
  --color-slate-800: 217.2 32.6% 17.5%;
  --color-slate-900: 222.2 47.4% 11.2%;
  
  /* 品牌色 - 蓝色系 */
  --color-blue-50: 213 100% 97%;
  --color-blue-100: 214.3 100% 95%;
  --color-blue-500: 217.2 91.2% 59.8%;
  --color-blue-600: 221.2 83.2% 53.3%;
  --color-blue-700: 221.2 83.2% 43.3%;
  
  /* 功能色 */
  --color-success: 142 76% 36%;    /* 绿色 */
  --color-warning: 38 92% 50%;     /* 橙色 */
  --color-danger: 0 84% 60%;       /* 红色 */
  --color-info: 199 89% 48%;       /* 蓝色 */
}

/* 深色模式 */
.dark {
  --color-slate-50: 222.2 47.4% 11.2%;
  --color-slate-100: 217.2 32.6% 17.5%;
  --color-slate-800: 212.7 26.8% 83.9%;
  --color-slate-900: 210 40% 98%;
}
```

### 2. 语义令牌 (Semantic Tokens)

```css
:root {
  /* 背景色 */
  --background: 0 0% 100%;
  --foreground: 222.2 47.4% 11.2%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 47.4% 11.2%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 47.4% 11.2%;
  
  /* 主色 */
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  
  /* 次要色 */
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  
  /* 功能色 */
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  
  /* 状态色 */
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  
  /* 边框和输入 */
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
  
  /* 圆角 */
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 深色模式 */
.dark {
  --background: 222.2 47.4% 11.2%;
  --foreground: 210 40% 98%;
  --card: 222.2 47.4% 11.2%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --border: 217.2 32.6% 17.5%;
}
```

### 3. 组件令牌 (Component Tokens)

```css
/* 按钮 */
--button-primary-bg: var(--primary);
--button-primary-fg: var(--primary-foreground);
--button-primary-hover: color-mix(in srgb, var(--primary), black 10%);
--button-primary-active: color-mix(in srgb, var(--primary), black 20%);

--button-secondary-bg: var(--secondary);
--button-secondary-fg: var(--secondary-foreground);
--button-secondary-hover: color-mix(in srgb, var(--secondary), black 5%);

--button-ghost-bg: transparent;
--button-ghost-fg: var(--foreground);
--button-ghost-hover: var(--accent);

/* 输入框 */
--input-bg: transparent;
--input-border: var(--border);
--input-ring: var(--ring);
--input-placeholder: var(--muted-foreground);

/* 卡片 */
--card-bg: var(--card);
--card-border: var(--border);
--card-shadow: var(--shadow-md);
--card-radius: var(--radius-lg);
```

---

## 📐 间距与布局系统

### 8px 网格系统

```css
:root {
  /* 间距标尺 (基于 8px) */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
  
  /* 容器宽度 */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1536px;
}
```

### 响应式断点

```css
/* Mobile First */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

---

## 🔤 字体系统

### 字体堆栈

```css
:root {
  /* 无衬线字体 (界面) */
  --font-sans: 
    'Inter',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'Roboto',
    'Helvetica Neue',
    Arial,
    sans-serif;
  
  /* 等宽字体 (代码) */
  --font-mono:
    'JetBrains Mono',
    'Fira Code',
    'SF Mono',
    Consolas,
    monospace;
  
  /* 字体大小标尺 */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  
  /* 字重 */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  
  /* 字间距 */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
}
```

### 中文优化

```css
body {
  font-family: var(--font-sans), 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-feature-settings: "rlig" 1, "calt" 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 代码块 */
code, pre {
  font-family: var(--font-mono), 'Cascadia Code', monospace;
}
```

---

## 🎨 组件设计规范

### 1. 按钮 (Button)

```html
<!-- 主要按钮 -->
<button class="btn btn-primary">
  主要操作
</button>

<!-- 次要按钮 -->
<button class="btn btn-secondary">
  次要操作
</button>

<!-- 幽灵按钮 -->
<button class="btn btn-ghost">
  幽灵按钮
</button>

<!-- 破坏性按钮 -->
<button class="btn btn-destructive">
  删除
</button>

<!-- 带图标按钮 -->
<button class="btn btn-primary btn-icon">
  <i class="ri-add-line"></i>
  新建
</button>

<!-- 加载状态 -->
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  加载中...
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: 1;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  outline: none;
}

.btn:focus-visible {
  box-shadow: 0 0 0 2px var(--background), 0 0 0 4px var(--ring);
}

.btn-primary {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.btn-primary:hover {
  background: color-mix(in srgb, hsl(var(--primary)), black 10%);
}

.btn-secondary {
  background: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
}

.btn-ghost {
  background: transparent;
  color: hsl(var(--foreground));
}

.btn-ghost:hover {
  background: hsl(var(--accent));
}

.btn-destructive {
  background: hsl(var(--destructive));
  color: hsl(var(--destructive-foreground));
}

/* 尺寸变体 */
.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
}

/* 图标按钮 */
.btn-icon {
  padding: var(--space-2);
}
```

### 2. 输入框 (Input)

```html
<div class="form-group">
  <label class="form-label">用户名</label>
  <div class="input-wrapper">
    <span class="input-icon">
      <i class="ri-user-line"></i>
    </span>
    <input 
      type="text" 
      class="input" 
      placeholder="请输入用户名"
    >
  </div>
  <p class="form-hint">支持字母、数字、下划线</p>
</div>

<!-- 错误状态 -->
<div class="form-group has-error">
  <label class="form-label">密码</label>
  <input type="password" class="input input-error" value="123">
  <p class="form-message form-message-error">
    <i class="ri-error-warning-line"></i>
    密码至少 8 位
  </p>
</div>

<!-- 成功状态 -->
<div class="form-group has-success">
  <label class="form-label">邮箱</label>
  <input type="email" class="input input-success" value="test@example.com">
  <p class="form-message form-message-success">
    <i class="ri-checkbox-circle-line"></i>
    格式正确
  </p>
</div>
```

```css
.form-group {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: hsl(var(--foreground));
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: hsl(var(--muted-foreground));
  pointer-events: none;
}

.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  padding-left: var(--space-10); /* 留出图标空间 */
  font-size: var(--text-sm);
  background: transparent;
  border: 1px solid hsl(var(--input));
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
  outline: none;
}

.input:focus {
  border-color: hsl(var(--ring));
  box-shadow: 0 0 0 2px var(--background), 0 0 0 4px hsl(var(--ring) / 0.2);
}

.input::placeholder {
  color: hsl(var(--muted-foreground));
}

.input-error {
  border-color: hsl(var(--destructive));
}

.input-success {
  border-color: hsl(var(--success));
}

.form-hint {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: hsl(var(--muted-foreground));
}

.form-message {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  margin-top: var(--space-2);
  font-size: var(--text-xs);
}

.form-message-error {
  color: hsl(var(--destructive));
}

.form-message-success {
  color: hsl(var(--success));
}
```

### 3. 卡片 (Card)

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">学情概览</h3>
    <p class="card-description">最近 7 天学习数据</p>
  </div>
  <div class="card-content">
    <!-- 内容区 -->
  </div>
  <div class="card-footer">
    <button class="btn btn-sm btn-ghost">查看详情</button>
  </div>
</div>
```

```css
.card {
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid hsl(var(--border));
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: hsl(var(--foreground));
  margin: 0 0 var(--space-1) 0;
}

.card-description {
  font-size: var(--text-sm);
  color: hsl(var(--muted-foreground));
  margin: 0;
}

.card-content {
  padding: var(--space-6);
}

.card-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid hsl(var(--border));
  background: hsl(var(--muted) / 0.3);
}
```

### 4. 表格 (Table)

```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>学生</th>
        <th>课程</th>
        <th>进度</th>
        <th>状态</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <div class="user-cell">
            <div class="avatar">张</div>
            <div class="user-info">
              <div class="user-name">张三</div>
              <div class="user-email">zhang@example.com</div>
            </div>
          </div>
        </td>
        <td>数据结构</td>
        <td>
          <div class="progress-bar">
            <div class="progress-fill" style="width: 75%"></div>
          </div>
          <span class="progress-text">75%</span>
        </td>
        <td>
          <span class="badge badge-success">进行中</span>
        </td>
        <td>
          <div class="action-buttons">
            <button class="btn-icon btn-ghost">
              <i class="ri-eye-line"></i>
            </button>
            <button class="btn-icon btn-ghost">
              <i class="ri-edit-line"></i>
            </button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

```css
.table-container {
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.table th {
  padding: var(--space-3) var(--space-4);
  font-weight: var(--font-medium);
  color: hsl(var(--muted-foreground));
  text-align: left;
  border-bottom: 1px solid hsl(var(--border));
  background: hsl(var(--muted) / 0.3);
}

.table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid hsl(var(--border));
  color: hsl(var(--foreground));
}

.table tbody tr:hover {
  background: hsl(var(--muted) / 0.3);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary) / 0.7));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.progress-bar {
  width: 120px;
  height: 6px;
  background: hsl(var(--muted));
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: hsl(var(--primary));
  border-radius: 999px;
  transition: width 0.3s ease;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
}

.badge-success {
  background: hsl(var(--success) / 0.1);
  color: hsl(var(--success));
}
```

### 5. 对话框 (Dialog/Modal)

```html
<div class="dialog-overlay" id="dialog">
  <div class="dialog">
    <div class="dialog-header">
      <h3 class="dialog-title">确认删除</h3>
      <p class="dialog-description">此操作不可撤销，请谨慎操作。</p>
    </div>
    <div class="dialog-content">
      <!-- 内容 -->
    </div>
    <div class="dialog-footer">
      <button class="btn btn-ghost" onclick="closeDialog()">取消</button>
      <button class="btn btn-destructive">删除</button>
    </div>
  </div>
</div>
```

```css
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
}

.dialog-overlay.open {
  opacity: 1;
  visibility: visible;
}

.dialog {
  background: hsl(var(--background));
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-width: 480px;
  padding: var(--space-6);
  transform: scale(0.95) translateY(10px);
  transition: transform 0.2s ease;
}

.dialog-overlay.open .dialog {
  transform: scale(1) translateY(0);
}

.dialog-header {
  margin-bottom: var(--space-4);
}

.dialog-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: hsl(var(--foreground));
  margin: 0 0 var(--space-1) 0;
}

.dialog-description {
  font-size: var(--text-sm);
  color: hsl(var(--muted-foreground));
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-6);
}
```

### 6. 下拉菜单 (Dropdown)

```html
<div class="dropdown">
  <button class="btn btn-secondary dropdown-trigger">
    更多操作
    <i class="ri-arrow-down-s-line"></i>
  </button>
  <div class="dropdown-menu">
    <a href="#" class="dropdown-item">
      <i class="ri-eye-line"></i>
      查看
    </a>
    <a href="#" class="dropdown-item">
      <i class="ri-edit-line"></i>
      编辑
    </a>
    <div class="dropdown-divider"></div>
    <a href="#" class="dropdown-item dropdown-item-danger">
      <i class="ri-delete-bin-line"></i>
      删除
    </a>
  </div>
</div>
```

```css
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 180px;
  background: hsl(var(--popover));
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--space-2);
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 0.15s ease;
}

.dropdown.open .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: hsl(var(--foreground));
  border-radius: var(--radius-sm);
  text-decoration: none;
  transition: background 0.1s ease;
}

.dropdown-item:hover {
  background: hsl(var(--accent));
}

.dropdown-item-danger {
  color: hsl(var(--destructive));
}

.dropdown-divider {
  height: 1px;
  background: hsl(var(--border));
  margin: var(--space-2) 0;
}
```

---

## 📱 页面布局模板

### 1. 登录页面

```html
<div class="auth-page">
  <div class="auth-container">
    <!-- 左侧品牌区 -->
    <div class="auth-brand">
      <div class="brand-content">
        <div class="brand-logo">
          <i class="ri-graduation-cap-fill"></i>
        </div>
        <h1 class="brand-title">课程助教系统</h1>
        <p class="brand-slogan">Agent 驱动 · 答疑 · 批改 · 出题</p>
        
        <div class="brand-features">
          <div class="feature">
            <i class="ri-robot-2-line"></i>
            <span>AI 智能答疑</span>
          </div>
          <div class="feature">
            <i class="ri-bar-chart-box-line"></i>
            <span>学情分析</span>
          </div>
          <div class="feature">
            <i class="ri-file-list-3-line"></i>
            <span>自动批改</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧表单区 -->
    <div class="auth-form-container">
      <div class="auth-form-card">
        <div class="auth-form-header">
          <h2>欢迎回来</h2>
          <p>请输入账号密码登录</p>
        </div>
        
        <form class="auth-form">
          <!-- 表单内容 -->
        </form>
        
        <div class="auth-footer">
          <p>还没有账号？<a href="/register">立即注册</a></p>
        </div>
      </div>
    </div>
  </div>
</div>
```

```css
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: var(--space-6);
}

.auth-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1000px;
  width: 100%;
  background: hsl(var(--background));
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.auth-brand {
  background: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary) / 0.8));
  padding: var(--space-16);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.brand-content {
  max-width: 320px;
}

.brand-logo {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-bottom: var(--space-6);
}

.brand-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  margin: 0 0 var(--space-2) 0;
}

.brand-slogan {
  font-size: var(--text-sm);
  opacity: 0.9;
  margin-bottom: var(--space-8);
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.feature {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.auth-form-container {
  padding: var(--space-12);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-form-card {
  width: 100%;
  max-width: 360px;
}

.auth-form-header {
  margin-bottom: var(--space-8);
}

.auth-form-header h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: hsl(var(--foreground));
  margin: 0 0 var(--space-2) 0;
}

.auth-form-header p {
  font-size: var(--text-sm);
  color: hsl(var(--muted-foreground));
  margin: 0;
}

.auth-footer {
  margin-top: var(--space-6);
  text-align: center;
  font-size: var(--text-sm);
  color: hsl(var(--muted-foreground));
}

/* 响应式 */
@media (max-width: 768px) {
  .auth-container {
    grid-template-columns: 1fr;
  }
  
  .auth-brand {
    display: none;
  }
}
```

### 2. Dashboard 布局

```html
<div class="dashboard-layout">
  <!-- 顶部导航 -->
  <header class="topbar">
    <div class="topbar-start">
      <button class="btn-icon btn-ghost menu-toggle">
        <i class="ri-menu-line"></i>
      </button>
      <div class="brand">
        <i class="ri-graduation-cap-fill"></i>
        <span>课程助教系统</span>
      </div>
    </div>
    <div class="topbar-end">
      <div class="user-menu">
        <div class="avatar">王</div>
        <span>王老师</span>
        <i class="ri-arrow-down-s-line"></i>
      </div>
    </div>
  </header>
  
  <!-- 侧边栏 -->
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="nav-section-title">教学</div>
        <a href="#" class="nav-item active">
          <i class="ri-dashboard-3-line"></i>
          <span>学情看板</span>
        </a>
        <a href="#" class="nav-item">
          <i class="ri-folder-cloud-line"></i>
          <span>知识库</span>
        </a>
        <a href="#" class="nav-item">
          <i class="ri-checkbox-circle-line"></i>
          <span>作业批改</span>
        </a>
      </div>
    </nav>
  </aside>
  
  <!-- 主内容区 -->
  <main class="main-content">
    <div class="content-header">
      <h1 class="page-title">学情看板</h1>
      <div class="page-actions">
        <button class="btn btn-primary">
          <i class="ri-add-line"></i>
          新建课程
        </button>
      </div>
    </div>
    
    <div class="content-body">
      <!-- 页面内容 -->
    </div>
  </main>
</div>
```

```css
.dashboard-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px 1fr;
  grid-template-rows: 60px 1fr;
}

/* 顶部导航 */
.topbar {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  background: hsl(var(--background));
  border-bottom: 1px solid hsl(var(--border));
  z-index: 40;
}

.topbar-start, .topbar-end {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: hsl(var(--foreground));
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: hsl(var(--muted));
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 0.15s;
}

.user-menu:hover {
  background: hsl(var(--accent));
}

/* 侧边栏 */
.sidebar {
  grid-row: 2 / -1;
  background: hsl(var(--background));
  border-right: 1px solid hsl(var(--border));
  padding: var(--space-4);
  overflow-y: auto;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.nav-section-title {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: hsl(var(--muted-foreground));
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: hsl(var(--muted-foreground));
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all 0.15s;
}

.nav-item:hover {
  background: hsl(var(--muted));
  color: hsl(var(--foreground));
}

.nav-item.active {
  background: hsl(var(--primary) / 0.1);
  color: hsl(var(--primary));
}

.nav-item i {
  font-size: var(--text-lg);
}

/* 主内容区 */
.main-content {
  padding: var(--space-6);
  overflow-y: auto;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: hsl(var(--foreground));
  margin: 0;
}

.page-actions {
  display: flex;
  gap: var(--space-2);
}

.content-body {
  background: hsl(var(--background));
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  min-height: calc(100vh - 200px);
}
```

---

## 📁 输出文件清单

### CSS 文件
- [ ] `app/static/css/design-tokens.css` - 设计令牌（颜色/间距/字体）
- [ ] `app/static/css/components/button.css` - 按钮组件
- [ ] `app/static/css/components/input.css` - 输入框组件
- [ ] `app/static/css/components/card.css` - 卡片组件
- [ ] `app/static/css/components/table.css` - 表格组件
- [ ] `app/static/css/components/dialog.css` - 对话框组件
- [ ] `app/static/css/components/dropdown.css` - 下拉菜单组件
- [ ] `app/static/css/layouts/auth.css` - 认证页面布局
- [ ] `app/static/css/layouts/dashboard.css` - Dashboard 布局
- [ ] `app/static/css/utilities.css` - 工具类

### JavaScript 文件
- [ ] `app/static/js/components/dialog.js` - 对话框交互
- [ ] `app/static/js/components/dropdown.js` - 下拉菜单交互
- [ ] `app/static/js/components/form-validation.js` - 表单验证
- [ ] `app/static/js/utils/theme.js` - 主题切换

### 模板文件
- [ ] `app/templates/components/ui/button.html` - 按钮组件模板
- [ ] `app/templates/components/ui/input.html` - 输入框模板
- [ ] `app/templates/components/ui/card.html` - 卡片模板
- [ ] `app/templates/components/ui/table.html` - 表格模板
- [ ] `app/templates/layouts/auth.html` - 认证布局
- [ ] `app/templates/layouts/dashboard.html` - Dashboard 布局

---

## ✅ 验收标准

### 视觉验收
- [ ] 颜色系统一致（主色/次要色/功能色）
- [ ] 间距统一（8px 网格系统）
- [ ] 圆角一致（sm/md/lg/xl）
- [ ] 阴影层次分明（sm/md/lg/xl）
- [ ] 字体层次清晰（xs/sm/base/lg/xl/2xl）

### 交互验收
- [ ] 所有按钮有 hover/focus/active 状态
- [ ] 输入框有焦点环（4px 蓝色外环）
- [ ] 对话框可 ESC 关闭
- [ ] 下拉菜单可键盘操作
- [ ] 表格支持行 hover

### 可访问性验收
- [ ] 颜色对比度 ≥ 4.5:1（AA 标准）
- [ ] 所有交互元素可键盘访问
- [ ] 焦点可见（2px 蓝色外环）
- [ ] 表单有 label 关联
- [ ] 图标按钮有 aria-label

### 响应式验收
- [ ] 移动端 (< 768px) 单栏布局
- [ ] 平板端 (768px - 1024px) 自适应
- [ ] 桌面端 (> 1024px) 完整布局
- [ ] 触摸设备优化（按钮最小 44px）

### 性能验收
- [ ] CSS 文件大小 < 50KB（gzip 后）
- [ ] 首屏加载 < 2s
- [ ] 动画帧率 > 60fps
- [ ] 无布局抖动（CLS < 0.1）

---

## 🎨 配色方案

### 主色板（基于 shadcn/ui）

```css
:root {
  /* 中性色 */
  --slate-50: 210 40% 98%;
  --slate-100: 210 40% 96.1%;
  --slate-200: 214.3 31.8% 91.4%;
  --slate-300: 212.7 26.8% 83.9%;
  --slate-400: 215 20.2% 65.1%;
  --slate-500: 215.4 16.3% 46.9%;
  --slate-600: 215.3 25% 36.5%;
  --slate-700: 215.3 31% 26.5%;
  --slate-800: 217.2 32.6% 17.5%;
  --slate-900: 222.2 47.4% 11.2%;
  
  /* 品牌色 - 蓝色 */
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  
  /* 功能色 */
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --danger: 0 84% 60%;
  --info: 199 89% 48%;
}
```

---

## 🚀 执行步骤

1. **第 1 步**: 创建设计令牌系统（CSS 变量）
2. **第 2 步**: 实现基础组件（按钮/输入框/卡片）
3. **第 3 步**: 实现复杂组件（表格/对话框/下拉菜单）
4. **第 4 步**: 创建页面布局模板（登录/Dashboard）
5. **第 5 步**: 添加交互动画（过渡/反馈）
6. **第 6 步**: 实现响应式适配
7. **第 7 步**: 可访问性优化
8. **第 8 步**: 性能优化
9. **第 9 步**: 视觉验收
10. **第 10 步**: 文档编写

---

## 📚 参考资源

- **shadcn/ui**: https://ui.shadcn.com
- **Tailwind CSS**: https://tailwindcss.com
- **Radix UI**: https://radix-ui.com
- **Vercel Design**: https://vercel.com/design
- **Linear**: https://linear.app/design

---

**提示词结束** - 直接复制给执行 Agent 使用
