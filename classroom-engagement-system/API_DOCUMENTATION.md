# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### 1. Analyze Meeting (Upload Audio)
**Endpoint**: `POST /analyze-meeting`

Upload an audio file for speaker diarization and engagement analysis.

**Request**:
```bash
curl -X POST http://localhost:8000/api/analyze-meeting \
  -F "file=@meeting.wav" \
  -F "meeting_id=class-001" \
  -F "source_type=teams"
```

**Parameters** (multipart/form-data):
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | Audio file (.wav, .mp3) |
| meeting_id | String | No | Unique meeting identifier (auto-generated if not provided) |
| source_type | String | No | "live" or "teams" (default: "teams") |

**Response** (200 OK):
```json
{
  "status": "processing",
  "meeting_id": "class-001",
  "task_id": "abc123def456",
  "message": "Audio analysis started. Check status with task_id"
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Invalid file type. Accepted: {'audio/wav', 'audio/mpeg'}"
}
```

---

### 2. Get Analysis Results
**Endpoint**: `GET /analysis/{meeting_id}`

Retrieve the analysis results for a specific meeting.

**Request**:
```bash
curl http://localhost:8000/api/analysis/class-001
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "_id": "65a1b2c3d4e5f6g7h8i9j0",
    "meeting_id": "class-001",
    "source_type": "teams",
    "duration": 300.5,
    "segments": [
      {
        "start": 0.0,
        "end": 5.2,
        "speaker_id": "Speaker_1",
        "confidence": 0.95
      },
      {
        "start": 5.2,
        "end": 12.3,
        "speaker_id": "Speaker_2",
        "confidence": 0.92
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
    "created_at": "2024-01-15T10:30:00.123456",
    "audio_file_name": "meeting.wav"
  }
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Analysis not found"
}
```

---

### 3. Get Task Status
**Endpoint**: `GET /task-status/{task_id}`

Check the status of a Celery task.

**Request**:
```bash
curl http://localhost:8000/api/task-status/abc123def456
```

**Response**:
```json
{
  "task_id": "abc123def456",
  "status": "SUCCESS",
  "result": {
    "status": "success",
    "analysis_id": "65a1b2c3d4e5f6g7h8i9j0",
    "meeting_id": "class-001",
    "metrics": {
      "speaker_talk_time": {"Speaker_1": 180.0, "Speaker_2": 120.5},
      "speaker_participation": {"Speaker_1": 59.87, "Speaker_2": 40.13},
      "turn_taking_frequency": 2.4,
      "engagement_score": 72.5
    }
  }
}
```

**Possible Status Values**:
- `PENDING`: Task is waiting to be executed
- `STARTED`: Task has started executing
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed
- `RETRY`: Task is being retried
- `REVOKED`: Task was cancelled

---

### 4. Get All Analyses
**Endpoint**: `GET /all-analyses`

Retrieve all meeting analyses with pagination.

**Request**:
```bash
curl "http://localhost:8000/api/all-analyses?limit=50"
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | Integer | 50 | Maximum number of results to return |

**Response** (200 OK):
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0",
      "meeting_id": "class-001",
      "source_type": "teams",
      "duration": 300.5,
      "engagement_score": 72.5,
      "turn_taking_frequency": 2.4,
      "created_at": "2024-01-15T10:30:00.123456"
    },
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j1",
      "meeting_id": "class-002",
      "source_type": "live",
      "duration": 1800.0,
      "engagement_score": 68.2,
      "turn_taking_frequency": 1.8,
      "created_at": "2024-01-14T09:15:00.123456"
    }
  ]
}
```

---

### 5. Live Class WebSocket
**Endpoint**: `WS /ws/live-class/{meeting_id}`

Accept audio chunks in real-time from a live class session.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/live-class/live-001');

ws.addEventListener('open', (event) => {
  console.log('Connected to server');
});

ws.addEventListener('message', (event) => {
  const response = JSON.parse(event.data);
  console.log('Chunk received:', response);
});

ws.addEventListener('close', (event) => {
  console.log('Disconnected from server');
});
```

**Sending Audio Chunks**:
```javascript
// Send audio chunk (ArrayBuffer)
const audioChunk = new Uint8Array([...audioData]);
ws.send(audioChunk.buffer);
```

**Response Message**:
```json
{
  "status": "chunk_received",
  "meeting_id": "live-001",
  "chunk_count": 5
}
```

---

### 6. Finalize Live Session
**Endpoint**: `POST /finalize-live-session/{meeting_id}`

Finalize a live class session and trigger analysis.

**Request**:
```bash
curl -X POST http://localhost:8000/api/finalize-live-session/live-001
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Live session live-001 finalized",
  "meeting_id": "live-001"
}
```

---

## Data Models

### SpeakerSegment
```json
{
  "start": 0.0,
  "end": 5.2,
  "speaker_id": "Speaker_1",
  "confidence": 0.95
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| start | Float | Start time in seconds |
| end | Float | End time in seconds |
| speaker_id | String | Speaker identifier (e.g., "Speaker_1") |
| confidence | Float | Confidence score (0.0-1.0) |

### MeetingAnalysis
```json
{
  "_id": "ObjectId",
  "meeting_id": "string",
  "source_type": "live|teams",
  "duration": 300.5,
  "segments": [...],
  "engagement_score": 72.5,
  "speaker_talk_time": {...},
  "speaker_participation": {...},
  "turn_taking_frequency": 2.4,
  "created_at": "2024-01-15T10:30:00.123456",
  "audio_file_name": "meeting.wav"
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| meeting_id | String | Unique meeting identifier |
| source_type | String | "live" or "teams" |
| duration | Float | Duration in seconds |
| segments | Array | List of SpeakerSegment objects |
| engagement_score | Float | Overall engagement (0-100) |
| speaker_talk_time | Object | Talk time per speaker in seconds |
| speaker_participation | Object | Percentage per speaker |
| turn_taking_frequency | Float | Speaker switches per minute |
| created_at | DateTime | When analysis was created |
| audio_file_name | String | Original filename |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format or parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Code Examples

### Python (requests)
```python
import requests

# Upload file
files = {'file': open('meeting.wav', 'rb')}
data = {'meeting_id': 'class-001', 'source_type': 'teams'}
response = requests.post('http://localhost:8000/api/analyze-meeting', files=files, data=data)
print(response.json())

# Get analysis
analysis = requests.get('http://localhost:8000/api/analysis/class-001').json()
print(analysis['data']['engagement_score'])
```

### JavaScript (fetch)
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('meeting_id', 'class-001');
formData.append('source_type', 'teams');

const response = await fetch('http://localhost:8000/api/analyze-meeting', {
  method: 'POST',
  body: formData
});
const data = await response.json();
console.log(data.task_id);

// Get analysis
const analysis = await fetch('http://localhost:8000/api/analysis/class-001').then(r => r.json());
console.log(analysis.data.engagement_score);
```

### cURL
```bash
# Upload
curl -X POST http://localhost:8000/api/analyze-meeting \
  -F "file=@meeting.wav" \
  -F "meeting_id=class-001"

# Get analysis
curl http://localhost:8000/api/analysis/class-001

# Get all
curl "http://localhost:8000/api/all-analyses?limit=10"

# Check task
curl http://localhost:8000/api/task-status/task-id-here
```

---

## Rate Limiting

Currently, there is no rate limiting. In production, consider implementing:
- Per-IP rate limits
- Per-user quotas
- Task queue priorities

---

## CORS

CORS is enabled for all origins. Modify in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Considerations

- Audio files up to 1GB are supported
- Typical processing: 1 minute of audio takes 30-120 seconds
- WebSocket connections remain open for the entire session
- MongoDB indexes optimize query performance

---

## Webhook Support (Future)

For async notifications when analysis completes:
```bash
POST /api/register-webhook
{
  "url": "https://your-domain.com/webhook",
  "meeting_id": "class-001"
}
```
