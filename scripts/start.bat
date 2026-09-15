@echo off
chcp 65001 >nul 2>&1
REM Course TA System - Windows startup script
REM Double-click to start; or pass: start / stop / restart / status / logs

setlocal enabledelayedexpansion

REM Set directories
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 18+
    echo 下载地址：https://nodejs.org/
    pause
    exit /b 1
)

REM Check venv
if not exist "%PROJECT_DIR%\.venv\Scripts\activate.bat" (
    echo [ERROR] 未找到虚拟环境 .venv
    echo 请先运行：python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check node_modules
if not exist "%PROJECT_DIR%\frontend\node_modules" (
    echo [WARN] frontend/node_modules 不存在，正在安装依赖...
    cd /d "%PROJECT_DIR%\frontend"
    call npm install
    cd /d "%SCRIPT_DIR%"
)

REM Activate venv
call "%PROJECT_DIR%\.venv\Scripts\activate.bat"

REM Default command is start (double-click to launch)
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=start"

REM Run command
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
) else (
    echo [ERROR] 未知命令：%COMMAND%
    echo.
    echo 可用命令: start / stop / restart / status / logs
)

if "%COMMAND%"=="start" (
    echo.
    echo 浏览器访问 http://localhost:5173 即可使用
    echo 按任意键关闭此窗口（服务继续在后台运行）
    pause >nul
)

endlocal
