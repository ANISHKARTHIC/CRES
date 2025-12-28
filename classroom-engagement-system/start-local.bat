@echo off
REM Local development startup script for Classroom Engagement System (Windows)
REM For Linux/macOS use start-local.sh

setlocal enabledelayedexpansion

echo.
echo Classroom Engagement System - Local Startup (Windows)
echo =====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.9 or later.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found. Please install Node.js.
    exit /b 1
)

echo Python and Node.js found
echo.

REM Setup virtual environment
echo Setting up Python virtual environment...
if not exist "backend\venv" (
    python -m venv backend\venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo Installing backend dependencies...
call backend\venv\Scripts\activate.bat
pip install -q --upgrade pip setuptools
pip install -q -r backend\requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Some packages failed to install ^(pyannote-audio, torch^)
    echo Core dependencies installed. You can install missing ones manually.
)

echo Backend dependencies ready
echo.

REM Create .env files if they don't exist
if not exist "backend\.env" (
    echo Creating backend\.env...
    (
        echo MONGODB_URL=mongodb://localhost:27017/classroom
        echo REDIS_URL=redis://localhost:6379
        echo CELERY_BROKER_URL=redis://localhost:6379
        echo CELERY_RESULT_BACKEND=redis://localhost:6379
        echo DEBUG=true
    ) > backend\.env
    echo backend\.env created
)

if not exist "frontend\.env" (
    echo Creating frontend\.env...
    (
        echo VITE_API_URL=http://localhost:8000
    ) > frontend\.env
    echo frontend\.env created
)

echo.
echo Ready to start services!
echo.
echo To start the services, run in separate terminals:
echo.
echo Terminal 1 (Backend^):
echo cd backend
echo venv\Scripts\activate.bat
echo python -m uvicorn app.main:app --reload --port 8000
echo.
echo Terminal 2 (Frontend^):
echo cd frontend
echo npm start
echo.
echo Terminal 3 (Celery Worker - optional^):
echo cd backend
echo venv\Scripts\activate.bat
echo celery -A app.tasks.celery_app worker --loglevel=info
echo.
echo Access the application at:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
