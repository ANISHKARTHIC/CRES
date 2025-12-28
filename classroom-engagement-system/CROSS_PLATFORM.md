# Cross-Platform Setup Guide

This guide ensures the Classroom Engagement System works seamlessly on Docker, local Linux, local macOS, and local Windows.

## Deployment Options

### 1. Docker (All Platforms)
Most reliable way to ensure consistency across all machines.

```bash
docker-compose up --build
```

**Pros:**
- Same environment on all machines
- Easy to deploy to cloud
- No dependency on local installations

**Cons:**
- Requires Docker installation
- Slower than native

---

### 2. Local Development (Linux/macOS/Windows)
Best for development and debugging.

---

## Environment Detection & Configuration

### Automatic Detection

The project uses environment variables to detect and configure for different platforms:

```bash
# Detect OS and set appropriate paths
OS=$(uname -s)
case "${OS}" in
    Linux*)   OS_TYPE="Linux";;
    Darwin*)  OS_TYPE="MacOS";;
    MINGW*)   OS_TYPE="Windows";;
    MSYS*)    OS_TYPE="Windows";;
    *)        OS_TYPE="UNKNOWN";;
esac
```

### Environment Files

#### Linux/macOS vs Windows Paths

```
# Linux/macOS
backend/venv/bin/python
backend/venv/bin/activate

# Windows
backend\venv\Scripts\python.exe
backend\venv\Scripts\activate.bat
```

---

## Platform-Specific Setup

### Linux (Fedora/RHEL)

**Install Dependencies:**
```bash
sudo dnf install -y \
    python3 python3-devel python3-pip \
    nodejs npm \
    mongodb-org \
    redis
```

**Start Services:**
```bash
sudo systemctl start mongod
sudo systemctl start redis-server
```

**Setup Project:**
```bash
bash start-local.sh
```

### Linux (Ubuntu/Debian)

**Install Dependencies:**
```bash
sudo apt update && sudo apt install -y \
    python3 python3-venv python3-dev python3-pip \
    nodejs npm \
    mongodb \
    redis-server
```

**Start Services:**
```bash
sudo systemctl start mongodb
sudo systemctl start redis-server
```

**Setup Project:**
```bash
bash start-local.sh
```

### macOS

**Install Dependencies:**
```bash
brew install python@3.11 node mongodb-community redis
```

**Start Services:**
```bash
brew services start mongodb-community
brew services start redis
```

**Setup Project:**
```bash
bash start-local.sh
```

### Windows

**Install via Chocolatey (Recommended):**
```powershell
choco install python nodejs mongodb-community redis-64 -y
```

**Or Manual Installation:**
1. Download Python from https://www.python.org/downloads/
2. Download Node.js from https://nodejs.org/
3. Download MongoDB from https://www.mongodb.com/try/download/community
4. Download Redis from https://www.memurai.com/

**Start Services:**
```powershell
# MongoDB
net start MongoDB

# Redis (if installed as service)
net start Redis
```

**Setup Project:**
```bash
start-local.bat
```

---

## Port Configuration

The application uses these ports by default:

| Service | Port | Environment Variable |
|---------|------|----------------------|
| Backend (FastAPI) | 8000 | N/A |
| Frontend (React) | 3000 | N/A |
| MongoDB | 27017 | MONGODB_URL |
| Redis | 6379 | REDIS_URL |

### Changing Ports

**Backend Port:**
```bash
python -m uvicorn app.main:app --port 8001
```

**Frontend Port (Windows):**
```bash
set PORT=3001 && npm start
```

**Frontend Port (Linux/macOS):**
```bash
PORT=3001 npm start
```

---

## Database Configuration

### MongoDB Connection Strings

**Local (Default):**
```
mongodb://localhost:27017/classroom
```

**With Authentication:**
```
mongodb://username:password@localhost:27017/classroom
```

**Docker (from docker-compose.yml):**
```
mongodb://root:rootpassword@mongodb:27017/classroom?authSource=admin
```

### Redis Connection Strings

**Local (Default):**
```
redis://localhost:6379
```

**Docker (from docker-compose.yml):**
```
redis://redis:6379
```

---

## Python Virtual Environment Management

### Creation

**Linux/macOS:**
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

**Windows:**
```bash
python -m venv backend\venv
backend\venv\Scripts\activate.bat
```

### Dependency Installation

```bash
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Handling Platform-Specific Issues

**Issue: `distutils` module not found (Python 3.13)**
```bash
pip install setuptools
```

**Issue: PyTorch download timeout**
```bash
# Install CPU version
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Or skip it
pip install -r requirements.txt --ignore-installed torch
```

**Issue: Pyannote-audio installation fails**
```bash
# It's optional; core functionality works without it
pip install -r requirements.txt --ignore-installed pyannote-audio
```

---

## Service Health Checks

### Check if Services are Running

**MongoDB:**
```bash
# Linux/macOS
mongosh --eval "db.adminCommand('ping')"

# Windows
mongosh --eval "db.adminCommand('ping')"
```

**Redis:**
```bash
# All platforms
redis-cli ping
# Should return: PONG
```

**Backend:**
```bash
curl http://localhost:8000/health
```

**Frontend:**
```bash
curl http://localhost:3000
```

---

## Cross-Platform Script Examples

### Universal Environment Setup Script

```bash
#!/bin/bash
# setup-universal.sh

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)   OS_TYPE="Linux";;
    Darwin*)  OS_TYPE="MacOS";;
    *)        OS_TYPE="Windows";;
esac

echo "Detected OS: $OS_TYPE"

# Create venv
if [ "$OS_TYPE" = "Windows" ]; then
    python -m venv backend\venv
    backend\venv\Scripts\activate.bat
else
    python3 -m venv backend/venv
    source backend/venv/bin/activate
fi

# Install dependencies
pip install --upgrade pip setuptools
pip install -r backend/requirements.txt

echo "Setup complete!"
```

---

## Troubleshooting by Platform

### Linux Issues

**`sudo: systemctl: command not found`**
- Using non-systemd distro; manually start services instead

**`port 8000 already in use`**
```bash
lsof -i :8000  # Find what's using it
kill -9 <PID>  # Kill the process
```

### macOS Issues

**`brew: command not found`**
- Install Homebrew first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

**`permission denied while trying to connect to Docker daemon`**
```bash
sudo chown -R $(whoami):docker /var/run/docker.sock
```

### Windows Issues

**`python: command not found`**
- Python not in PATH; reinstall with "Add Python to PATH" option

**`npm: command not found`**
- Node.js not in PATH; restart terminal after installation

**`port already in use`**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## CI/CD Compatibility

### GitHub Actions Example

```yaml
name: Test on Multiple Platforms

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
      
      - name: Run tests
        run: |
          pytest backend/
```

---

## Production Deployment

### Docker to Cloud (Recommended)

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Push to registry
docker tag classroom-engagement-system:latest myregistry/classroom:latest
docker push myregistry/classroom:latest

# Deploy to cloud platform
# AWS: aws ecs create-service ...
# GCP: gcloud run deploy ...
# Azure: az container create ...
```

### Local to Cloud

For local installations, it's recommended to use Docker for deployment to ensure consistency.

---

## Summary Table

| Feature | Docker | Linux | macOS | Windows |
|---------|--------|-------|-------|---------|
| Installation Ease | Easy | Medium | Medium | Medium |
| Development Speed | Slow | Fast | Fast | Fast |
| Consistency | Best | Good | Good | Good |
| Production Ready | Excellent | Good | Good | Good |
| Learning Curve | Low | Low | Low | Medium |

**Recommendation:**
- **Development**: Use local setup for fast iteration
- **Production**: Use Docker for consistency and reliability
- **CI/CD**: Use Docker for reproducible builds
