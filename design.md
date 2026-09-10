# 设计规范 - 课程助教系统

**设计风格：KONTUR 纸感 CRM**  
**版本：1.0**  
**最后更新：2026-09-09**

---

## 1. 配色系统

### 1.1 核心色板

| 色名 | 变量名 | RGB 值 | HEX | 用途 |
|------|--------|--------|-----|------|
| **Ink (暖黑)** | `--ink` | `30, 25, 15` | `#16150F` | 主文字、深色元素、侧边栏背景 |
| **Paper (暖纸)** | `--paper` | `244, 242, 236` | `#F4F2EC` | 页面背景 |
| **Card (浅卡)** | `--card` | `251, 250, 246` | `#FBFAF6` | 卡片背景、输入框背景 |
| **Line (暖灰)** | `--line` | `218, 213, 200` | `#DAD5C8` | 边框线、分割线 |
| **Green (强调绿)** | `--green` | `30, 92, 66` | `#1E5C42` | 成功状态、积极数据、主按钮 |
| **Amber (琥珀)** | `--amber` | `183, 121, 31` | `#B7791F` | 警告状态、高亮标记 |

### 1.2 功能色板

| 用途 | 变量名 | RGB 值 | HEX |
|------|--------|--------|-----|
| 成功背景 | `--success-bg` | `223, 232, 227` | `#DFE8E3` |
| 警告背景 | `--warning-bg` | `240, 230, 210` | `#F0E6D2` |
| 危险背景 | `--danger-bg` | `254, 242, 242` | `#FEF2F2` |
| 破坏性操作 | `--destructive` | `220, 38, 38` | `#DC2626` |
| 破坏性文字 | `--danger-text` | `185, 28, 28` | `#B91C1C` |

### 1.3 文字颜色

| 用途 | 变量名 | RGB 值 | HEX | 说明 |
|------|--------|--------|-----|------|
| 主文字 | `--foreground` | `30, 25, 15` | `#16150F` | 标题、正文 |
| 次要文字 | `--foreground-secondary` | `102, 102, 102` | `#666666` | 副标题、说明 |
| 辅助文字 | `--foreground-muted` | `161, 161, 170` | `#A1A1AA` | 占位符、禁用文字 |

### 1.4 背景色

| 用途 | 变量名 | RGB 值 | HEX |
|------|--------|--------|-----|
| 卡片背景 | `--background` | `251, 250, 246` | `#FBFAF6` |
| 页面背景 | `--background-secondary` | `244, 242, 236` | `#F4F2EC` |
| 分组背景 | `--background-tertiary` | `233, 229, 217` | `#E9E5D9` |
| 侧边栏背景 | `--bg-sidebar` | `30, 25, 15` | `#16150F` |

### 1.5 边框颜色

| 用途 | 变量名 | RGB 值 | HEX |
|------|--------|--------|-----|
| 默认边框 | `--border` | `218, 213, 200` | `#DAD5C8` |
| 深色边框 | `--border-strong` | `208, 202, 188` | `#D0CABC` |

---

## 2. 字体系统

### 2.1 字体家族

```css
--font-serif: 'Instrument Serif', 'Georgia', serif;    /* 装饰标题 */
--font-sans: 'Archivo', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
--font-mono: 'IBM Plex Mono', 'Fira Code', Consolas, monospace;
```

**使用规则：**
- **Instrument Serif** - 页面大标题、品牌 Logo
- **Archivo** - 正文、按钮、表单、导航
- **IBM Plex Mono** - 数字、代码、徽章、表格表头、时间戳

### 2.2 字号层级

| 级别 | 变量名 | 字号 | 字重 | 行高 | 用途 |
|------|--------|------|------|------|------|
| 超小 | `--text-xs` | 10px | 400 | 1.5 | 徽章、标签、辅助信息 |
| 小 | `--text-sm` | 11px | 400 | 1.5 | 次要文字、注释 |
| 基准 | `--text-base` | 13px | 400 | 1.5 | 正文、导航链接 |
| 大 | `--text-lg` | 14px | 500 | 1.5 | 按钮、表单标签 |
| 超大 | `--text-xl` | 16px | 500 | 1.5 | 卡片标题 |
| 特大 | `--text-2xl` | 18px | 600 | 1.25 | 页面副标题 |
| 巨大 | `--text-3xl` | 20px | 600 | 1.25 | 页面标题 |
| 页面标题 | `--text-page-title` | 22px | 400 | 1.25 | 主页面标题（Serif） |
| 数值 | `--text-metric-value` | 28px | 500 | 1.25 | KPI 数值显示 |

### 2.3 字重

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--font-normal` | 400 | 正文、导航 |
| `--font-medium` | 500 | 按钮、标签、标题 |
| `--font-semibold` | 600 | 强调文字、表头 |
| `--font-bold` | 700 | 强强调（少用） |

### 2.4 字间距

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--tracking-tight` | `-0.02em` | Serif 标题 |
| `--tracking-normal` | `0` | 正文 |
| `--tracking-wide` | `0.08em` | 徽章、小标签 |
| `--tracking-wider` | `0.14em` | 表格表头、导航分类 |
| `--tracking-widest` | `0.22em` | 品牌副标题、装饰文字 |

---

## 3. 间距系统

### 3.1 基础间距（8px 网格）

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--space-1` | 4px | 极小间距 |
| `--space-2` | 8px | 小间距 |
| `--space-3` | 12px | 标准内边距 |
| `--space-4` | 16px | 标准内边距 |
| `--space-5` | 20px | 中等内边距 |
| `--space-6` | 24px | 大内边距 |
| `--space-8` | 32px | 页面边距 |
| `--space-10` | 40px | 大页面边距 |
| `--space-12` | 48px | 极大间距 |

### 3.2 页面边距

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--page-padding-x` | 16px | 页面横向内边距 |
| `--page-padding-y` | 24px | 页面纵向内边距 |
| `--section-gap` | 24px | 模块间距 |
| `--card-gap` | 16px | 卡片间距 |

### 3.3 组件间距规则

**卡片内边距：** `20px 24px`（垂直 × 水平）

**按钮内边距：**
- 默认：`0 18px`
- 小按钮：`0 12px`
- 大按钮：`0 24px`

**表单元素间距：**
- 标签与输入框：`6px`
- 表单组之间：`16px`

**表格单元格内边距：** `12px 16px`

---

## 4. 组件样式规范

### 4.1 圆角系统

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--radius-sm` | 4px | 小标签、徽章 |
| `--radius-md` | 6px | 按钮、输入框、卡片 |
| `--radius-lg` | 8px | 大卡片、表格容器 |
| `--radius-xl` | 12px | 模态框、下拉菜单 |
| `--radius-full` | 9999px | 圆形头像、徽章 |

### 4.2 阴影系统

**设计原则：极简，几乎无阴影**

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `--shadow-sm` | `0 1px 0 rgb(218, 213, 200, 0.5)` | 卡片默认、按钮默认 |
| `--shadow-md` | `0 2px 4px rgb(218, 213, 200, 0.3)` | 悬停状态 |
| `--shadow-lg` | `0 4px 8px rgb(218, 213, 200, 0.2)` | Toast、下拉菜单 |

### 4.3 边框规则

**默认边框：** `1px solid rgb(218, 213, 200)`（暖灰 Line 色）

**激活/选中边框：** 使用左侧内嵌色条（`box-shadow: inset 2px 0 0`）

**表格边框：** 仅底部边框，无垂直边框

**卡片边框：** 四边完整边框

### 4.4 按钮样式

**默认按钮：**
```css
.btn {
  height: 40px;
  padding: 0 18px;
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  box-shadow: var(--shadow-sm);
}
.btn:hover {
  background: rgba(var(--ink), 0.04);
  box-shadow: none;
}
```

**主按钮（绿色）：**
```css
.btn-primary {
  background: rgb(var(--green));
  color: rgb(var(--paper));
  border: none;
  box-shadow: 0 2px 0 rgba(var(--ink), 0.2);
}
```

**按钮尺寸：**
| 尺寸 | 高度 | 内边距 | 字号 |
|------|------|--------|------|
| 小 | 32px | 0 12px | 11.5px |
| 默认 | 40px | 0 18px | 13px |
| 大 | 44px | 0 24px | 14.5px |

### 4.5 卡片样式

```css
.card {
  background: rgb(var(--card));
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-sm);
}
.card h2 {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  letter-spacing: var(--tracking-wide);
}
```

### 4.6 导航栏样式

**侧边栏：**
- 宽度：`224px`
- 背景：`rgb(var(--ink))`（暖黑）
- 边框：右侧 `1px solid rgb(var(--line))`
- 导航项内边距：`8px 12px`
- 激活状态：浅色背景 + 左侧 2px 绿色条

**顶部导航栏：**
- 高度：`56px`
- 背景：`rgb(var(--card))`
- 底部边框：`1px solid rgb(var(--line))`

### 4.7 表格样式

```css
table {
  font-size: var(--text-sm);
}
th {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  opacity: 0.6;
  background: rgb(var(--background-tertiary));
}
td {
  padding: 12px 16px;
  border-bottom: 1px solid rgb(var(--line));
}
tbody tr:hover {
  background: rgba(var(--ink), 0.02);
}
```

### 4.8 徽章/标签样式

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}
```

**阶段标签（Stage Chip）：**
| 阶段 | 背景色 | 文字色 |
|------|--------|--------|
| Qualified | `#E9E5D9` | `#16150F` |
| Proposal | `#DFE8E3` | `#1E5C42` |
| Negotiation | `#F0E6D2` | `#B7791F` |
| Closing | `#1E5C42` | `#F4F2EC` |

### 4.9 表单样式

**输入框：**
```css
.form-input {
  height: 36px;
  padding: 0 12px;
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  font-size: var(--text-base);
}
.form-input:focus {
  outline: none;
  border-color: rgb(var(--ink));
  box-shadow: 0 0 0 2px rgb(var(--card)), 0 0 0 4px rgba(var(--ink), 0.15);
}
```

---

## 5. 布局规则

### 5.1 页面结构

```
┌─────────────────────────────────────┐
│         Sidebar (224px)             │
│  ┌─────────────────────────────┐    │
│  │  Logo / Brand               │    │
│  ├─────────────────────────────┤    │
│  │  Navigation Items           │    │
│  │  - 智能答疑                  │    │
│  │  - 答题练习                  │    │
│  │  - ...                      │    │
│  ├─────────────────────────────┤    │
│  │  User Profile + Logout      │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
         ┌────────────────────────────────────┐
         │         Topbar (56px)              │
         │  Page Title    |    Actions        │
         ├────────────────────────────────────┤
         │                                    │
         │         Main Content               │
         │         (max-width: 1400px)        │
         │                                    │
         └────────────────────────────────────┘
```

### 5.2 响应式断点

| 断点 | 宽度 | 行为 |
|------|------|------|
| Desktop | > 1024px | 侧边栏固定显示 |
| Tablet | 640px - 1024px | 侧边栏隐藏，汉堡菜单 |
| Mobile | < 640px | 紧凑布局，小字号 |

---

## 6. 设计原则

### 6.1 颜色使用规则

1. **禁止使用蓝紫色渐变** - 仅使用暖色中性色
2. **禁止使用 emoji** - 使用纯文字或 SVG 图标
3. **主色调仅使用暖黑/暖纸/暖灰** - 保持纸感质感
4. **强调色仅使用绿色和琥珀色** - 用于成功/警告状态

### 6.2 字体使用规则

1. **Serif 字体仅用于大标题** - 品牌感、装饰性
2. **Sans 字体用于正文** - 可读性优先
3. **Mono 字体用于数字和代码** - 等宽对齐

### 6.3 间距使用规则

1. **所有间距使用 8px 网格** - 保持视觉节奏
2. **卡片间距固定 16px** - 统一模块分隔
3. **页面边距固定 16px/24px** - 统一内外边距

### 6.4 交互反馈

1. **悬停状态：透明度变化或浅色叠加**
2. **焦点状态：4px 外发光环（暖黑色，15% 透明度）**
3. **点击状态：移除阴影，无位移**

---

## 7. CSS 变量速查

```css
/* 核心色 */
rgb(var(--ink))         /* 暖黑 #16150F */
rgb(var(--paper))       /* 暖纸 #F4F2EC */
rgb(var(--card))        /* 浅卡 #FBFAF6 */
rgb(var(--line))        /* 暖灰 #DAD5C8 */
rgb(var(--green))       /* 强调绿 #1E5C42 */
rgb(var(--amber))       /* 琥珀 #B7791F */

/* 文字 */
var(--text-primary)     /* 主文字 */
var(--text-secondary)   /* 次要文字 */
var(--text-muted)       /* 辅助文字 */

/* 背景 */
var(--bg-page)          /* 页面背景 */
var(--bg-card)          /* 卡片背景 */
var(--bg-sidebar)       /* 侧边栏背景 */

/* 字体 */
var(--font-sans)        /* 正文字体 */
var(--font-serif)       /* 标题字体 */
var(--font-mono)        /* 代码字体 */

/* 间距 */
var(--space-2)          /* 8px */
var(--space-4)          /* 16px */
var(--space-6)          /* 24px */

/* 圆角 */
var(--radius-sm)        /* 4px */
var(--radius-md)        /* 6px */
var(--radius-lg)        /* 8px */

/* 阴影 */
var(--shadow-sm)        /* 默认阴影 */
```

---

## 8. 新页面开发清单

开发新页面时，请按以下顺序检查：

- [ ] 页面背景使用 `var(--bg-page)`
- [ ] 卡片背景使用 `var(--bg-card)`
- [ ] 文字颜色使用 `var(--text-primary/secondary/muted)`
- [ ] 边框使用 `rgb(var(--line))`
- [ ] 字号使用预定义层级（`--text-xs` 到 `--text-page-title`）
- [ ] 间距使用 8px 网格（`--space-*` 变量）
- [ ] 圆角使用预定义值（`--radius-*`）
- [ ] 按钮使用 `.btn` 基础类 + 变体
- [ ] 表格使用统一表头样式（Mono 字体 + 大写 + 字间距）
- [ ] 无 emoji、无渐变、无彩色阴影

---

**文档维护：** 每次设计迭代后更新此文档，确保代码与文档同步。
