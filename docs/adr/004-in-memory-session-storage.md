# ADR-004: 使用内存态会话而非 Redis

## 状态

**已废弃** — 已被 [ADR-008](008-use-redis-for-session-storage.md) 替代。

本决策曾作为项目初期的会话存储选型，后因需要支持服务重启后会话持久化与多实例扩展，已迁移至 Redis（开发环境连接失败时降级为 fakeredis）。详见 ADR-008。以下内容保留以记录决策历史。

---

## 上下文

在实现用户会话管理功能时，需要选择会话存储方案。系统需要支持用户登录后的会话保持，包括用户信息、角色权限、课程上下文等数据的存储。

## 决策

选择使用 **内存态会话存储**，而非 Redis 等外部会话服务。作为可选降级方案，支持后续切换到 Redis。

## 理由

1. **简化部署**：作为毕业设计演示系统，减少外部服务依赖可以降低部署复杂度。

2. **开发效率**：内存态会话无需额外的配置和连接管理，便于快速开发和调试。

3. **可选降级**：系统设计时考虑了可扩展性，后续可以通过修改 `core/session.py` 切换到 Redis。

4. **演示系统定位**：对于演示和开发环境，内存态会话已经足够，无需引入 Redis 增加运维负担。

## 实现方式

```python
# 内存态会话存储
_sessions = {}  # token → {user_id, real_name, role, ...}

def create_session(user_id, real_name, role) → token
def get_session(token) → session_data
def destroy_session(token)
```

## 切换到 Redis 的方法

修改 `core/session.py`，将 `_sessions` 字典替换为 Redis 客户端：

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_session(user_id, real_name, role):
    token = generate_token()
    redis_client.setex(f"session:{token}", SESSION_TTL, session_data)
    return token
```

## 后果

### 正面影响

- 部署简单，无需 Redis 服务
- 开发调试方便
- 响应速度快（无网络开销）

### 负面影响

- 服务重启后会话丢失
- 不支持多实例水平扩展
- 内存占用随会话数增长

## 相关文档

- `app/core/session.py` - 会话管理实现（已迁移至 Redis）
- `框架说明文档.md` - 第 4.4.3 节 会话管理
- [ADR-008](008-use-redis-for-session-storage.md) - 替代本决策的 Redis 会话存储选型
