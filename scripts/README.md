# 课程助教系统 - 启动脚本说明

## 快速开始

### Windows

```batch
# 启动服务
scripts\start.bat start

# 停止服务
scripts\start.bat stop

# 重启服务
scripts\start.bat restart

# 查看状态
scripts\start.bat status

# 查看日志
scripts\start.bat logs

# 跟踪日志
scripts\start.bat logs --follow
```

### Linux / Mac

```bash
# 启动服务
./scripts/start.sh start

# 停止服务
./scripts/start.sh stop

# 重启服务
./scripts/start.sh restart

# 查看状态
./scripts/start.sh status

# 查看日志
./scripts/start.sh logs

# 跟踪日志
./scripts/start.sh logs --follow

# 守护进程模式
./scripts/start.sh daemon
```

## 功能特性

### 1. 生命周期管理

- **启动**: 自动检测并启动前后端服务
- **停止**: 优雅停止所有服务
- **重启**: 先停止再启动
- **状态**: 显示所有服务运行状态

### 2. Daemon 守护进程模式

Linux/Mac 支持后台守护进程模式：

```bash
./scripts/start.sh daemon
```

Windows 可使用：

```batch
start /B python scripts\start.py daemon
```

### 3. 日志管理

所有日志保存在 `scripts/.logs/` 目录：

- `backend.log` - 后端日志
- `frontend.log` - 前端日志

查看日志：

```bash
# 查看最近 50 行
scripts/start.sh logs

# 跟踪日志输出
scripts/start.sh logs --follow
```

### 4. 跨平台适配

| 功能 | Windows | Linux/Mac |
|------|---------|-----------|
| 启动/停止 | ✓ | ✓ |
| 重启 | ✓ | ✓ |
| 状态查看 | ✓ | ✓ |
| 日志跟踪 | ✓ | ✓ |
| 守护进程 | ✗ | ✓ |

## 手动启动

如果不想使用启动脚本，也可以手动启动：

### 后端

```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 环境要求

### 必需

- Python 3.10+
- Node.js 18+
- Redis 6.0+

### 可选

- Git (用于版本控制)

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
scripts/start.sh logs --follow

# 检查端口占用
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000
```

### Redis 连接失败

```bash
# 检查 Redis 状态
# Windows: redis-cli ping
# Linux: redis-cli ping

# 启动 Redis
# Windows: redis-server
# Linux: sudo systemctl start redis
```

### 虚拟环境问题

```bash
# 重新创建虚拟环境
python -m venv .venv

# 激活并安装依赖
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
```

## 配置文件

启动脚本会读取以下环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `REDIS_HOST` | localhost | Redis 主机 |
| `REDIS_PORT` | 6379 | Redis 端口 |
| `SESSION_TTL` | 28800 | 会话过期时间 (秒) |

可在项目根目录创建 `.env` 文件配置：

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
SESSION_TTL=28800
```

## PID 文件

运行中的进程 PID 保存在 `scripts/.pids/` 目录：

- `main.pid` - 主进程信息
- `backend.pid` - 后端 PID
- `frontend.pid` - 前端 PID

手动清理 PID 文件：

```bash
rm scripts/.pids/*.pid  # Linux/Mac
del scripts\.pids\*.pid  # Windows
```
