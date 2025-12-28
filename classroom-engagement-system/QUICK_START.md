#!/bin/bash
# Quick Start Guide - Print this to understand how to use the system

cat << 'EOF'

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        🎓 Classroom Engagement System - Quick Start Guide 🎓                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 PROJECT OVERVIEW
───────────────────────────────────────────────────────────────────────────────
The Classroom Engagement System analyzes speaker participation in classroom
recordings using speaker diarization and engagement metrics.

🎯 KEY FEATURES
───────────────────────────────────────────────────────────────────────────────
✓ Speaker Diarization - Identify different speakers in recordings
✓ Participation Analysis - Measure speaking time and turn-taking
✓ Engagement Metrics - Calculate engagement scores
✓ Interactive Dashboard - Visualize results with charts and waveforms
✓ REST API - Programmatic access to all features
✓ WebSocket Support - Real-time audio streaming

🚀 RUNNING THE APPLICATION
───────────────────────────────────────────────────────────────────────────────

OPTION 1: Using Docker (All Platforms)
───────────────────────────────────────
Run once, works everywhere (Linux, macOS, Windows with Docker Desktop):

    docker-compose up --build

    Access at: http://localhost:3000

OPTION 2: Local Development (Linux/macOS)
──────────────────────────────────────────
Fastest for development, requires local setup:

    bash start-local.sh

    Then start services in separate terminals:
    
    Terminal 1 (Backend):
    cd backend && source venv/bin/activate
    python -m uvicorn app.main:app --reload --port 8000
    
    Terminal 2 (Frontend):
    cd frontend && npm start
    
    Access at: http://localhost:3000

OPTION 3: Local Development (Windows)
──────────────────────────────────────
    start-local.bat
    
    Then start services in separate terminals:
    
    Terminal 1 (Backend):
    cd backend
    venv\Scripts\activate.bat
    python -m uvicorn app.main:app --reload --port 8000
    
    Terminal 2 (Frontend):
    cd frontend
    npm start
    
    Access at: http://localhost:3000

🌐 ACCESS POINTS
───────────────────────────────────────────────────────────────────────────────

Frontend Application
  URL:     http://localhost:3000
  Purpose: Upload recordings and view analysis

Backend API
  URL:     http://localhost:8000
  Docs:    http://localhost:8000/docs      (Swagger UI)
  Redoc:   http://localhost:8000/redoc     (Alternative docs)
  Health:  http://localhost:8000/health    (Status check)

📚 DOCUMENTATION
───────────────────────────────────────────────────────────────────────────────

Local Setup Instructions
  File: LOCAL_SETUP.md
  For: Detailed platform-specific setup

Cross-Platform Deployment
  File: CROSS_PLATFORM.md
  For: Understanding platform differences

Project Architecture
  File: ARCHITECTURE.md
  For: Technical deep-dive

API Reference
  File: API_DOCUMENTATION.md
  For: Endpoint documentation

Deployment Guide
  File: DEPLOYMENT.md
  For: Production deployment

🎮 USING THE APPLICATION
───────────────────────────────────────────────────────────────────────────────

1. UPLOAD A RECORDING
   - Go to http://localhost:3000
   - Click "Upload Meeting" button
   - Select an audio file (MP3, WAV, etc.)
   - Wait for processing to complete

2. VIEW ANALYSIS
   - See speaker participation breakdown
   - View engagement metrics
   - Explore interactive waveform visualization
   - Check turn-taking frequency and participation balance

3. USE THE API (PROGRAMMATICALLY)
   - POST /api/meetings/upload - Upload recording
   - GET /api/meetings - List all meetings
   - GET /api/meetings/{id} - Get analysis results
   - DELETE /api/meetings/{id} - Delete recording

🛠️ COMMON COMMANDS
───────────────────────────────────────────────────────────────────────────────

Check Backend Status
  curl http://localhost:8000/health

Check API Documentation
  Visit: http://localhost:8000/docs

Restart Backend
  Press Ctrl+C in backend terminal
  Run: python -m uvicorn app.main:app --reload --port 8000

Restart Frontend
  Press Ctrl+C in frontend terminal
  Run: npm start

Clear Node Modules (if issues)
  cd frontend && rm -rf node_modules package-lock.json && npm install

Stop All Services
  Press Ctrl+C in all terminals
  Or: docker-compose down (for Docker)

🐛 TROUBLESHOOTING
───────────────────────────────────────────────────────────────────────────────

Backend won't start?
  ✓ Check if port 8000 is already in use
  ✓ Ensure MongoDB and Redis are running
  ✓ Check that virtual environment is activated
  ✓ See LOCAL_SETUP.md for platform-specific issues

Frontend won't start?
  ✓ Check if port 3000 is already in use
  ✓ Ensure Node.js is installed (node --version)
  ✓ Try: rm -rf node_modules && npm install
  ✓ Check that backend is running

Can't connect to database?
  ✓ MongoDB: mongosh --eval "db.adminCommand('ping')"
  ✓ Redis: redis-cli ping (should return PONG)
  ✓ See LOCAL_SETUP.md for service startup instructions

⚙️ ENVIRONMENT SETUP
───────────────────────────────────────────────────────────────────────────────

Backend Configuration (backend/.env)
  MONGODB_URL=mongodb://localhost:27017/classroom
  REDIS_URL=redis://localhost:6379
  DEBUG=true (for development)

Frontend Configuration (frontend/.env)
  VITE_API_URL=http://localhost:8000

🔧 OPTIONAL FEATURES
───────────────────────────────────────────────────────────────────────────────

Background Job Processing with Celery
  cd backend && source venv/bin/activate
  celery -A app.tasks.celery_app worker --loglevel=info

Speaker Diarization (Advanced)
  pip install pyannote.audio
  Requires HuggingFace token for model access

GPU Acceleration (Optional)
  pip install torch --index-url https://download.pytorch.org/whl/cu121
  (Requires NVIDIA GPU with CUDA support)

📦 PROJECT STRUCTURE
───────────────────────────────────────────────────────────────────────────────

backend/              - FastAPI backend server
  ├── app/            - Application code
  │   ├── main.py     - FastAPI entry point
  │   ├── config.py   - Configuration
  │   ├── models/     - MongoDB models
  │   ├── routes/     - API endpoints
  │   ├── tasks/      - Background tasks
  │   └── utils/      - Utilities
  ├── venv/           - Virtual environment
  ├── requirements.txt - Python dependencies
  └── .env            - Environment variables

frontend/            - React frontend application
  ├── src/            - React components
  ├── public/         - Static files
  ├── package.json    - Node dependencies
  └── .env            - Environment variables

docker-compose.yml   - Docker orchestration
start-local.sh       - Linux/macOS setup script
start-local.bat      - Windows setup script

📞 SUPPORT & LEARNING
───────────────────────────────────────────────────────────────────────────────

Quick References:
  • README.md - Project overview
  • LOCAL_SETUP.md - Detailed setup guide
  • CROSS_PLATFORM.md - Platform-specific info
  • API_DOCUMENTATION.md - API endpoints
  • ARCHITECTURE.md - Technical design

Tech Stack:
  Backend:  FastAPI, Python, MongoDB, Redis, Celery
  Frontend: React, Vite, Tailwind CSS
  Tools:    Docker, Uvicorn, Webpack

🎉 YOU'RE ALL SET!
───────────────────────────────────────────────────────────────────────────────

The application is ready to use. Choose your deployment method above and start
analyzing classroom engagement metrics!

Questions? Check the documentation files or review the comments in the code.

Good luck! 🚀

EOF
