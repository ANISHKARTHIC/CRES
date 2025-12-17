from pydantic import BaseModel, Field
from typing import List, Optional
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


class MeetingAnalysis(BaseModel):
    meeting_id: str
    source_type: SourceType
    duration: float
    segments: List[SpeakerSegment]
    engagement_score: float
    speaker_talk_time: dict  # {speaker_id: total_time}
    speaker_participation: dict  # {speaker_id: percentage}
    turn_taking_frequency: float  # turns per minute
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
