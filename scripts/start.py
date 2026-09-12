#!/usr/bin/env python3
"""
课程助教系统 - 统一启动脚本

同时启动前后端服务，支持：
- 生命周期管理（启动/停止/重启）
- Daemon 守护进程模式
- Linux 和 Windows 跨平台适配

使用方法:
    python start.py start      # 启动服务
    python start.py stop       # 停止服务
    python start.py restart    # 重启服务
    python start.py status     # 查看状态
    python start.py logs       # 查看日志
"""
import os
import sys
import signal
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
PID_DIR = SCRIPTS_DIR / ".pids"
LOG_DIR = SCRIPTS_DIR / ".logs"

# 优先使用项目 venv 的 Python，确保依赖完整
# sys.executable 可能指向系统 Python（依赖不一定装全），venv 更可靠
if sys.platform == "win32":
    _VENV_PYTHON = str(BASE_DIR / ".venv" / "Scripts" / "python.exe")
else:
    _VENV_PYTHON = str(BASE_DIR / ".venv" / "bin" / "python")
PYTHON_EXE = _VENV_PYTHON if os.path.isfile(_VENV_PYTHON) else sys.executable

# 进程配置
PROCESSES = {
    "backend": {
        "name": "后端服务 (FastAPI)",
        "command": [
            PYTHON_EXE, "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ],
        "cwd": str(BASE_DIR),
        "env": {**os.environ},
    },
    "frontend": {
        "name": "前端服务 (Vite)",
        "command": ["npm.cmd", "run", "dev"]
        if sys.platform == "win32"
        else ["npm", "run", "dev"],
        "cwd": str(BASE_DIR / "frontend"),
        "env": {**os.environ},
    }
}

# PID 文件路径
PID_FILES = {
    "backend": PID_DIR / "backend.pid",
    "frontend": PID_DIR / "frontend.pid",
}

# 日志文件路径
LOG_FILES = {
    "backend": LOG_DIR / "backend.log",
    "frontend": LOG_DIR / "frontend.log",
}


def ensure_dirs():
    """确保所需目录存在。"""
    PID_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_pid(name: str) -> int | None:
    """获取进程 PID。"""
    pid_file = PID_FILES.get(name)
    if not pid_file or not pid_file.exists():
        return None
    
    try:
        return int(pid_file.read_text().strip())
    except (ValueError, IOError):
        return None


def is_process_running(pid: int) -> bool:
    """检查进程是否正在运行。"""
    if not pid:
        return False
    
    try:
        if sys.platform == "win32":
            # Windows: 使用 tasklist 检查进程
            # 注意：npm run dev 会启动 node 子进程，需要检查进程树
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                encoding="gbk",
                errors="replace"
            )
            if result.stdout and str(pid) in result.stdout:
                return True
            
            # 如果直接 PID 找不到，检查是否有 node 进程在运行（Vite 的子进程）
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq node.exe", "/FO", "CSV"],
                capture_output=True,
                text=True,
                encoding="gbk",
                errors="replace"
            )
            # 只要有 node 进程就认为前端在运行（简化检查）
            return result.returncode == 0 and "node.exe" in result.stdout
        else:
            # Linux/Mac: 使用 kill 0 检查
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
    except Exception:
        return False


def stop_process(name: str, pid: int, timeout: int = 5):
    """停止进程。"""
    print(f"  正在停止 {name} (PID: {pid})...")
    
    try:
        if sys.platform == "win32":
            # Windows: 使用 taskkill
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True
            )
        else:
            # Linux/Mac: 使用 kill
            os.kill(pid, signal.SIGTERM)
            
            # 等待进程退出
            for _ in range(timeout):
                if not is_process_running(pid):
                    break
                time.sleep(1)
            else:
                # 强制终止
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
    except Exception as e:
        print(f"  警告：停止 {name} 时出错：{e}")


def start_process(name: str, daemon: bool = False):
    """启动进程。"""
    config = PROCESSES[name]
    pid_file = PID_FILES[name]
    log_file = LOG_FILES[name]
    
    # 检查是否已在运行
    existing_pid = get_pid(name)
    if existing_pid and is_process_running(existing_pid):
        print(f"  {config['name']} 已在运行 (PID: {existing_pid})")
        return existing_pid
    
    # 准备日志文件（直接重定向 stdout，避免 PIPE 在 npm.cmd 退出后
    # 导致 node.exe 子进程写入 broken pipe 而崩溃）
    log_fh = open(log_file, "a", encoding="utf-8")
    
    # 启动进程
    print(f"  启动 {config['name']}...")
    
    try:
        if sys.platform == "win32":
            # Windows: 使用 CREATE_NEW_PROCESS_GROUP
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(
                config["command"],
                cwd=config["cwd"],
                env=config["env"],
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            # Linux/Mac: 使用 preexec_fn 创建新进程组
            process = subprocess.Popen(
                config["command"],
                cwd=config["cwd"],
                env=config["env"],
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                preexec_fn=os.setsid if not daemon else None,
            )
    except FileNotFoundError as e:
        log_fh.close()
        # 查找具体找不到的命令
        cmd_name = config["command"][0] if config["command"] else "unknown"
        raise RuntimeError(f"找不到命令：{cmd_name}，请确保已安装") from e
    
    # 写入 PID 文件
    pid_file.write_text(str(process.pid))
    print(f"  {config['name']} 已启动 (PID: {process.pid})")
    
    return process.pid


def start_all(daemon: bool = False):
    """启动所有服务。"""
    print("=" * 60)
    print("启动课程助教系统...")
    print("=" * 60)
    
    ensure_dirs()
    
    # 前置检查：确认 Python 解释器和关键依赖可用
    _preflight_check()
    
    # 检查后端是否已在运行
    backend_pid = get_pid("backend")
    if backend_pid and is_process_running(backend_pid):
        print(f"  后端服务已在运行 (PID: {backend_pid})")
    else:
        # 启动后端
        backend_pid = start_process("backend", daemon)
    
    # 等待后端启动
    print("  等待后端服务就绪...")
    time.sleep(3)
    
    # 检查前端是否已在运行
    frontend_pid = get_pid("frontend")
    if frontend_pid and is_process_running(frontend_pid):
        print(f"  前端服务已在运行 (PID: {frontend_pid})")
    else:
        # 启动前端
        frontend_pid = start_process("frontend", daemon)
    
    # 等待前端启动并验证
    print("  等待前端服务就绪...")
    if not _wait_for_port(5173, timeout=15):
        print("  ⚠ 前端服务在 15 秒内未就绪，请检查 scripts/.logs/frontend.log")
    else:
        print("  ✓ 前端服务已就绪")
    
    print("=" * 60)
    print("✓ 所有服务已启动")
    print("=" * 60)
    print(f"  后端 API:  http://localhost:8000")
    print(f"  前端页面：http://localhost:5173")
    print(f"  API 文档：http://localhost:8000/docs")
    print("=" * 60)
    
    # 写入主 PID 文件
    main_pid_file = PID_DIR / "main.pid"
    main_pid_file.write_text(json.dumps({
        "backend": backend_pid,
        "frontend": frontend_pid,
        "started_at": datetime.now().isoformat(),
    }))


def _preflight_check():
    """启动前检查：确认 Python 依赖、MySQL、Redis 可用。"""
    import socket
    import socket
    
    # 1. 检查 Python 依赖
    print("  [检查] Python 依赖...")
    result = subprocess.run(
        [PYTHON_EXE, "-c",
         "import importlib.util as u; deps=['fastapi','uvicorn','sqlalchemy','pymysql','redis','fakeredis','openai','langchain','langgraph','faiss','pypdf','dotenv']; missing=[d for d in deps if u.find_spec(d) is None]; print(','.join(missing) if missing else ''); exit(1 if missing else 0)"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        missing = result.stdout.strip() or "未知依赖"
        print(f"  ✗ Python 依赖缺失: {missing}")
        print(f"    请运行: {PYTHON_EXE} -m pip install -r requirements.txt")
        sys.exit(1)
    print("  ✓ Python 依赖完整")
    
    # 2. 检查 MySQL 端口
    print("  [检查] MySQL (:3306)...")
    if not _is_port_open("127.0.0.1", 3306):
        print("  ⚠ MySQL 未在 :3306 监听，后端将无法连接数据库")
        print("    请启动 MySQL 服务后再试")
        sys.exit(1)
    print("  ✓ MySQL 可连接")
    
    # 3. 检查 Redis（可选 — 降级 fakeredis）
    print("  [检查] Redis (:6379)...")
    if _is_port_open("127.0.0.1", 6379):
        print("  ✓ Redis 可连接")
    else:
        print("  ⚠ Redis 未在 :6379 监听，将降级为 fakeredis（重启后会话丢失）")
    
    # 4. 检查前端 node_modules
    node_modules = BASE_DIR / "frontend" / "node_modules"
    if not node_modules.exists():
        print("  ⚠ 前端 node_modules 不存在，请先运行: cd frontend && npm install")
        sys.exit(1)
    print("  ✓ 前端依赖已安装")


def _is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """检查 TCP 端口是否可连接。"""
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, OSError):
        return False


def _wait_for_port(port: int, timeout: int = 15) -> bool:
    """等待端口可连接，超时返回 False。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _is_port_open("127.0.0.1", port, timeout=1.0):
            return True
        time.sleep(1)
    return False


def stop_all():
    """停止所有服务。"""
    print("=" * 60)
    print("停止课程助教系统...")
    print("=" * 60)
    
    # 先停止前端（依赖后端）
    frontend_pid = get_pid("frontend")
    if frontend_pid and is_process_running(frontend_pid):
        stop_process("frontend", frontend_pid)
    else:
        print("  前端服务未运行")
    
    # 再停止后端
    backend_pid = get_pid("backend")
    if backend_pid and is_process_running(backend_pid):
        stop_process("backend", backend_pid)
    else:
        print("  后端服务未运行")
    
    # 清理 PID 文件
    for pid_file in PID_FILES.values():
        if pid_file.exists():
            pid_file.unlink()
    
    main_pid_file = PID_DIR / "main.pid"
    if main_pid_file.exists():
        main_pid_file.unlink()
    
    print("=" * 60)
    print("✓ 所有服务已停止")
    print("=" * 60)


def restart_all(daemon: bool = False):
    """重启所有服务。"""
    print("重启服务...")
    stop_all()
    time.sleep(2)
    start_all(daemon)


def show_status():
    """显示服务状态。"""
    print("=" * 60)
    print("课程助教系统状态")
    print("=" * 60)
    
    main_pid_file = PID_DIR / "main.pid"
    if not main_pid_file.exists():
        print("  服务未启动")
        return
    
    try:
        info = json.loads(main_pid_file.read_text())
        print(f"  启动时间：{info.get('started_at', '未知')}")
        print()
        
        for name in ["backend", "frontend"]:
            pid = get_pid(name)
            config = PROCESSES[name]
            running = pid and is_process_running(pid)
            
            status = "✓ 运行中" if running else "✗ 已停止"
            if pid and not running:
                status = "✗ 异常退出"
            
            print(f"  {config['name']}: {status} (PID: {pid or 'N/A'})")
        
        print()
        print(f"  后端 API:  http://localhost:8000")
        print(f"  前端页面：http://localhost:5173")
        print(f"  API 文档：http://localhost:8000/docs")
        
    except (json.JSONDecodeError, IOError) as e:
        print(f"  读取状态失败：{e}")
    
    print("=" * 60)


def show_logs(follow: bool = False, lines: int = 50):
    """显示日志。"""
    print("=" * 60)
    print("系统日志")
    print("=" * 60)
    
    for name, log_file in LOG_FILES.items():
        if not log_file.exists():
            continue
        
        print(f"\n--- {name} ---")
        
        try:
            content = log_file.read_text(encoding="utf-8")
            log_lines = content.splitlines()
            
            # 显示最后 N 行
            for line in log_lines[-lines:]:
                print(line)
            
            if follow:
                # 持续跟踪日志
                print(f"\n[跟踪 {name} 日志，按 Ctrl+C 停止...]")
                with open(log_file, "r", encoding="utf-8") as f:
                    f.seek(0, 2)  # 移动到文件末尾
                    while True:
                        line = f.readline()
                        if line:
                            print(line, end="")
                        else:
                            time.sleep(0.1)
        except Exception as e:
            print(f"  读取日志失败：{e}")


def main():
    """主函数。"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n可用命令:")
        print("  start     - 启动服务")
        print("  stop      - 停止服务")
        print("  restart   - 重启服务")
        print("  status    - 查看状态")
        print("  logs      - 查看日志")
        print("  daemon    - 守护进程模式启动")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_all(daemon=False)
    elif command == "stop":
        stop_all()
    elif command == "restart":
        restart_all(daemon=False)
    elif command == "status":
        show_status()
    elif command == "logs":
        follow = "--follow" in sys.argv or "-f" in sys.argv
        show_logs(follow=follow)
    elif command == "daemon":
        # 守护进程模式
        if sys.platform != "win32":
            # Linux/Mac: 使用 fork 创建守护进程
            pid = os.fork()
            if pid > 0:
                print(f"守护进程已启动 (PID: {pid})")
                sys.exit(0)
            
            # 创建新会话
            os.setsid()
            
            # 再次 fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
            
            # 重定向标准输出
            sys.stdout = open(LOG_DIR / "daemon.out", "a")
            sys.stderr = open(LOG_DIR / "daemon.err", "a")
        
        start_all(daemon=True)
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到退出信号，正在停止...")
            stop_all()
    else:
        print(f"未知命令：{command}")
        print("\n可用命令:")
        print("  start     - 启动服务")
        print("  stop      - 停止服务")
        print("  restart   - 重启服务")
        print("  status    - 查看状态")
        print("  logs      - 查看日志")
        print("  daemon    - 守护进程模式启动")
        sys.exit(1)


if __name__ == "__main__":
    main()
