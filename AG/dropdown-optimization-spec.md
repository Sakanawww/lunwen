# 下拉框组件优化规范

> 统一所有下拉框的视觉与交互体验  
> 适用页面：学情看板 / 智能答疑 / 作业批改 / 试题生成 / 知识库

---

## 📋 一、下拉框类型总览

| 类型 | 使用场景 | 优先级 | 特殊要求 |
|------|----------|--------|----------|
| 课程选择 | 看板/答疑/批改页 | P0 | 支持搜索 + 图标 |
| 时间范围 | 看板筛选 | P0 | 快捷选项 + 自定义 |
| 类型筛选 | 表格筛选 | P1 | 多选支持 |
| 分页大小 | 表格底部 | P2 | 简洁数字 |
| 用户菜单 | 导航栏 | P1 | 头像 + 下拉 |

---

## 🎨 二、视觉设计规范

### 2.1 标准下拉框（课程/时间选择）

```css
/* 容器 */
.dropdown-container {
  position: relative;
  display: inline-block;
  min-width: 180px;
}

/* 触发器 */
.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  
  height: 40px;
  padding: 0 12px;
  
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 8px;
  
  cursor: pointer;
  transition: all 0.2s ease;
  
  /* 悬停状态 */
}
.dropdown-trigger:hover {
  border-color: #5B7FFF;
  background: #F8FAFF;
}
.dropdown-trigger:focus-within {
  border-color: #5B7FFF;
  box-shadow: 0 0 0 3px rgba(91, 127, 255, 0.1);
}

/* 下拉箭头 */
.dropdown-arrow {
  width: 16px;
  height: 16px;
  color: #99AAB5;
  transition: transform 0.2s ease;
}
.dropdown-trigger.active .dropdown-arrow {
  transform: rotate(180deg);
}

/* 下拉面板 */
.dropdown-panel {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  
  min-width: 200px;
  max-height: 280px;
  overflow-y: auto;
  
  background: #FFFFFF;
  border: 1px solid #E8ECF0;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
  transition: all 0.2s ease;
  z-index: 1000;
}
.dropdown-panel.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

/* 选项列表 */
.dropdown-list {
  padding: 6px;
  list-style: none;
  margin: 0;
}

/* 单个选项 */
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  
  height: 40px;
  padding: 0 12px;
  
  border-radius: 6px;
  cursor: pointer;
  
  font-size: 14px;
  color: #1A1A1A;
  transition: background 0.15s ease;
}
.dropdown-item:hover {
  background: #F0F2F5;
}
.dropdown-item.selected {
  background: rgba(91, 127, 255, 0.1);
  color: #5B7FFF;
  font-weight: 500;
}
.dropdown-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 选项图标 */
.dropdown-item-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #99AAB5;
}
.dropdown-item.selected .dropdown-item-icon {
  color: #5B7FFF;
}

/* 选中标记 */
.dropdown-item-check {
  margin-left: auto;
  width: 16px;
  height: 16px;
  color: #5B7FFF;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.2s ease;
}
.dropdown-item.selected .dropdown-item-check {
  opacity: 1;
  transform: scale(1);
}

/* 分割线 */
.dropdown-divider {
  height: 1px;
  margin: 6px 0;
  background: #E8ECF0;
}

/* 空状态 */
.dropdown-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  height: 80px;
  padding: 12px;
  
  color: #99AAB5;
  font-size: 14px;
}
```

---

### 2.2 带搜索的下拉框（课程选择）

```html
<div class="dropdown-container dropdown-searchable">
  <div class="dropdown-trigger" tabindex="0">
    <div class="dropdown-trigger-content">
      <i class="ri-book-open-line dropdown-trigger-icon"></i>
      <span class="dropdown-trigger-label">数据结构</span>
    </div>
    <i class="ri-arrow-down-s-line dropdown-arrow"></i>
  </div>
  
  <div class="dropdown-panel">
    <!-- 搜索框 -->
    <div class="dropdown-search">
      <i class="ri-search-line"></i>
      <input type="text" placeholder="搜索课程..." />
    </div>
    
    <!-- 选项列表 -->
    <ul class="dropdown-list">
      <li class="dropdown-item selected" data-value="1">
        <i class="ri-book-open-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">数据结构</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="2">
        <i class="ri-calculator-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">算法分析</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="3">
        <i class="ri-database-2-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">数据库原理</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
    </ul>
    
    <!-- 空状态 -->
    <div class="dropdown-empty" style="display: none;">
      <i class="ri-inbox-line"></i>
      <span>没有找到匹配的课程</span>
    </div>
  </div>
</div>
```

**搜索功能 JS：**

```javascript
function initSearchableDropdown(container) {
  const trigger = container.querySelector('.dropdown-trigger');
  const panel = container.querySelector('.dropdown-panel');
  const searchInput = container.querySelector('.dropdown-search input');
  const items = container.querySelectorAll('.dropdown-item');
  
  // 点击触发器
  trigger.addEventListener('click', () => {
    const isOpen = panel.classList.contains('show');
    closeAllDropdowns();
    if (!isOpen) {
      panel.classList.add('show');
      trigger.classList.add('active');
      searchInput.focus();
    }
  });
  
  // 搜索过滤
  searchInput.addEventListener('input', (e) => {
    const keyword = e.target.value.toLowerCase().trim();
    
    items.forEach(item => {
      const label = item.querySelector('.dropdown-item-label').textContent;
      const match = label.toLowerCase().includes(keyword);
      item.style.display = match ? '' : 'none';
    });
    
    // 更新空状态
    const visibleItems = Array.from(items).filter(i => i.style.display !== 'none');
    const emptyState = container.querySelector('.dropdown-empty');
    emptyState.style.display = visibleItems.length === 0 ? 'flex' : 'none';
  });
  
  // 选择选项
  items.forEach(item => {
    item.addEventListener('click', () => {
      selectDropdownItem(container, item);
    });
  });
  
  // 点击外部关闭
  document.addEventListener('click', (e) => {
    if (!container.contains(e.target)) {
      panel.classList.remove('show');
      trigger.classList.remove('active');
    }
  });
}

function selectDropdownItem(container, selectedItem) {
  const items = container.querySelectorAll('.dropdown-item');
  items.forEach(item => item.classList.remove('selected'));
  selectedItem.classList.add('selected');
  
  const label = selectedItem.querySelector('.dropdown-item-label').textContent;
  const icon = selectedItem.querySelector('.dropdown-item-icon').outerHTML;
  
  const triggerLabel = container.querySelector('.dropdown-trigger-label');
  const triggerIcon = container.querySelector('.dropdown-trigger-icon');
  
  triggerLabel.textContent = label;
  triggerIcon.outerHTML = icon;
  
  // 触发自定义事件
  container.dispatchEvent(new CustomEvent('dropdown-change', {
    detail: {
      value: selectedItem.dataset.value,
      label: label
    }
  }));
  
  // 关闭面板
  const panel = container.querySelector('.dropdown-panel');
  const trigger = container.querySelector('.dropdown-trigger');
  panel.classList.remove('show');
  trigger.classList.remove('active');
}
```

---

### 2.3 时间范围选择器

```html
<div class="dropdown-container">
  <div class="dropdown-trigger" tabindex="0">
    <div class="dropdown-trigger-content">
      <i class="ri-time-line dropdown-trigger-icon"></i>
      <span class="dropdown-trigger-label">最近 30 天</span>
    </div>
    <i class="ri-arrow-down-s-line dropdown-arrow"></i>
  </div>
  
  <div class="dropdown-panel">
    <div class="dropdown-section">
      <div class="dropdown-section-title">快捷选项</div>
      <ul class="dropdown-list">
        <li class="dropdown-item" data-value="7">
          <i class="ri-calendar-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">最近 7 天</span>
          <i class="ri-check-line dropdown-item-check"></i>
        </li>
        <li class="dropdown-item selected" data-value="30">
          <i class="ri-calendar-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">最近 30 天</span>
          <i class="ri-check-line dropdown-item-check"></i>
        </li>
        <li class="dropdown-item" data-value="90">
          <i class="ri-calendar-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">最近 90 天</span>
          <i class="ri-check-line dropdown-item-check"></i>
        </li>
      </ul>
    </div>
    
    <div class="dropdown-divider"></div>
    
    <div class="dropdown-section">
      <div class="dropdown-section-title">全部数据</div>
      <ul class="dropdown-list">
        <li class="dropdown-item" data-value="all">
          <i class="ri-infinity-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">全部</span>
          <i class="ri-check-line dropdown-item-check"></i>
        </li>
      </ul>
    </div>
    
    <div class="dropdown-divider"></div>
    
    <div class="dropdown-section">
      <div class="dropdown-section-title">自定义范围</div>
      <div class="dropdown-custom-range">
        <input type="date" class="date-input" placeholder="开始日期" />
        <span class="date-separator">至</span>
        <input type="date" class="date-input" placeholder="结束日期" />
        <button class="btn-primary btn-sm btn-block">应用</button>
      </div>
    </div>
  </div>
</div>
```

**CSS 增强：**

```css
/* 分组标题 */
.dropdown-section {
  padding: 8px 6px;
}
.dropdown-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #99AAB5;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 4px 12px;
  margin-bottom: 4px;
}

/* 自定义日期范围 */
.dropdown-custom-range {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}
.date-input {
  width: 100%;
  height: 36px;
  padding: 0 10px;
  border: 1px solid #E8ECF0;
  border-radius: 6px;
  font-size: 14px;
  color: #1A1A1A;
  background: #F8FAFF;
}
.date-input:focus {
  border-color: #5B7FFF;
  outline: none;
  background: #FFFFFF;
}
.date-separator {
  text-align: center;
  color: #99AAB5;
  font-size: 12px;
}
```

---

### 2.4 类型筛选下拉框（支持多选）

```html
<div class="dropdown-container dropdown-multi">
  <div class="dropdown-trigger" tabindex="0">
    <div class="dropdown-trigger-content">
      <i class="ri-filter-3-line dropdown-trigger-icon"></i>
      <span class="dropdown-trigger-label">全部类型</span>
      <span class="dropdown-selected-count" style="display: none;">(2)</span>
    </div>
    <i class="ri-arrow-down-s-line dropdown-arrow"></i>
  </div>
  
  <div class="dropdown-panel">
    <!-- 全选 -->
    <div class="dropdown-select-all">
      <label class="checkbox-label">
        <input type="checkbox" class="select-all-checkbox" checked />
        <span class="checkbox-text">全选</span>
      </label>
      <span class="dropdown-selected-info">已选 4 项</span>
    </div>
    
    <div class="dropdown-divider"></div>
    
    <!-- 选项列表 -->
    <ul class="dropdown-list">
      <li class="dropdown-item selected" data-value="submission">
        <label class="checkbox-label">
          <input type="checkbox" checked />
          <i class="ri-file-list-3-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">作业提交</span>
        </label>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item selected" data-value="question">
        <label class="checkbox-label">
          <input type="checkbox" checked />
          <i class="ri-message-3-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">答疑提问</span>
        </label>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="kb-access">
        <label class="checkbox-label">
          <input type="checkbox" />
          <i class="ri-book-open-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">知识库访问</span>
        </label>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="grading">
        <label class="checkbox-label">
          <input type="checkbox" />
          <i class="ri-edit-line dropdown-item-icon"></i>
          <span class="dropdown-item-label">作业批改</span>
        </label>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
    </ul>
    
    <div class="dropdown-divider"></div>
    
    <!-- 操作按钮 -->
    <div class="dropdown-actions">
      <button class="btn-secondary btn-sm">重置</button>
      <button class="btn-primary btn-sm">确定</button>
    </div>
  </div>
</div>
```

**多选 JS 逻辑：**

```javascript
function initMultiSelectDropdown(container) {
  const trigger = container.querySelector('.dropdown-trigger');
  const panel = container.querySelector('.dropdown-panel');
  const checkboxes = container.querySelectorAll('input[type="checkbox"]');
  const selectAll = container.querySelector('.select-all-checkbox');
  const selectedInfo = container.querySelector('.dropdown-selected-info');
  const selectedCount = container.querySelector('.dropdown-selected-count');
  
  // 全选/取消全选
  selectAll.addEventListener('change', (e) => {
    const checked = e.target.checked;
    checkboxes.forEach(cb => {
      cb.checked = checked;
      cb.closest('.dropdown-item').classList.toggle('selected', checked);
    });
    updateSelectedCount();
  });
  
  // 单项选择
  checkboxes.forEach(cb => {
    if (cb !== selectAll) {
      cb.addEventListener('change', (e) => {
        e.target.closest('.dropdown-item').classList.toggle('selected', e.target.checked);
        updateSelectedCount();
        
        // 更新全选状态
        const allChecked = Array.from(checkboxes)
          .filter(c => c !== selectAll)
          .every(c => c.checked);
        selectAll.checked = allChecked;
      });
    }
  });
  
  function updateSelectedCount() {
    const checkedCount = Array.from(checkboxes)
      .filter(cb => cb !== selectAll && cb.checked)
      .length;
    
    selectedInfo.textContent = `已选 ${checkedCount} 项`;
    selectedCount.textContent = `(${checkedCount})`;
    selectedCount.style.display = checkedCount > 0 ? 'inline' : 'none';
  }
}
```

---

### 2.5 分页大小选择器（简洁版）

```html
<div class="dropdown-container dropdown-compact">
  <div class="dropdown-trigger dropdown-trigger-compact" tabindex="0">
    <span class="dropdown-trigger-label">10</span>
    <i class="ri-arrow-down-s-line dropdown-arrow"></i>
  </div>
  
  <div class="dropdown-panel dropdown-panel-compact">
    <ul class="dropdown-list">
      <li class="dropdown-item selected" data-value="10">
        <span class="dropdown-item-label">10 条/页</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="20">
        <span class="dropdown-item-label">20 条/页</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="50">
        <span class="dropdown-item-label">50 条/页</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
      <li class="dropdown-item" data-value="100">
        <span class="dropdown-item-label">100 条/页</span>
        <i class="ri-check-line dropdown-item-check"></i>
      </li>
    </ul>
  </div>
</div>
```

```css
/* 紧凑版样式 */
.dropdown-compact .dropdown-trigger {
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  min-width: auto;
}

.dropdown-panel-compact {
  min-width: 120px;
  max-height: 200px;
}

.dropdown-panel-compact .dropdown-item {
  height: 36px;
}
```

---

### 2.6 用户菜单下拉框

```html
<div class="dropdown-container dropdown-user-menu">
  <div class="dropdown-trigger dropdown-trigger-user" tabindex="0">
    <div class="user-avatar">
      <img src="/static/avatar/default.png" alt="用户头像" />
      <span class="user-status online"></span>
    </div>
    <div class="user-info">
      <span class="user-name">张老师</span>
      <span class="user-role">教师</span>
    </div>
    <i class="ri-arrow-down-s-line dropdown-arrow"></i>
  </div>
  
  <div class="dropdown-panel dropdown-user-panel">
    <!-- 用户信息卡片 -->
    <div class="user-card-header">
      <div class="user-avatar large">
        <img src="/static/avatar/default.png" alt="用户头像" />
      </div>
      <div class="user-card-info">
        <div class="user-name">张老师</div>
        <div class="user-email">zhang@example.edu.cn</div>
        <div class="user-role-badge">教师账号</div>
      </div>
    </div>
    
    <div class="dropdown-divider"></div>
    
    <!-- 菜单项 -->
    <ul class="dropdown-list">
      <li class="dropdown-item">
        <i class="ri-user-settings-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">个人设置</span>
      </li>
      <li class="dropdown-item">
        <i class="ri-notification-3-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">消息通知</span>
        <span class="dropdown-item-badge">3</span>
      </li>
      <li class="dropdown-item">
        <i class="ri-shield-keyhole-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">权限管理</span>
      </li>
      <li class="dropdown-item">
        <i class="ri-question-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">帮助文档</span>
      </li>
    </ul>
    
    <div class="dropdown-divider"></div>
    
    <!-- 退出登录 -->
    <ul class="dropdown-list">
      <li class="dropdown-item dropdown-item-danger">
        <i class="ri-logout-box-line dropdown-item-icon"></i>
        <span class="dropdown-item-label">退出登录</span>
      </li>
    </ul>
  </div>
</div>
```

```css
/* 用户菜单特殊样式 */
.dropdown-user-menu .dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
}
.dropdown-user-menu .dropdown-trigger:hover {
  background: #F0F2F5;
}

.user-avatar {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
}
.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.user-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #10B981;
  border: 2px solid #FFFFFF;
}
.user-status.online { background: #10B981; }
.user-status.away { background: #F59E0B; }
.user-status.offline { background: #99AAB5; }

.user-info {
  display: flex;
  flex-direction: column;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1A1A1A;
}
.user-role {
  font-size: 12px;
  color: #99AAB5;
}

/* 用户面板头部 */
.user-card-header {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #F8FAFF, #F0F2F5);
}
.user-card-header .user-avatar.large {
  width: 48px;
  height: 48px;
}
.user-card-info .user-name {
  font-size: 16px;
  font-weight: 600;
}
.user-card-info .user-email {
  font-size: 13px;
  color: #667788;
  margin-top: 2px;
}
.user-role-badge {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(91, 127, 255, 0.1);
  color: #5B7FFF;
  font-size: 12px;
  border-radius: 4px;
  margin-top: 6px;
}

/* 危险操作项 */
.dropdown-item-danger {
  color: #EF4444;
}
.dropdown-item-danger:hover {
  background: rgba(239, 68, 68, 0.1);
}
.dropdown-item-danger .dropdown-item-icon {
  color: #EF4444;
}

/* 徽章 */
.dropdown-item-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #EF4444;
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  margin-left: auto;
}
```

---

## ⚡ 三、交互行为规范

### 3.1 键盘导航

```javascript
// 通用键盘导航
function initDropdownKeyboard(container) {
  const trigger = container.querySelector('.dropdown-trigger');
  const panel = container.querySelector('.dropdown-panel');
  const items = Array.from(panel.querySelectorAll('.dropdown-item:not(.disabled)'));
  
  let focusedIndex = -1;
  
  trigger.addEventListener('keydown', (e) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
      case 'ArrowDown':
        e.preventDefault();
        openDropdown();
        break;
      case 'Escape':
        closeDropdown();
        break;
    }
  });
  
  panel.addEventListener('keydown', (e) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        focusedIndex = Math.min(focusedIndex + 1, items.length - 1);
        focusItem(focusedIndex);
        break;
      case 'ArrowUp':
        e.preventDefault();
        focusedIndex = Math.max(focusedIndex - 1, 0);
        focusItem(focusedIndex);
        break;
      case 'Home':
        e.preventDefault();
        focusedIndex = 0;
        focusItem(focusedIndex);
        break;
      case 'End':
        e.preventDefault();
        focusedIndex = items.length - 1;
        focusItem(focusedIndex);
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (focusedIndex >= 0) {
          items[focusedIndex].click();
        }
        break;
      case 'Escape':
        closeDropdown();
        trigger.focus();
        break;
    }
  });
  
  function openDropdown() {
    closeAllDropdowns();
    panel.classList.add('show');
    trigger.classList.add('active');
    focusedIndex = items.findIndex(i => i.classList.contains('selected'));
    if (focusedIndex === -1) focusedIndex = 0;
    focusItem(focusedIndex);
  }
  
  function closeDropdown() {
    panel.classList.remove('show');
    trigger.classList.remove('active');
  }
  
  function focusItem(index) {
    items.forEach((item, i) => {
      if (i === index) {
        item.focus();
        item.scrollIntoView({ block: 'nearest' });
      }
    });
  }
}
```

### 3.2 点击外部关闭

```javascript
// 全局点击处理
document.addEventListener('click', (e) => {
  const dropdowns = document.querySelectorAll('.dropdown-container');
  
  dropdowns.forEach(container => {
    if (!container.contains(e.target)) {
      const panel = container.querySelector('.dropdown-panel');
      const trigger = container.querySelector('.dropdown-trigger');
      panel?.classList.remove('show');
      trigger?.classList.remove('active');
    }
  });
});

// 阻止面板内部点击冒泡
document.querySelectorAll('.dropdown-panel').forEach(panel => {
  panel.addEventListener('click', (e) => {
    e.stopPropagation();
  });
});
```

### 3.3 滚动位置保持

```javascript
// 保持下拉面板在视口内
function adjustDropdownPosition(panel, trigger) {
  const rect = trigger.getBoundingClientRect();
  const panelRect = panel.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  
  // 下方空间不足时，显示在上方
  if (rect.bottom + panelRect.height > viewportHeight - 10) {
    panel.style.top = 'auto';
    panel.style.bottom = '100%';
    panel.style.marginBottom = '4px';
  } else {
    panel.style.top = '100%';
    panel.style.bottom = 'auto';
    panel.style.marginTop = '4px';
  }
  
  // 右侧溢出调整
  if (rect.right + panelRect.width > window.innerWidth - 10) {
    panel.style.left = 'auto';
    panel.style.right = '0';
  }
}
```

---

## 🎬 四、动效规范

### 4.1 展开/收起动画

```css
@keyframes dropdownSlideIn {
  from {
    opacity: 0;
    transform: translateY(-8px) scaleY(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scaleY(1);
  }
}

@keyframes dropdownSlideOut {
  from {
    opacity: 1;
    transform: translateY(0) scaleY(1);
  }
  to {
    opacity: 0;
    transform: translateY(-8px) scaleY(0.95);
  }
}

.dropdown-panel {
  animation: dropdownSlideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.dropdown-panel.closing {
  animation: dropdownSlideOut 0.15s cubic-bezier(0.16, 1, 0.3, 1);
}
```

### 4.2 选项悬停动画

```css
.dropdown-item {
  position: relative;
  overflow: hidden;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(91, 127, 255, 0.05), transparent);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.dropdown-item:hover::before {
  transform: translateX(100%);
}
```

### 4.3 选中状态动画

```css
.dropdown-item-check {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.dropdown-item.selected .dropdown-item-check {
  animation: checkmarkPop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes checkmarkPop {
  0% {
    opacity: 0;
    transform: scale(0.5) rotate(-15deg);
  }
  50% {
    transform: scale(1.2) rotate(5deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}
```

---

## 📱 五、响应式适配

```css
/* 移动端优化 */
@media (max-width: 768px) {
  .dropdown-panel {
    position: fixed;
    left: 16px !important;
    right: 16px !important;
    max-height: 60vh;
    border-radius: 16px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  }
  
  .dropdown-trigger {
    height: 44px; /* 触摸友好 */
  }
  
  .dropdown-item {
    height: 48px; /* 触摸友好 */
    padding: 0 16px;
  }
  
  /* 移动端遮罩层 */
  .dropdown-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
    z-index: 999;
  }
  .dropdown-overlay.show {
    opacity: 1;
    pointer-events: auto;
  }
}
```

---

## ✅ 六、验收清单

### 视觉
- [ ] 所有下拉框使用统一样式（白色背景 + 蓝色强调）
- [ ] 悬停状态有明确视觉反馈（边框变蓝 + 背景变浅）
- [ ] 选中状态有蓝色背景 + 对勾图标
- [ ] 禁用状态有灰色半透明效果
- [ ] 图标与文字对齐正确

### 功能
- [ ] 点击触发器展开/收起
- [ ] 点击选项后自动关闭
- [ ] 点击外部关闭下拉框
- [ ] 键盘导航（上下箭头/Enter/Escape）
- [ ] 搜索过滤（可搜索下拉框）
- [ ] 多选计数更新（多选下拉框）

### 交互
- [ ] 展开动画流畅（200ms cubic-bezier）
- [ ] 选项悬停有高亮反馈
- [ ] 选中动画有弹性效果
- [ ] 移动端触摸区域足够大（44px+）
- [ ] 下拉面板位置自动调整（不溢出视口）

### 无障碍
- [ ] 支持键盘 Tab 导航
- [ ] 支持 Enter/Space 选择
- [ ] 支持 Escape 关闭
- [ ] 支持上下箭头切换选项
- [ ] 屏幕阅读器可读（aria 属性）

---

## 📦 七、文件结构

```
app/static/css/
└── components/
    └── dropdown.css        # 下拉框通用样式

app/static/js/
└── components/
    └── dropdown.js         # 下拉框交互逻辑

app/templates/
└── components/
    └── dropdown.html       # 下拉框宏/Jinja2 组件
```

---

> **最后更新**：2025 年  
> **适用范围**：所有页面下拉框组件  
> **设计参考**：Ant Design / Element Plus / Radix UI
