# 注册页面重新设计 - 执行提示词

> 直接复制本提示词给执行 Agent，无需修改

---

## 📸 当前页面诊断

### 截图分析
![当前注册页面](截图显示：简洁但单调的注册表单)

**核心问题**:
1. ❌ **背景过于单调** - 淡紫色渐变缺少视觉层次
2. ❌ **表单布局紧凑** - 输入框间距小，呼吸感不足
3. ❌ **角色选项单一** - 只有"学生"，缺少"教师"选项
4. ❌ **缺少品牌元素** - 没有 Logo、Slogan、课程特色展示
5. ❌ **视觉吸引力弱** - 整体平淡，缺少记忆点
6. ❌ **表单验证反馈不清晰** - 红色感叹号太小

---

## 🎨 设计理念

### 参考风格
- **DeepSeek HARNESS** - 专业、简洁、科技感
- **Notion** - 清晰的信息层次
- **Linear** - 精致的细节处理
- **Stripe** - 优雅的渐变和阴影

### 设计目标
1. ✅ **专业感** - 教育平台的可信度
2. ✅ **科技感** - AI 助教的现代化形象
3. ✅ **易用性** - 清晰的表单引导
4. ✅ **美观度** - 视觉吸引力，愿意分享

---

## 🎨 视觉规范

### 1. 背景设计

**方案 A: 渐变网格背景**
```css
.registration-page {
  background: 
    linear-gradient(135deg, #667eea 0%, #764ba2 100%),
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

**方案 B: 抽象图形背景（推荐）**
```css
.registration-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

.registration-page::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 20s ease-in-out infinite;
}

.registration-page::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 25s ease-in-out infinite reverse;
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

**方案 C: 玻璃态背景**
```css
.registration-page {
  background: 
    linear-gradient(135deg, #667eea 0%, #764ba2 100%),
    url('pattern.svg');
  position: relative;
}

.registration-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}
```

---

### 2. 卡片布局优化

**当前布局**: 单列紧凑表单

**新布局**: 双栏设计（左侧品牌展示 + 右侧表单）

```html
<div class="registration-container">
  <!-- 左侧品牌区 -->
  <div class="brand-panel">
    <div class="brand-content">
      <div class="logo-wrapper">
        <img src="/static/images/logo.svg" alt="Logo" class="logo">
      </div>
      <h1 class="brand-title">AI 课程助教系统</h1>
      <p class="brand-slogan">让学习更高效，让教学更智能</p>
      
      <div class="feature-list">
        <div class="feature-item">
          <div class="feature-icon">🤖</div>
          <div class="feature-content">
            <h4>AI 智能答疑</h4>
            <p>24/7 在线解答学习问题</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📊</div>
          <div class="feature-content">
            <h4>知识图谱</h4>
            <p>可视化知识点关系网络</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📝</div>
          <div class="feature-content">
            <h4>智能批改</h4>
            <p>自动批改作业和试题</p>
          </div>
        </div>
      </div>
      
      <div class="brand-stats">
        <div class="stat-item">
          <span class="stat-number">10+</span>
          <span class="stat-label">精品课程</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">5000+</span>
          <span class="stat-label">活跃学生</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">98%</span>
          <span class="stat-label">好评率</span>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 右侧表单区 -->
  <div class="form-panel">
    <div class="form-card">
      <div class="form-header">
        <h2 class="form-title">创建账号</h2>
        <p class="form-subtitle">加入 AI 助教系统，开启智能学习之旅</p>
      </div>
      
      <form class="registration-form">
        <!-- 表单内容 -->
      </form>
    </div>
  </div>
</div>
```

**CSS 布局**:
```css
.registration-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  background: #f8fafc;
}

.brand-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 60px;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.brand-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,...") repeat;
  opacity: 0.1;
}

.form-panel {
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.form-card {
  width: 100%;
  max-width: 420px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .registration-container {
    grid-template-columns: 1fr;
  }
  
  .brand-panel {
    display: none; /* 移动端隐藏品牌区 */
  }
}
```

---

### 3. 表单组件优化

#### 3.1 输入框样式

**当前**: 简单边框，无焦点状态

**新设计**:
```css
.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  font-size: 15px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: #ffffff;
  transition: all 0.2s ease;
  outline: none;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 
    0 0 0 4px rgba(102, 126, 234, 0.1),
    0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.form-input.success {
  border-color: #10b981;
  background: #f0fdf4;
}

/* 输入框图标 */
.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  pointer-events: none;
  transition: color 0.2s;
}

.input-wrapper:focus-within .input-icon {
  color: #667eea;
}

.form-input.with-icon {
  padding-left: 48px;
}

/* 验证提示 */
.form-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 13px;
  color: #6b7280;
}

.form-hint.error {
  color: #ef4444;
}

.form-hint.success {
  color: #10b981;
}
```

#### 3.2 角色选择器优化

**当前**: 原生下拉框，样式简陋

**新设计**: 卡片式选择器

```html
<div class="role-selector">
  <label class="form-label">选择角色</label>
  <div class="role-options">
    <label class="role-card student">
      <input type="radio" name="role" value="student" checked>
      <div class="role-card-content">
        <div class="role-icon">👨‍🎓</div>
        <div class="role-info">
          <h4>学生</h4>
          <p>选课学习，完成作业</p>
        </div>
        <div class="role-check">✓</div>
      </div>
    </label>
    
    <label class="role-card teacher">
      <input type="radio" name="role" value="teacher">
      <div class="role-card-content">
        <div class="role-icon">👨‍🏫</div>
        <div class="role-info">
          <h4>教师</h4>
          <p>创建课程，管理学生</p>
        </div>
        <div class="role-check">✓</div>
      </div>
    </label>
  </div>
</div>
```

```css
.role-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 8px;
}

.role-card {
  position: relative;
  cursor: pointer;
}

.role-card input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.role-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.role-card:hover .role-card-content {
  border-color: #667eea;
  background: #f5f3ff;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.role-card input:checked + .role-card-content {
  border-color: #667eea;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.role-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.role-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.role-info p {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.role-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  opacity: 0;
  transform: scale(0);
  transition: all 0.2s;
}

.role-card input:checked + .role-card-content .role-check {
  opacity: 1;
  transform: scale(1);
}
```

#### 3.3 密码强度指示器

```html
<div class="form-group">
  <label class="form-label">密码</label>
  <div class="input-wrapper">
    <span class="input-icon">🔒</span>
    <input type="password" class="form-input" id="password" placeholder="至少 8 位，包含字母和数字">
  </div>
  
  <div class="password-strength">
    <div class="strength-bar">
      <div class="strength-fill weak"></div>
    </div>
    <span class="strength-text">密码强度：弱</span>
  </div>
  
  <div class="password-requirements">
    <div class="requirement" data-met="true">✓ 至少 8 个字符</div>
    <div class="requirement" data-met="true">✓ 包含大写字母</div>
    <div class="requirement" data-met="false">✗ 包含小写字母</div>
    <div class="requirement" data-met="false">✗ 包含数字</div>
    <div class="requirement" data-met="false">✗ 包含特殊字符</div>
  </div>
</div>
```

```css
.password-strength {
  margin-top: 12px;
}

.strength-bar {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.strength-fill {
  height: 100%;
  width: 0%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-fill.weak {
  width: 25%;
  background: #ef4444;
}

.strength-fill.fair {
  width: 50%;
  background: #f59e0b;
}

.strength-fill.good {
  width: 75%;
  background: #3b82f6;
}

.strength-fill.strong {
  width: 100%;
  background: #10b981;
}

.password-requirements {
  margin-top: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 13px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  color: #9ca3af;
  transition: color 0.2s;
}

.requirement[data-met="true"] {
  color: #10b981;
}
```

---

### 4. 提交按钮优化

**当前**: 简单蓝色按钮

**新设计**:
```css
.submit-btn {
  width: 100%;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 加载状态 */
.submit-btn.loading {
  color: transparent;
  pointer-events: none;
}

.submit-btn.loading::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  left: 50%;
  top: 50%;
  margin-left: -10px;
  margin-top: -10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 成功状态 */
.submit-btn.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
```

---

### 5. 表单验证反馈

**实时验证**:
```javascript
class RegistrationForm {
  constructor(formElement) {
    this.form = formElement;
    this.fields = {
      username: formElement.querySelector('#username'),
      realName: formElement.querySelector('#realName'),
      password: formElement.querySelector('#password'),
      role: formElement.querySelector('input[name="role"]')
    };
    
    this.initValidation();
  }
  
  initValidation() {
    // 用户名验证
    this.fields.username.addEventListener('blur', () => {
      this.validateUsername();
    });
    
    this.fields.username.addEventListener('input', () => {
      this.validateUsernameLength();
    });
    
    // 密码强度
    this.fields.password.addEventListener('input', () => {
      this.checkPasswordStrength();
    });
  }
  
  validateUsername() {
    const value = this.fields.username.value.trim();
    const errorEl = this.fields.username.parentElement.querySelector('.form-hint');
    
    if (value.length < 3) {
      this.showError(this.fields.username, '用户名至少 3 个字符');
      return false;
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      this.showError(this.fields.username, '只能包含字母、数字和下划线');
      return false;
    }
    
    this.showSuccess(this.fields.username, '用户名可用');
    return true;
  }
  
  checkPasswordStrength() {
    const password = this.fields.password.value;
    const strengthBar = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text');
    const requirements = document.querySelectorAll('.requirement');
    
    let score = 0;
    
    // 检查各项要求
    requirements[0].dataset.met = password.length >= 8;
    requirements[1].dataset.met = /[A-Z]/.test(password);
    requirements[2].dataset.met = /[a-z]/.test(password);
    requirements[3].dataset.met = /[0-9]/.test(password);
    requirements[4].dataset.met = /[!@#$%^&*]/.test(password);
    
    // 计算强度
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[!@#$%^&*]/.test(password)) score++;
    
    // 更新 UI
    const levels = ['weak', 'fair', 'good', 'strong'];
    const labels = ['弱', '一般', '良好', '强'];
    const levelIndex = Math.min(Math.floor(score / 1.25), 3);
    
    strengthBar.className = `strength-fill ${levels[levelIndex]}`;
    strengthText.textContent = `密码强度：${labels[levelIndex]}`;
  }
  
  showError(input, message) {
    input.classList.add('error');
    input.classList.remove('success');
    
    const hint = input.parentElement.querySelector('.form-hint');
    hint.textContent = message;
    hint.className = 'form-hint error';
  }
  
  showSuccess(input, message) {
    input.classList.remove('error');
    input.classList.add('success');
    
    const hint = input.parentElement.querySelector('.form-hint');
    hint.textContent = message;
    hint.className = 'form-hint success';
  }
}
```

---

### 6. 品牌展示区（左侧面板）

```html
<div class="brand-panel">
  <div class="brand-content">
    <!-- Logo -->
    <div class="logo-wrapper">
      <div class="logo-icon">
        <svg viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="20" fill="white" fill-opacity="0.2"/>
          <path d="M24 14L28 20L24 26L20 20L24 14Z" fill="white"/>
          <circle cx="24" cy="30" r="4" fill="white"/>
        </svg>
      </div>
      <h1 class="brand-title">AI 课程助教系统</h1>
    </div>
    
    <!-- Slogan -->
    <p class="brand-slogan">
      让学习更高效，让教学更智能
      <br>
      <span class="slogan-en">Make Learning Efficient, Make Teaching Intelligent</span>
    </p>
    
    <!-- 功能特色 -->
    <div class="feature-list">
      <div class="feature-item">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" fill="white" fill-opacity="0.2"/>
            <path d="M16 10L18 14L16 18L14 14L16 10Z" fill="white"/>
          </svg>
        </div>
        <div class="feature-content">
          <h4>AI 智能答疑</h4>
          <p>24/7 在线解答学习问题，平均响应时间 < 1 秒</p>
        </div>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" fill="white" fill-opacity="0.2"/>
            <path d="M10 16L14 20L22 12" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="feature-content">
          <h4>知识图谱</h4>
          <p>可视化知识点关系网络，建立系统性认知</p>
        </div>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" fill="white" fill-opacity="0.2"/>
            <path d="M12 16L16 20L20 12" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="feature-content">
          <h4>智能批改</h4>
          <p>自动批改作业和试题，即时反馈学习情况</p>
        </div>
      </div>
    </div>
    
    <!-- 数据统计 -->
    <div class="brand-stats">
      <div class="stat-item">
        <span class="stat-number">10+</span>
        <span class="stat-label">精品课程</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">5000+</span>
        <span class="stat-label">活跃学生</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">98%</span>
        <span class="stat-label">好评率</span>
      </div>
    </div>
    
    <!-- 用户评价 -->
    <div class="testimonial">
      <div class="testimonial-content">
        <p class="testimonial-text">"AI 助教帮我快速理解了数据结构的核心概念，知识图谱特别有用！"</p>
        <div class="testimonial-author">
          <div class="author-avatar">张</div>
          <div class="author-info">
            <span class="author-name">张同学</span>
            <span class="author-school">计算机科学与技术专业</span>
          </div>
          <div class="testimonial-rating">★★★★★</div>
        </div>
      </div>
    </div>
  </div>
</div>
```

```css
.brand-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  color: #ffffff;
}

.brand-content {
  max-width: 480px;
  position: relative;
  z-index: 1;
}

.logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  text-align: center;
}

.brand-slogan {
  font-size: 16px;
  text-align: center;
  opacity: 0.9;
  margin-bottom: 48px;
  line-height: 1.6;
}

.slogan-en {
  font-size: 14px;
  opacity: 0.7;
  display: block;
  margin-top: 8px;
}

.feature-list {
  margin-bottom: 48px;
}

.feature-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s;
}

.feature-item:hover {
  transform: translateX(8px);
}

.feature-icon {
  flex-shrink: 0;
}

.feature-content h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.feature-content p {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
}

.brand-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 48px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
}

.testimonial {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.testimonial-text {
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 16px 0;
  font-style: italic;
  opacity: 0.9;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.author-info {
  flex: 1;
}

.author-name {
  display: block;
  font-weight: 600;
  font-size: 14px;
}

.author-school {
  display: block;
  font-size: 12px;
  opacity: 0.7;
}

.testimonial-rating {
  color: #fbbf24;
  font-size: 14px;
}
```

---

## 📁 输出文件清单

### 样式文件
- [ ] `app/static/css/auth/registration.css` - 注册页面主样式
- [ ] `app/static/css/auth/components.css` - 表单组件样式
- [ ] `app/static/css/auth/role-selector.css` - 角色选择器样式
- [ ] `app/static/css/auth/animations.css` - 动画效果

### JavaScript 文件
- [ ] `app/static/js/auth/registration.js` - 表单验证逻辑
- [ ] `app/static/js/auth/password-strength.js` - 密码强度检测
- [ ] `app/static/js/auth/form-validation.js` - 通用表单验证

### 模板文件
- [ ] `app/templates/auth/register.html` - 注册页面模板（双栏布局）
- [ ] `app/templates/auth/components/role_selector.html` - 角色选择组件
- [ ] `app/templates/auth/components/password_strength.html` - 密码强度组件

### 资源文件
- [ ] `app/static/images/auth/logo.svg` - Logo 图片
- [ ] `app/static/images/auth/pattern.svg` - 背景纹理
- [ ] `app/static/images/auth/icons/` - 功能图标集

---

## ✅ 验收标准

### 视觉验收
- [ ] 双栏布局（左侧品牌 + 右侧表单）
- [ ] 渐变背景（紫色系）
- [ ] 卡片式角色选择器
- [ ] 密码强度指示器（4 级）
- [ ] 输入框焦点状态（阴影 + 颜色）
- [ ] 按钮加载动画

### 功能验收
- [ ] 用户名实时验证（长度 + 格式）
- [ ] 密码强度实时检测
- [ ] 角色选择（学生/教师）
- [ ] 表单错误提示清晰
- [ ] 提交成功跳转

### 响应式验收
- [ ] 桌面端：双栏布局（> 1024px）
- [ ] 平板端：单栏布局（768px - 1024px）
- [ ] 移动端：紧凑布局（< 768px）

### 性能验收
- [ ] 首屏加载 < 2s
- [ ] 表单验证响应 < 100ms
- [ ] 动画帧率 > 60fps

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
  
  /* 背景 */
  --bg-canvas: #f8fafc;
  --bg-surface: #ffffff;
  --bg-overlay: rgba(0, 0, 0, 0.5);
}
```

---

## 🚀 执行步骤

1. **第 1 步**: 创建双栏布局结构（品牌区 + 表单区）
2. **第 2 步**: 实现渐变背景和动画效果
3. **第 3 步**: 优化表单组件样式（输入框、按钮）
4. **第 4 步**: 实现角色选择器（卡片式）
5. **第 5 步**: 添加密码强度指示器
6. **第 6 步**: 实现表单验证逻辑
7. **第 7 步**: 添加响应式适配
8. **第 8 步**: 视觉验收 + 细节调整

---

**提示词结束** - 直接复制给执行 Agent 使用
