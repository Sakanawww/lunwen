#!/bin/bash
#
# 课程助教系统 - Linux/Mac 启动脚本
#
# 使用方法:
#   ./start.sh start      # 启动服务
#   ./start.sh stop       # 停止服务
#   ./start.sh restart    # 重启服务
#   ./start.sh status     # 查看状态
#   ./start.sh logs       # 查看日志
#   ./start.sh daemon     # 守护进程模式
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 是否可用
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 python3，请先安装 Python 3.10+"
        exit 1
    fi
}

# 检查 Node.js 是否可用
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "未找到 node，请先安装 Node.js 18+"
        exit 1
    fi
}

# 检查 Redis 是否运行
check_redis() {
    if ! command -v redis-cli &> /dev/null; then
        print_warn "未找到 redis-cli，请确保 Redis 服务正在运行"
        return
    fi
    
    if ! redis-cli ping &> /dev/null; then
        print_warn "Redis 服务未运行，请启动 Redis"
        print_info "  启动命令：redis-server 或 systemctl start redis"
    fi
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "$PROJECT_DIR/.venv" ]; then
        print_error "未找到虚拟环境 .venv"
        print_info "请先运行：python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
}

# 检查 node_modules
check_node_modules() {
    if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
        print_warn "frontend/node_modules 不存在，正在安装依赖..."
        cd "$PROJECT_DIR/frontend"
        npm install
        cd "$PROJECT_DIR"
    fi
}

# 主函数
main() {
    local command="${1:-help}"
    
    # 前置检查
    check_python
    check_node
    check_redis
    check_venv
    check_node_modules
    
    # 执行命令
    case "$command" in
        start|stop|restart|status|logs)
            cd "$SCRIPT_DIR"
            source "$PROJECT_DIR/.venv/bin/activate"
            python3 start.py "$command" "$@"
            ;;
        daemon)
            cd "$SCRIPT_DIR"
            source "$PROJECT_DIR/.venv/bin/activate"
            nohup python3 start.py daemon > /dev/null 2>&1 &
            print_info "守护进程已启动"
            ;;
        help|--help|-h)
            echo "课程助教系统 - 启动脚本"
            echo ""
            echo "使用方法:"
            echo "  $0 start      - 启动服务"
            echo "  $0 stop       - 停止服务"
            echo "  $0 restart    - 重启服务"
            echo "  $0 status     - 查看状态"
            echo "  $0 logs       - 查看日志"
            echo "  $0 daemon     - 守护进程模式"
            echo "  $0 help       - 显示帮助"
            echo ""
            echo "选项:"
            echo "  -f, --follow  跟踪日志输出 (仅 logs 命令)"
            echo ""
            echo "示例:"
            echo "  $0 start                  # 启动服务"
            echo "  $0 logs --follow          # 跟踪日志"
            echo "  $0 restart                # 重启服务"
            ;;
        *)
            print_error "未知命令：$command"
            echo ""
            echo "运行 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

main "$@"
