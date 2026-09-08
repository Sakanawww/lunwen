#!/usr/bin/env bash
# 确保干净启动：先杀掉残留，再用 venv 解释器启动单个实例
set -e
cd "$(dirname "$0")"
powershell -Command "Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force" 2>/dev/null
sleep 2
exec .venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
