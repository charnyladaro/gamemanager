@echo off
REM ============================================
REM GameManager - Install All Dependencies
REM Installs Python and Node.js dependencies
REM ============================================

echo.
echo ============================================
echo   GameManager - Dependency Installer
echo ============================================
echo.

REM Store the root directory
set ROOT_DIR=%cd%

REM ============================================
REM Install Backend Dependencies (Python)
REM ============================================

echo [1/3] Installing Backend Dependencies (Python)...
echo.

cd "%ROOT_DIR%\backend"

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Backend dependencies installed!
echo.

REM ============================================
REM Install Frontend Dependencies (Node.js)
REM ============================================

echo [2/3] Installing Frontend Dependencies (Node.js)...
echo.

cd "%ROOT_DIR%\frontend"

if not exist "package.json" (
    echo ERROR: package.json not found
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

call npm install

if errorlevel 1 (
    echo ERROR: Failed to install Frontend dependencies
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Frontend dependencies installed!
echo.

REM ============================================
REM Install Admin Dashboard Dependencies (Node.js)
REM ============================================

echo [3/3] Installing Admin Dashboard Dependencies (Node.js)...
echo.

cd "%ROOT_DIR%\admin-dashboard"

if not exist "package.json" (
    echo ERROR: package.json not found
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

call npm install

if errorlevel 1 (
    echo ERROR: Failed to install Admin Dashboard dependencies
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Admin Dashboard dependencies installed!
echo.

REM ============================================
REM Installation Complete
REM ============================================

cd "%ROOT_DIR%"

echo ============================================
echo   ALL DEPENDENCIES INSTALLED!
echo ============================================
echo.
echo Next Steps:
echo   1. Run 'start-all.bat' to start all services
echo   2. Or run 'build-all.bat' to build executables
echo.
echo ============================================
echo.

pause
