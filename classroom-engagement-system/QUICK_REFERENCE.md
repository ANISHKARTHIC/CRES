# Quick Reference Guide

## 🚀 Quick Start (5 minutes)

### With Docker (Recommended)
```bash
cd classroom-engagement-system
docker-compose up --build
```

Then:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Without Docker
```bash
# Terminal 1: MongoDB & Redis
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=rootpassword mongo:6.0
docker run -d -p 6379:6379 redis:7-alpine

# Terminal 2: FastAPI Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 3: Celery Worker
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 4: React Frontend
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
classroom-engagement-system/
├── backend/
│   ├── app/
│   │   ├── models/meeting.py          # Data models
│   │   ├── routes/meetings.py         # API endpoints
│   │   ├── tasks/
│   │   │   ├── celery_app.py         # Celery setup
│   │   │   └── diarization.py        # Audio analysis
│   │   ├── config.py                  # Configuration
│   │   └── main.py                    # FastAPI app
│   ├── requirements.txt               # Python packages
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx        # Upload form
│   │   │   └── MeetingDashboard.jsx  # Results display
│   │   ├── styles/                    # CSS files
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── public/index.html
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml                 # Multi-container setup
├── README.md                          # Full documentation
├── GETTING_STARTED.md                 # Setup guide
├── API_DOCUMENTATION.md               # API reference
├── ARCHITECTURE.md                    # Technical design
├── QUICK_REFERENCE.md                 # This file
└── test_engagement_system.py          # Unit tests
```

## 🔧 Common Tasks

### Upload Audio File
```bash
curl -X POST http://localhost:8000/api/analyze-meeting \
  -F "file=@meeting.wav" \
  -F "meeting_id=class-001" \
  -F "source_type=teams"

# Response:
# {"status": "processing", "task_id": "abc123", "meeting_id": "class-001"}
```

### Check Analysis Status
```bash
curl http://localhost:8000/api/task-status/abc123
# Check status: PENDING, STARTED, SUCCESS, FAILURE
```

### Get Analysis Results
```bash
curl http://localhost:8000/api/analysis/class-001
# Returns: segments, engagement_score, turn_taking, participation %
```

### View All Analyses
```bash
curl "http://localhost:8000/api/all-analyses?limit=10"
```

## 📊 Understanding Metrics

| Metric | Range | Meaning |
|--------|-------|---------|
| **Engagement Score** | 0-100 | Overall classroom engagement |
| **Turn-Taking Frequency** | 0-10+ | Speaker switches per minute |
| **Participation %** | 0-100% | Talk time percentage per speaker |
| **Duration** | seconds | Total meeting length |

### Interpretation Guide

**Engagement Score:**
- 0-40: Low engagement (few interruptions, imbalanced participation)
- 40-70: Moderate engagement (some interaction)
- 70-100: High engagement (balanced, interactive discussion)

**Turn-Taking:**
- < 1.0: Very low (mostly monologue)
- 1.0-3.0: Normal (good interaction)
- > 3.0: Very high (frequent switches, possibly chaotic)

**Participation:**
- < 20%: One person dominating
- 20-50%: Varied participation
- > 50% per person: Equal sharing (ideal in groups)

## 🔌 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **POST** | `/api/analyze-meeting` | Upload audio file |
| **GET** | `/api/analysis/{id}` | Get analysis results |
| **GET** | `/api/all-analyses` | List all analyses |
| **GET** | `/api/task-status/{id}` | Check processing status |
| **WS** | `/api/ws/live-class/{id}` | Live audio streaming |
| **POST** | `/api/finalize-live-session/{id}` | End live session |

## 🐛 Troubleshooting

### "Connection refused" to MongoDB
```bash
# Start MongoDB container
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=rootpassword mongo:6.0
```

### "Cannot connect to Redis"
```bash
# Start Redis container
docker run -d -p 6379:6379 redis:7-alpine
```

### Celery worker not processing tasks
```bash
# Check Celery is running
celery -A app.tasks.celery_app worker --loglevel=info

# Verify Redis connection
docker exec <redis-container> redis-cli ping
# Should return: PONG
```

### Frontend can't reach backend
```bash
# Check .env file
cat frontend/.env
# Should have: REACT_APP_API_URL=http://localhost:8000/api

# Restart frontend
npm start
```

### Audio file upload fails
- Check file is actual audio (.wav, .mp3)
- Check file size < 500MB
- Check backend logs for errors

### Diarization model not found
- First run downloads model (takes time)
- Requires HuggingFace token (usually auto-detected)
- Check internet connection

## 🔑 Environment Variables

### Backend (.env)
```
MONGODB_URL=mongodb://root:rootpassword@localhost:27017/classroom?authSource=admin
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
DEBUG=False
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## 📱 Using the Application

### 1. Upload a Meeting
- Go to http://localhost:3000
- Click "Upload & Analyze"
- Select audio file (.wav, .mp3)
- (Optional) Enter meeting ID
- Choose source type (Teams/Live)
- Click "Upload & Analyze"
- Copy task ID shown in message

### 2. Check Status
```bash
# Check if processing is done
curl http://localhost:8000/api/task-status/<task-id>
# Wait until status = "SUCCESS"
```

### 3. View Results
- Dashboard refreshes automatically
- Click meeting in sidebar to view
- See waveform, metrics, and charts

## 🎯 Key Features

✅ **Speaker Diarization** - Identifies different speakers  
✅ **Engagement Metrics** - Measures participation and interaction  
✅ **Real-time WebSocket** - Support for live streaming  
✅ **Async Processing** - Background task handling with Celery  
✅ **Interactive Dashboard** - Visual analysis display  
✅ **REST API** - Complete API for integration  
✅ **MongoDB Storage** - Persistent data persistence  
✅ **Docker Support** - Easy deployment  

## 🚦 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid file, missing params) |
| 404 | Resource not found (meeting_id doesn't exist) |
| 500 | Server error (check logs) |

## 📊 Sample Analysis Output

```json
{
  "meeting_id": "class-001",
  "source_type": "teams",
  "duration": 300.5,
  "engagement_score": 72.5,
  "turn_taking_frequency": 2.4,
  "speaker_talk_time": {
    "Speaker_1": 180.0,
    "Speaker_2": 120.5
  },
  "speaker_participation": {
    "Speaker_1": 59.87,
    "Speaker_2": 40.13
  },
  "segments": [
    {"start": 0.0, "end": 5.2, "speaker_id": "Speaker_1"},
    {"start": 5.2, "end": 12.3, "speaker_id": "Speaker_2"}
  ]
}
```

## 🔗 Useful Links

- **API Documentation**: http://localhost:8000/docs
- **React Component Docs**: https://react.dev/
- **Pyannote Audio**: https://github.com/pyannote/pyannote-audio
- **FastAPI Guide**: https://fastapi.tiangolo.com/
- **Celery Docs**: https://docs.celeryproject.io/

## 💡 Tips & Tricks

1. **Speed up first diarization**: Model caches after first use
2. **Reuse meeting IDs**: Same ID overwrites previous analysis
3. **Check logs**: `docker-compose logs <service>` for debugging
4. **API Testing**: Use http://localhost:8000/docs (Swagger UI)
5. **Database Query**: `docker exec classroom-mongodb mongosh ...`

## 📈 Performance Benchmarks

| Task | Time |
|------|------|
| Upload 5MB file | < 1s |
| 1-minute audio diarization | 30-60s |
| 10-minute audio diarization | 3-5m |
| Dashboard load | < 1s |
| Metrics calculation | < 100ms |

## ✅ Checklist for First Run

- [ ] Docker installed and running
- [ ] Cloned repository
- [ ] Ran `docker-compose up --build`
- [ ] Frontend loads at http://localhost:3000
- [ ] API docs at http://localhost:8000/docs
- [ ] Upload test audio file
- [ ] Dashboard shows results
- [ ] Engagement score displayed

## 🤝 Contributing

Found an issue? Want to add features?
1. Check ARCHITECTURE.md for design details
2. Review test_engagement_system.py for testing patterns
3. Follow existing code style
4. Test locally before submitting

## 📞 Support

For issues:
1. Check GETTING_STARTED.md
2. Review API_DOCUMENTATION.md
3. Check logs: `docker-compose logs`
4. Review GitHub issues

---

**Happy analyzing! 🎓**
