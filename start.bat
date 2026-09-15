@echo off
chcp 65001 >nul 2>&1
REM 根目录一键启动入口 — 转发到 scripts/start.bat
call "%~dp0scripts\start.bat" %*
