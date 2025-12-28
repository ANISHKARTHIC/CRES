from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    LIVE = "live"
    TEAMS = "teams"


class SpeakerSegment(BaseModel):
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    speaker_id: str = Field(..., description="Speaker identifier")
    confidence: Optional[float] = Field(default=None)


class SilenceSegment(BaseModel):
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    duration: float = Field(..., description="Duration in seconds")


class SpeakerAnalysis(BaseModel):
    """Comprehensive analysis for a single speaker"""
    speaker_id: str
    talk_time: float
    participation_percentage: float
    
    # Transcription
    transcript: str = Field(default="")
    word_count: int = Field(default=0)
    
    # Filler words
    filler_count: int = Field(default=0)
    filler_ratio: float = Field(default=0.0)
    filler_breakdown: Dict[str, int] = Field(default_factory=dict)
    
    # Silence/pauses
    total_silence_duration: float = Field(default=0.0)
    silence_percentage: float = Field(default=0.0)
    pause_count: int = Field(default=0)
    average_pause_duration: float = Field(default=0.0)
    
    # Sentiment & tone
    sentiment_polarity: float = Field(default=0.0)  # -1 to 1
    sentiment_label: str = Field(default="neutral")
    engagement_from_sentiment: float = Field(default=0.0)
    dominant_emotion: str = Field(default="neutral")
    
    # Engagement metrics
    speaker_engagement_score: float = Field(default=0.0)
    turn_count: int = Field(default=0)


class MeetingAnalysis(BaseModel):
    meeting_id: str
    source_type: SourceType
    duration: float
    segments: List[SpeakerSegment]
    
    # Overall engagement metrics
    engagement_score: float
    speaker_talk_time: dict  # {speaker_id: total_time}
    speaker_participation: dict  # {speaker_id: percentage}
    turn_taking_frequency: float  # turns per minute
    
    # Per-speaker comprehensive analysis
    speaker_analysis: Dict[str, SpeakerAnalysis] = Field(default_factory=dict)
    
    # Overall statistics
    meeting_transcript: str = Field(default="")
    total_filler_count: int = Field(default=0)
    average_filler_ratio: float = Field(default=0.0)
    most_common_fillers: Dict[str, int] = Field(default_factory=dict)
    
    # Silence statistics
    total_silence_time: float = Field(default=0.0)
    silence_segments: List[SilenceSegment] = Field(default_factory=list)
    pause_statistics: Dict[str, Any] = Field(default_factory=dict)
    
    # Sentiment statistics
    overall_sentiment: str = Field(default="neutral")
    average_polarity: float = Field(default=0.0)
    emotional_tone: str = Field(default="calm")
    
    # Insights and recommendations
    analysis_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    audio_file_name: Optional[str] = None


class FileUploadRequest(BaseModel):
    meeting_id: str
    source_type: SourceType


class AudioChunkRequest(BaseModel):
    meeting_id: str
    source_type: SourceType
    chunk: bytes
    timestamp: float
