@echo off
title SkyGuard AI - Team AetherX
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Python virtual environment not found.
    echo Create/activate your existing .venv first.
    echo.
    pause
    exit /b 1
)

echo Starting SkyGuard AI...
".venv\Scripts\python.exe" desktop_app.py
pause
