#!/bin/bash
# Local development startup script for Classroom Engagement System
# Works on Linux/macOS - for Windows use start-local.bat

set -e

echo "🚀 Classroom Engagement System - Local Startup"
echo "=============================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*) OS_TYPE="Linux";;
    Darwin*) OS_TYPE="MacOS";;
    *) OS_TYPE="UNKNOWN";;
esac

echo "📍 Detected OS: $OS_TYPE"
echo ""

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! command -v redis-cli &> /dev/null && ! command -v valkey-cli &> /dev/null; then
    echo "❌ Redis/Valkey not found. Please install Redis first."
    echo "   Linux (Fedora): sudo dnf install redis"
    echo "   Linux (Ubuntu): sudo apt install redis-server"
    echo "   macOS: brew install redis"
    exit 1
fi

# Check if MongoDB is running
echo "🔍 Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    if [ "$OS_TYPE" = "Linux" ]; then
        echo "⚠️  MongoDB not running. Starting MongoDB..."
        sudo systemctl start mongod 2>/dev/null || echo "Could not start MongoDB via systemctl"
    elif [ "$OS_TYPE" = "MacOS" ]; then
        echo "⚠️  MongoDB not running. Starting MongoDB..."
        brew services start mongodb-community 2>/dev/null || echo "Could not start MongoDB via brew"
    fi
fi

echo "✅ Services checked"
echo ""

# Setup virtual environment
echo "📦 Setting up Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "📦 Installing backend dependencies..."
source backend/venv/bin/activate
pip install -q --upgrade pip setuptools
pip install -q -r backend/requirements.txt 2>/dev/null || {
    echo "⚠️  Some optional packages failed to install (pyannote-audio, torch)"
    echo "    Core dependencies installed. You can install missing ones manually."
}

echo "✅ Backend dependencies ready"
echo ""

# Create .env files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env..."
    cat > backend/.env << 'EOF'
MONGODB_URL=mongodb://localhost:27017/classroom
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
DEBUG=true
EOF
    echo "✅ backend/.env created"
fi

if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend/.env..."
    cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
    echo "✅ frontend/.env created"
fi

echo ""
echo "🎯 Ready to start services!"
echo ""
echo "📋 To start the services, run in separate terminals:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   cd frontend && npm start"
echo ""
echo "   Terminal 3 (Celery Worker - optional):"
echo "   cd backend && source venv/bin/activate && celery -A app.tasks.celery_app worker --loglevel=info"
echo ""
echo "🌐 Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
