# ADR-008: 迁移至 Redis 会话存储，替代内存态

## 状态

已采纳

## 上下文

本项目早期会话存储采用 Python 进程内字典（内存态），见 [ADR-004](004-in-memory-session-storage.md)。随着系统功能演进，出现了以下问题：

1. **重启丢会话**：内存态会话在服务重启后全部丢失，用户需重新登录，影响演示与答辩体验。
2. **多实例扩展受限**：若未来需要横向扩展后端，内存态会话无法跨实例共享，成为扩展瓶颈。
3. **TTL 管理缺失**：内存态需手动实现过期清理逻辑，Redis 原生支持 TTL，更可靠。
4. **与前端 SPA 配合**：Vue 3 SPA（见 [ADR-007](007-use-vue3-spa-for-frontend.md)）采用 Bearer token 认证，会话需有持久化的存储后端。

## 决策

将会话存储从内存态字典迁移至 **Redis**，技术方案为：

- **Redis** — 会话持久化存储（Hash 结构 `session:{token}`）
- **环境变量配置** — `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `SESSION_TTL`
- **降级策略** — 开发环境 Redis 连接失败时降级为 `fakeredis`（内存模拟），保证本地可运行

## 理由

1. **会话持久化**：Redis 持久化（RDB/AOF）可在服务重启后保留会话，提升用户体验。
2. **原生 TTL**：Redis `EXPIRE` 原生支持会话过期，无需手动清理。
3. **Hash 结构清晰**：会话字段（`user_id` / `real_name` / `role` / `created_at`）以 Hash 存储，便于单字段读写。
4. **开发友好降级**：`fakeredis` 让无 Redis 环境也能本地开发，生产部署真实 Redis 即可。
5. **为扩展铺路**：Redis 会话天然支持多实例共享，后续水平扩展无障碍。

## 架构示意

```
┌─────────────────────────────────────────────┐
│              FastAPI 后端进程                │
│   app/core/session.py (SessionStore 单例)   │
├─────────────────────────────────────────────┤
│     Redis 客户端  ←→  Redis 服务 (6379)      │
│     session:{token} → Hash { user_id, ... } │
│     EXPIRE session:{token} SESSION_TTL      │
└─────────────────────────────────────────────┘
        │ 开发环境降级
        ▼
   fakeredis (进程内模拟，重启丢失)
```

## 后果

### 正面影响

- 服务重启后会话不丢失（Redis 持久化）
- 原生 TTL 过期管理
- 支持多实例水平扩展
- 与 SPA Bearer token 认证模式契合

### 负面影响

- 生产环境需部署 Redis 服务，增加运维依赖
- 多一次网络 I/O（可通过连接池缓解）
- 降级方案 `fakeredis` 仅限开发，生产不可用

## 迁移要点

- `app/core/session.py` — `SessionStore` 类，`_create_client()` 连接 Redis，失败降级 `fakeredis`
- 环境变量：`REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `SESSION_TTL`
- 便捷函数保持向后兼容：`create_session` / `get_session` / `destroy_session`

## 相关文档

- [ADR-004](004-in-memory-session-storage.md) — 本决策替代的旧内存态选型（已废弃）
- `app/core/session.py` — Redis 会话存储实现
- `README.md` — 项目运行说明（含 Redis 依赖）
