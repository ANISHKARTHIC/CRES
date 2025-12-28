# Architecture & Design Document

## System Overview

The Classroom Engagement System is a distributed application that analyzes audio recordings to measure classroom engagement through speaker diarization and participation metrics.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        React Frontend (Port 3000)                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  FileUpload Component  │  MeetingDashboard Component       │    │
│  │  - File selection      │  - WaveSurfer visualization      │    │
│  │  - Upload progress     │  - Engagement metrics display    │    │
│  │  - Source type select  │  - Recharts pie chart            │    │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Routes (app/routes/meetings.py)                            │    │
│  │  ├── POST /analyze-meeting      (File upload)              │    │
│  │  ├── GET /analysis/{id}         (Retrieve results)          │    │
│  │  ├── GET /all-analyses          (List all)                  │    │
│  │  ├── GET /task-status/{id}      (Task polling)             │    │
│  │  ├── WS /ws/live-class/{id}     (Live streaming)           │    │
│  │  └── POST /finalize-live-session (End session)             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│          │                      │                      │              │
│          ▼                      ▼                      ▼              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  File Storage    │  │  MongoDB Client  │  │  Celery Client   │  │
│  │  (uploads/)      │  │  Connection      │  │  Task Dispatch   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└────────────────────────┬──────────────────────────┬──────────────────┘
                         │                          │
                         ▼                          ▼
        ┌────────────────────────┐    ┌─────────────────────────────┐
        │  MongoDB (Port 27017)  │    │  Redis (Port 6379)          │
        │  ┌──────────────────┐  │    │  ┌─────────────────────┐    │
        │  │ meetings         │  │    │  │ Celery Broker       │    │
        │  │ ├─ meeting_id    │  │    │  │ ├─ Task Queue       │    │
        │  │ ├─ source_type   │  │    │  │ ├─ Result Backend   │    │
        │  │ ├─ segments      │  │    │  │ └─ Session Cache    │    │
        │  │ ├─ metrics       │  │    │  └─────────────────────┘    │
        │  │ └─ created_at    │  │    │                             │
        │  └──────────────────┘  │    └─────────────────────────────┘
        └────────────────────────┘
                    ▲
                    │ Task Results
                    │
        ┌───────────────────────────────────────────────┐
        │  Celery Worker (Async Task Processing)        │
        │  ┌─────────────────────────────────────────┐  │
        │  │  Diarization Task                       │  │
        │  │  1. Load audio file                     │  │
        │  │  2. Perform speaker diarization         │  │
        │  │  3. Calculate engagement metrics        │  │
        │  │  4. Save to MongoDB                     │  │
        │  └────────┬──────────────────────┬─────────┘  │
        │           │                      │             │
        │           ▼                      ▼             │
        │  ┌──────────────────┐  ┌──────────────────┐   │
        │  │  Pyannote Audio  │  │  Librosa         │   │
        │  │  (Diarization)   │  │  (Audio Process) │   │
        │  └──────────────────┘  └──────────────────┘   │
        └───────────────────────────────────────────────┘
```

## Component Details

### Frontend Architecture

#### MeetingDashboard Component
- **Purpose**: Display analysis results and visualization
- **Key Dependencies**: WaveSurfer.js, Recharts, Axios
- **State Management**: React hooks (useState, useEffect)
- **Features**:
  - Waveform visualization with speaker regions
  - Metrics display (engagement score, turn-taking, duration)
  - Participation pie chart
  - Talk time statistics table
  - Meeting list sidebar with refresh

#### FileUpload Component
- **Purpose**: Handle audio file uploads
- **Features**:
  - File type validation
  - Upload progress tracking
  - Meeting ID assignment
  - Source type selection
  - Error handling and user feedback

### Backend Architecture

#### FastAPI Application
- **Entry Point**: `app/main.py`
- **CORS**: Enabled for all origins (configurable)
- **Middleware**: CORS, error handling
- **Routes**: Included from `app/routes/meetings.py`

#### Data Models (`app/models/meeting.py`)
```
SourceType: Enum
├── LIVE: Live classroom session
└── TEAMS: Teams meeting

SpeakerSegment
├── start: float
├── end: float
├── speaker_id: str
└── confidence: float

MeetingAnalysis
├── meeting_id: str
├── source_type: SourceType
├── duration: float
├── segments: List[SpeakerSegment]
├── engagement_score: float
├── speaker_talk_time: dict
├── speaker_participation: dict
├── turn_taking_frequency: float
├── created_at: datetime
└── audio_file_name: str
```

#### Celery Task System

**Purpose**: Async processing of audio analysis

**Flow**:
1. FastAPI receives file → saves to disk
2. Creates Celery task with file path
3. Returns task ID immediately (non-blocking)
4. Celery worker processes in background
5. Results saved to MongoDB
6. Frontend polls task status or fetches results

**Task Details** (`app/tasks/diarization.py`):
- `analyze_audio_task()`: Main async function
- Uses Pyannote.audio for diarization
- Calculates metrics
- Handles errors gracefully

#### DiarizationService
**Methods**:
- `load_audio()`: Load audio using librosa
- `perform_diarization()`: Run pyannote pipeline
- `calculate_engagement_metrics()`: Compute all metrics
- `save_analysis_to_db()`: Persist to MongoDB

### Engagement Metrics Calculation

#### 1. Speaker Talk Time
```python
for each segment in segments:
    speaker_talk_time[speaker_id] += (segment.end - segment.start)
```

#### 2. Participation Percentage
```python
total_talk_time = sum(speaker_talk_time.values())
for each speaker:
    participation[speaker] = (talk_time / total_talk_time) * 100
```

#### 3. Turn-Taking Frequency
```python
turn_count = 0
for i in range(len(segments) - 1):
    if segments[i].speaker_id != segments[i+1].speaker_id:
        turn_count += 1

turn_taking_frequency = turn_count / (duration_in_minutes)
```

#### 4. Engagement Score (Composite)
```python
# Balance metric: How equal is participation?
balance_score = 100 - abs(100 - max(participation_values))

# Turn metric: How interactive?
turn_score = min(100, (turn_frequency / 2) * 100)

# Final score: Weighted combination
engagement_score = (balance_score × 0.4) + (turn_score × 0.6)
```

## Data Flow

### Upload & Analysis Flow
```
1. User selects file → Frontend
2. Form submission → FileUpload component
3. FormData POST /api/analyze-meeting → FastAPI
4. File validation
5. Save file to uploads/
6. Create Celery task
7. Return {status, meeting_id, task_id} → Frontend
8. Frontend shows task_id to user
```

### Task Processing Flow
```
1. Celery worker picks up task
2. Load audio file
3. Extract audio data with librosa
4. Initialize Pyannote pipeline
5. Run diarization
6. Parse segments
7. Calculate metrics
8. Create MeetingAnalysis document
9. Insert to MongoDB
10. Delete temp audio file
11. Return result with analysis_id
```

### Results Retrieval Flow
```
1. User clicks meeting in dashboard
2. Frontend GET /api/analysis/{meeting_id}
3. FastAPI queries MongoDB
4. Returns MeetingAnalysis document
5. Frontend initializes WaveSurfer
6. Draws speaker regions
7. Renders charts and metrics
```

## Database Schema

### MongoDB Collections

#### meetings
```json
{
  "_id": ObjectId,
  "meeting_id": "unique-string",
  "source_type": "live" | "teams",
  "duration": 300.5,
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "speaker_id": "Speaker_1",
      "confidence": 0.95
    }
  ],
  "engagement_score": 72.5,
  "speaker_talk_time": {
    "Speaker_1": 180.0,
    "Speaker_2": 120.5
  },
  "speaker_participation": {
    "Speaker_1": 59.87,
    "Speaker_2": 40.13
  },
  "turn_taking_frequency": 2.4,
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "audio_file_name": "meeting.wav"
}
```

**Indexes**:
```javascript
db.meetings.createIndex({ "meeting_id": 1 }, { unique: true })
db.meetings.createIndex({ "created_at": -1 })
db.meetings.createIndex({ "source_type": 1 })
```

## Technology Rationale

### FastAPI
- **Why**: Modern, fast, type-hinted, auto-API docs
- **Alternative**: Flask, Django (heavier)
- **WebSocket support**: Out-of-the-box

### Celery + Redis
- **Why**: Scalable async task processing
- **Alternative**: RQ, APScheduler (simpler but less powerful)
- **Benefits**: Distributed, persistent queue, result backend

### MongoDB
- **Why**: Document-oriented, flexible schema
- **Alternative**: PostgreSQL (relational), DynamoDB (cloud)
- **Reason**: Nested documents (segments) fit naturally

### Pyannote.audio
- **Why**: SOTA speaker diarization, pre-trained models
- **Alternative**: Azure Speech, Google Cloud Speech (cloud)
- **Model**: pyannote/speaker-diarization-3.1

### React + Axios
- **Why**: Component-based, rich ecosystem
- **Alternative**: Vue, Angular (overkill)
- **State**: React hooks, minimal library

### WaveSurfer.js
- **Why**: Web audio API wrapper, simple integration
- **Alternative**: Tone.js (music-focused), Web Audio API directly
- **Features**: Waveform rendering, zoom, seek

### Recharts
- **Why**: React components for charts, declarative
- **Alternative**: D3.js (complex), Chart.js (jQuery)
- **Charts**: Pie, Bar, Line, Area (easily composable)

## Scalability Considerations

### Horizontal Scaling
1. **Multiple Celery Workers**: Add more worker instances
2. **Load Balancer**: Nginx/HAProxy for FastAPI instances
3. **Sharded MongoDB**: For large datasets
4. **Redis Cluster**: For distributed caching

### Performance Optimization
1. **Caching**: Cache analysis results (Redis)
2. **Compression**: Gzip audio files
3. **Async Processing**: All I/O operations are async
4. **Database Indexing**: Query optimization
5. **CDN**: Serve frontend assets globally

### Monitoring & Logging
```python
# Add logging
import logging
logger = logging.getLogger(__name__)

# Add metrics collection
from prometheus_client import Counter, Histogram
task_duration = Histogram('task_duration_seconds', 'Task duration')
```

## Security Considerations

### File Upload Security
```python
# Validate file size
MAX_FILE_SIZE = 1024 * 1024 * 500  # 500MB
if file.size > MAX_FILE_SIZE:
    raise HTTPException(413, "File too large")

# Validate MIME type
valid_types = {"audio/wav", "audio/mpeg"}
if file.content_type not in valid_types:
    raise HTTPException(400, "Invalid file type")

# Scan for malware (future)
# Use ClamAV or similar service
```

### API Security
```python
# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@limiter.limit("100/minute")

# Add authentication
from fastapi.security import HTTPBearer
security = HTTPBearer()

# CORS restriction (production)
allow_origins = ["https://yourdomain.com"]
```

### Data Security
- Use HTTPS in production
- Encrypt MongoDB at rest
- Secure Redis with authentication
- Use environment variables for secrets
- Implement user authentication

## Testing Strategy

### Unit Tests
```python
# Test engagement metric calculations
def test_turn_taking_frequency():
    segments = [...]
    freq = service.calculate_engagement_metrics(segments, 300)
    assert freq["turn_taking_frequency"] == expected_value
```

### Integration Tests
```python
# Test full upload → analysis flow
def test_audio_analysis_pipeline():
    # Upload file
    # Wait for task
    # Verify results in DB
```

### Load Testing
```bash
# Use locust or k6
locust -f locustfile.py --host=http://localhost:8000
```

## Deployment Architecture

### Docker Compose (Development)
All services in single network, shared volumes.

### Kubernetes (Production)
```yaml
Services:
  - fastapi-deployment (3 replicas)
  - celery-worker-deployment (5 replicas)
  - react-deployment (2 replicas)
  - mongodb-statefulset
  - redis-deployment
```

### Cloud Deployment Options
1. **AWS**: ECS, Lambda, RDS (MongoDB)
2. **Azure**: App Service, Container Instances, CosmosDB
3. **GCP**: Cloud Run, Cloud Tasks, Firestore
4. **Heroku**: Easy but expensive for workers

## Future Enhancements

### Phase 3: Advanced Analytics
- Sentiment analysis per speaker
- Emotion detection
- Topic modeling
- Student attention tracking

### Phase 4: ML Integration
- Predict engagement levels
- Recommend interventions
- Personalized feedback
- Anomaly detection

### Phase 5: Enterprise Features
- Multi-tenant support
- User authentication & authorization
- Audit logging
- SLA monitoring
- Backup & disaster recovery

## Conclusion

This architecture provides a scalable, maintainable foundation for classroom engagement analysis. The separation of concerns (frontend, backend, workers), async processing, and persistent storage enable reliable operation at scale.
