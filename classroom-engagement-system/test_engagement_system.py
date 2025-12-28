"""
Sample test file for Classroom Engagement System
Tests cover:
1. Engagement metric calculations
2. API endpoints
3. Celery task processing
"""

import pytest
import json
from datetime import datetime
from app.models.meeting import SpeakerSegment, MeetingAnalysis, SourceType
from app.tasks.diarization import DiarizationService


class TestEngagementMetrics:
    """Test engagement metric calculations"""
    
    def test_speaker_talk_time_calculation(self):
        """Test calculation of talk time per speaker"""
        segments = [
            SpeakerSegment(start=0.0, end=5.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=5.0, end=10.0, speaker_id="Speaker_2"),
            SpeakerSegment(start=10.0, end=15.0, speaker_id="Speaker_1"),
        ]
        
        service = DiarizationService()
        metrics = service.calculate_engagement_metrics(segments, 15.0)
        
        assert metrics["speaker_talk_time"]["Speaker_1"] == 10.0
        assert metrics["speaker_talk_time"]["Speaker_2"] == 5.0
    
    def test_participation_percentage(self):
        """Test participation percentage calculation"""
        segments = [
            SpeakerSegment(start=0.0, end=6.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=6.0, end=10.0, speaker_id="Speaker_2"),
        ]
        
        service = DiarizationService()
        metrics = service.calculate_engagement_metrics(segments, 10.0)
        
        assert metrics["speaker_participation"]["Speaker_1"] == 60.0
        assert metrics["speaker_participation"]["Speaker_2"] == 40.0
    
    def test_turn_taking_frequency(self):
        """Test turn-taking frequency calculation"""
        segments = [
            SpeakerSegment(start=0.0, end=2.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=2.0, end=4.0, speaker_id="Speaker_2"),  # Turn 1
            SpeakerSegment(start=4.0, end=6.0, speaker_id="Speaker_1"),  # Turn 2
            SpeakerSegment(start=6.0, end=8.0, speaker_id="Speaker_2"),  # Turn 3
        ]
        
        service = DiarizationService()
        metrics = service.calculate_engagement_metrics(segments, 8.0)  # 8 seconds = 0.133 minutes
        
        # 3 turns in 8 seconds = 3 / (8/60) = 22.5 turns per minute
        expected_frequency = 3 / (8 / 60)
        assert abs(metrics["turn_taking_frequency"] - expected_frequency) < 0.01
    
    def test_engagement_score_high_participation_balance(self):
        """Test engagement score with balanced participation"""
        segments = [
            SpeakerSegment(start=0.0, end=5.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=5.0, end=5.5, speaker_id="Speaker_2"),
            SpeakerSegment(start=5.5, end=10.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=10.0, end=10.5, speaker_id="Speaker_2"),
        ]
        
        service = DiarizationService()
        metrics = service.calculate_engagement_metrics(segments, 10.5)
        
        # Should have reasonable balance and turn-taking
        assert metrics["engagement_score"] > 50.0
        assert metrics["engagement_score"] <= 100.0
    
    def test_engagement_score_low_with_unbalanced_participation(self):
        """Test engagement score with imbalanced participation"""
        segments = [
            SpeakerSegment(start=0.0, end=100.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=100.0, end=105.0, speaker_id="Speaker_2"),
        ]
        
        service = DiarizationService()
        metrics = service.calculate_engagement_metrics(segments, 105.0)
        
        # Very imbalanced (95% vs 5%)
        assert metrics["engagement_score"] < 50.0


class TestDataModels:
    """Test Pydantic data models"""
    
    def test_speaker_segment_creation(self):
        """Test SpeakerSegment model"""
        segment = SpeakerSegment(
            start=0.0,
            end=5.0,
            speaker_id="Speaker_1",
            confidence=0.95
        )
        
        assert segment.start == 0.0
        assert segment.end == 5.0
        assert segment.speaker_id == "Speaker_1"
        assert segment.confidence == 0.95
    
    def test_meeting_analysis_creation(self):
        """Test MeetingAnalysis model"""
        analysis = MeetingAnalysis(
            meeting_id="test-001",
            source_type=SourceType.TEAMS,
            duration=300.0,
            segments=[
                SpeakerSegment(start=0.0, end=5.0, speaker_id="Speaker_1"),
                SpeakerSegment(start=5.0, end=10.0, speaker_id="Speaker_2"),
            ],
            engagement_score=75.5,
            speaker_talk_time={"Speaker_1": 150.0, "Speaker_2": 150.0},
            speaker_participation={"Speaker_1": 50.0, "Speaker_2": 50.0},
            turn_taking_frequency=2.4,
            audio_file_name="meeting.wav"
        )
        
        assert analysis.meeting_id == "test-001"
        assert analysis.source_type == SourceType.TEAMS
        assert len(analysis.segments) == 2
        assert analysis.engagement_score == 75.5
    
    def test_meeting_analysis_json_serialization(self):
        """Test JSON serialization"""
        analysis = MeetingAnalysis(
            meeting_id="test-001",
            source_type=SourceType.LIVE,
            duration=300.0,
            segments=[],
            engagement_score=75.5,
            speaker_talk_time={},
            speaker_participation={},
            turn_taking_frequency=2.4
        )
        
        # Should be serializable to dict
        data = analysis.model_dump()
        assert data["meeting_id"] == "test-001"
        assert data["source_type"] == "live"


class TestMockSegments:
    """Test mock segment generation"""
    
    def test_mock_segments_generation(self):
        """Test that mock segments are generated correctly"""
        service = DiarizationService()
        segments = service._create_mock_segments()
        
        assert len(segments) == 4
        assert segments[0].speaker_id == "Speaker_1"
        assert segments[0].start == 0.0
        assert segments[0].end == 5.0


# Example usage test
class TestAPIWorkflow:
    """Test complete workflow (requires running services)"""
    
    @pytest.mark.skip(reason="Requires running backend and MongoDB")
    def test_complete_upload_and_analysis_workflow(self):
        """
        Test:
        1. Upload file
        2. Get task status
        3. Retrieve analysis
        4. Validate metrics
        """
        import requests
        
        # Upload
        files = {"file": open("test_audio.wav", "rb")}
        response = requests.post(
            "http://localhost:8000/api/analyze-meeting",
            files=files,
            data={"meeting_id": "test-001", "source_type": "teams"}
        )
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Poll status
        # (In real test, use polling loop)
        import time
        time.sleep(10)
        
        status_response = requests.get(f"http://localhost:8000/api/task-status/{task_id}")
        assert status_response.json()["status"] in ["SUCCESS", "PENDING"]
        
        # Get analysis
        analysis_response = requests.get("http://localhost:8000/api/analysis/test-001")
        assert analysis_response.status_code == 200
        data = analysis_response.json()["data"]
        
        # Verify metrics exist
        assert "engagement_score" in data
        assert "turn_taking_frequency" in data
        assert "speaker_participation" in data


# Performance test example
@pytest.mark.skip(reason="Performance test - run separately")
def test_large_audio_processing():
    """Test processing of large audio file"""
    import time
    
    service = DiarizationService()
    
    # Create large segment list
    segments = []
    for i in range(1000):
        segments.append(
            SpeakerSegment(
                start=float(i),
                end=float(i + 1),
                speaker_id=f"Speaker_{(i % 5) + 1}"
            )
        )
    
    start_time = time.time()
    metrics = service.calculate_engagement_metrics(segments, 1000.0)
    elapsed_time = time.time() - start_time
    
    print(f"Processing 1000 segments took {elapsed_time:.3f} seconds")
    assert elapsed_time < 1.0  # Should be fast


if __name__ == "__main__":
    # Run tests with: pytest test_engagement_system.py -v
    pytest.main([__file__, "-v"])
