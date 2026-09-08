# 学情数据看板页面 - 完整功能规格说明书

> UI 风格参考：DeepSeek HARNESS / Notion / Linear  
> 技术约束：Jinja2 模板 + 原生 JS + 浅色主题 + ECharts 图表

---

## 📐 一、页面布局

### 1.1 整体结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 顶部导航栏 (56px, 白色背景，底部细边框 #E8ECF0)                          │
│ [📚 Logo] 课程助教系统    [知识库] [作业批改] [试题生成] [👤 用户] [退出] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  📊 学情数据看板                                                   │  │
│  │  实时查看课程学习数据与 AI 助教使用情况                             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  选择课程  [数据结构 ▼]  [时间范围 最近 30 天 ▼]                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  📈 核心指标（6 个数据卡片）                                        │  │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                 │  │
│  │  │ 45  │ │ 128 │ │ 89  │ │ 82.5│ │ 356 │ │ 12  │                 │  │
│  │  │选课人数│ │作业提交│ │已批改│ │平均分│ │答疑消息│ │活跃学生│          │  │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐       │
│  │  📅 学习趋势（折线图）        │ │  📝 作业完成情况（环形图）   │       │
│  │  [图表区域 400px 高]         │ │  [图表区域 400px 高]          │       │
│  │                             │ │                             │       │
│  │  ┌─────────────────────┐    │ │    ┌─────────┐             │       │
│  │  │  │  ╱╲  ╱╲          │    │ │    │   ███   │  已完成 65% │       │
│  │  │  │ ╱  ╲╱  ╲         │    │ │    │  ██ ██  │  待提交 25% │       │
│  │  │  └─────────────────│    │ │    │   ███   │  已逾期 10% │       │
│  │  └─────────────────────┘ └─────────────────────────────┘       │
│  └─────────────────────────────┘ └─────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐       │
│  │  📚 知识库使用（柱状图）      │ │  💬 热门问题（列表）         │       │
│  │  [图表区域 300px 高]         │ │  ┌──────────────────────┐   │       │
│  │                             │ │  │ 🔥 什么是二叉树遍历？  │   │       │
│  │  ████  ███  ██  █           │ │  │ 🔥 链表插入怎么实现？  │   │       │
│  │  文档  片段  提问  批改       │ │  │ 🔥 时间复杂度怎么算？  │   │       │
│  └─────────────────────────────┘ └──────────────────────────────┘       │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  📋 最近学习动态（表格）                                            │  │
│  │  ┌────┬──────┬────────┬────────┬────────┬────────┐               │  │
│  │  │时间│ 学生  │ 类型   │ 内容   │ 状态   │ 得分   │               │  │
│  │  ├────┼──────┼────────┼────────┼────────┼────────┤               │  │
│  │  │10:30│ 张三  │ 作业提交│ 线性表  │ 已批改  │ 85.0   │               │  │
│  │  └────┴──────┴────────┴────────┴────────┴────────┘               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 尺寸规范

| 区域 | 宽度 | 高度 | 说明 |
|------|------|------|------|
| 顶部导航 | 100% | 56px | 固定 |
| 页面标题区 | 100% | 自动 | 包含标题 + 副标题 |
| 筛选栏 | 100% | 64px | 课程/时间选择 |
| 核心指标卡 | 100% | 140px | 6 个卡片网格 |
| 图表区 | 50% | 400px | 左右两列 |
| 数据表格 | 100% | 自动 | 分页显示 |

---

## 🎨 二、视觉设计规范

### 2.1 配色方案（浅色主题）

```css
:root {
  /* 背景 */
  --bg-page: #F5F7FA;
  --bg-card: #FFFFFF;
  --bg-hover: #F0F2F5;
  
  /* 文字 */
  --text-primary: #1A1A1A;
  --text-secondary: #667788;
  --text-muted: #99AAB5;
  
  /* 主色 */
  --primary: #5B7FFF;
  --primary-hover: #4665E8;
  --primary-light: rgba(91, 127, 255, 0.1);
  
  /* 图表配色 */
  --chart-blue: #5B7FFF;
  --chart-purple: #8B5CF6;
  --chart-green: #10B981;
  --chart-yellow: #F59E0B;
  --chart-red: #EF4444;
  --chart-cyan: #06B6D4;
  
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
}
```

### 2.2 图标规范（Remix Icon）

```html
<!-- 引入 -->
<link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">

<!-- 看板图标 -->
<i class="ri-bar-chart-box-line"></i>    <!-- 数据看板 -->
<i class="ri-user-line"></i>             <!-- 选课人数 -->
<i class="ri-file-list-3-line"></i>      <!-- 作业提交 -->
<i class="ri-checkbox-circle-line"></i>  <!-- 已批改 -->
<i class="ri-star-line"></i>             <!-- 平均分 -->
<i class="ri-question-line"></i>         <!-- 答疑消息 -->
<i class="ri-fire-line"></i>             <!-- 活跃学生 -->
<i class="ri-trend-up-line"></i>         <!-- 学习趋势 -->
<i class="ri-pie-chart-line"></i>        <!-- 作业完成 -->
<i class="ri-book-open-line"></i>        <!-- 知识库 -->
<i class="ri-message-3-line"></i>        <!-- 热门问题 -->
<i class="ri-time-line"></i>             <!-- 时间 -->
<i class="ri-download-line"></i>         <!-- 导出 -->
<i class="ri-refresh-line"></i>          <!-- 刷新 -->
```

---

## 🧩 三、核心功能模块

### 3.1 页面标题区

```html
<div class="page-header">
  <div class="page-title">
    <h1>
      <i class="ri-bar-chart-box-line"></i>
      <span>学情数据看板</span>
    </h1>
    <p class="page-subtitle">实时查看课程学习数据与 AI 助教使用情况</p>
  </div>
  <div class="page-actions">
    <button class="btn-secondary" id="refreshBtn">
      <i class="ri-refresh-line"></i>
      <span>刷新</span>
    </button>
    <button class="btn-primary" id="exportBtn">
      <i class="ri-download-line"></i>
      <span>导出报告</span>
    </button>
  </div>
</div>
```

**样式要求：**
- 标题：24px 粗体，深蓝 #1A1A1A
- 副标题：14px 中灰 #667788
- 图标：24x24px，渐变背景
- 按钮组：右对齐，刷新/导出

---

### 3.2 筛选栏（优化下拉框）

> 📌 **下拉框规范**：详见 [`dropdown-optimization-spec.md`](./dropdown-optimization-spec.md)

```html
<div class="filter-bar">
  <!-- 课程选择（带搜索） -->
  <div class="filter-group">
    <label>
      <i class="ri-book-open-line"></i>
      <span>选择课程</span>
    </label>
    
    <div class="dropdown-container dropdown-searchable" id="courseDropdown">
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
      </div>
    </div>
  </div>
  
  <!-- 时间范围（带快捷选项 + 自定义） -->
  <div class="filter-group">
    <label>
      <i class="ri-time-line"></i>
      <span>时间范围</span>
    </label>
    
    <div class="dropdown-container" id="timeRangeDropdown">
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
      </div>
    </div>
  </div>
  
  <div class="filter-actions">
    <button class="btn-secondary btn-sm">
      <i class="ri-compare-line"></i>
      <span>对比班级</span>
    </button>
  </div>
</div>
```

**样式要求：**
- 容器：白色卡片，高度 64px，边框 1px solid #E8ECF0，圆角 12px
- 下拉触发器：高度 40px，悬停边框变蓝 + 浅蓝背景
- 下拉面板：白色背景，圆角 12px，阴影 0 8px 24px rgba(0,0,0,0.12)
- 选项：高度 40px，悬停浅灰背景 #F0F2F5，选中蓝色背景 rgba(91,127,255,0.1)
- 图标：Remix Icon，20x20px，选中时变蓝色
- 动画：展开 200ms cubic-bezier(0.16, 1, 0.3, 1)

**交互行为：**
- 点击触发器展开/收起
- 点击选项后自动关闭并更新选中状态
- 点击外部关闭
- 支持键盘导航（↑↓选择，Enter 确认，Escape 关闭）
- 课程选择支持搜索过滤
- 时间范围支持自定义日期（可选扩展）

---

### 3.3 核心指标卡（6 个）

```html
<div class="metrics-grid">
  <!-- 选课人数 -->
  <div class="metric-card">
    <div class="metric-icon" style="background: linear-gradient(135deg, #5B7FFF, #8B5CF6);">
      <i class="ri-user-line"></i>
    </div>
    <div class="metric-content">
      <div class="metric-value">45</div>
      <div class="metric-label">选课人数</div>
      <div class="metric-trend up">
        <i class="ri-arrow-up-line"></i>
        <span>12% 较上周</span>
      </div>
    </div>
  </div>
  
  <!-- 作业提交 -->
  <div class="metric-card">
    <div class="metric-icon" style="background: linear-gradient(135deg, #10B981, #34D399);">
      <i class="ri-file-list-3-line"></i>
    </div>
    <div class="metric-content">
      <div class="metric-value">128</div>
      <div class="metric-label">作业提交</div>
      <div class="metric-trend up">
        <i class="ri-arrow-up-line"></i>
        <span>8% 较上周</span>
      </div>
    </div>
  </div>
  
  <!-- 已批改 -->
  <div class="metric-card">
    <div class="metric-icon" style="background: linear-gradient(135deg, #F59E0B, #FBBF24);">
      <i class="ri-checkbox-circle-line"></i>
    </div>
    <div class="metric-content">
      <div class="metric-value">89</div>
      <div class="metric-label">已批改</div>
      <div class="metric-trend neutral">
        <i class="ri-minus-line"></i>
        <span>持平</span>
      </div>
    </div>
  </div>
  
  <!-- 平均分 -->
  <div class="metric-card">
    <div class="metric-icon" style="background: linear-gradient(135deg, #06B6D4, #22D3EE);">
      <i class="ri-star-line"></i>
    </div>
    <div class="metric-content">
      <div class="metric-value">82.5</div>
      <div class="metric-label">平均分</div>
      <div class="metric-trend up">
        <i class="ri-arrow-up-line"></i>
        <span>3.2 分提升</span>
      </div>
    </div>
  </div>
  
  <!-- 答疑消息 -->
  <div class="metric-card">
    <div class="metric-icon" style="background: linear-gradient(135deg, #8B5CF6, #A78BFA);">
      <i class="ri-message-3-line"></i>
    </div>
    <div class="metric-content">
      <div class="metric-value">356</div>
      <div class="metric-label">答疑消息</div>
      <div class="metric-trend up">
        <i class="ri-arrow-up-line"></i>
        <span>23% 较上周</span>
      </div>
    </div>
  </div>
  
  <!-- 活跃学生 -->
  <div class="metric-card">
    <div class="metric-icon" style="background: linear-gradient(135deg, #EF4444, #F87171);">
      <i class="ri-fire-line"></i>
    </div>
    <div class="metric-content">
      <div class="metric-value">12</div>
      <div class="metric-label">活跃学生</div>
      <div class="metric-trend down">
        <i class="ri-arrow-down-line"></i>
        <span>2% 较上周</span>
      </div>
    </div>
  </div>
</div>
```

**样式要求：**
- 卡片：白色背景，圆角 12px，细边框
- 图标：48x48px 渐变圆角方
- 数值：32px 粗体，深蓝
- 标签：14px 中灰
- 趋势：绿色向上/红色向下/灰色持平
- 悬停：卡片上浮 2px + 阴影加深

---

### 3.4 学习趋势图（ECharts 折线图）

```html
<div class="chart-card">
  <div class="chart-header">
    <div class="chart-title">
      <i class="ri-trend-up-line"></i>
      <span>学习趋势</span>
    </div>
    <div class="chart-actions">
      <button class="chart-tab active" data-type="week">周</button>
      <button class="chart-tab" data-type="month">月</button>
      <button class="chart-tab" data-type="year">年</button>
    </div>
  </div>
  <div class="chart-container" id="trendChart"></div>
</div>
```

**ECharts 配置：**

```javascript
const trendOption = {
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#E8ECF0',
    borderWidth: 1,
    textStyle: { color: '#1A1A1A' },
    extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px;'
  },
  legend: {
    data: ['作业提交', '答疑提问', '知识库访问'],
    bottom: 0,
    icon: 'circle',
    itemWidth: 8,
    itemHeight: 8,
    textStyle: { color: '#667788' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    top: '5%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLine: { lineStyle: { color: '#E8ECF0' } },
    axisLabel: { color: '#99AAB5' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#F0F2F5', type: 'dashed' } },
    axisLabel: { color: '#99AAB5' }
  },
  series: [
    {
      name: '作业提交',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#5B7FFF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(91, 127, 255, 0.3)' },
          { offset: 1, color: 'rgba(91, 127, 255, 0.05)' }
        ])
      },
      data: [45, 52, 38, 65, 48, 72, 58]
    },
    {
      name: '答疑提问',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#8B5CF6' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
          { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
        ])
      },
      data: [28, 35, 42, 38, 55, 48, 62]
    },
    {
      name: '知识库访问',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#10B981' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
          { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
        ])
      },
      data: [120, 132, 128, 145, 158, 142, 165]
    }
  ]
};
```

---

### 3.5 作业完成情况（ECharts 环形图）

```html
<div class="chart-card">
  <div class="chart-header">
    <div class="chart-title">
      <i class="ri-pie-chart-line"></i>
      <span>作业完成情况</span>
    </div>
    <div class="chart-actions">
      <button class="btn-icon">
        <i class="ri-more-2-fill"></i>
      </button>
    </div>
  </div>
  <div class="chart-container" id="completionChart"></div>
  <div class="chart-legend">
    <div class="legend-item">
      <span class="legend-dot" style="background: #10B981;"></span>
      <span class="legend-label">已完成</span>
      <span class="legend-value">65%</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot" style="background: #F59E0B;"></span>
      <span class="legend-label">待提交</span>
      <span class="legend-value">25%</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot" style="background: #EF4444;"></span>
      <span class="legend-label">已逾期</span>
      <span class="legend-value">10%</span>
    </div>
  </div>
</div>
```

**ECharts 配置：**

```javascript
const completionOption = {
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}%',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#E8ECF0',
    textStyle: { color: '#1A1A1A' }
  },
  series: [
    {
      name: '作业完成情况',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      padAngle: 3,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#FFFFFF',
        borderWidth: 2
      },
      label: { show: false },
      data: [
        { value: 65, name: '已完成', itemStyle: { color: '#10B981' } },
        { value: 25, name: '待提交', itemStyle: { color: '#F59E0B' } },
        { value: 10, name: '已逾期', itemStyle: { color: '#EF4444' } }
      ]
    }
  ]
};
```

---

### 3.6 知识库使用（柱状图）

```html
<div class="chart-card">
  <div class="chart-header">
    <div class="chart-title">
      <i class="ri-book-open-line"></i>
      <span>知识库使用</span>
    </div>
  </div>
  <div class="chart-container" id="kbChart"></div>
</div>
```

**ECharts 配置：**

```javascript
const kbOption = {
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '5%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['文档上传', '知识片段', '提问引用', '作业批改'],
    axisLabel: {
      color: '#99AAB5',
      interval: 0,
      rotate: 0
    }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#F0F2F5', type: 'dashed' } },
    axisLabel: { color: '#99AAB5' }
  },
  series: [
    {
      name: '使用次数',
      type: 'bar',
      barWidth: '40%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#5B7FFF' },
          { offset: 1, color: '#8B5CF6' }
        ]),
        borderRadius: [8, 8, 0, 0]
      },
      data: [45, 128, 356, 89],
      label: {
        show: true,
        position: 'top',
        color: '#667788',
        fontSize: 12
      }
    }
  ]
};
```

---

### 3.7 热门问题列表

```html
<div class="hot-questions-card">
  <div class="card-header">
    <div class="card-title">
      <i class="ri-fire-line" style="color: #EF4444;"></i>
      <span>热门问题 TOP 5</span>
    </div>
    <a href="/chat" class="card-link">查看全部 →</a>
  </div>
  <div class="question-list">
    <div class="question-item">
      <div class="question-rank">1</div>
      <div class="question-content">
        <div class="question-text">什么是二叉树的前序遍历？</div>
        <div class="question-meta">
          <span><i class="ri-message-3-line"></i> 45 次提问</span>
          <span><i class="ri-time-line"></i> 10 分钟前</span>
        </div>
      </div>
      <div class="question-trend">
        <i class="ri-arrow-up-line"></i>
        <span>12%</span>
      </div>
    </div>
    
    <div class="question-item">
      <div class="question-rank">2</div>
      <div class="question-content">
        <div class="question-text">链表和数组有什么区别？</div>
        <div class="question-meta">
          <span><i class="ri-message-3-line"></i> 38 次提问</span>
          <span><i class="ri-time-line"></i> 25 分钟前</span>
        </div>
      </div>
      <div class="question-trend">
        <i class="ri-arrow-up-line"></i>
        <span>8%</span>
      </div>
    </div>
    
    <!-- 更多问题... -->
  </div>
</div>
```

**样式要求：**
- 卡片：白色背景，圆角 12px，细边框
- 排名：圆形背景，前 3 名金/银/铜色
- 问题文字：14px 深蓝，超出省略
- 元数据：12px 灰色，图标 + 文字
- 趋势：红色向上箭头 + 百分比
- 悬停：浅灰背景

---

### 3.8 最近学习动态（表格）

```html
<div class="activity-table-card">
  <div class="card-header">
    <div class="card-title">
      <i class="ri-time-line"></i>
      <span>最近学习动态</span>
    </div>
    <div class="card-actions">
      <div class="search-box">
        <i class="ri-search-line"></i>
        <input type="text" placeholder="搜索学生/作业..." />
      </div>
      
      <!-- 类型筛选下拉框（多选） -->
      <div class="dropdown-container dropdown-multi" id="typeFilterDropdown">
        <div class="dropdown-trigger" tabindex="0">
          <div class="dropdown-trigger-content">
            <i class="ri-filter-3-line dropdown-trigger-icon"></i>
            <span class="dropdown-trigger-label">全部类型</span>
            <span class="dropdown-selected-count" style="display: none;">(0)</span>
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
    </div>
  </div>
  
  <div class="table-container">
    <table class="data-table">
      <thead>
        <tr>
          <th>时间</th>
          <th>学生</th>
          <th>类型</th>
          <th>内容</th>
          <th>状态</th>
          <th>得分</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <div class="time-cell">
              <div>10:30</div>
              <div class="time-date">2024-01-15</div>
            </div>
          </td>
          <td>
            <div class="student-cell">
              <div class="student-avatar">张</div>
              <span>张三</span>
            </div>
          </td>
          <td>
            <span class="type-badge" data-type="submission">
              <i class="ri-file-list-3-line"></i>
              作业提交
            </span>
          </td>
          <td class="content-cell">
            线性表综合练习
          </td>
          <td>
            <span class="status-badge graded">
              <i class="ri-checkbox-circle-line"></i>
              已批改
            </span>
          </td>
          <td class="score-cell">85.0</td>
          <td>
            <button class="btn-icon btn-sm">
              <i class="ri-eye-line"></i>
            </button>
          </td>
        </tr>
        
        <tr>
          <td>
            <div class="time-cell">
              <div>09:45</div>
              <div class="time-date">2024-01-15</div>
            </div>
          </td>
          <td>
            <div class="student-cell">
              <div class="student-avatar" style="background: linear-gradient(135deg, #10B981, #34D399);">李</div>
              <span>李四</span>
            </div>
          </td>
          <td>
            <span class="type-badge" data-type="question">
              <i class="ri-message-3-line"></i>
              答疑提问
            </span>
          </td>
          <td class="content-cell">
            什么是二叉树的前序遍历？
          </td>
          <td>
            <span class="status-badge answered">
              <i class="ri-check-line"></i>
              已回答
            </span>
          </td>
          <td class="score-cell">-</td>
          <td>
            <button class="btn-icon btn-sm">
              <i class="ri-eye-line"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 分页 -->
    <div class="table-pagination">
      <div class="pagination-info">共 156 条记录</div>
      <div class="pagination-controls">
        <button class="btn-icon" disabled>
          <i class="ri-arrow-left-s-line"></i>
        </button>
        <span class="page-numbers">
          <button class="page-btn active">1</button>
          <button class="page-btn">2</button>
          <button class="page-btn">3</button>
          <span class="page-ellipsis">...</span>
          <button class="page-btn">10</button>
        </span>
        <button class="btn-icon">
          <i class="ri-arrow-right-s-line"></i>
        </button>
      </div>
      <div class="page-size">
        <span>每页</span>
        
        <!-- 分页大小下拉框（简洁版） -->
        <div class="dropdown-container dropdown-compact" id="pageSizeDropdown">
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
        
        <span>条</span>
      </div>
    </div>
  </div>
</div>
```

---

## ⚡ 四、交互功能

### 4.1 数据刷新

```javascript
// 刷新按钮
document.getElementById('refreshBtn').addEventListener('click', async () => {
  const btn = event.currentTarget;
  btn.classList.add('loading');
  
  try {
    await loadDashboardData();
  } finally {
    btn.classList.remove('loading');
  }
});

// 加载看板数据
async function loadDashboardData() {
  const courseId = document.getElementById('courseSelect').value;
  const timeRange = document.getElementById('timeRange').value;
  
  const response = await fetch(`/api/dashboard/course/${courseId}?range=${timeRange}`);
  const data = await response.json();
  
  // 更新核心指标
  updateMetrics(data.metrics);
  
  // 更新图表
  updateCharts(data.charts);
  
  // 更新表格
  updateActivityTable(data.activities);
}

// 自动刷新（每 5 分钟）
setInterval(() => {
  loadDashboardData();
}, 5 * 60 * 1000);
```

### 4.2 筛选联动

```javascript
// 课程/时间筛选
document.getElementById('courseSelect').addEventListener('change', loadDashboardData);
document.getElementById('timeRange').addEventListener('change', loadDashboardData);

// 图表类型切换
document.querySelectorAll('.chart-tab').forEach(tab => {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
    this.classList.add('active');
    
    const type = this.dataset.type;
    updateTrendChart(type);
  });
});
```

### 4.3 导出报告

```javascript
document.getElementById('exportBtn').addEventListener('click', async () => {
  const courseId = document.getElementById('courseSelect').value;
  const timeRange = document.getElementById('timeRange').value;
  
  const response = await fetch(`/api/dashboard/export?course=${courseId}&range=${timeRange}`);
  const blob = await response.blob();
  
  // 下载 PDF
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `学情报告_${new Date().toISOString().split('T')[0]}.pdf`;
  a.click();
  window.URL.revokeObjectURL(url);
});
```

### 4.4 表格搜索

```javascript
const searchInput = document.querySelector('.search-box input');
let searchTimeout;

searchInput.addEventListener('input', function(e) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    const keyword = e.target.value.trim();
    filterTable(keyword);
  }, 300);
});

function filterTable(keyword) {
  const rows = document.querySelectorAll('.data-table tbody tr');
  
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(keyword.toLowerCase()) ? '' : 'none';
  });
}
```

---

## 📱 五、响应式断点

```css
/* 桌面端 (>1024px) - 完整布局 */

/* 平板 (768-1024px) - 图表单列 */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* 手机 (<768px) - 指标卡片 2 列 */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-actions {
    display: none;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .data-table {
    min-width: 800px;
  }
}
```

---

## 🎬 六、动效规范

### 6.1 卡片加载动画

```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.metric-card {
  animation: fadeInUp 0.5s ease-out;
}

.metric-card:nth-child(1) { animation-delay: 0.1s; }
.metric-card:nth-child(2) { animation-delay: 0.2s; }
.metric-card:nth-child(3) { animation-delay: 0.3s; }
/* ... */
```

### 6.2 数字增长动画

```javascript
function animateNumber(element, target, duration = 1000) {
  const start = 0;
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // 缓动函数
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    
    const current = Math.floor(start + (target - start) * easeOutQuart);
    element.textContent = current.toLocaleString();
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  requestAnimationFrame(update);
}
```

### 6.3 图表加载动画

```css
@keyframes chartGrow {
  from {
    transform: scaleY(0);
    opacity: 0;
  }
  to {
    transform: scaleY(1);
    opacity: 1;
  }
}

.echarts-series {
  animation: chartGrow 0.8s ease-out;
}
```

---

## 📦 七、输出文件结构

```
app/templates/
└── dashboard.html          # 学情看板完整模板

app/static/css/
├── variables.css           # CSS 变量定义
├── dashboard.css          # 看板页专用样式
└── components.css         # 通用组件样式

app/static/js/
├── dashboard.js           # 看板页交互逻辑
├── charts.js              # ECharts 配置
└── utils.js               # 工具函数

app/api/
└── dashboard.py           # 看板数据接口
```

---

## ✅ 八、验收标准

### 视觉
- [ ] 浅色主题，白色卡片 + 浅灰背景
- [ ] 所有图标使用 Remix Icon
- [ ] 指标卡片渐变图标 + 数字增长动画
- [ ] 图表配色统一（蓝/紫/绿/黄/红）
- [ ] 表格状态 Badge 颜色正确

### 功能
- [ ] 课程/时间筛选联动
- [ ] 图表类型切换（周/月/年）
- [ ] 导出 PDF 报告
- [ ] 表格搜索/分页
- [ ] 自动刷新（5 分钟）

### 性能
- [ ] 首屏加载 <2 秒
- [ ] 图表渲染流畅 60fps
- [ ] 大数据量表格虚拟滚动
- [ ] 响应式适配移动端

### 数据准确性
- [ ] 核心指标与数据库一致
- [ ] 图表数据与 API 返回一致
- [ ] 表格分页计数正确
- [ ] 时间范围筛选准确

---

## 🎨 九、图表配色规范

```javascript
// 主色板
const CHART_COLORS = {
  primary: '#5B7FFF',      // 主蓝色
  purple: '#8B5CF6',       // 紫色
  green: '#10B981',        // 绿色
  yellow: '#F59E0B',       // 黄色
  red: '#EF4444',          // 红色
  cyan: '#06B6D4',         // 青色
  
  // 渐变配置
  gradients: {
    blue: {
      start: 'rgba(91, 127, 255, 0.3)',
      end: 'rgba(91, 127, 255, 0.05)'
    },
    purple: {
      start: 'rgba(139, 92, 246, 0.3)',
      end: 'rgba(139, 92, 246, 0.05)'
    },
    green: {
      start: 'rgba(16, 185, 129, 0.3)',
      end: 'rgba(16, 185, 129, 0.05)'
    }
  }
};
```

---

> **最后更新**：2025 年  
> **参考产品**：DeepSeek HARNESS / Notion / Linear / Tableau  
> **适用项目**：《基于 Agent 的课程助教系统设计与实现》
