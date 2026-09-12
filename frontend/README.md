# 课程助教系统 - 前端 (Vue 3 SPA)

基于 **Vue 3 + Vite + TypeScript + Pinia + Vue Router** 的单页应用前端。

## 技术栈

- **Vue 3** — 响应式组件化框架（`<script setup lang="ts">`）
- **Vite** — 构建工具 + 开发服务器（HMR）
- **TypeScript** — 类型安全
- **Pinia** — 状态管理（`auth.store.ts`、`chat.store.ts`）
- **Vue Router** — 客户端路由，按角色 (`meta.roles`) 做路由守卫
- **Tailwind CSS 4** — 原子化 CSS（shadcn/ui 风格设计令牌）
- **ECharts / vue-echarts** — 数据看板可视化
- **Axios** — HTTP 客户端（统一 Bearer token 注入）

## 开发

```bash
cd frontend
npm install        # 首次安装依赖
npm run dev        # 启动开发服务器 (http://localhost:5173)
npm run build      # 生产构建 (输出至 dist/)
npm run preview    # 预览生产构建
```

开发模式下，Vite 会将 `/api` 和 `/auth` 请求代理至后端 `http://localhost:8000`（见 `vite.config.ts`）。

## 目录结构

```
src/
├── views/           # 页面组件（LoginView, ChatView, DashboardView 等）
├── layouts/         # 布局组件（DashboardLayout — 按角色动态导航）
├── stores/          # Pinia 状态管理（auth, chat）
├── router/          # 路由定义 + 角色守卫
├── utils/           # Axios 请求封装（request.ts）
├── components/      # 可复用组件
├── App.vue          # 根组件
├── main.ts          # 应用入口
└── style.css        # 全局样式 + 设计令牌
```
