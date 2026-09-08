# 知识图谱视觉优化 - 执行提示词

> 直接复制本提示词给执行 Agent，无需修改

---

## 🎨 当前问题分析

### 截图诊断
![当前问题](截图显示：节点颜色单一、连线不可见、层级不清晰)

**核心问题**:
1. ❌ **节点颜色单一** - 所有节点都是浅紫色，无法区分重要程度
2. ❌ **连线太细太淡** - 关系几乎看不见，失去知识图谱意义
3. ❌ **节点大小无差异** - 重要知识点和次要知识点一样大
4. ❌ **知识树层级模糊** - 左侧树列表没有缩进，父子关系不清晰
5. ❌ **视觉密度过高** - 80 个节点挤在一起，缺少留白
6. ❌ **缺少视觉焦点** - 没有中心节点，用户不知道看哪里

---

## 🎯 优化目标

### 参考风格
- **Notion Graph** - 清晰的层级关系
- **Obsidian Graph** - 优雅的连线和节点
- **DeepSeek HARNESS** - 简洁专业的配色
- **Linear** - 精准的信息密度控制

---

## 📐 视觉规范

### 1. 节点分级系统

**5 级节点重要度**（根据知识点出现频率 + 关联题目数）:

| 等级 | 节点大小 | 颜色 | 描边 | 用途 |
|------|----------|------|------|------|
| **核心概念** | 24px | #2563eb (深蓝) | 3px #1e40af | 课程核心主题 |
| **重要知识点** | 18px | #3b82f6 (蓝色) | 2px #2563eb | 章节重点 |
| **普通知识点** | 12px | #60a5fa (浅蓝) | 1px #3b82f6 | 常规内容 |
| **细节知识点** | 8px | #93c5fd (淡蓝) | 无 | 补充说明 |
| **叶子节点** | 6px | #dbeafe (极淡蓝) | 无 | 示例/备注 |

**ECharts 配置**:
```javascript
const nodeLevels = {
  L1: { // 核心概念
    symbolSize: 24,
    itemStyle: {
      color: '#2563eb',
      borderColor: '#1e40af',
      borderWidth: 3,
      shadowBlur: 10,
      shadowColor: 'rgba(37, 99, 235, 0.3)'
    },
    label: {
      show: true,
      fontSize: 14,
      fontWeight: 'bold',
      color: '#1e293b'
    }
  },
  L2: { // 重要知识点
    symbolSize: 18,
    itemStyle: {
      color: '#3b82f6',
      borderColor: '#2563eb',
      borderWidth: 2
    },
    label: {
      show: true,
      fontSize: 12,
      fontWeight: 500
    }
  },
  L3: { // 普通知识点
    symbolSize: 12,
    itemStyle: {
      color: '#60a5fa',
      borderColor: '#3b82f6',
      borderWidth: 1
    },
    label: {
      show: true,
      fontSize: 11
    }
  },
  L4: { // 细节知识点
    symbolSize: 8,
    itemStyle: {
      color: '#93c5fd',
      borderColor: 'transparent'
    },
    label: {
      show: false // 不显示文字，避免拥挤
    }
  },
  L5: { // 叶子节点
    symbolSize: 6,
    itemStyle: {
      color: '#dbeafe',
      borderColor: 'transparent'
    },
    label: { show: false }
  }
};
```

---

### 2. 连线分级系统

**3 级关系强度**:

| 关系类型 | 线宽 | 颜色 | 线型 | 动画 |
|----------|------|------|------|------|
| **强关系** (父子/包含) | 3px | #3b82f6 | 实线 | 流动 1s |
| **中关系** (关联/参考) | 2px | #93c5fd | 实线 | 无 |
| **弱关系** (相关/延伸) | 1px | #dbeafe | 虚线 | 无 |

**ECharts 配置**:
```javascript
edges: [
  {
    source: '数据结构',
    target: '线性表',
    lineStyle: {
      width: 3,
      color: '#3b82f6',
      type: 'solid',
      curveness: 0.1
    },
    label: {
      show: true,
      text: '包含',
      fontSize: 10,
      color: '#64748b'
    }
  },
  {
    source: '线性表',
    target: '链表',
    lineStyle: {
      width: 2,
      color: '#93c5fd',
      type: 'solid'
    }
  },
  {
    source: '链表',
    target: '循环链表',
    lineStyle: {
      width: 1,
      color: '#dbeafe',
      type: 'dashed'
    }
  }
]
```

**连线动画**（仅强关系）:
```css
@keyframes flowLine {
  0% {
    stroke-dashoffset: 20;
  }
  100% {
    stroke-dashoffset: 0;
  }
}

.edge-strong {
  animation: flowLine 1s linear infinite;
  stroke-dasharray: 5, 5;
}
```

---

### 3. 知识树层级结构优化

**当前问题**: 所有节点平铺，没有父子层级

**优化后结构**:
```html
<div class="knowledge-tree">
  <div class="tree-section">
    <div class="section-header">
      <span class="toggle-icon">▼</span>
      <span class="section-title">📖 图论基础</span>
      <span class="section-count">12 个知识点</span>
    </div>
    <ul class="tree-level-1">
      <li class="tree-node mastered">
        <span class="node-icon">✅</span>
        <span class="node-name">图的基本概念</span>
        <span class="node-progress">100%</span>
        <ul class="tree-children">
          <li class="tree-node learning">
            <span class="node-icon">📍</span>
            <span class="node-name">深度优先搜索</span>
            <span class="node-progress">60%</span>
          </li>
          <li class="tree-node pending">
            <span class="node-icon">⚪</span>
            <span class="node-name">广度优先搜索</span>
            <span class="node-progress">0%</span>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</div>
```

**CSS 样式**:
```css
.knowledge-tree {
  padding: 16px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
}

.tree-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #e0e7ff;
  border-radius: 6px;
  font-weight: 600;
  color: #3730a3;
  cursor: pointer;
  transition: background 0.2s;
}

.section-header:hover {
  background: #c7d2fe;
}

.tree-level-1 {
  margin-left: 20px;
  border-left: 2px solid #e2e8f0;
  padding-left: 12px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  margin: 4px 0;
  border-radius: 4px;
  transition: all 0.15s;
}

.tree-node:hover {
  background: #f1f5f9;
  transform: translateX(2px);
}

.tree-node.mastered .node-icon {
  color: #10b981;
}

.tree-node.learning .node-icon {
  color: #f59e0b;
}

.tree-node.pending .node-icon {
  color: #94a3b8;
}

.node-progress {
  margin-left: auto;
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}
```

---

### 4. 配色方案优化

**当前问题**: 整体偏灰白，缺少活力

**新配色方案**（基于 Tailwind 2024）:

```css
:root {
  /* 主色调 - 蓝色系 */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-200: #bfdbfe;
  --primary-300: #93c5fd;
  --primary-400: #60a5fa;
  --primary-500: #3b82f6;  /* 主色 */
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  --primary-800: #1e40af;
  --primary-900: #1e3a8a;
  
  /* 节点颜色 - 按重要度 */
  --node-core: #2563eb;      /* 核心概念 */
  --node-important: #3b82f6;  /* 重要知识点 */
  --node-normal: #60a5fa;     /* 普通知识点 */
  --node-detail: #93c5fd;     /* 细节知识点 */
  --node-leaf: #dbeafe;       /* 叶子节点 */
  
  /* 连线颜色 - 按关系强度 */
  --edge-strong: #3b82f6;
  --edge-medium: #93c5fd;
  --edge-weak: #dbeafe;
  
  /* 背景色 */
  --bg-canvas: #f8fafc;
  --bg-panel: #ffffff;
  --bg-node: #ffffff;
  
  /* 文字颜色 */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-tertiary: #94a3b8;
  
  /* 状态色 */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}
```

**渐变背景**（可选）:
```css
.knowledge-graph-container {
  background: linear-gradient(
    135deg,
    #f8fafc 0%,
    #f1f5f9 50%,
    #e2e8f0 100%
  );
}
```

---

### 5. 布局优化

**当前问题**: 80 个节点挤在一起，缺少留白

**新布局方案**:

```javascript
// ECharts 力导向布局优化
const graphOption = {
  series: [{
    type: 'graph',
    layout: 'force',
    force: {
      repulsion: 1200,      // 增加斥力（原 800）
      edgeLength: 200,      // 增加边长（原 150）
      gravity: 0.08,        // 减小引力（原 0.1）
      friction: 0.6         // 增加摩擦（原默认）
    },
    roam: true,             // 支持拖拽缩放
    draggable: true,        // 节点可拖动
    focusNodeAdjacency: true, // 悬停时高亮邻接节点
    
    // 视图中心区域（核心概念放中间）
    center: ['50%', '50%'],
    zoom: 1.2,              // 初始缩放
    
    // 边界约束
    left: '10%',
    right: '10%',
    top: '10%',
    bottom: '10%'
  }]
};
```

**画布尺寸**:
```css
.graph-container {
  width: calc(100vw - 320px);  /* 减去左侧知识树 280px + 间距 40px */
  height: calc(100vh - 180px);  /* 减去顶部导航和工具栏 */
  min-height: 600px;
  min-width: 800px;
}
```

---

### 6. 交互动画优化

#### 6.1 节点悬停效果

```css
.graph-node {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.graph-node:hover {
  transform: scale(1.15);
  filter: drop-shadow(0 4px 12px rgba(37, 99, 235, 0.4));
}

.graph-node.core-level:hover {
  transform: scale(1.1);
  filter: drop-shadow(0 6px 16px rgba(37, 99, 235, 0.5));
}
```

#### 6.2 节点展开动画（0.2 秒延迟）

```javascript
class KnowledgeNode {
  constructor(element, data) {
    this.element = element;
    this.hoverDelay = 200; // 0.2 秒
    this.hoverTimer = null;
    this.isExpanded = false;
    
    this.bindEvents();
  }
  
  bindEvents() {
    this.element.addEventListener('mouseenter', (e) => {
      this.hoverTimer = setTimeout(() => {
        this.expand(e.target);
      }, this.hoverDelay);
    });
    
    this.element.addEventListener('mouseleave', () => {
      clearTimeout(this.hoverTimer);
      setTimeout(() => this.collapse(), 150);
    });
  }
  
  expand(target) {
    if (this.isExpanded) return;
    
    // 创建详情卡片
    const tooltip = document.createElement('div');
    tooltip.className = 'node-tooltip expanded';
    tooltip.innerHTML = `
      <div class="tooltip-header">
        <h4>${this.data.name}</h4>
        <span class="node-level-badge">${this.data.level}</span>
      </div>
      <div class="tooltip-body">
        <p class="node-description">${this.data.description}</p>
        <div class="node-stats">
          <span class="stat">📚 ${this.data.relatedCount} 关联</span>
          <span class="stat">📝 ${this.data.questionCount} 题目</span>
          <span class="stat">✅ ${this.data.masteryRate}% 掌握</span>
        </div>
      </div>
      <div class="tooltip-arrow"></div>
    `;
    
    document.body.appendChild(tooltip);
    this.isExpanded = true;
    
    // 淡入动画
    tooltip.style.opacity = '0';
    tooltip.style.transform = 'translateY(10px)';
    requestAnimationFrame(() => {
      tooltip.style.transition = 'all 0.2s ease';
      tooltip.style.opacity = '1';
      tooltip.style.transform = 'translateY(0)';
    });
  }
  
  collapse() {
    const tooltip = this.element.querySelector('.node-tooltip');
    if (!tooltip) return;
    
    tooltip.style.transition = 'all 0.15s ease';
    tooltip.style.opacity = '0';
    tooltip.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
      tooltip.remove();
      this.isExpanded = false;
    }, 150);
  }
}
```

#### 6.3 连线高亮动画

```javascript
// 鼠标悬停节点时，高亮所有关联连线
graph.on('mouseover', (params) => {
  if (params.dataType === 'node') {
    // 高亮邻接边
    chart.setOption({
      series: [{
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 5,
            color: '#2563eb',
            opacity: 1
          }
        }
      }]
    });
    
    // 流动动画
    const edges = chart.getModel().getSeriesByIndex(0).getData().graph.edges;
    edges.forEach(edge => {
      if (edge.node1 === params.dataIndex || edge.node2 === params.dataIndex) {
        edge.lineStyle.animatedPosition = 0;
        // 触发动画
      }
    });
  }
});
```

---

### 7. 信息密度控制

**问题**: 80 个节点全部显示，信息过载

**解决方案**: 分级显示 + 搜索聚焦

#### 7.1 默认只显示核心节点

```javascript
// 初始加载时只显示 L1 + L2 节点
const initialNodes = allNodes.filter(node => 
  node.level === 'L1' || node.level === 'L2'
);

chart.setOption({
  series: [{
    data: initialNodes
  }]
});

// "显示更多"按钮
document.getElementById('show-more-btn').addEventListener('click', () => {
  // 展开下一级节点
  const nextLevelNodes = allNodes.filter(node => 
    node.level === 'L3' && !node.isHidden
  );
  // 添加动画
});
```

#### 7.2 搜索聚焦模式

```javascript
// 搜索时高亮相关节点，淡化其他
searchInput.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase();
  
  if (query.length < 2) {
    // 恢复全量显示
    chart.setOption({
      series: [{
        data: allNodes.map(node => ({
          ...node,
          itemStyle: { opacity: 1 }
        }))
      }]
    });
    return;
  }
  
  // 模糊匹配
  const matchedNodes = allNodes.filter(node => 
    node.name.toLowerCase().includes(query) ||
    node.description?.toLowerCase().includes(query)
  );
  
  // 高亮匹配节点，淡化其他
  chart.setOption({
    series: [{
      data: allNodes.map(node => {
        const isMatched = matchedNodes.includes(node);
        return {
          ...node,
          itemStyle: {
            opacity: isMatched ? 1 : 0.15
          },
          label: {
            show: isMatched
          }
        };
      })
    }]
  });
});
```

---

## 📁 输出文件清单

### 样式文件
- [ ] `app/static/css/knowledge-graph/visual-vars.css` - CSS 变量定义
- [ ] `app/static/css/knowledge-graph/nodes.css` - 节点样式（5 级）
- [ ] `app/static/css/knowledge-graph/edges.css` - 连线样式（3 级）
- [ ] `app/static/css/knowledge-graph/tree.css` - 知识树样式
- [ ] `app/static/css/knowledge-graph/animations.css` - 动画定义
- [ ] `app/static/css/knowledge-graph/responsive.css` - 响应式布局

### JavaScript 文件
- [ ] `app/static/js/knowledge-graph/config.js` - 图表配置（节点/连线分级）
- [ ] `app/static/js/knowledge-graph/levels.js` - 节点分级逻辑
- [ ] `app/static/js/knowledge-graph/interactions.js` - 交互逻辑（悬停/展开）
- [ ] `app/static/js/knowledge-graph/layout.js` - 力导向布局优化
- [ ] `app/static/js/knowledge-graph/search.js` - 搜索聚焦逻辑

### 模板文件
- [ ] `app/templates/knowledge_graph.html` - 主页面（更新结构）
- [ ] `app/templates/components/knowledge_tree.html` - 知识树组件
- [ ] `app/templates/components/node_tooltip.html` - 节点详情卡片

---

## ✅ 验收标准

### 视觉验收
- [ ] 5 级节点大小明显区分（24px → 6px）
- [ ] 5 级节点颜色渐变（深蓝 → 极淡蓝）
- [ ] 3 级连线清晰可见（3px/2px/1px）
- [ ] 核心节点有阴影发光效果
- [ ] 知识树有明显层级缩进（20px/级）
- [ ] 整体配色协调（蓝色系为主）

### 交互验收
- [ ] 悬停节点 → 0.2 秒后展开详情
- [ ] 悬停节点 → 关联连线高亮
- [ ] 点击树节点 → 图谱定位到对应位置
- [ ] 搜索关键词 → 匹配节点高亮，其他淡化
- [ ] 拖拽节点 → 力导向布局平滑更新
- [ ] 缩放画布 → 节点标签自动显隐

### 性能验收
- [ ] 初始加载 < 1s（只加载 L1+L2 节点）
- [ ] 展开详情 < 200ms
- [ ] 搜索响应 < 100ms
- [ ] 拖拽帧率 > 50fps

---

## 🎨 视觉效果参考

### 节点分级示例
```
● 数据结构与算法 (24px, 深蓝，发光)  ← 核心概念
  │
  ├─● 线性表 (18px, 蓝色)  ← 重要知识点
  │  ├─● 链表 (12px, 浅蓝)  ← 普通知识点
  │  │  ├─○ 单链表 (8px, 淡蓝)  ← 细节知识点
  │  │  └─○ 循环链表 (8px, 淡蓝)
  │  └─● 顺序表 (12px, 浅蓝)
  │
  └─● 树 (18px, 蓝色)
     ├─○ 二叉树 (8px, 淡蓝)
     └─○ 平衡树 (8px, 淡蓝)
```

### 知识树层级示例
```
📚 知识树
├─ ▼ 图论基础 (12 个知识点) [85%]
│  ├─ ✅ 图的基本概念
│  │  ├─ ✅ 顶点和边
│  │  └─ ✅ 有向图/无向图
│  ├─ ⚠️ 图的遍历
│  │  ├─ ✅ 深度优先搜索 (DFS)
│  │  └─ ⚠️ 广度优先搜索 (BFS)
│  └─ ⚪ 最短路径
│     ├─ ⚪ Dijkstra 算法
│     └─ ⚪ Floyd 算法
│
├─ ▼ 数据结构 (28 个知识点) [65%]
│  ├─ ✅ 线性表
│  ├─ ⚠️ 树和二叉树
│  └─ ⚪ 图
│
└─ ▼ 算法设计 (15 个知识点) [45%]
   ├─ ✅ 排序算法
   └─ ⚠️ 查找算法
```

---

## 🚀 执行步骤

1. **第 1 步**: 创建 CSS 变量文件（配色系统）
2. **第 2 步**: 实现 5 级节点样式
3. **第 3 步**: 实现 3 级连线样式
4. **第 4 步**: 优化知识树层级结构
5. **第 5 步**: 添加交互动画（0.2 秒延迟展开）
6. **第 6 步**: 实现搜索聚焦功能
7. **第 7 步**: 性能优化（分级加载）
8. **第 8 步**: 视觉验收 + 调整

---

**提示词结束** - 直接复制给执行 Agent 使用
