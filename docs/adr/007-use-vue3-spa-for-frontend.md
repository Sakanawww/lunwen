# ADR-007: 迁移至 Vue 3 SPA 前端，替代 Jinja2

## 状态

已采纳

## 上下文

本项目早期前端采用 Jinja2 服务端模板 + 原生 JavaScript（见 [ADR-003](003-use-jinja2-for-frontend.md)）。随着系统功能演进，出现了以下问题：

1. **复杂状态管理**：系统支持学生 / 教师 / 管理员三种角色，每个角色有独立的路由和页面状态，Jinja2 的 SSR 模式下需要为每个角色重复渲染整页，前端状态难以跨页面保持。
2. **流式答疑交互**：智能答疑使用 SSE（Server-Sent Events）流式输出，配合消息气泡动画、Markdown 渲染、引用溯源折叠等交互，原生 JS 手动操作 DOM 维护成本极高。
3. **数据可视化看板**：Dashboard 需要集成 ECharts（趋势折线图 / 饼图 / 柱状图），并支持时间范围（周 / 月 / 季 / 全部）动态切换，SSR 模板无法高效更新图表数据。
4. **组件复用**：下拉菜单、品牌标识、侧边栏导航等 UI 组件在多页面间重复，缺乏组件化机制导致样式不一致（例如登录页与注册页的 `brand-subtitle` 字号不统一）。

## 决策

将前端从 Jinja2 模板迁移至 **Vue 3 SPA（单页应用）**，技术栈为：

- **Vue 3** + **Vite** + **TypeScript** — 响应式组件化开发，Vite 提供 HMR 快速构建
- **Pinia** — 状态管理（auth、chat 等 store）
- **Vue Router** — 客户端路由，按角色（`meta.roles`）做路由守卫
- **Tailwind CSS 4 + shadcn/ui 风格** — HSL 设计令牌 + 纸感风格
- **ECharts / vue-echarts** — 数据看板可视化
- **Axios** — HTTP 客户端，统一请求拦截（Bearer token 注入）

后端 FastAPI 仅提供 JSON API（`/api/*`、`/auth/*`），不再做模板渲染。前端开发期通过 Vite proxy 代理至后端。

## 理由

1. **组件化解决复用与一致性**：品牌标识、导航、下拉菜单等抽象为可复用组件，从根源避免页面间样式漂移。
2. **Pinia 集中状态管理**：用户会话、当前课程、聊天历史等跨页面共享状态由 store 统一管理，无需手动同步 DOM。
3. **流式交互原生支持**：Vue 的响应式数据 + `EventSource` 天然适合 SSE 流式答疑，消息气泡、Markdown 渲染、引用折叠均可声明式实现。
4. **ECharts 深度集成**：`vue-echarts` 组件可响应数据变化自动重绘，适合时间范围切换等动态看板。
5. **类型安全**：TypeScript + `vue-tsc` 在构建期捕获类型错误，降低前后端接口对接的出错率。
6. **保留毕设可解释性**：SPA 架构是业界主流前端方案，论文中可作为"技术选型演进"章节内容，说明从 SSR 迁移至 SPA 的工程决策与权衡。

## 架构示意

```
┌────────────────────────────────────────────────────┐
│              前端层 (Vue 3 SPA / Vite)              │
│  LoginView · ChatView · DashboardView · ...        │
│  Pinia (auth/chat) · Vue Router (角色守卫)          │
├────────────────────────────────────────────────────┤
│         Vite Dev Proxy  (/api · /auth)              │
├────────────────────────────────────────────────────┤
│              后端层 (FastAPI JSON API)              │
│  /api/*  ·  /auth/*  ·  SSE /api/chat/stream        │
└────────────────────────────────────────────────────┘
```

## 后果

### 正面影响

- 组件化开发，UI 一致性从工程层面得到保障
- Pinia 管理全局状态，跨页面数据流清晰
- 流式答疑、动态图表等复杂交互可声明式实现
- TypeScript 提升代码可维护性与接口安全性
- 前后端分离，可独立部署和开发

### 负面影响

- 需要前端构建步骤（`npm run build`），部署复杂度高于纯 SSR
- 首屏加载需下载 SPA bundle，首屏时间略长于 SSR（可通过 Vite 代码分割 + 懒加载路由缓解）
- 前后端跨域需配置 CORS 中间件
- 增加了 Node.js / npm 构建链依赖

## 迁移要点

- `frontend/src/router/index.ts` — 路由定义，`meta.roles` 做角色级访问控制
- `frontend/src/stores/` — Pinia store（auth、chat 等）
- `frontend/src/utils/request.ts` — Axios 实例，统一 Bearer token 注入与 401 跳转
- `frontend/src/layouts/DashboardLayout.vue` — 按角色动态渲染导航
- `app/core/session.py` — 后端会话存储（配合前端 token）
- Vite 配置 `/api` 与 `/auth` 反向代理至 `localhost:8000`

## 相关文档

- [ADR-003](003-use-jinja2-for-frontend.md) — 本决策替代的旧 Jinja2 选型（已废弃）
- `frontend/` — Vue 3 SPA 工程目录
- `README.md` — 项目运行说明（含前端构建与启动）
- `框架说明文档.md` — 第 2.1 节 技术栈总览（需同步更新）
