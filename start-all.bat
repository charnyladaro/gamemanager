@echo off
REM ============================================
REM GameManager - Start All Services
REM Starts Backend, Frontend, and Admin Dashboard
REM ============================================

echo.
echo ============================================
echo   GameManager - Starting All Services
echo ============================================
echo.

REM Store the root directory
set ROOT_DIR=%cd%

REM Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
where node >nul 2>nul
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo [1/3] Starting Backend Server (Flask)...
start "GameManager Backend" cmd /k "cd /d %ROOT_DIR%\backend && python run.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend (User Client)...
start "GameManager Frontend" cmd /k "cd /d %ROOT_DIR%\frontend && npm start"
timeout /t 2 /nobreak >nul

echo [3/3] Starting Admin Dashboard...
start "GameManager Admin" cmd /k "cd /d %ROOT_DIR%\admin-dashboard && npm start"

echo.
echo ============================================
echo   ALL SERVICES STARTED!
echo ============================================
echo.
echo Running Services:
echo   - Backend API: http://localhost:5000
echo   - User Client: Electron window
echo   - Admin Dashboard: Electron window
echo.
echo Press Ctrl+C in each window to stop services
echo.
echo Close this window safely - services run in separate windows
echo ============================================
echo.

pause
