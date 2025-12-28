# Local Development Setup Guide

This guide helps you run the Classroom Engagement System locally without Docker, supporting both Linux and Windows.

## Prerequisites

### Linux (Fedora/RHEL)
```bash
# Install system dependencies
sudo dnf install -y python3 python3-devel python3-pip nodejs npm

# Install and start MongoDB
sudo dnf install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Install and start Redis
sudo dnf install -y redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-dev python3-pip nodejs npm

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-8.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Install Redis
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 node mongodb-community redis

# Start services
brew services start mongodb-community
brew services start redis
```

### Windows
1. **Python**: Download from [python.org](https://www.python.org/downloads/)
2. **Node.js**: Download from [nodejs.org](https://nodejs.org/)
3. **MongoDB**: Download from [mongodb.com](https://www.mongodb.com/try/download/community)
4. **Redis**: Download from [memurai.com](https://www.memurai.com/) or use WSL2

## Quick Start

### Option 1: Automated Setup (Recommended for Linux/macOS)

```bash
cd /path/to/classroom-engagement-system
bash start-local.sh
```

This script will:
- Check for required services (Redis, MongoDB)
- Create Python virtual environment
- Install dependencies
- Create `.env` files
- Display instructions for starting services

### Option 2: Manual Setup

#### 1. Create and Activate Virtual Environment

**Linux/macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

#### 2. Install Python Dependencies

```bash
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

Note: If `torch` or `pyannote-audio` fail to install, you can skip them initially:
```bash
pip install -r requirements.txt --ignore-installed torch pyannote-audio
```

#### 3. Create Environment Files

**Backend** - Create `backend/.env`:
```
MONGODB_URL=mongodb://localhost:27017/classroom
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
DEBUG=true
```

**Frontend** - Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

#### 4. Start Services in Separate Terminals

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate.bat  # Windows

python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Terminal 3 - Celery Worker (Optional, for async tasks):**
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate.bat  # Windows

celery -A app.tasks.celery_app worker --loglevel=info
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## Service Status

### Check MongoDB Status

**Linux:**
```bash
sudo systemctl status mongod
```

**macOS:**
```bash
brew services list | grep mongodb
```

**Windows:** Check MongoDB in Services application

### Check Redis Status

**Linux:**
```bash
sudo systemctl status redis-server
# or redis-cli ping
```

**macOS:**
```bash
brew services list | grep redis
# or redis-cli ping
```

**Windows:** Check Memurai in Services application, or use `redis-cli ping`

## Troubleshooting

### MongoDB Connection Error
```
Error: Failed to connect to mongodb://localhost:27017
```
**Solution:**
- Verify MongoDB is running: `mongod --version`
- Start MongoDB:
  - Linux: `sudo systemctl start mongod`
  - macOS: `brew services start mongodb-community`
  - Windows: Start MongoDB service from Services app

### Redis Connection Error
```
Error: Failed to connect to redis://localhost:6379
```
**Solution:**
- Verify Redis is running: `redis-cli ping` (should return PONG)
- Start Redis:
  - Linux: `sudo systemctl start redis-server`
  - macOS: `brew services start redis`
  - Windows: Start Memurai from Services app

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution:** Change the port in the command:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### Python Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Node Modules Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Project Structure

```
classroom-engagement-system/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Configuration
│   │   ├── models/            # MongoDB models
│   │   ├── routes/            # API routes
│   │   ├── tasks/             # Celery tasks
│   │   └── utils/             # Utilities
│   ├── venv/                  # Virtual environment (created by setup)
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (created by setup)
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.jsx           # Main component
│   │   ├── components/       # React components
│   │   └── styles/           # CSS files
│   ├── package.json          # Node dependencies
│   └── .env                  # Environment variables (created by setup)
│
├── start-local.sh            # Linux/macOS startup script
└── start-local.bat           # Windows startup script
```

## Environment Variables

### Backend (backend/.env)
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string
- `CELERY_BROKER_URL`: Celery broker URL (usually Redis)
- `CELERY_RESULT_BACKEND`: Celery result backend (usually Redis)
- `DEBUG`: Enable debug mode (true/false)

### Frontend (frontend/.env)
- `VITE_API_URL`: Backend API base URL

## Optional: Installing Heavy Dependencies

### PyTorch (for GPU acceleration)
```bash
# CPU version
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# CUDA 12.1 version (for NVIDIA GPUs)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Pyannote Audio (for speaker diarization)
```bash
pip install pyannote.audio
# Requires HuggingFace token for model access
```

## Production Deployment

For production, use Docker:
```bash
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Docker deployment instructions.

## Getting Help

- Check backend logs: Terminal 1
- Check frontend logs: Terminal 2
- Check API docs: http://localhost:8000/docs
- Check browser console: Press F12 in frontend browser tab
