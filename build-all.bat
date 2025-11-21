@echo off
REM ============================================
REM GameManager Build Script
REM Builds both GameManager.exe and GameManagerAdmin.exe
REM ============================================

echo.
echo ============================================
echo   GameManager Build Script
echo ============================================
echo.

REM Store the root directory
set ROOT_DIR=%cd%

REM ============================================
REM Build Frontend (GameManager.exe)
REM ============================================

echo [1/2] Building GameManager (Frontend)...
echo.

cd "%ROOT_DIR%\frontend"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo Building GameManager.exe...
call npx electron-packager . GameManager --platform=win32 --arch=x64 --out=dist --overwrite --ignore="dist|node_modules/((?!electron).)*$"
if errorlevel 1 (
    echo ERROR: Failed to build GameManager
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

echo.
echo [SUCCESS] GameManager built successfully!
echo Location: %ROOT_DIR%\frontend\dist\GameManager-win32-x64\
echo.

REM ============================================
REM Build Admin Dashboard (GameManagerAdmin.exe)
REM ============================================

echo [2/2] Building GameManagerAdmin (Admin Dashboard)...
echo.

cd "%ROOT_DIR%\admin-dashboard"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing admin dashboard dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install admin dashboard dependencies
        cd "%ROOT_DIR%"
        pause
        exit /b 1
    )
)

echo Building GameManagerAdmin.exe...
call npx electron-packager . GameManagerAdmin --platform=win32 --arch=x64 --out=dist --overwrite --ignore="dist|node_modules/((?!electron).)*$"
if errorlevel 1 (
    echo ERROR: Failed to build GameManagerAdmin
    cd "%ROOT_DIR%"
    pause
    exit /b 1
)

echo.
echo [SUCCESS] GameManagerAdmin built successfully!
echo Location: %ROOT_DIR%\admin-dashboard\dist\GameManagerAdmin-win32-x64\
echo.

REM ============================================
REM Build Complete
REM ============================================

cd "%ROOT_DIR%"

echo ============================================
echo   BUILD COMPLETE!
echo ============================================
echo.
echo Built Applications:
echo   1. GameManager.exe
echo      Location: %ROOT_DIR%\frontend\dist\GameManager-win32-x64\GameManager.exe
echo.
echo   2. GameManagerAdmin.exe
echo      Location: %ROOT_DIR%\admin-dashboard\dist\GameManagerAdmin-win32-x64\GameManagerAdmin.exe
echo.
echo IMPORTANT: To run these apps, you need:
echo   - Copy the ENTIRE folder (not just the .exe)
echo   - The backend server must be running (python backend\run.py)
echo.
echo ============================================
echo.

pause
