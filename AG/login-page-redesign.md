# 登录页面重新设计 - 执行提示词

> 直接复制本提示词给执行 Agent，无需修改

---

## 📸 当前页面诊断

### 截图分析
![当前登录页面](截图显示：简洁但单调的登录表单)

**核心问题**:
1. ❌ **背景过于单调** - 淡蓝色渐变缺少层次感和记忆点
2. ❌ **卡片设计平淡** - 纯白卡片，缺少品牌识别度
3. ❌ **输入框样式基础** - 缺少焦点状态和交互动画
4. ❌ **演示账号区域简陋** - 虚线框 + 灰色背景，视觉廉价
5. ❌ **缺少视觉吸引力** - 整体平淡，无差异化
6. ❌ **Logo 设计简单** - 学士帽图标过于通用

---

## 🎨 设计理念

### 参考风格
- **DeepSeek HARNESS** - 科技感、专业、简洁
- **Vercel** - 极简主义、精致细节
- **Raycast** - 玻璃态、渐变、阴影
- **Linear** - 优雅动画、精准间距

### 设计目标
1. ✅ **专业感** - 教育平台的可信度
2. ✅ **科技感** - AI 助教的现代化形象
3. ✅ **视觉层次** - 清晰的焦点引导
4. ✅ **品牌识别** - 独特的视觉记忆点
5. ✅ **交互反馈** - 流畅的动画过渡

---

## 🎨 视觉规范

### 1. 背景设计升级

**方案 A: 动态网格背景（推荐）**
```css
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  position: relative;
  overflow: hidden;
}

/* 网格层 */
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(99, 102, 241, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.1) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black 20%, transparent 80%);
}

/* 渐变光晕层 */
.login-page::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -20%;
  width: 150%;
  height: 150%;
  background: radial-gradient(ellipse at 50% 50%, 
    rgba(99, 102, 241, 0.15) 0%, 
    transparent 50%);
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 浮动光斑 */
.login-page .orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #667eea;
  top: 10%;
  right: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #764ba2;
  bottom: 10%;
  left: 10%;
  animation-delay: -5s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: #06b6d4;
  top: 50%;
  left: 50%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}
```

**方案 B: 深色渐变背景**
```css
.login-page {
  background: 
    linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
  min-height: 100vh;
  position: relative;
}

/* 添加噪点纹理 */
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,...") repeat;
  opacity: 0.05;
  mix-blend-mode: overlay;
}
```

**方案 C: 玻璃态背景（浅色模式）**
```css
.login-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

/* 抽象形状 */
.login-page::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: float 15s ease-in-out infinite;
}

.login-page::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: -10%;
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.25;
  animation: float 20s ease-in-out infinite reverse;
}
```

---

### 2. 登录卡片优化

**当前**: 简单圆角白卡片

**新设计**: 玻璃态 + 分层阴影

```html
<div class="login-card">
  <!-- 玻璃态背景 -->
  <div class="glass-effect"></div>
  
  <!-- 内容区 -->
  <div class="card-content">
    <!-- Logo 区 -->
    <div class="logo-section">
      <div class="logo-wrapper">
        <div class="logo-gradient"></div>
        <svg class="logo-icon" viewBox="0 0 48 48">
          <!-- AI 助手图标 -->
        </svg>
      </div>
      <h1 class="brand-title">课程助教系统</h1>
      <p class="brand-subtitle">Agent 驱动 · 答疑 · 批改 · 出题</p>
    </div>
    
    <!-- 表单区 -->
    <form class="login-form">
      <!-- 输入框 -->
    </form>
    
    <!-- 演示账号 -->
    <div class="demo-accounts">
      <!-- 优化后的设计 -->
    </div>
  </div>
</div>
```

```css
.login-card {
  position: relative;
  width: 100%;
  max-width: 440px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

/* 深色模式变体 */
.login-card.dark {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05);
}

/* 玻璃态高光 */
.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.8),
    transparent
  );
}
```

---

### 3. Logo 区域优化

**当前**: 简单学士帽图标 + 文字

**新设计**: 动态渐变 Logo + 品牌动画

```html
<div class="logo-section">
  <div class="logo-wrapper">
    <div class="logo-bg-gradient"></div>
    <div class="logo-icon-wrapper">
      <svg class="logo-icon" viewBox="0 0 48 48" fill="none">
        <!-- AI 助手图标 - 抽象大脑 + 学士帽组合 -->
        <defs>
          <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea"/>
            <stop offset="50%" style="stop-color:#764ba2"/>
            <stop offset="100%" style="stop-color:#06b6d4"/>
          </linearGradient>
        </defs>
        
        <!-- 外环 -->
        <circle cx="24" cy="24" r="20" stroke="url(#logoGradient)" stroke-width="2" fill="none"/>
        
        <!-- 学士帽 -->
        <path d="M24 14L30 18L24 22L18 18L24 14Z" fill="url(#logoGradient)"/>
        <rect x="20" y="22" width="8" height="2" fill="url(#logoGradient)"/>
        
        <!-- AI 节点 -->
        <circle cx="24" cy="30" r="3" fill="url(#logoGradient)"/>
        <circle cx="18" cy="34" r="2" fill="url(#logoGradient)" opacity="0.6"/>
        <circle cx="30" cy="34" r="2" fill="url(#logoGradient)" opacity="0.6"/>
        
        <!-- 连接线 -->
        <path d="M24 30L18 34M24 30L30 34" stroke="url(#logoGradient)" stroke-width="1.5" opacity="0.6"/>
      </svg>
      
      <!-- 发光效果 -->
      <div class="logo-glow"></div>
    </div>
    
    <!-- 脉冲动画 -->
    <div class="logo-pulse-ring"></div>
  </div>
  
  <h1 class="brand-title">
    <span class="title-gradient">课程助教系统</span>
  </h1>
  <p class="brand-subtitle">
    <span class="subtitle-item">🤖 Agent 驱动</span>
    <span class="subtitle-dot">·</span>
    <span class="subtitle-item">💬 智能答疑</span>
    <span class="subtitle-dot">·</span>
    <span class="subtitle-item">📝 自动批改</span>
    <span class="subtitle-dot">·</span>
    <span class="subtitle-item">🎯 精准出题</span>
  </p>
</div>
```

```css
.logo-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.logo-bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  transform: rotate(12deg);
  filter: blur(20px);
  opacity: 0.3;
  animation: pulse 3s ease-in-out infinite;
}

.logo-icon-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 24px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.logo-icon {
  width: 48px;
  height: 48px;
  position: relative;
  z-index: 1;
}

.logo-glow {
  position: absolute;
  inset: -10px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
  border-radius: 24px;
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes pulse {
  0%, 100% {
    transform: rotate(12deg) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: rotate(12deg) scale(1.1);
    opacity: 0.5;
  }
}

@keyframes glow {
  from {
    opacity: 0.3;
    transform: scale(1);
  }
  to {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
}

.title-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 13px;
  color: #6b7280;
  text-align: center;
  margin-bottom: 32px;
}

.subtitle-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.subtitle-dot {
  color: #d1d5db;
  margin: 0 4px;
}
```

---

### 4. 输入框优化

**当前**: 简单边框 + 浅蓝背景

**新设计**: 悬浮标签 + 图标动画 + 焦点效果

```html
<div class="form-group">
  <label class="input-label" for="username">
    <span class="label-icon">👤</span>
    用户名
  </label>
  <div class="input-wrapper">
    <span class="input-icon">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 10a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0 2c-4.418 0-8 2.239-8 5v1h16v-1c0-2.761-3.582-5-8-5z" fill="currentColor"/>
      </svg>
    </span>
    <input 
      type="text" 
      id="username" 
      class="form-input" 
      placeholder="请输入用户名"
      autocomplete="username"
    >
    <div class="input-border"></div>
  </div>
  <div class="input-hint">
    <span class="hint-icon">ℹ️</span>
    <span class="hint-text">使用注册时的用户名或邮箱</span>
  </div>
</div>

<div class="form-group">
  <label class="input-label" for="password">
    <span class="label-icon">🔒</span>
    密码
  </label>
  <div class="input-wrapper">
    <span class="input-icon">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <rect x="3" y="9" width="14" height="8" rx="2" stroke="currentColor" stroke-width="2"/>
        <path d="M7 9V6a3 3 0 1 1 6 0v3" stroke="currentColor" stroke-width="2"/>
      </svg>
    </span>
    <input 
      type="password" 
      id="password" 
      class="form-input" 
      placeholder="请输入密码"
      autocomplete="current-password"
    >
    <button type="button" class="password-toggle" aria-label="切换密码显示">
      <svg class="eye-open" width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" fill="currentColor"/>
        <path d="M10 4C5 4 2 10 2 10s3 6 8 6 8-6 8-6-3-6-8-6z" stroke="currentColor" stroke-width="2"/>
      </svg>
      <svg class="eye-closed" width="20" height="20" viewBox="0 0 20 20" fill="none" style="display:none">
        <path d="M3 3l14 14" stroke="currentColor" stroke-width="2"/>
        <path d="M10 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" fill="currentColor"/>
        <path d="M17.071 14.929C15.536 16.464 13.268 18 10 18c-5 0-8-6-8-6a14.49 14.49 0 0 1 2.686-3.618" stroke="currentColor" stroke-width="2"/>
        <path d="M2.929 2.929c1.535-1.535 3.803-3.071 7.071-3.071 5 0 8 6 8 6a14.49 14.49 0 0 1-2.686 3.618" stroke="currentColor" stroke-width="2"/>
      </svg>
    </button>
    <div class="input-border"></div>
  </div>
</div>
```

```css
.form-group {
  margin-bottom: 24px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
  transition: color 0.2s;
}

.label-icon {
  font-size: 16px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  color: #9ca3af;
  transition: color 0.2s;
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  font-size: 15px;
  color: #1f2937;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.2s ease;
  outline: none;
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-input:focus {
  background: #ffffff;
  border-color: #667eea;
  box-shadow: 
    0 0 0 4px rgba(102, 126, 234, 0.1),
    0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.form-input:focus + .input-border,
.input-wrapper:focus-within .input-icon {
  color: #667eea;
}

.input-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  border-radius: 2px;
}

.input-wrapper:focus-within .input-border {
  transform: scaleX(1);
}

.password-toggle {
  position: absolute;
  right: 12px;
  padding: 4px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  color: #6b7280;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

.hint-icon {
  font-size: 12px;
}
```

---

### 5. 登录按钮优化

**当前**: 简单渐变按钮

**新设计**: 多层效果 + 加载动画 + 悬浮粒子

```html
<button type="submit" class="login-btn">
  <span class="btn-content">
    <span class="btn-text">登 录</span>
    <span class="btn-loading">
      <svg class="spinner" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="31.4 31.4" stroke-linecap="round">
          <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
        </circle>
      </svg>
      <span>登录中...</span>
    </span>
  </span>
  <span class="btn-shine"></span>
  <span class="btn-particles"></span>
</button>
```

```css
.login-btn {
  position: relative;
  width: 100%;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 14px rgba(102, 126, 234, 0.4),
    0 1px 2px rgba(0, 0, 0, 0.1);
}

.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 24px rgba(102, 126, 234, 0.5),
    0 1px 2px rgba(0, 0, 0, 0.1);
}

.login-btn:hover::before {
  opacity: 1;
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 
    0 2px 8px rgba(102, 126, 234, 0.4),
    0 1px 1px rgba(0, 0, 0, 0.1);
}

/* 光泽扫过动画 */
.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: left 0.5s;
}

.login-btn:hover .btn-shine {
  left: 100%;
}

/* 粒子效果 */
.btn-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.btn-particles::before,
.btn-particles::after {
  content: '';
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: particle 2s ease-in-out infinite;
}

.btn-particles::before {
  left: 20%;
  top: 50%;
  animation-delay: 0s;
}

.btn-particles::after {
  left: 80%;
  top: 50%;
  animation-delay: -1s;
}

@keyframes particle {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  50% {
    transform: translateY(-20px) scale(1.5);
    opacity: 1;
  }
}

/* 加载状态 */
.login-btn.loading .btn-text {
  display: none;
}

.login-btn.loading .btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login-btn.loading {
  pointer-events: none;
}

.btn-content,
.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-loading {
  display: none;
}

.spinner circle {
  animation: spinner 0.8s linear infinite;
}

@keyframes spinner {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 成功状态 */
.login-btn.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
}
```

---

### 6. 演示账号区域优化

**当前**: 虚线框 + 灰色背景

**新设计**: 卡片式 + 一键复制 + 角色标签

```html
<div class="demo-accounts">
  <div class="demo-header">
    <span class="demo-icon">🎯</span>
    <span class="demo-title">演示账号</span>
    <span class="demo-badge">快速体验</span>
  </div>
  
  <div class="demo-note">
    <span class="note-label">密码均为</span>
    <code class="password-code">123456</code>
  </div>
  
  <div class="demo-list">
    <div class="demo-item" data-username="student" data-password="123456">
      <div class="demo-avatar student">
        <span>👨‍🎓</span>
      </div>
      <div class="demo-info">
        <div class="demo-username">
          <code>student</code>
          <button class="copy-btn" title="复制用户名">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="4" y="4" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M6 6H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h5a2 2 0 0 0 2-2v-1" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>
        </div>
        <div class="demo-role student">学生</div>
      </div>
      <button class="quick-login-btn" title="一键登录">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M4 10a6 6 0 1 1 12 0 6 6 0 0 1-12 0z" stroke="currentColor" stroke-width="2"/>
          <path d="M10 7v3l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    
    <div class="demo-item" data-username="teacher" data-password="123456">
      <div class="demo-avatar teacher">
        <span>👨‍🏫</span>
      </div>
      <div class="demo-info">
        <div class="demo-username">
          <code>teacher</code>
          <button class="copy-btn" title="复制用户名">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="4" y="4" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M6 6H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h5a2 2 0 0 0 2-2v-1" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>
        </div>
        <div class="demo-role teacher">教师</div>
      </div>
      <button class="quick-login-btn" title="一键登录">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M4 10a6 6 0 1 1 12 0 6 6 0 0 1-12 0z" stroke="currentColor" stroke-width="2"/>
          <path d="M10 7v3l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    
    <div class="demo-item" data-username="admin" data-password="123456">
      <div class="demo-avatar admin">
        <span>👤</span>
      </div>
      <div class="demo-info">
        <div class="demo-username">
          <code>admin</code>
          <button class="copy-btn" title="复制用户名">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="4" y="4" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M6 6H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h5a2 2 0 0 0 2-2v-1" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>
        </div>
        <div class="demo-role admin">管理员</div>
      </div>
      <button class="quick-login-btn" title="一键登录">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M4 10a6 6 0 1 1 12 0 6 6 0 0 1-12 0z" stroke="currentColor" stroke-width="2"/>
          <path d="M10 7v3l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </div>
  
  <!-- 复制成功提示 -->
  <div class="toast" id="copy-toast">
    <span class="toast-icon">✓</span>
    <span class="toast-message">已复制用户名</span>
  </div>
</div>
```

```css
.demo-accounts {
  margin-top: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
}

.demo-accounts::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2, #06b6d4);
}

.demo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.demo-icon {
  font-size: 20px;
}

.demo-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.demo-badge {
  padding: 2px 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.demo-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #6b7280;
}

.note-label {
  color: #9ca3af;
}

.password-code {
  padding: 4px 10px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.demo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.demo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  cursor: pointer;
}

.demo-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateX(4px);
}

.demo-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.demo-avatar.student {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.demo-avatar.teacher {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.demo-avatar.admin {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
}

.demo-info {
  flex: 1;
  min-width: 0;
}

.demo-username {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.demo-username code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.copy-btn {
  padding: 4px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-btn:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.demo-role {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.demo-role.student {
  background: #dbeafe;
  color: #1e40af;
}

.demo-role.teacher {
  background: #fef3c7;
  color: #92400e;
}

.demo-role.admin {
  background: #fce7f3;
  color: #9d174d;
}

.quick-login-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.quick-login-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Toast 提示 */
.toast {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #1f2937;
  color: white;
  font-size: 13px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.toast.show {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

.toast-icon {
  width: 20px;
  height: 20px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}
```

---

### 7. 页脚链接优化

**当前**: 简单文字链接

**新设计**: 分隔线 + 多链接

```html
<div class="form-footer">
  <div class="footer-divider">
    <span class="divider-line"></span>
    <span class="divider-text">还没有账号？</span>
    <span class="divider-line"></span>
  </div>
  
  <div class="footer-links">
    <a href="/register" class="footer-link primary">
      <span class="link-icon">✨</span>
      立即注册
    </a>
    <a href="/forgot-password" class="footer-link">
      <span class="link-icon">🔑</span>
      忘记密码？
    </a>
    <a href="/help" class="footer-link">
      <span class="link-icon">❓</span>
      帮助中心
    </a>
  </div>
</div>
```

```css
.form-footer {
  margin-top: 32px;
}

.footer-divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
}

.divider-text {
  font-size: 13px;
  color: #9ca3af;
  white-space: nowrap;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #6b7280;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.footer-link:hover {
  background: #f3f4f6;
  color: #667eea;
}

.footer-link.primary {
  color: #667eea;
  font-weight: 500;
}

.link-icon {
  font-size: 16px;
}
```

---

## 📁 输出文件清单

### 样式文件
- [ ] `app/static/css/auth/login.css` - 登录页面主样式
- [ ] `app/static/css/auth/background.css` - 背景动画样式
- [ ] `app/static/css/auth/components.css` - 表单组件样式
- [ ] `app/static/css/auth/demo-accounts.css` - 演示账号样式
- [ ] `app/static/css/auth/animations.css` - 交互动画

### JavaScript 文件
- [ ] `app/static/js/auth/login.js` - 登录逻辑
- [ ] `app/static/js/auth/password-toggle.js` - 密码显示切换
- [ ] `app/static/js/auth/demo-accounts.js` - 演示账号交互
- [ ] `app/static/js/auth/form-validation.js` - 表单验证

### 模板文件
- [ ] `app/templates/auth/login.html` - 登录页面模板
- [ ] `app/templates/auth/components/demo_accounts.html` - 演示账号组件
- [ ] `app/templates/auth/components/footer_links.html` - 页脚链接组件

### 资源文件
- [ ] `app/static/images/auth/logo.svg` - 新版 Logo
- [ ] `app/static/images/auth/background-pattern.svg` - 背景纹理
- [ ] `app/static/images/auth/icons/` - 图标集

---

## ✅ 验收标准

### 视觉效果
- [ ] 动态网格/渐变背景
- [ ] 玻璃态卡片效果
- [ ] Logo 渐变 + 发光动画
- [ ] 输入框焦点状态（阴影 + 底边）
- [ ] 按钮悬浮粒子效果
- [ ] 演示账号卡片式布局

### 交互效果
- [ ] 输入框聚焦动画
- [ ] 密码显示/隐藏切换
- [ ] 一键复制用户名
- [ ] 快速登录按钮
- [ ] 加载状态动画
- [ ] Toast 提示

### 响应式
- [ ] 桌面端完整布局（> 1024px）
- [ ] 平板端适配（768px - 1024px）
- [ ] 移动端紧凑布局（< 768px）

### 性能
- [ ] 首屏加载 < 2s
- [ ] 动画帧率 > 60fps
- [ ] 无布局抖动

---

## 🎨 配色方案

```css
:root {
  /* 主色 - 紫色渐变 */
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --primary-500: #667eea;
  --primary-600: #5568d3;
  --primary-700: #4552b8;
  
  /* 辅助色 */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #3b82f6;
  --cyan: #06b6d4;
  
  /* 中性色 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 深色模式 */
  --dark-bg: #0f172a;
  --dark-surface: #1e293b;
  --dark-border: #334155;
}
```

---

## 🚀 执行步骤

1. **第 1 步**: 创建动态背景（网格 + 浮动光斑）
2. **第 2 步**: 设计玻璃态登录卡片
3. **第 3 步**: 优化 Logo 区域（渐变 + 动画）
4. **第 4 步**: 重构输入框样式（焦点效果）
5. **第 5 步**: 优化登录按钮（粒子 + 光泽）
6. **第 6 步**: 重新设计演示账号区域
7. **第 7 步**: 添加页脚链接
8. **第 8 步**: 实现交互动画
9. **第 9 步**: 响应式适配
10. **第 10 步**: 视觉验收

---

**提示词结束** - 直接复制给执行 Agent 使用
