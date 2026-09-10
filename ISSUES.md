# 🚨 项目主要问题清单

> **项目**: 基于 Agent 的课程助教系统  
> **测试日期**: 2024 年  
> **优先级定义**: P0-严重 | P1-高 | P2-中 | P3-低

---

## 📋 问题总览

| 优先级 | 数量 | 描述 |
|--------|------|------|
| 🔴 P0 | 3 | 架构冲突、安全隐患、数据管理缺失 |
| 🟠 P1 | 3 | 状态管理、错误处理、XSS 风险 |
| 🟡 P2 | 4 | 响应式设计、可访问性、性能、日志 |
| 🟢 P3 | 4 | 代码重复、测试、国际化、文档 |

**总计**: 14 个主要问题

---

## 🔴 P0 - 严重问题

### 1. 双前端架构冲突

**问题编号**: ISSUE-001  
**优先级**: P0  
**状态**: ⏳ 待修复

#### 问题描述

项目同时存在两套前端架构：
- **Jinja2 模板** (16 个 HTML 文件) - 服务端渲染
- **Vue 3 SPA** - 客户端渲染

导致路由冲突、状态不同步、维护成本翻倍。

#### 影响范围

- 用户体验割裂（页面刷新 vs 无刷新）
- 认证状态可能不一致
- 开发效率降低（需同时维护两套代码）

#### 代码位置

```
app/templates/          # Jinja2 模板目录
├── dashboard.html
├── chat.html
├── kb.html
└── ... (13 个文件)

frontend/src/views/     # Vue 组件目录
├── DashboardView.vue
├── ChatView.vue
├── KnowledgeView.vue
└── ... (11 个文件)
```

```python
# app/main.py - 路由混乱
@app.get("/dashboard")  # 返回 Jinja2 模板
def dashboard_page():
    return templates.TemplateResponse("dashboard.html", {...})

# 但 Vue 前端也有 /dashboard 路由
# frontend/src/router/index.ts
{ path: 'dashboard', component: DashboardView }
```

#### 修复建议

```
方案：统一为纯 Vue SPA 架构
工时：40-60 小时
步骤：
1. 创建缺失的 Vue 组件 (LogsView, AgentSettingsView 等)
2. 移除所有 Jinja2 模板渲染
3. 后端路由改为纯 API 或重定向到 Vue 前端
4. 更新前端路由配置
```

#### 参考文档

- [迁移指南](./JINJA2_MIGRATION.md)
- [迁移计划](./MIGRATION_PLAN.md)

---

### 2. 认证系统安全隐患

**问题编号**: ISSUE-002  
**优先级**: P0  
**状态**: ⏳ 待修复

#### 问题描述

- Session 存储在内存中，重启后丢失
- Cookie 无签名验证
- 缺少 CSRF 保护
- 无速率限制

#### 影响范围

- 用户会话可能丢失
- 存在会话劫持风险
- 无法防止暴力破解

#### 代码位置

```python
# app/main.py:42-48
def _ctx(request: Request):
    user = None
    token = request.cookies.get("token") or ""
    sess = sstore.get_session(token)  # ❌ 内存存储
    if sess:
        user = {"id": sess["user_id"], ...}
    return {"request": request, "user": user, ...}
```

```python
# app/core/session.py
_sessions = {}  # ❌ 纯内存字典，重启丢失

def get_session(token: str):
    return _sessions.get(token)
```

#### 修复建议

**方案 A: Redis + JWT (推荐)**

```python
# 安装依赖
# pip install python-jose[crpyto] redis

from fastapi_jwt_auth import AuthJWT
import redis

# Redis 存储
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@settings.load_config
def get_settings():
    return {
        'authjwt_secret_key': os.environ['JWT_SECRET'],
        'authjwt_token_location': {'cookies', 'headers'},
        'authjwt_cookie_csrf_protect': True,
        'authjwt_access_token_expires': 3600,  # 1 小时
    }

@app.post("/auth/login")
def login(username: str, password: str, Authorize: AuthJWT = Depends()):
    # 验证用户
    user = authenticate(username, password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    
    # 创建 JWT
    access_token = Authorize.create_access_token(subject=user.id)
    refresh_token = Authorize.create_refresh_token(subject=user.id)
    
    # 存储到 Redis
    redis_client.setex(f"session:{user.id}", 3600, access_token)
    
    return {"access_token": access_token, "refresh_token": refresh_token}
```

**方案 B: 数据库 Session (临时方案)**

```python
# 使用 SQLAlchemy 存储 Session
class Session(Base):
    __tablename__ = "sessions"
    token = Column(String, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    expires_at = Column(DateTime)

def get_session(token: str):
    session = db.query(Session).filter(
        Session.token == token,
        Session.expires_at > datetime.now()
    ).first()
    return session
```

#### 验收标准

- [ ] Session 存储到 Redis 或数据库
- [ ] JWT token 签名验证
- [ ] CSRF token 保护
- [ ] 登录速率限制 (5 次/分钟)

---

### 3. 数据库连接管理缺失

**问题编号**: ISSUE-003  
**优先级**: P0  
**状态**: ⏳ 待修复

#### 问题描述

- 无数据库迁移工具
- 外键约束未启用
- 无连接池配置

#### 影响范围

- 数据库 schema 变更困难
- 数据完整性无法保证
- 高并发时可能出现连接问题

#### 代码位置

```python
# app/core/database.py
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///./course_ta.db",
    # ❌ 缺少连接池配置
    # ❌ 未启用 SQLite 外键
)
```

#### 修复建议

**步骤 1: 启用 Alembic 迁移**

```bash
# 安装
pip install alembic

# 初始化
alembic init alembic
```

**步骤 2: 配置数据库**

```python
# app/core/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

# SQLite 配置
engine = create_engine(
    "sqlite:///./course_ta.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,  # 开发环境开启 SQL 日志
)

# 启用外键约束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# PostgreSQL 配置 (生产环境)
# engine = create_engine(
#     "postgresql://user:pass@localhost/dbname",
#     pool_size=10,
#     max_overflow=20,
#     pool_recycle=3600,
# )
```

**步骤 3: 创建迁移脚本**

```bash
# 创建初始迁移
alembic revision --autogenerate -m "Initial schema"

# 应用迁移
alembic upgrade head
```

#### 验收标准

- [ ] Alembic 迁移工具配置完成
- [ ] SQLite 外键约束启用
- [ ] 生产环境使用 PostgreSQL + 连接池

---

## 🟠 P1 - 高优先级问题

### 4. 前端状态管理混乱

**问题编号**: ISSUE-004  
**优先级**: P1  
**状态**: ⏳ 待修复

#### 问题描述

- 同时使用 Pinia store 和组件本地状态
- 无统一错误处理
- API 请求无统一拦截器

#### 代码位置

```typescript
// frontend/src/stores/auth.store.ts
export const useAuthStore = defineStore('auth', {...})

// frontend/src/stores/course.store.ts
export const useCourseStore = defineStore('course', {...})

// 但组件中也有自己的状态
// frontend/src/views/DashboardView.vue
const metrics = ref({...})  // ❌ 重复状态管理
```

#### 修复建议

```typescript
// 统一状态管理
// 1. 所有业务数据使用 Pinia
// 2. 组件本地状态仅用于 UI 状态（如 loading、展开/收起）

// 全局错误边界
// frontend/src/components/ErrorBoundary.vue
<template>
  <div v-if="error" class="error-state">
    <p>发生错误：{{ error.message }}</p>
    <button @click="retry">重试</button>
  </div>
  <slot v-else />
</template>

// API 拦截器
// frontend/src/utils/request.ts
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    if (error.response?.status === 401) {
      authStore.logout()
    }
    return Promise.reject(error)
  }
)
```

---

### 5. API 错误处理不完善

**问题编号**: ISSUE-005  
**优先级**: P1  
**状态**: ⏳ 待修复

#### 问题描述

- 缺少统一的异常处理器
- 错误响应格式不一致
- 前端无错误重试机制

#### 代码位置

```python
# app/api/dashboard.py
async def get_overview(...):
    data = compute(...)  # ❌ 无 try-catch
    return data
```

#### 修复建议

```python
# app/core/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "type": "validation_error",
            "title": "请求验证失败",
            "detail": exc.errors(),
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "http_error",
            "title": exc.detail,
            "status": exc.status_code,
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "type": "internal_error",
            "title": "服务器内部错误",
            "detail": str(exc),
        },
    )
```

---

### 6. XSS 攻击风险

**问题编号**: ISSUE-006  
**优先级**: P1  
**状态**: ⏳ 待修复

#### 问题描述

Jinja2 模板和 Vue 组件中存在 XSS 风险：
- 未转义的用户输入
- 使用 `v-html` 渲染不可信内容

#### 代码位置

```html
<!-- app/templates/chat.html -->
<div class="bubble">{{ message.content }}</div>  <!-- ❌ 可能包含恶意脚本 -->

<!-- frontend/src/views/ChatView.vue -->
<div v-html="message.content"></div>  <!-- ❌ XSS 风险 -->
```

#### 修复建议

```vue
<!-- 使用 DOMPurify 清理 HTML -->
<!-- npm install dompurify @types/dompurify -->
<template>
  <div v-html="sanitizedContent"></div>
</template>

<script setup lang="ts">
import DOMPurify from 'dompurify'

const sanitizedContent = computed(() => {
  return DOMPurify.sanitize(props.message.content)
})
</script>
```

```python
# 添加 Content-Security-Policy 头
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    return response
```

---

## 🟡 P2 - 中优先级问题

### 7. 响应式设计不完整

**问题编号**: ISSUE-007  
**优先级**: P2  
**状态**: ⏳ 待修复

#### 问题描述

- 侧边栏在移动端可收起，但部分页面布局未适配
- 表格在小屏设备上横向滚动体验差
- 图表在移动设备上未优化

#### 影响范围

- 移动端用户体验差
- 部分功能在小屏设备上无法使用

#### 修复建议

```css
/* 移动端优化 */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    position: fixed;
  }
  
  .data-table {
    display: block;
    overflow-x: auto;
  }
  
  /* 表格转卡片布局 */
  .data-table tbody tr {
    display: block;
    margin-bottom: 16px;
    padding: 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
  }
  
  .data-table td {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border: none;
  }
  
  .data-table td::before {
    content: attr(data-label);
    font-weight: 600;
    margin-right: 8px;
  }
}
```

---

### 8. 可访问性 (Accessibility) 缺失

**问题编号**: ISSUE-008  
**优先级**: P2  
**状态**: ⏳ 待修复

#### 问题描述

- 缺少 ARIA 标签
- 键盘导航不完整
- 颜色对比度不足

#### 修复建议

```vue
<!-- 添加 ARIA 标签 -->
<button 
  @click="toggleMenu"
  aria-label="切换菜单"
  aria-expanded="isOpen"
  aria-controls="menu-content"
>
  <i class="ri-menu-line"></i>
</button>

<!-- 键盘导航 -->
<script setup>
const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    closeMenu()
  }
  if (e.key === 'Tab') {
    trapFocus(e)
  }
}
</script>
```

---

### 9. 性能优化空间

**问题编号**: ISSUE-009  
**优先级**: P2  
**状态**: ⏳ 待修复

#### 问题描述

- 静态资源无版本控制
- 图片未压缩
- 无 Service Worker 缓存
- ECharts 按需加载未实现

#### 修复建议

```typescript
// Vite 配置优化
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'chart-vendor': ['echarts', 'vue-echarts'],
        },
      },
    },
  },
})

// Service Worker
// npm install vite-plugin-pwa
import { VitePWA } from 'vite-plugin-pwa'

plugins: [
  VitePWA({
    registerType: 'autoUpdate',
    workbox: {
      globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/api\.example\.com\//i,
          handler: 'NetworkFirst',
          options: {
            cacheName: 'api-cache',
            expiration: { maxEntries: 100, maxAgeSeconds: 300 },
          },
        },
      ],
    },
  }),
]
```

---

### 10. 日志系统不完善

**问题编号**: ISSUE-010  
**优先级**: P2  
**状态**: ⏳ 待修复

#### 修复建议

```python
# 使用 Python logging 模块
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# 使用
logger.info("用户登录成功", extra={"user_id": user_id})
logger.warning("登录失败次数过多", extra={"username": username})
logger.error("数据库连接失败", exc_info=True)
```

---

## 🟢 P3 - 低优先级问题

### 11. 代码重复

**问题编号**: ISSUE-011  
**优先级**: P3

#### 问题描述

- 多个页面重复的筛选逻辑
- CSS 变量重复定义
- 工具函数分散

#### 修复建议

```typescript
// 提取公共组件
// frontend/src/components/common/FilterBar.vue
// frontend/src/components/common/Pagination.vue

// 统一工具函数
// frontend/src/utils/index.ts
export function formatDate(date: string): string { ... }
export function debounce<T extends (...args: any[]) => any>(fn: T, delay: number): T { ... }
```

---

### 12. 缺少单元测试

**问题编号**: ISSUE-012  
**优先级**: P3

#### 修复建议

```bash
# 后端测试
pip install pytest httpx pytest-asyncio

# 前端测试
npm install -D vitest @vue/test-utils jsdom
```

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "username": "test",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

```typescript
// tests/DashboardView.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardView from '@/views/DashboardView.vue'

describe('DashboardView', () => {
  it('renders metrics correctly', () => {
    const wrapper = mount(DashboardView, {
      global: {
        mocks: { $route: { query: {} } }
      }
    })
    expect(wrapper.find('.metric-value').text()).toBe('0')
  })
})
```

---

### 13. 国际化支持缺失

**问题编号**: ISSUE-013  
**优先级**: P3

#### 修复建议

```typescript
// npm install vue-i18n
// frontend/src/i18n.ts
import { createI18n } from 'vue-i18n'

const i18n = createI18n({
  locale: 'zh-CN',
  messages: {
    'zh-CN': {
      dashboard: {
        title: '学情数据看板',
        subtitle: '实时查看课程学习数据',
      },
    },
    'en-US': {
      dashboard: {
        title: 'Dashboard',
        subtitle: 'Real-time learning analytics',
      },
    },
  },
})

export default i18n
```

---

### 14. 文档不完整

**问题编号**: ISSUE-014  
**优先级**: P3

#### 修复建议

```markdown
# README.md

## 快速开始

### 开发环境

1. 安装依赖
```bash
pip install -r requirements.txt
cd frontend && npm install
```

2. 启动后端
```bash
uvicorn app.main:app --reload --port 8000
```

3. 启动前端
```bash
cd frontend && npm run dev
```

### 生产部署

```bash
# 构建前端
cd frontend && npm run build

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档

访问 http://localhost:8000/docs 查看 Swagger UI
```

---

## 📊 问题统计

### 按优先级

| 优先级 | 数量 | 已修复 | 待修复 |
|--------|------|--------|--------|
| P0 | 3 | 0 | 3 |
| P1 | 3 | 0 | 3 |
| P2 | 4 | 0 | 4 |
| P3 | 4 | 0 | 4 |

### 按类型

| 类型 | 数量 |
|------|------|
| 架构问题 | 3 |
| 安全问题 | 3 |
| 性能问题 | 2 |
| 代码质量 | 4 |
| 文档/测试 | 2 |

---

## 🎯 修复计划

### 第 1 周 (P0)
- [ ] 统一为 Vue SPA 架构
- [ ] 实现 JWT 认证
- [ ] 添加数据库迁移工具

### 第 2 周 (P1)
- [ ] 统一状态管理
- [ ] 添加全局错误处理
- [ ] 修复 XSS 漏洞

### 第 3 周 (P2)
- [ ] 完善响应式设计
- [ ] 添加 ARIA 标签
- [ ] 实现 Service Worker

### 第 4 周 (P3)
- [ ] 提取公共组件
- [ ] 编写单元测试
- [ ] 完善文档

---

**文档创建时间**: 2024 年  
**最后更新**: 2024 年  
**负责人**: 开发团队
