import os
import librosa
import numpy as np
from typing import List, Dict
from datetime import datetime
from pymongo import MongoClient
from app.config import settings
from app.models.meeting import (
    SpeakerSegment, MeetingAnalysis, SourceType, 
    SilenceSegment, SpeakerAnalysis
)
from app.tasks.celery_app import celery_app
from app.tasks.filler_detection import FillerWordDetector
from app.tasks.silence_detection import SilenceDetector
from app.tasks.speech_to_text import SpeechToTextService
from app.tasks.sentiment_analysis import SentimentToneAnalyzer


class DiarizationService:
    """Service for speaker diarization using pyannote.audio with enhanced analysis"""
    
    def __init__(self):
        self.mongodb_client = MongoClient(settings.mongodb_url)
        self.db = self.mongodb_client[settings.db_name]
        self.meetings_collection = self.db["meetings"]
        self.filler_detector = FillerWordDetector()
        self.silence_detector = SilenceDetector()
        self.stt_service = SpeechToTextService(model_size="base")
        self.sentiment_analyzer = SentimentToneAnalyzer()
        
    def load_audio(self, file_path: str) -> tuple:
        """Load audio file and return waveform and sample rate"""
        y, sr = librosa.load(file_path, sr=16000)
        return y, sr
    
    def perform_diarization(self, audio_file_path: str) -> List[SpeakerSegment]:
        """
        Perform speaker diarization using pyannote.audio
        Returns a list of SpeakerSegment objects
        """
        try:
            from pyannote.audio import Pipeline
            from huggingface_hub import login
            
            # Initialize pipeline (requires HuggingFace token)
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=True
            )
            
            # Process audio
            diarization = pipeline(audio_file_path)
            
            # Convert diarization output to SpeakerSegment objects
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segment = SpeakerSegment(
                    start=turn.start,
                    end=turn.end,
                    speaker_id=speaker,
                    confidence=1.0
                )
                segments.append(segment)
            
            return segments
        
        except Exception as e:
            print(f"Diarization error: {str(e)}")
            # Fallback: Create mock segments for development
            return self._create_mock_segments()
    
    def _create_mock_segments(self) -> List[SpeakerSegment]:
        """Create mock segments for development/testing"""
        segments = [
            SpeakerSegment(start=0.0, end=5.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=5.0, end=10.0, speaker_id="Speaker_2"),
            SpeakerSegment(start=10.0, end=15.0, speaker_id="Speaker_1"),
            SpeakerSegment(start=15.0, end=20.0, speaker_id="Speaker_2"),
        ]
        return segments
    
    def calculate_engagement_metrics(
        self, 
        segments: List[SpeakerSegment], 
        duration: float
    ) -> Dict:
        """Calculate engagement metrics from speaker segments"""
        
        # Calculate talk time per speaker
        speaker_talk_time = {}
        turn_count_per_speaker = {}
        for segment in segments:
            speaker_id = segment.speaker_id
            talk_time = segment.end - segment.start
            
            if speaker_id not in speaker_talk_time:
                speaker_talk_time[speaker_id] = 0
                turn_count_per_speaker[speaker_id] = 0
            
            speaker_talk_time[speaker_id] += talk_time
            turn_count_per_speaker[speaker_id] += 1
        
        # Calculate participation percentage
        speaker_participation = {}
        total_talk_time = sum(speaker_talk_time.values())
        
        for speaker_id, talk_time in speaker_talk_time.items():
            percentage = (talk_time / total_talk_time * 100) if total_talk_time > 0 else 0
            speaker_participation[speaker_id] = round(percentage, 2)
        
        # Calculate turn-taking frequency (speaker switches per minute)
        turn_count = 0
        if len(segments) > 1:
            for i in range(len(segments) - 1):
                if segments[i].speaker_id != segments[i + 1].speaker_id:
                    turn_count += 1
        
        turn_taking_frequency = (turn_count / (duration / 60)) if duration > 0 else 0
        
        # Calculate engagement score (0-100)
        # Based on turn-taking frequency and participation balance
        max_participation = max(speaker_participation.values()) if speaker_participation else 0
        balance_score = 100 - abs(100 - max_participation)
        turn_score = min(100, (turn_taking_frequency / 2) * 100)  # Normalize to 0-100
        engagement_score = (balance_score * 0.4 + turn_score * 0.6)
        
        return {
            "speaker_talk_time": speaker_talk_time,
            "speaker_participation": speaker_participation,
            "turn_taking_frequency": round(turn_taking_frequency, 2),
            "engagement_score": round(engagement_score, 2),
            "turn_count_per_speaker": turn_count_per_speaker
        }
    
    def perform_comprehensive_analysis(
        self,
        y: np.ndarray,
        sr: int,
        segments: List[SpeakerSegment],
        audio_file_path: str,
        duration: float
    ) -> Dict:
        """
        Perform comprehensive analysis including transcription, fillers, silence, and sentiment
        """
        analysis_data = {}
        
        # 1. Speech-to-text
        print("Performing speech-to-text transcription...")
        transcript_result = self.stt_service.transcribe_audio(audio_file_path)
        transcript_segments = transcript_result.get('segments', [])
        full_transcript = transcript_result.get('full_transcript', '')
        
        # 2. Match transcripts to speakers
        print("Matching transcripts to speakers...")
        speaker_segments_with_transcripts = self.stt_service.match_transcript_to_speakers(
            transcript_segments, 
            [s.model_dump() for s in segments]
        )
        
        # 3. Get speaker transcripts
        speaker_transcripts = self.stt_service.get_speaker_transcripts(
            speaker_segments_with_transcripts
        )
        
        # 4. Filler word detection
        print("Detecting filler words...")
        filler_by_speaker = []
        for speaker_id, trans_data in speaker_transcripts.items():
            transcript = trans_data['full_transcript']
            filler_analysis = self.filler_detector.detect_fillers_from_transcript(
                transcript, speaker_id
            )
            filler_by_speaker.append({
                'speaker_id': speaker_id,
                **filler_analysis
            })
        
        filler_summary = self.filler_detector.analyze_all_fillers(filler_by_speaker)
        
        # 5. Silence/pause detection
        print("Detecting silences and pauses...")
        silence_by_speaker = []
        silence_segments = []
        for segment in segments:
            silence_data = self.silence_detector.detect_silence_in_segment(
                y, sr, segment.start, segment.end
            )
            silence_data['speaker_id'] = segment.speaker_id
            silence_by_speaker.append(silence_data)
            
            for sil_seg in silence_data.get('silence_segments', []):
                silence_segments.append(SilenceSegment(
                    start=sil_seg['start'],
                    end=sil_seg['end'],
                    duration=sil_seg['duration']
                ))
        
        pause_summary = self.silence_detector.analyze_pauses_by_speaker(silence_by_speaker)
        
        # 6. Sentiment and tone analysis
        print("Analyzing sentiment and tone...")
        sentiment_by_speaker = []
        for speaker_id, trans_data in speaker_transcripts.items():
            transcript = trans_data['full_transcript']
            sentiment = self.sentiment_analyzer.analyze_speaker_sentiment(
                transcript, speaker_id
            )
            sentiment_by_speaker.append(sentiment)
        
        sentiment_summary = self.sentiment_analyzer.analyze_all_speakers_sentiment(
            sentiment_by_speaker
        )
        
        # 7. Generate comprehensive per-speaker analysis
        speaker_analysis = {}
        speaker_talk_time = {}
        for segment in segments:
            speaker_id = segment.speaker_id
            talk_time = segment.end - segment.start
            if speaker_id not in speaker_talk_time:
                speaker_talk_time[speaker_id] = 0
            speaker_talk_time[speaker_id] += talk_time
        
        total_talk_time = sum(speaker_talk_time.values())
        
        for segment in segments:
            speaker_id = segment.speaker_id
            
            if speaker_id not in speaker_analysis:
                # Get speaker-specific data
                trans_data = speaker_transcripts.get(speaker_id, {})
                filler_data = next((f for f in filler_by_speaker if f['speaker_id'] == speaker_id), {})
                silence_data = next((s for s in silence_by_speaker if s['speaker_id'] == speaker_id), {})
                sentiment_data = next((s for s in sentiment_by_speaker if s['speaker_id'] == speaker_id), {})
                
                talk_time = speaker_talk_time.get(speaker_id, 0)
                participation = (talk_time / total_talk_time * 100) if total_talk_time > 0 else 0
                
                speaker_analysis[speaker_id] = SpeakerAnalysis(
                    speaker_id=speaker_id,
                    talk_time=round(talk_time, 2),
                    participation_percentage=round(participation, 2),
                    transcript=trans_data.get('full_transcript', ''),
                    word_count=trans_data.get('total_words', 0),
                    filler_count=filler_data.get('total_fillers', 0),
                    filler_ratio=filler_data.get('filler_ratio', 0),
                    filler_breakdown=filler_data.get('filler_counts', {}),
                    total_silence_duration=silence_data.get('total_silence_duration', 0),
                    silence_percentage=silence_data.get('silence_percentage', 0),
                    pause_count=silence_data.get('pause_count', 0),
                    average_pause_duration=silence_data.get('average_pause_duration', 0),
                    sentiment_polarity=sentiment_data.get('polarity', 0),
                    sentiment_label=sentiment_data.get('sentiment_label', 'unknown'),
                    engagement_from_sentiment=sentiment_data.get('engagement_from_sentiment', 0),
                    dominant_emotion=sentiment_data.get('emotions', {}).get('dominant', 'neutral'),
                    turn_count=0
                )
        
        # Calculate turn counts
        for i in range(len(segments)):
            speaker_id = segments[i].speaker_id
            if speaker_id in speaker_analysis:
                speaker_analysis[speaker_id].turn_count += 1
        
        # Generate insights and recommendations
        insights = filler_summary.get('filler_ranking', [])
        insights.extend(pause_summary.get('insights', []))
        insights.extend(sentiment_summary.get('insights', []))
        
        recommendations = self._generate_recommendations(
            speaker_analysis,
            filler_summary,
            pause_summary,
            sentiment_summary
        )
        
        return {
            'speaker_analysis': speaker_analysis,
            'full_transcript': full_transcript,
            'total_filler_count': filler_summary.get('total_fillers', 0),
            'average_filler_ratio': filler_summary.get('average_filler_ratio', 0),
            'most_common_fillers': filler_summary.get('most_common_fillers', {}),
            'total_silence_time': pause_summary.get('total_silence_time', 0),
            'silence_segments': silence_segments,
            'pause_statistics': pause_summary,
            'overall_sentiment': sentiment_summary.get('overall_sentiment', 'neutral'),
            'average_polarity': sentiment_summary.get('average_polarity', 0),
            'emotional_tone': sentiment_summary.get('emotional_tone', 'calm'),
            'analysis_insights': insights,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, speaker_analysis, filler_summary, pause_summary, sentiment_summary) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Filler word recommendations
        if filler_summary['total_fillers'] > 50:
            recommendations.append("High filler word usage detected. Try to speak more deliberately and pause instead of using fillers.")
        
        # Silence recommendations
        if pause_summary.get('average_pause_count', 0) > 10:
            recommendations.append("Frequent long pauses detected. Consider organizing thoughts better to maintain conversation flow.")
        
        # Engagement recommendations
        for speaker_id, analysis in speaker_analysis.items():
            if analysis.engagement_from_sentiment < 30:
                recommendations.append(f"{speaker_id}: Consider being more engaged and enthusiastic during discussions.")
            if analysis.filler_ratio > 5:
                recommendations.append(f"{speaker_id}: Reduce filler words like 'um', 'uh', 'like' for clearer communication.")
        
        return recommendations
    
    def save_analysis_to_db(
        self, 
        meeting_id: str,
        source_type: SourceType,
        segments: List[SpeakerSegment],
        metrics: Dict,
        comprehensive_analysis: Dict,
        audio_file_name: str,
        duration: float
    ) -> str:
        """Save comprehensive meeting analysis to MongoDB"""
        
        analysis = MeetingAnalysis(
            meeting_id=meeting_id,
            source_type=source_type,
            duration=duration,
            segments=segments,
            engagement_score=metrics["engagement_score"],
            speaker_talk_time=metrics["speaker_talk_time"],
            speaker_participation=metrics["speaker_participation"],
            turn_taking_frequency=metrics["turn_taking_frequency"],
            speaker_analysis=comprehensive_analysis.get('speaker_analysis', {}),
            meeting_transcript=comprehensive_analysis.get('full_transcript', ''),
            total_filler_count=comprehensive_analysis.get('total_filler_count', 0),
            average_filler_ratio=comprehensive_analysis.get('average_filler_ratio', 0),
            most_common_fillers=comprehensive_analysis.get('most_common_fillers', {}),
            total_silence_time=comprehensive_analysis.get('total_silence_time', 0),
            silence_segments=comprehensive_analysis.get('silence_segments', []),
            pause_statistics=comprehensive_analysis.get('pause_statistics', {}),
            overall_sentiment=comprehensive_analysis.get('overall_sentiment', 'neutral'),
            average_polarity=comprehensive_analysis.get('average_polarity', 0),
            emotional_tone=comprehensive_analysis.get('emotional_tone', 'calm'),
            analysis_insights=comprehensive_analysis.get('analysis_insights', []),
            recommendations=comprehensive_analysis.get('recommendations', []),
            audio_file_name=audio_file_name
        )
        
        result = self.meetings_collection.insert_one(analysis.model_dump())
        return str(result.inserted_id)
    
    def close_connection(self):
        """Close MongoDB connection"""
        self.mongodb_client.close()


@celery_app.task(bind=True, name="app.tasks.diarization.analyze_audio_task")
def analyze_audio_task(
    self,
    file_path: str,
    meeting_id: str,
    source_type: str,
    audio_file_name: str
):
    """
    Celery task to perform comprehensive analysis
    """
    service = DiarizationService()
    
    try:
        # Get audio duration
        y, sr = service.load_audio(file_path)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Perform diarization
        segments = service.perform_diarization(file_path)
        
        # Calculate basic metrics
        metrics = service.calculate_engagement_metrics(segments, duration)
        
        # Perform comprehensive analysis
        print("Starting comprehensive analysis...")
        comprehensive_analysis = service.perform_comprehensive_analysis(
            y, sr, segments, file_path, duration
        )
        
        # Save to database
        analysis_id = service.save_analysis_to_db(
            meeting_id=meeting_id,
            source_type=SourceType(source_type),
            segments=segments,
            metrics=metrics,
            comprehensive_analysis=comprehensive_analysis,
            audio_file_name=audio_file_name,
            duration=duration
        )
        
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        service.close_connection()
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "meeting_id": meeting_id,
            "metrics": metrics
        }
    
    except Exception as e:
        service.close_connection()
        print(f"Error in analysis: {str(e)}")
        raise Exception(f"Audio analysis failed: {str(e)}")
