@echo off
REM
REM 课程助教系统 - Windows 启动脚本 (Batch)
REM
REM 使用方法:
REM   start.bat start      - 启动服务
REM   start.bat stop       - 停止服务
REM   start.bat restart    - 重启服务
REM   start.bat status     - 查看状态
REM   start.bat logs       - 查看日志
REM   start.bat daemon     - 守护进程模式
REM

setlocal enabledelayedexpansion

REM 设置目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址：https://www.python.org/downloads/
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 18+
    echo 下载地址：https://nodejs.org/
    exit /b 1
)

REM 检查虚拟环境
if not exist "%PROJECT_DIR%\.venv\Scripts\activate.bat" (
    echo [ERROR] 未找到虚拟环境 .venv
    echo 请先运行：python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

REM 检查 node_modules
if not exist "%PROJECT_DIR%\frontend\node_modules" (
    echo [WARN] frontend/node_modules 不存在，正在安装依赖...
    cd /d "%PROJECT_DIR%\frontend"
    call npm install
    cd /d "%SCRIPT_DIR%"
)

REM 激活虚拟环境
call "%PROJECT_DIR%\.venv\Scripts\activate.bat"

REM 获取命令
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=help"

REM 执行命令
if /i "%COMMAND%"=="start" (
    python "%SCRIPT_DIR%start.py" start
) else if /i "%COMMAND%"=="stop" (
    python "%SCRIPT_DIR%start.py" stop
) else if /i "%COMMAND%"=="restart" (
    python "%SCRIPT_DIR%start.py" restart
) else if /i "%COMMAND%"=="status" (
    python "%SCRIPT_DIR%start.py" status
) else if /i "%COMMAND%"=="logs" (
    python "%SCRIPT_DIR%start.py" logs %2 %3 %4
) else if /i "%COMMAND%"=="daemon" (
    echo [INFO] Windows 不支持 daemon 模式，请直接使用 start 命令
    echo [INFO] 如需后台运行，可使用：start /B python start.py daemon
) else if /i "%COMMAND%"=="help" (
    echo 课程助教系统 - Windows 启动脚本
    echo.
    echo 使用方法:
    echo   %~nx0 start      - 启动服务
    echo   %~nx0 stop       - 停止服务
    echo   %~nx0 restart    - 重启服务
    echo   %~nx0 status     - 查看状态
    echo   %~nx0 logs       - 查看日志
    echo   %~nx0 daemon     - 守护进程模式 ^(不推荐^)
    echo.
    echo 示例:
    echo   %~nx0 start                  - 启动服务
    echo   %~nx0 logs                   - 查看日志
    echo   %~nx0 restart                - 重启服务
) else (
    echo [ERROR] 未知命令：%COMMAND%
    echo.
    echo 运行 '%~nx0 help' 查看帮助
    exit /b 1
)

endlocal
