# Classroom Engagement System - Getting Started Guide

## Quick Start with Docker

The fastest way to get the entire system running is with Docker Compose.

### Prerequisites
- Docker (v20.10+)
- Docker Compose (v2.0+)
- 4GB RAM minimum

### Start the System

```bash
cd classroom-engagement-system
docker-compose up --build
```

The first build takes 5-10 minutes. Once complete, you'll see:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

### Test the System

#### 1. Upload a Meeting Recording
Open http://localhost:3000 and use the upload form with any `.wav` file.

#### 2. Via API
```bash
curl -X POST http://localhost:8000/api/analyze-meeting \
  -F "file=@sample_audio.wav" \
  -F "meeting_id=test-001" \
  -F "source_type=teams"
```

#### 3. Check Results
Navigate to the Dashboard tab or visit:
```bash
curl http://localhost:8000/api/analysis/test-001
```

## Local Development Setup

### Backend Development

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Start Services (Required)**
You need MongoDB and Redis running:

```bash
# Option 1: Using Docker (recommended)
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=rootpassword mongo:6.0
docker run -d -p 6379:6379 redis:7-alpine

# Option 2: Install locally if you prefer
```

4. **Create .env file**
```bash
cp .env.example .env
```

5. **Run FastAPI Server**
```bash
uvicorn app.main:app --reload
```

Server runs at http://localhost:8000

6. **Run Celery Worker** (in another terminal)
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend Development

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Create .env file**
```bash
cp .env.example .env
```

3. **Start Development Server**
```bash
npm start
```

Frontend opens at http://localhost:3000

## Project Structure Explanation

### Backend Structure

```
backend/
├── app/
│   ├── config.py              # Settings management
│   ├── main.py                # FastAPI app
│   ├── models/
│   │   └── meeting.py         # Data models (Pydantic)
│   ├── routes/
│   │   └── meetings.py        # API endpoints
│   ├── tasks/
│   │   ├── celery_app.py      # Celery initialization
│   │   └── diarization.py     # Speaker diarization task
│   └── utils/                 # Helper functions
├── uploads/                   # Temporary audio files
├── requirements.txt           # Dependencies
└── Dockerfile                 # Container config
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── MeetingDashboard.jsx   # Main dashboard
│   │   └── FileUpload.jsx         # Upload component
│   ├── styles/
│   │   ├── App.css
│   │   ├── Dashboard.css
│   │   ├── FileUpload.css
│   │   └── index.css
│   ├── App.jsx                # Root component
│   └── index.jsx              # Entry point
├── public/
│   └── index.html
└── package.json               # Dependencies
```

## Key Components

### 1. FileUpload Component
**Location**: `frontend/src/components/FileUpload.jsx`

Handles audio file selection and upload with:
- File validation
- Progress tracking
- Meeting ID assignment
- Source type selection (Teams/Live)

### 2. MeetingDashboard Component
**Location**: `frontend/src/components/MeetingDashboard.jsx`

Displays:
- WaveSurfer audio waveform with speaker regions
- Engagement metrics (score, turn-taking, duration)
- Participation pie chart
- Talk time statistics table

### 3. FastAPI Routes
**Location**: `backend/app/routes/meetings.py`

Endpoints:
- `POST /api/analyze-meeting` - Upload audio
- `GET /api/analysis/{meeting_id}` - Get results
- `GET /api/all-analyses` - List all
- `WS /api/ws/live-class/{meeting_id}` - Live streaming

### 4. Diarization Task
**Location**: `backend/app/tasks/diarization.py`

Celery task that:
1. Loads audio file
2. Performs speaker diarization
3. Calculates engagement metrics
4. Saves to MongoDB

## Understanding the Data Flow

### Upload → Analysis → Results

```
1. User uploads audio file
        ↓
2. FastAPI saves file and creates Celery task
        ↓
3. Celery worker processes audio with pyannote
        ↓
4. Speaker segments are extracted
        ↓
5. Engagement metrics are calculated
        ↓
6. Results saved to MongoDB
        ↓
7. Frontend fetches and displays results
```

## Understanding Engagement Metrics

### Turn-Taking Frequency
- **Metric**: Turns per minute
- **Calculation**: Count speaker switches / (duration in minutes)
- **Interpretation**: Higher = more interactive discussion

Example: 10 speaker switches in 5 minutes = 2 turns/minute

### Participation Balance
- **Metric**: Percentage of talk time per speaker
- **Calculation**: (Speaker talk time / Total talk time) × 100
- **Interpretation**: More balanced = better engagement

Example: Speaker 1: 60%, Speaker 2: 40%

### Engagement Score
- **Metric**: 0-100 scale
- **Calculation**: 
  - Balance Score = 100 - |100 - max_participation|
  - Turn Score = (turn_frequency / 2) × 100
  - Final = (Balance × 0.4) + (Turn × 0.6)
- **Interpretation**: 
  - 0-40: Low engagement
  - 40-70: Moderate engagement
  - 70-100: High engagement

## Advanced Features

### Phase 2: Real-Time Audio Streaming

#### Live Class WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/live-class/class-001');

ws.onopen = () => {
  // Send audio chunks
  ws.send(audioChunk);
};

ws.onmessage = (event) => {
  console.log(event.data); // Acknowledgment
};
```

#### Finalize Session
```bash
curl -X POST http://localhost:8000/api/finalize-live-session/class-001
```

### Speaker Identification

The system can identify and label speakers:
- Teacher (typically Speaker_1, usually high talk time)
- Students (Speaker_2, 3, 4... typically lower talk time)

### MongoDB Collections

#### meetings collection
```json
{
  "_id": ObjectId,
  "meeting_id": "string",
  "source_type": "live" | "teams",
  "duration": 120.5,
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "speaker_id": "Speaker_1",
      "confidence": 0.95
    }
  ],
  "engagement_score": 75.5,
  "speaker_talk_time": { "Speaker_1": 70.0, "Speaker_2": 50.5 },
  "speaker_participation": { "Speaker_1": 58.02, "Speaker_2": 41.98 },
  "turn_taking_frequency": 2.4,
  "created_at": "2024-01-15T10:30:00",
  "audio_file_name": "meeting.wav"
}
```

## Troubleshooting

### Issue: "Connection refused" to MongoDB
**Solution**: 
```bash
docker-compose up -d mongodb
# Or install MongoDB locally
```

### Issue: Audio file upload fails
**Solution**: Check file format is `.wav` or `.mp3`

### Issue: Diarization takes too long
**Solution**: Normal for first run (model downloads). Subsequent runs are faster.

### Issue: WebSocket connection fails
**Solution**: Ensure WebSocket support in frontend and backend

## Environment Variables

### Backend (.env)
```
MONGODB_URL=mongodb://root:password@localhost:27017/classroom?authSource=admin
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
DEBUG=False
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## Performance Tips

1. **Use SSD** for MongoDB (faster data access)
2. **Increase Docker resources** (memory, CPU) for faster processing
3. **Disable debug mode** in production
4. **Use CDN** for frontend assets
5. **Cache analysis results** for repeated queries

## Next Steps

1. **Test with real audio**: Upload actual meeting recordings
2. **Customize metrics**: Modify calculation logic in `diarization.py`
3. **Add authentication**: Implement JWT in FastAPI
4. **Deploy**: Use Kubernetes or cloud providers
5. **Integrate**: Connect with other education platforms

## Support & Resources

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Pyannote Docs**: https://github.com/pyannote/pyannote-audio
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

## Common Commands

```bash
# Stop all services
docker-compose down

# View logs
docker-compose logs -f fastapi

# Rebuild images
docker-compose build --no-cache

# Access MongoDB CLI
docker exec classroom-mongodb mongosh -u root -p rootpassword

# Clear uploads
rm backend/uploads/*

# Reset database
docker-compose down -v  # Remove volumes
docker-compose up
```
