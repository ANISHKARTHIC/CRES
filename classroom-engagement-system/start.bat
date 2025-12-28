@echo off
REM Build and start the Classroom Engagement System (Windows)

echo.
echo 🚀 Classroom Engagement System - Startup Script (Windows)
echo ========================================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker for Windows.
    pause
    exit /b 1
)

echo ✅ Docker is installed
echo.

REM Create .env files if they don't exist
if not exist "backend\.env" (
    echo 📝 Creating backend\.env from template...
    copy backend\.env.example backend\.env
    echo    Created backend\.env - Update with your settings if needed
)

if not exist "frontend\.env" (
    echo 📝 Creating frontend\.env from template...
    copy frontend\.env.example frontend\.env
    echo    Created frontend\.env - Update with your settings if needed
)

echo.
echo 🐳 Building Docker images...
docker-compose build --no-cache

echo.
echo 🚀 Starting services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to start (30 seconds)...
timeout /t 30

echo.
echo ✅ Services started!
echo.
echo 📍 Access the application:
echo    Frontend: http://localhost:3000
echo    API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📊 View logs:
echo    docker-compose logs -f
echo.
echo 🛑 Stop services:
echo    docker-compose down
echo.
echo 🎉 Classroom Engagement System is running!
pause
