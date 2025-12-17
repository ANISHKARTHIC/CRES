# Classroom Engagement System

A comprehensive FARM stack application (FastAPI, React, MongoDB) for analyzing classroom engagement through speaker diarization and participation metrics.

## Features

### Backend (FastAPI)
- **Async File Upload**: Upload audio recordings for analysis
- **Speaker Diarization**: Uses `pyannote.audio` to identify different speakers
- **WebSocket Support**: Real-time audio streaming for live classes
- **Celery Workers**: Background task processing with Redis
- **MongoDB Integration**: Persistent storage of analysis results
- **REST API**: Comprehensive API endpoints for all operations

### Frontend (React)
- **Meeting Dashboard**: Visual analysis of recorded meetings
- **WaveSurfer.js Integration**: Interactive audio waveform visualization
- **Speaker Visualization**: Color-coded regions for different speakers
- **Recharts Integration**: Interactive charts for participation metrics
- **File Upload**: Easy-to-use interface for uploading audio files

### Engagement Metrics
- **Turn-Taking Frequency**: Measures how often speakers switch (turns per minute)
- **Participation Balance**: Shows talk time percentage for each speaker
- **Engagement Score**: Composite metric based on participation balance and turn-taking
- **Talk Time Analysis**: Detailed breakdown of speaking time per speaker

## Project Structure

```
classroom-engagement-system/
├── backend/
│   ├── app/
│   │   ├── models/          # Pydantic models
│   │   ├── routes/          # FastAPI endpoints
│   │   ├── tasks/           # Celery tasks
│   │   ├── utils/           # Utility functions
│   │   ├── main.py          # FastAPI app entry point
│   │   └── config.py        # Configuration settings
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── styles/          # CSS files
│   │   ├── App.jsx          # Main app component
│   │   └── index.jsx        # React entry point
│   ├── public/              # Static files
│   ├── package.json         # Node dependencies
│   └── Dockerfile           # Docker configuration
├── docker-compose.yml       # Multi-container orchestration
└── README.md               # This file
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **MongoDB**: Document database
- **Pyannote.audio**: Speaker diarization models
- **Librosa**: Audio processing library
- **WebSockets**: Real-time communication

### Frontend
- **React**: UI library
- **WaveSurfer.js**: Audio waveform visualization
- **Recharts**: Data visualization library
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first CSS framework

## Setup & Installation

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository
```bash
cd classroom-engagement-system
```

2. Build and run all services
```bash
docker-compose up --build
```

3. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Celery Worker
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Meeting Analysis
- **POST** `/api/analyze-meeting` - Upload and analyze a meeting recording
- **GET** `/api/analysis/{meeting_id}` - Get analysis results for a meeting
- **GET** `/api/all-analyses` - List all meeting analyses
- **GET** `/api/task-status/{task_id}` - Check Celery task status

### WebSocket
- **WS** `/api/ws/live-class/{meeting_id}` - Live audio streaming endpoint
- **POST** `/api/finalize-live-session/{meeting_id}` - Finalize live session

## Usage Example

### Upload and Analyze a Meeting
```bash
curl -X POST http://localhost:8000/api/analyze-meeting \
  -F "file=@meeting.wav" \
  -F "meeting_id=class-001" \
  -F "source_type=teams"
```

### Check Task Status
```bash
curl http://localhost:8000/api/task-status/task-id-here
```

### Get Analysis Results
```bash
curl http://localhost:8000/api/analysis/class-001
```

## Key Features Explained

### 1. Speaker Diarization
The system uses pyannote.audio's state-of-the-art models to identify and separate different speakers in an audio recording. The diarization process:
- Detects speaker boundaries
- Assigns unique speaker IDs
- Provides confidence scores for each segment

### 2. Engagement Metrics
The system calculates several metrics:
- **Turn-Taking Frequency**: Higher frequency indicates more interactive discussions
- **Participation Balance**: Shows equity in speaking time
- **Engagement Score**: Combines metrics to provide an overall engagement rating (0-100)

### 3. Real-Time Support (Phase 2)
- WebSocket endpoint accepts audio chunks during live classes
- Support for both live classroom and Teams meeting scenarios
- Real-time engagement metrics calculation

### 4. Data Persistence
- MongoDB stores all analysis results
- Indexed queries for quick retrieval
- Support for historical analysis tracking

## Configuration

### Environment Variables (`.env`)
```
MONGODB_URL=mongodb://root:rootpassword@localhost:27017/classroom?authSource=admin
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
REACT_APP_API_URL=http://localhost:8000/api
```

## Troubleshooting

### Pyannote.audio Model Loading
The system requires a HuggingFace token for downloading models. Set the token as an environment variable:
```bash
export HF_TOKEN=your_huggingface_token
```

### MongoDB Connection Issues
Ensure MongoDB is running and the connection string is correct:
```bash
docker exec classroom-mongodb mongosh -u root -p rootpassword
```

### Redis Connection Issues
Verify Redis is accessible:
```bash
docker exec classroom-redis redis-cli ping
```

## Future Enhancements

- Real-time sentiment analysis during meetings
- Speaker identification and labeling
- Automatic meeting transcription
- Integration with video processing
- Advanced analytics and reporting
- Mobile application support
- Multi-language support

## License

MIT License

## Support

For issues or questions, please open an issue in the repository.
