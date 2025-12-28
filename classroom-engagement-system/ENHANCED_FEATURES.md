# 🎓 Advanced Classroom Engagement System - v2.0

An intelligent FARM stack application (FastAPI, React, MongoDB) with **AI-powered analysis** for comprehensive meeting engagement assessment, speaker diarization, and detailed conversation analytics.

---

## ✨ New Enhanced Features (v2.0)

### 🎤 **Speaker Identification & Transcription**
- Automatic speaker diarization using state-of-the-art AI
- Full meeting transcription with per-speaker attribution
- Speaker turn tracking and conversation flow analysis

### 📝 **Filler Word Detection**
- Detects common fillers: um, uh, aah, mmm, like, you know, basically, etc.
- Per-speaker filler statistics and ratios
- Identifies most common fillers used in the meeting
- Helps assess speech clarity and professional communication

### 🤐 **Silence & Pause Analysis**
- Comprehensive silence detection and duration tracking
- Pause frequency and average pause duration
- Identifies engagement patterns through natural speech flow
- Silence percentage per speaker

### 😊 **Sentiment & Tone Analysis**
- Sentiment polarity detection (positive/negative/neutral)
- Emotional tone classification (engaged, calm, frustrated, etc.)
- Per-speaker sentiment analysis with confidence scores
- Overall meeting emotional tone assessment

### 📊 **Comprehensive Engagement Scoring**
- Advanced engagement metrics combining multiple factors:
  - Turn-taking frequency
  - Participation balance
  - Speaker sentiment and tone
  - Speech clarity (inverse of filler usage)
  - Natural speech flow (pause patterns)

### 🎨 **Enhanced Interactive Dashboard**
- **Overview Tab**: High-level meeting metrics and charts
- **Speakers Tab**: Detailed per-speaker analysis with expandable cards
- **Fillers Tab**: Visual representation of filler word distribution
- **Silence Tab**: Pause statistics and silence duration breakdown
- **Sentiment Tab**: Emotional tone and sentiment analysis by speaker
- Real-time charts and visualizations using Recharts

### 📋 **AI-Generated Insights & Recommendations**
- Automatic insight generation based on analysis
- Actionable recommendations for improving engagement
- Speaker-specific feedback
- Meeting-wide observations

### 🎯 **Detailed Analysis Reports**
- Comprehensive formatted analysis reports
- Speaker-by-speaker breakdown
- Engagement metrics summary
- Actionable recommendations

---

## 📦 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **Celery**: Distributed task queue for background processing
- **Redis**: Message broker and result backend
- **MongoDB**: Document database for persistence
- **Pyannote.audio**: State-of-the-art speaker diarization
- **OpenAI Whisper**: Speech-to-text transcription
- **TextBlob + Transformers**: Sentiment and tone analysis
- **Librosa**: Audio processing and feature extraction

### Frontend
- **React 18**: Modern UI library
- **Recharts**: Beautiful data visualization
- **Axios**: HTTP client for API communication
- **Tailwind CSS**: Utility-first styling framework
- **CSS3**: Modern styling and animations

### Deployment
- **Docker & Docker Compose**: Containerization
- **Uvicorn**: ASGI server for FastAPI

---

## 🚀 Key Capabilities

### Analysis Metrics
- ✅ **Engagement Score** (0-100): Composite metric
- ✅ **Participation Balance**: Equal distribution analysis
- ✅ **Turn-Taking Frequency**: Turns per minute
- ✅ **Total Filler Count**: Quantified speech hesitations
- ✅ **Filler Ratio**: Percentage of fillers in speech
- ✅ **Silence Duration**: Total and average pauses
- ✅ **Sentiment Polarity**: -1 (negative) to +1 (positive)
- ✅ **Emotional Tone**: Classification of emotional state
- ✅ **Speaker Transcripts**: Full text of what each person said
- ✅ **Automatic Insights**: AI-generated observations
- ✅ **Recommendations**: Actionable improvement suggestions

### File Support
- **Audio**: WAV, MP3
- **Video**: MP4, WebM, Ogg, Matroska
  - Automatically extracts audio from video files
  - Converts to optimal format (16kHz mono WAV)

### Data Export
- JSON-formatted comprehensive analysis
- Per-speaker breakdowns
- Meeting transcripts
- Detailed metrics for further analysis

---

## 🎯 Analysis Pipeline

```
Video/Audio Upload
        ↓
[FFmpeg] Audio Extraction (if video)
        ↓
[Pyannote] Speaker Diarization
        ↓
[Whisper] Speech-to-Text Transcription
        ↓
┌─────────────────────────────────────┐
├─ Filler Detection                   │
├─ Silence Analysis                   │
├─ Sentiment & Tone Analysis          │
├─ Engagement Scoring                 │
└─────────────────────────────────────┘
        ↓
[MongoDB] Data Persistence
        ↓
[Report Generator] Create Insights & Recommendations
        ↓
[Dashboard] Interactive Visualization
```

---

## 📊 Dashboard Features

### Overview Tab
- Meeting duration and overall engagement score
- Participation distribution pie chart
- Top filler words bar chart
- Key insights summary
- Actionable recommendations

### Speakers Tab
- Expandable speaker cards with:
  - Talk time and participation percentage
  - Word count and turn count
  - Filler word usage
  - Silence and pause statistics
  - Sentiment analysis
  - Transcript preview

### Fillers Tab
- Overall filler statistics
- Visualization of most common fillers
- Speaker ranking by filler usage
- Recommendations for improvement

### Silence Tab
- Total silence time tracking
- Per-speaker pause statistics
- Average pause duration
- Insights on conversation flow

### Sentiment Tab
- Overall sentiment classification
- Sentiment distribution
- Per-speaker sentiment breakdown
- Emotional tone classification
- Engagement ranking by sentiment

---

## 🔧 Setup Instructions

### Prerequisites
- Docker and Docker Compose
- OR Python 3.9+, Node.js 16+

### Quick Start (Docker)

```bash
cd classroom-engagement-system
docker-compose up --build
```

Access at `http://localhost:3000`

### Local Development

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

---

## 📝 API Endpoints

### File Upload & Analysis
- `POST /api/analyze-meeting` - Upload audio/video for analysis

### Results Retrieval
- `GET /api/analysis/{meeting_id}` - Get specific meeting analysis
- `GET /api/all-analyses` - Get all meeting analyses (paginated)
- `GET /api/task-status/{task_id}` - Check processing status

### Live Sessions (WebSocket)
- `WS /api/ws/live-class/{meeting_id}` - Stream live audio
- `POST /api/finalize-live-session/{meeting_id}` - Finalize session

---

## 📈 Example Response Structure

```json
{
  "meeting_id": "meeting_123",
  "engagement_score": 78.5,
  "duration": 3600,
  "overall_sentiment": "positive",
  "emotional_tone": "engaged_and_positive",
  "total_filler_count": 23,
  "average_filler_ratio": 2.1,
  "total_silence_time": 245.3,
  "speaker_analysis": {
    "Speaker_1": {
      "talk_time": 1800,
      "participation_percentage": 50.0,
      "word_count": 2150,
      "filler_count": 12,
      "filler_ratio": 0.56,
      "total_silence_duration": 120.5,
      "silence_percentage": 6.7,
      "pause_count": 45,
      "average_pause_duration": 2.68,
      "sentiment_label": "positive",
      "sentiment_polarity": 0.65,
      "engagement_from_sentiment": 85.0,
      "dominant_emotion": "positive",
      "transcript": "Full transcript of speaker 1..."
    }
  },
  "analysis_insights": [
    "Speaker_1: Highly positive and enthusiastic",
    "Very engaged and interactive",
    "High filler word usage detected..."
  ],
  "recommendations": [
    "Reduce filler words like 'um', 'uh', 'like'",
    "Speaker_1: Consider organizing thoughts..."
  ]
}
```

---

## 🎓 Use Cases

1. **Educational Institutions**
   - Analyze classroom participation
   - Assess student engagement
   - Teacher training and feedback

2. **Corporate Meetings**
   - Team engagement metrics
   - Communication quality assessment
   - Executive presentation analysis

3. **Presentations**
   - Speaker clarity and confidence evaluation
   - Audience engagement assessment
   - Presentation improvement recommendations

4. **Interviews**
   - Candidate communication assessment
   - Interviewer bias detection
   - Engagement level analysis

5. **Content Creation**
   - Podcast quality analysis
   - Video content engagement metrics
   - Speaker performance feedback

---

## 🔐 Environment Variables

Create `.env` files in backend and frontend directories:

**Backend (.env)**
```
MONGODB_URL=mongodb://mongo:27017/
DATABASE_NAME=classroom_engagement
REDIS_URL=redis://redis:6379
APP_NAME=Classroom Engagement System
```

**Frontend (.env)**
```
REACT_APP_API_URL=http://localhost:8000/api
```

---

## 📚 Documentation Files

- `ARCHITECTURE.md` - System architecture and design
- `API_DOCUMENTATION.md` - Detailed API reference
- `DEPLOYMENT.md` - Deployment guide
- `LOCAL_SETUP.md` - Local development setup
- `GETTING_STARTED.md` - Quick start guide

---

## 🐛 Troubleshooting

### Audio Processing Issues
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check file permissions on upload directory
- Verify audio format is supported

### Whisper Model Download
- First run downloads the speech-to-text model (~140MB)
- Requires internet connection
- Model cached for subsequent runs

### Memory Usage
- Large video files may require more memory
- Reduce file size or use smaller Whisper model if needed
- Monitor Docker container memory limits

---

## 📄 License

This project is part of the IPS Semester 4 initiative.

---

## 🤝 Contributing

Contributions are welcome! Please ensure all new features include:
- Proper error handling
- Unit tests
- Documentation updates
- UI/UX considerations

---

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review API logs
3. Check browser console for frontend errors
4. Verify MongoDB and Redis connections

---

## 🎉 Version History

### v2.0 (Current)
- ✨ Added filler word detection
- ✨ Added silence & pause analysis
- ✨ Added speech-to-text with speaker attribution
- ✨ Added sentiment & tone analysis
- ✨ Enhanced dashboard with multiple views
- ✨ AI-generated insights and recommendations
- ✨ Comprehensive analysis reports

### v1.0
- Basic speaker diarization
- Simple engagement metrics
- File upload support

---

**Created with ❤️ for better meeting engagement analysis**
