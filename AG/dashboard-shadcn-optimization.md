# Dashboard 学情看板 - shadcn/ui 风格优化提示词

> 直接复制本提示词给执行 Agent，无需修改

---

## 📸 当前页面诊断

### 参考截图分析
![参考 Dashboard](截图显示：现代、简洁的数据看板设计)

**核心特点**:
- ✅ **极简卡片** - 白色背景 + 细边框 + 微妙阴影
- ✅ **大数字展示** - 指标数值突出（字重 600-700）
- ✅ **趋势指示器** - 绿色上升/红色下降徽章
- ✅ **面积图** - 渐变填充 + 平滑曲线
- ✅ **数据表格** - 简洁行 + 状态徽章 + 分页

### 当前页面问题

| 问题 | 严重度 | 修复方案 |
|------|--------|----------|
| 指标卡片过密 | 🔴 高 | 增加内边距，减少视觉噪音 |
| 颜色饱和度过高 | 🟡 中 | 降低饱和度，使用 HSL 调色 |
| 图表样式过时 | 🟡 中 | 改用面积图 + 渐变填充 |
| 表格行高过小 | 🟡 中 | 增加行高至 48px |
| 缺少趋势徽章 | 🔴 高 | 添加 +12.5% / -20% 趋势指示 |
| 卡片阴影过重 | 🟡 中 | 改用超淡阴影（1px 边框替代） |

---

## 🎨 设计目标

### 参考风格
- **shadcn/ui Dashboard** - 极简、专业、数据驱动
- **Vercel Analytics** - 面积图、渐变、大数字
- **Linear Insights** - 表格、趋势徽章、状态指示
- **Stripe Dashboard** - 卡片布局、指标展示

### 设计原则
```
1. 留白 > 装饰
2. 数据 > 文字
3. 趋势 > 静态
4. 一致 > 花哨
```

---

## 📐 优化方案

### 1. 指标卡片重构（6 卡片 → 4 卡片）

**当前**: 6 个紧凑卡片
**优化**: 4 个大卡片 + 趋势徽章

```html
<!-- 核心指标区 -->
<div class="metrics-grid">
  <!-- 卡片 1: 总收入 -->
  <div class="metric-card">
    <div class="metric-header">
      <span class="metric-label">总提交数</span>
      <span class="trend-badge trend-up">
        <i class="ri-arrow-up-line"></i>
        +12.5%
      </span>
    </div>
    <div class="metric-value">1,234</div>
    <div class="metric-description">
      <span class="trend-text">较上月增长</span>
    </div>
  </div>
  
  <!-- 卡片 2: 新用户 -->
  <div class="metric-card">
    <div class="metric-header">
      <span class="metric-label">活跃学生</span>
      <span class="trend-badge trend-down">
        <i class="ri-arrow-down-line"></i>
        -20%
      </span>
    </div>
    <div class="metric-value">45,678</div>
    <div class="metric-description">
      <span class="trend-text">用户留存强劲</span>
    </div>
  </div>
  
  <!-- 卡片 3: 平均分 -->
  <div class="metric-card">
    <div class="metric-header">
      <span class="metric-label">平均分</span>
      <span class="trend-badge trend-neutral">
        <i class="ri-minus-line"></i>
        0%
      </span>
    </div>
    <div class="metric-value">87.5</div>
    <div class="metric-description">
      <span class="trend-text">超过目标值</span>
    </div>
  </div>
  
  <!-- 卡片 4: 增长率 -->
  <div class="metric-card">
    <div class="metric-header">
      <span class="metric-label">完成率</span>
      <span class="trend-badge trend-up">
        <i class="ri-arrow-up-line"></i>
        +4.5%
      </span>
    </div>
    <div class="metric-value">92%</div>
    <div class="metric-description">
      <span class="trend-text">达成增长预测</span>
    </div>
  </div>
</div>
```

```css
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px 24px;
  transition: all 0.2s ease;
}

.metric-card:hover {
  border-color: #cbd5e1;
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
  color: #64748b;
}

.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.trend-up {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.trend-down {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.trend-neutral {
  background: rgba(100, 116, 139, 0.1);
  color: #64748b;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  color: #0f172a;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
}

.metric-description {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.trend-text {
  display: flex;
  align-items: center;
  gap: 4px;
}
```

---

### 2. 图表优化（面积图 + 渐变）

**当前**: 折线图
**优化**: 面积图 + 渐变填充 + 平滑曲线

```javascript
// ECharts 配置优化
const trendChartOption = {
  grid: {
    left: 48,
    right: 24,
    top: 24,
    bottom: 48
  },
  xAxis: {
    type: 'category',
    data: ['Apr 1', 'Apr 15', 'Apr 30', 'May 15', 'May 31', 'Jun 15'],
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
      color: '#94a3b8',
      fontSize: 12
    }
  },
  yAxis: {
    type: 'value',
    splitLine: {
      lineStyle: {
        color: '#f1f5f9',
        type: 'dashed'
      }
    },
    axisLabel: {
      color: '#94a3b8',
      fontSize: 12
    }
  },
  series: [
    {
      name: 'Desktop',
      type: 'line',
      smooth: true, // 平滑曲线
      symbol: 'none', // 无数据点
      lineStyle: {
        width: 2,
        color: '#0f172a' // 黑色实线
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(15, 23, 42, 0.3)' },
          { offset: 1, color: 'rgba(15, 23, 42, 0)' }
        ])
      }
    },
    {
      name: 'Mobile',
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: '#94a3b8', // 灰色线
        type: 'dashed'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(148, 163, 184, 0.2)' },
          { offset: 1, color: 'rgba(148, 163, 184, 0)' }
        ])
      }
    }
  ],
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e2e8f0',
    borderWidth: 1,
    textStyle: {
      color: '#0f172a',
      fontSize: 13
    },
    padding: [12, 16],
    shadowBlur: 8,
    shadowColor: 'rgba(0, 0, 0, 0.1)'
  }
};
```

---

### 3. 数据表格优化

**当前**: 紧凑表格
**优化**: 增加行高 + 状态徽章 + 悬停效果

```html
<table class="data-table">
  <thead>
    <tr>
      <th>Header Design</th>
      <th><span class="badge">Table of Contents</span></th>
      <th><span class="status-badge status-done">✓ Done</span></th>
      <th class="text-right">$45.00</th>
      <th class="text-right">$100.00</th>
      <th>Eddie Lake</th>
      <th class="text-right">
        <button class="icon-btn"><i class="ri-more-line"></i></button>
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="font-medium">Introduction</td>
      <td><span class="badge">Executive Summary</span></td>
      <td><span class="status-badge status-progress">⟳ In Progress</span></td>
      <td class="text-right font-medium">$150.00</td>
      <td class="text-right">$200.00</td>
      <td>Jamik Tashpulatov</td>
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
}

.data-table thead th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e2e8f0;
}

.data-table tbody td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  vertical-align: middle;
}

.data-table tbody tr {
  transition: background-color 0.15s ease;
}

.data-table tbody tr:hover {
  background-color: #f8fafc;
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

.status-done {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.status-progress {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

/* 图标按钮 */
.icon-btn {
  padding: 6px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
}

.icon-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

/* 字体变体 */
.font-medium {
  font-weight: 500;
}

.text-right {
  text-align: right;
}
```

---

### 4. 时间范围选择器

**当前**: 下拉框
**优化**: 分段控制器（Segmented Control）

```html
<div class="time-range-selector">
  <div class="segmented-control">
    <button class="segment-btn" data-range="7">7 days</button>
    <button class="segment-btn active" data-range="30">30 days</button>
    <button class="segment-btn" data-range="90">90 days</button>
    <button class="segment-btn" data-range="all">All time</button>
  </div>
</div>
```

```css
.segmented-control {
  display: inline-flex;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

.segment-btn {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.segment-btn:hover {
  color: #0f172a;
}

.segment-btn.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

---

### 5. 页面标题区优化

**当前**: 简单标题 + 副标题
**优化**: 增加面包屑 + 操作区

```html
<div class="page-header">
  <div class="page-title-group">
    <nav class="breadcrumb">
      <a href="/dashboard" class="breadcrumb-item">
        <i class="ri-dashboard-line"></i>
        Dashboard
      </a>
      <i class="ri-arrow-right-s-line breadcrumb-separator"></i>
      <span class="breadcrumb-item active">学情看板</span>
    </nav>
    <h1 class="page-title">总览</h1>
    <p class="page-description">
      实时查看课程学习数据与 AI 助教使用情况
    </p>
  </div>
  
  <div class="page-actions">
    <div class="btn-group">
      <button class="btn btn-ghost">
        <i class="ri-download-line"></i>
        导出
      </button>
      <button class="btn btn-primary">
        <i class="ri-share-forward-line"></i>
        分享
      </button>
    </div>
  </div>
</div>
```

```css
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.breadcrumb-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  text-decoration: none;
  transition: color 0.15s;
}

.breadcrumb-item:hover {
  color: #0f172a;
}

.breadcrumb-item.active {
  color: #0f172a;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #cbd5e1;
  font-size: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 8px 0;
  letter-spacing: -0.025em;
}

.page-description {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.btn-group {
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
  color: #64748b;
  border-color: #e2e8f0;
}

.btn-ghost:hover {
  background: #f8fafc;
  color: #0f172a;
}

.btn-primary {
  background: #0f172a;
  color: #ffffff;
}

.btn-primary:hover {
  background: #1e293b;
}
```

---

### 6. 空状态优化

**当前**: 简单文字
**优化**: 插图 + 引导文案

```html
<div class="empty-state">
  <div class="empty-icon">
    <i class="ri-bar-chart-box-line"></i>
  </div>
  <h3 class="empty-title">暂无数据</h3>
  <p class="empty-description">
    当前课程还没有学习数据，<br>
    请等待学生提交作业或提问。
  </p>
  <div class="empty-actions">
    <button class="btn btn-primary">
      <i class="ri-add-line"></i>
      创建课程
    </button>
    <button class="btn btn-ghost">
      <i class="ri-book-open-line"></i>
      查看文档
    </button>
  </div>
</div>
```

```css
.empty-state {
  text-align: center;
  padding: 60px 24px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #94a3b8;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
```

---

## 🎨 配色方案（shadcn/ui 风格）

```css
:root {
  /* 中性色 */
  --background: 0 0% 100%;
  --foreground: 222.2 47.4% 11.2%;
  
  /* 卡片 */
  --card: 0 0% 100%;
  --card-foreground: 222.2 47.4% 11.2%;
  
  /* 主色 */
  --primary: 222.2 47.4% 11.2%;
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
  
  /* 边框 */
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
  
  /* 圆角 */
  --radius: 0.5rem;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
}
```

---

## 📁 输出文件清单

### CSS 文件
- [ ] `app/static/css/dashboard/metrics.css` - 指标卡片样式
- [ ] `app/static/css/dashboard/charts.css` - 图表容器样式
- [ ] `app/static/css/dashboard/table.css` - 数据表格样式
- [ ] `app/static/css/dashboard/components.css` - 通用组件（徽章/按钮）

### JavaScript 文件
- [ ] `app/static/js/dashboard/charts.js` - ECharts 配置优化
- [ ] `app/static/js/dashboard/metrics.js` - 指标数据加载
- [ ] `app/static/js/dashboard/segmented-control.js` - 时间范围选择器

### 模板文件
- [ ] `app/templates/dashboard.html` - 主页面（重构）
- [ ] `app/templates/components/metric_card.html` - 指标卡片组件
- [ ] `app/templates/components/segmented_control.html` - 分段控制器组件

---

## ✅ 验收标准

### 视觉验收
- [ ] 指标卡片：白色背景 + 1px 边框 + 微阴影
- [ ] 趋势徽章：绿色上升/红色下降/灰色持平
- [ ] 面积图：渐变填充 + 平滑曲线
- [ ] 表格行高：≥ 48px
- [ ] 状态徽章：圆角 999px + 淡色背景

### 交互验收
- [ ] 卡片悬停：边框颜色变化 + 阴影加深
- [ ] 分段控制器：点击切换 + 平滑过渡
- [ ] 表格排序：点击表头排序
- [ ] 图表提示框：白色背景 + 阴影

### 响应式验收
- [ ] 桌面端：4 列指标卡片
- [ ] 平板端：2 列指标卡片
- [ ] 移动端：1 列指标卡片 + 隐藏次要信息

### 性能验收
- [ ] 首屏加载 < 2s
- [ ] 图表渲染 < 500ms
- [ ] 表格分页 < 100ms
- [ ] 动画帧率 > 60fps

---

## 🚀 执行步骤

1. **第 1 步**: 重构指标卡片（4 卡片布局）
2. **第 2 步**: 优化图表配置（面积图 + 渐变）
3. **第 3 步**: 重构数据表格（增加行高 + 状态徽章）
4. **第 4 步**: 添加分段控制器（时间范围）
5. **第 5 步**: 优化页面标题区（面包屑 + 操作）
6. **第 6 步**: 实现空状态组件
7. **第 7 步**: 响应式适配
8. **第 8 步**: 性能优化

---

## 📊 前后对比

### 指标卡片
```
修改前: 6 个紧凑卡片，信息过载
修改后: 4 个重点卡片，趋势徽章清晰
```

### 图表
```
修改前: 折线图，无填充，视觉单薄
修改后: 面积图 + 渐变，专业感强
```

### 表格
```
修改前: 行高 36px，信息密集
修改后: 行高 48px，呼吸感强
```

### 配色
```
修改前: 高饱和度渐变色
修改后: 低饱和度中性色（shadcn/ui 风格）
```

---

## 🎯 关键改进点

### 1. 视觉层次
```
一级：指标数值（字重 600-700，28-32px）
二级：指标标签（字重 500，13px）
三级：趋势描述（字重 400，12px，#94a3b8）
```

### 2. 间距系统
```
卡片内边距：20px 24px
卡片间距：16px
表格行高：48px
图表内边距：24px
```

### 3. 圆角规范
```
卡片：12px
徽章：999px（完全圆角）
按钮：8px
图表：10px
```

### 4. 阴影层级
```
默认：1px 边框（#e2e8f0）
悬停：0 4px 12px rgba(0,0,0,0.05)
聚焦：0 0 0 2px 白色，0 0 0 4px 蓝色外环
```

---

**提示词结束** - 直接复制给执行 Agent 使用
