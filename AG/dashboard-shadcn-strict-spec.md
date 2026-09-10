# Dashboard 学情看板 - shadcn/ui 严格规范提示词

> ⚠️ **严格参照截图执行，所有数值必须精确匹配**

---

## 🎨 色彩系统（严格参照截图）

### 1. 中性色板

```css
:root {
  /* 背景色 */
  --background: #ffffff;
  --background-secondary: #f8fafc;
  --background-tertiary: #f1f5f9;
  
  /* 前景色 */
  --foreground-primary: #0f172a;    /* 标题/重要文字 */
  --foreground-secondary: #475569;  /* 次要文字 */
  --foreground-tertiary: #94a3b8;   /* 辅助文字 */
  --foreground-muted: #cbd5e1;      /* 禁用/占位 */
  
  /* 边框色 */
  --border-default: #e2e8f0;
  --border-hover: #cbd5e1;
  --border-focus: #94a3b8;
}
```

### 2. 功能色板

```css
:root {
  /* 成功色（绿色） */
  --success-bg: rgba(16, 185, 129, 0.08);
  --success-border: rgba(16, 185, 129, 0.2);
  --success-text: #059669;
  --success-icon: #10b981;
  
  /* 警告色（红色） */
  --warning-bg: rgba(239, 68, 68, 0.08);
  --warning-border: rgba(239, 68, 68, 0.2);
  --warning-text: #dc2626;
  --warning-icon: #ef4444;
  
  /* 信息色（蓝色） */
  --info-bg: rgba(59, 130, 246, 0.08);
  --info-border: rgba(59, 130, 246, 0.2);
  --info-text: #2563eb;
  --info-icon: #3b82f6;
}
```

### 3. 渐变色（图表用）

```css
/* 面积图渐变 - 深色线 */
--chart-gradient-dark-start: rgba(15, 23, 42, 0.3);
--chart-gradient-dark-end: rgba(15, 23, 42, 0);

/* 面积图渐变 - 浅色线 */
--chart-gradient-light-start: rgba(148, 163, 184, 0.2);
--chart-gradient-light-end: rgba(148, 163, 184, 0);
```

---

## 📐 间距系统（8px 基准）

### 1. 页面级间距

```css
/* 页面边距 */
--page-padding-x: 24px;    /* 左右边距 */
--page-padding-y: 32px;    /* 上下边距 */

/* 区域间距 */
--section-gap: 24px;       /* 大区间距 */
--card-gap: 16px;          /* 卡片间距 */
```

### 2. 组件级间距

```css
/* 卡片内边距 */
--card-padding-x: 24px;
--card-padding-y: 20px;

/* 指标卡片 */
--metric-padding-x: 24px;
--metric-padding-y: 20px;
--metric-gap: 12px;        /* 指标项间距 */

/* 表格 */
--table-cell-padding-x: 16px;
--table-cell-padding-y: 14px;
--table-header-height: 48px;
--table-row-height: 56px;
```

### 3. 间距标尺

```css
--space-1: 4px;    /* 0.25rem */
--space-2: 8px;    /* 0.5rem */
--space-3: 12px;   /* 0.75rem */
--space-4: 16px;   /* 1rem */
--space-5: 20px;   /* 1.25rem */
--space-6: 24px;   /* 1.5rem */
--space-8: 32px;   /* 2rem */
--space-10: 40px;  /* 2.5rem */
--space-12: 48px;  /* 3rem */
```

---

## 🔤 字体系统（严格参照）

### 1. 字体堆栈

```css
:root {
  /* 英文字体 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  
  /* 中文字体 */
  --font-sans-cn: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  
  /* 等宽字体 */
  --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
}
```

### 2. 字号标尺

```css
/* 页面标题 */
--text-page-title: 24px;      /* 字重 600 */
--text-page-subtitle: 14px;   /* 字重 400 */

/* 卡片标题 */
--text-card-title: 14px;      /* 字重 500 */
--text-card-label: 13px;      /* 字重 500 */

/* 指标数值 */
--text-metric-value: 30px;    /* 字重 600 */
--text-metric-label: 13px;    /* 字重 400 */

/* 表格文字 */
--text-table-header: 12px;    /* 字重 600 */
--text-table-cell: 13px;      /* 字重 400 */

/* 辅助文字 */
--text-caption: 12px;         /* 字重 400 */
--text-small: 11px;           /* 字重 400 */
```

### 3. 字重规范

```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 4. 行高规范

```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

---

## 📦 组件规格（像素级精确）

### 1. 指标卡片（Metric Card）

```html
<div class="metric-card">
  <div class="metric-header">
    <span class="metric-label">Total Revenue</span>
    <span class="trend-badge trend-up">
      <svg class="trend-icon" width="12" height="12">...</svg>
      +12.5%
    </span>
  </div>
  <div class="metric-value">$1,250.00</div>
  <div class="metric-description">
    Trending up this month
    <svg class="inline-icon" width="12" height="12">...</svg>
  </div>
  <div class="metric-subtitle">Visitors for the last 6 months</div>
</div>
```

```css
.metric-card {
  /* 尺寸 */
  min-width: 280px;
  padding: var(--metric-padding-y) var(--metric-padding-x);
  
  /* 背景与边框 */
  background: #ffffff;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  
  /* 阴影 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  
  /* 过渡 */
  transition: all 0.2s ease;
}

.metric-card:hover {
  border-color: var(--border-hover);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.metric-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.metric-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--foreground-secondary);
}

.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.trend-badge.trend-up {
  background: var(--success-bg);
  color: var(--success-text);
  border: 1px solid var(--success-border);
}

.trend-badge.trend-down {
  background: var(--warning-bg);
  color: var(--warning-text);
  border: 1px solid var(--warning-border);
}

.metric-value {
  font-size: 30px;
  font-weight: 600;
  color: var(--foreground-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.metric-description {
  font-size: 13px;
  color: var(--foreground-secondary);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-subtitle {
  font-size: 12px;
  color: var(--foreground-tertiary);
}
```

---

### 2. 面积图卡片（Area Chart Card）

```html
<div class="chart-card">
  <div class="chart-header">
    <div class="chart-title-group">
      <h3 class="chart-title">Total Visitors</h3>
      <p class="chart-subtitle">Total for the last 3 months</p>
    </div>
    <div class="chart-tabs">
      <button class="tab-btn active">3 months</button>
      <button class="tab-btn">30 days</button>
      <button class="tab-btn">7 days</button>
    </div>
  </div>
  <div class="chart-container">
    <!-- ECharts 渲染区 -->
  </div>
  <div class="chart-legend">
    <div class="legend-item">
      <span class="legend-line legend-line-dark"></span>
      Desktop
    </div>
    <div class="legend-item">
      <span class="legend-line legend-line-light"></span>
      Mobile
    </div>
  </div>
</div>
```

```css
.chart-card {
  background: #ffffff;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  padding: var(--card-padding-y) var(--card-padding-x);
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--foreground-primary);
  margin: 0 0 4px 0;
}

.chart-subtitle {
  font-size: 13px;
  color: var(--foreground-tertiary);
  margin: 0;
}

.chart-tabs {
  display: inline-flex;
  background: var(--background-tertiary);
  padding: 4px;
  border-radius: 8px;
}

.tab-btn {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--foreground-tertiary);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.tab-btn.active {
  background: #0f172a;
  color: #ffffff;
}

.chart-container {
  height: 320px;
  margin-bottom: 16px;
}

.chart-legend {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: var(--foreground-tertiary);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-line {
  width: 24px;
  height: 2px;
}

.legend-line-dark {
  background: #0f172a;
}

.legend-line-light {
  background: #94a3b8;
}
```

---

### 3. ECharts 配置（严格参照截图）

```javascript
const chartOption = {
  // 网格配置
  grid: {
    left: 48,
    right: 24,
    top: 16,
    bottom: 48
  },
  
  // X 轴
  xAxis: {
    type: 'category',
    data: ['Apr 1', 'Apr 15', 'Apr 30', 'May 15', 'May 31', 'Jun 15', 'Jun 3'],
    boundaryGap: false,
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#94a3b8',
      fontSize: 12,
      margin: 12
    }
  },
  
  // Y 轴
  yAxis: {
    type: 'value',
    splitLine: {
      lineStyle: {
        color: '#f1f5f9',
        type: 'solid'
      }
    },
    axisLabel: {
      color: '#94a3b8',
      fontSize: 12
    }
  },
  
  // 提示框
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.98)',
    borderColor: '#e2e8f0',
    borderWidth: 1,
    textStyle: {
      color: '#0f172a',
      fontSize: 13
    },
    padding: [12, 16],
    shadowBlur: 8,
    shadowColor: 'rgba(0, 0, 0, 0.1)'
  },
  
  // 系列配置
  series: [
    {
      name: 'Desktop',
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2.5,
        color: '#0f172a'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(15, 23, 42, 0.3)' },
          { offset: 1, color: 'rgba(15, 23, 42, 0)' }
        ])
      },
      data: [/* 数据 */]
    },
    {
      name: 'Mobile',
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2.5,
        color: '#94a3b8'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(148, 163, 184, 0.2)' },
          { offset: 1, color: 'rgba(148, 163, 184, 0)' }
        ])
      },
      data: [/* 数据 */]
    }
  ]
};
```

---

### 4. 数据表格（严格参照）

```html
<table class="data-table">
  <thead>
    <tr>
      <th>Header</th>
      <th>Section Type</th>
      <th>Status</th>
      <th class="text-right">Target</th>
      <th class="text-right">Limit</th>
      <th>Reviewer</th>
      <th class="text-right"></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="font-medium">Header Design</td>
      <td><span class="badge">Table of Contents</span></td>
      <td><span class="status-badge status-done">✓ Done</span></td>
      <td class="text-right font-medium">$45.00</td>
      <td class="text-right">$100.00</td>
      <td>Eddie Lake</td>
      <td class="text-right">
        <button class="icon-btn"><i class="ri-more-line"></i></button>
      </td>
    </tr>
  </tbody>
</table>
```

```css
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
  font-family: var(--font-sans);
}

/* 表头 */
.data-table thead th {
  padding: var(--table-cell-padding-y) var(--table-cell-padding-x);
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--foreground-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-default);
  background: #ffffff;
}

/* 表体 */
.data-table tbody td {
  padding: var(--table-cell-padding-y) var(--table-cell-padding-x);
  border-bottom: 1px solid var(--border-default);
  color: var(--foreground-secondary);
  vertical-align: middle;
  height: var(--table-row-height);
}

.data-table tbody tr {
  transition: background-color 0.15s ease;
}

.data-table tbody tr:hover {
  background-color: var(--background-secondary);
}

/* 徽章 */
.badge {
  display: inline-block;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  background: var(--background-tertiary);
  border-radius: 999px;
  color: var(--foreground-secondary);
}

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-done {
  background: var(--success-bg);
  color: var(--success-text);
}

.status-badge.status-done::before {
  content: '✓';
  font-size: 10px;
  font-weight: 700;
}

.status-badge.status-progress {
  background: var(--background-tertiary);
  color: var(--foreground-tertiary);
}

.status-badge.status-progress::before {
  content: '⟳';
  font-size: 10px;
}

/* 图标按钮 */
.icon-btn {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--foreground-tertiary);
  cursor: pointer;
  transition: all 0.15s;
}

.icon-btn:hover {
  background: var(--background-tertiary);
  color: var(--foreground-primary);
}

/* 文字对齐 */
.text-right {
  text-align: right;
}

.font-medium {
  font-weight: 500;
}
```

---

## 📱 页面布局（严格参照）

### 1. 整体布局结构

```html
<div class="dashboard-layout">
  <!-- 左侧导航 -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand">
        <div class="brand-logo">🔲</div>
        <span class="brand-name">Acme Inc.</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <a href="#" class="nav-item active">
        <i class="nav-icon"></i>
        Dashboard
      </a>
      <a href="#" class="nav-item">
        <i class="nav-icon"></i>
        Lifecycle
      </a>
      <!-- 更多导航项 -->
    </nav>
    <div class="sidebar-footer">
      <div class="user-profile">
        <div class="user-avatar">SC</div>
        <div class="user-info">
          <div class="user-name">shadcn</div>
          <div class="user-email">m@example.com</div>
        </div>
      </div>
    </div>
  </aside>
  
  <!-- 主内容区 -->
  <main class="main-content">
    <!-- 顶部栏 -->
    <header class="topbar">
      <div class="topbar-start">
        <button class="menu-toggle"><i class="ri-menu-line"></i></button>
        <div class="breadcrumb">
          <span>Dashboard</span>
        </div>
      </div>
      <div class="topbar-actions">
        <button class="btn btn-ghost">
          <i class="ri-download-line"></i>
          下载完整项目
        </button>
        <button class="btn btn-primary">
          <i class="ri-arrow-left-line"></i>
          返回模板
        </button>
      </div>
    </header>
    
    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 指标卡片 -->
      <!-- 图表 -->
      <!-- 表格 -->
    </div>
  </main>
</div>
```

```css
.dashboard-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  background: var(--background-secondary);
}

/* 左侧导航 */
.sidebar {
  background: #ffffff;
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.sidebar-header {
  margin-bottom: 24px;
  padding: 0 12px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  width: 32px;
  height: 32px;
  background: #0f172a;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.brand-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--foreground-secondary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.15s;
}

.nav-item:hover {
  background: var(--background-tertiary);
  color: var(--foreground-primary);
}

.nav-item.active {
  background: #0f172a;
  color: #ffffff;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border-default);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--background-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--foreground-secondary);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--foreground-primary);
}

.user-email {
  font-size: 12px;
  color: var(--foreground-tertiary);
}

/* 主内容区 */
.main-content {
  display: flex;
  flex-direction: column;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-default);
}

.topbar-start {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--foreground-secondary);
  cursor: pointer;
}

.breadcrumb {
  font-size: 14px;
  font-weight: 500;
  color: var(--foreground-primary);
}

.topbar-actions {
  display: flex;
  gap: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-ghost {
  background: transparent;
  color: var(--foreground-secondary);
  border-color: var(--border-default);
}

.btn-ghost:hover {
  background: var(--background-tertiary);
}

.btn-primary {
  background: #0f172a;
  color: #ffffff;
}

.btn-primary:hover {
  background: #1e293b;
}

.page-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
```

---

## 📊 指标卡片网格布局

```css
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

/* 响应式断点 */
@media (max-width: 1400px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 📈 图表卡片网格

```css
.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

/* 大图表（占满整行） */
.chart-card.full-width {
  grid-column: 1 / -1;
}
```

---

## 📋 表格卡片

```css
.table-card {
  background: #ffffff;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  overflow: hidden;
}

.table-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-default);
}

.table-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--foreground-primary);
}

.table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-top: 1px solid var(--border-default);
  font-size: 12px;
  color: var(--foreground-tertiary);
}
```

---

## 📁 输出文件清单

### CSS 文件
- [ ] `app/static/css/dashboard/variables.css` - 设计令牌（颜色/间距/字体）
- [ ] `app/static/css/dashboard/layout.css` - 布局系统（网格/侧边栏/主内容）
- [ ] `app/static/css/dashboard/metrics.css` - 指标卡片样式
- [ ] `app/static/css/dashboard/charts.css` - 图表容器样式
- [ ] `app/static/css/dashboard/table.css` - 数据表格样式
- [ ] `app/static/css/dashboard/components.css` - 通用组件（按钮/徽章/图标）

### JavaScript 文件
- [ ] `app/static/js/dashboard/charts.js` - ECharts 配置（严格参照规范）
- [ ] `app/static/js/dashboard/metrics.js` - 指标数据加载
- [ ] `app/static/js/dashboard/tabs.js` - 分段控制器交互

### 模板文件
- [ ] `app/templates/dashboard.html` - 主页面（完全重构）
- [ ] `app/templates/components/metric_card.html` - 指标卡片组件
- [ ] `app/templates/components/segmented_control.html` - 分段控制器组件
- [ ] `app/templates/layouts/dashboard.html` - Dashboard 布局模板

---

## ✅ 验收标准（像素级精确）

### 1. 色彩验收
- [ ] 背景色：#ffffff（卡片）/ #f8fafc（页面）
- [ ] 边框色：#e2e8f0（默认）/ #cbd5e1（悬停）
- [ ] 文字色：#0f172a（主）/ #475569（次）/ #94a3b8（辅助）
- [ ] 成功色：背景 rgba(16,185,129,0.08) / 文字 #059669
- [ ] 警告色：背景 rgba(239,68,68,0.08) / 文字 #dc2626

### 2. 间距验收
- [ ] 卡片内边距：20px 24px
- [ ] 卡片间距：16px
- [ ] 表格单元格：14px 16px
- [ ] 页面边距：24px

### 3. 字体验收
- [ ] 指标数值：30px / 600
- [ ] 卡片标题：14px / 600
- [ ] 表格表头：12px / 600
- [ ] 表格内容：13px / 400

### 4. 圆角验收
- [ ] 卡片：12px
- [ ] 徽章：999px（完全圆角）
- [ ] 按钮：8px
- [ ] 图表：12px

### 5. 阴影验收
- [ ] 默认：0 1px 2px rgba(0,0,0,0.02)
- [ ] 悬停：0 4px 12px rgba(0,0,0,0.05)
- [ ] 提示框：0 8px 24px rgba(0,0,0,0.1)

### 6. 交验收
- [ ] 卡片悬停：边框色变深 + 阴影加深
- [ ] 按钮悬停：背景色变深
- [ ] 表格行悬停：背景 #f8fafc
- [ ] 分段控制器：active 状态黑色背景

### 7. 图表验收
- [ ] 面积图渐变：0.3 → 0 透明度
- [ ] 曲线平滑：smooth: true
- [ ] 线宽：2.5px
- [ ] 网格线：#f1f5f9 虚线

### 8. 响应式验收
```
> 1400px: 4 列指标卡片
1024px - 1400px: 2 列指标卡片
< 768px: 1 列指标卡片 + 隐藏次要信息
```

---

## 🚀 执行步骤

1. **第 1 步**: 创建设计令牌（CSS 变量）- 严格参照色值
2. **第 2 步**: 实现布局框架（侧边栏 + 主内容）
3. **第 3 步**: 实现指标卡片（4 卡片布局 + 趋势徽章）
4. **第 4 步**: 实现面积图（ECharts 配置严格参照）
5. **第 5 步**: 实现数据表格（行高 56px + 状态徽章）
6. **第 6 步**: 实现分段控制器（时间范围选择）
7. **第 7 步**: 添加交互动画（悬停/点击）
8. **第 8 步**: 响应式适配（断点测试）
9. **第 9 步**: 像素级验收（截图对比）
10. **第 10 步**: 性能优化（图表渲染 < 500ms）

---

## 📊 前后对比检查表

| 项目 | 修改前 | 修改后（目标） |
|------|--------|----------------|
| 卡片背景 | 渐变白 | #ffffff 纯色 |
| 卡片边框 | 不可见 | 1px #e2e8f0 |
| 卡片阴影 | 重阴影 | 0 1px 2px rgba(0,0,0,0.02) |
| 指标数值 | 24px | 30px / 600 |
| 趋势徽章 | 无 | 圆角 999px + 淡色背景 |
| 图表类型 | 折线图 | 面积图 + 渐变 |
| 表格行高 | 36px | 56px |
| 状态显示 | 纯文字 | 徽章 + 图标 |
| 时间选择 | 下拉框 | 分段控制器 |
| 字体 | 系统默认 | Inter + PingFang SC |

---

## ⚠️ 关键注意事项

1. **颜色必须精确** - 使用色值 #0f172a，不可用 `black` 或 `dark`
2. **间距必须统一** - 所有间距基于 8px 网格
3. **圆角必须一致** - 卡片 12px，徽章 999px
4. **字重必须精确** - 标题 600，正文 400，强调 500
5. **阴影必须微妙** - 不超过 12px 模糊半径
6. **动画必须流畅** - 过渡时间 0.15s-0.2s
7. **图表必须平滑** - smooth: true，禁用数据点
8. **表格必须透气** - 行高 ≥ 56px

---

**提示词结束** - 直接复制给执行 Agent 使用
