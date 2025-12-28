"""
Silence Detection Module
Detects and analyzes silence/pauses in audio recordings
"""

import numpy as np
import librosa
from typing import List, Dict
from scipy import signal


class SilenceDetector:
    """Detects and analyzes silence/pauses in audio"""
    
    def __init__(self, silence_threshold_db: float = -40, min_duration: float = 0.3):
        """
        Initialize silence detector
        
        Args:
            silence_threshold_db: Threshold in dB for detecting silence
            min_duration: Minimum duration (seconds) to count as silence
        """
        self.silence_threshold_db = silence_threshold_db
        self.min_duration = min_duration
    
    def detect_silence_in_segment(
        self,
        y: np.ndarray,
        sr: int,
        segment_start: float,
        segment_end: float
    ) -> Dict:
        """
        Detect silence in a specific audio segment
        
        Args:
            y: Full audio waveform
            sr: Sample rate
            segment_start: Segment start time in seconds
            segment_end: Segment end time in seconds
            
        Returns:
            Dictionary with silence statistics
        """
        try:
            # Extract segment
            start_sample = int(segment_start * sr)
            end_sample = int(segment_end * sr)
            segment = y[start_sample:end_sample]
            
            if len(segment) == 0:
                return {
                    'total_silence_duration': 0.0,
                    'silence_percentage': 0.0,
                    'pause_count': 0,
                    'average_pause_duration': 0.0,
                    'longest_pause': 0.0,
                    'silence_segments': []
                }
            
            segment_duration = segment_end - segment_start
            
            # Compute RMS energy
            S = librosa.feature.melspectrogram(y=segment, sr=sr)
            S_db = librosa.power_to_db(S, ref=np.max)
            
            # Frame-level energy
            energy = np.mean(S_db, axis=0)
            
            # Detect silence frames
            silence_frames = energy < self.silence_threshold_db
            
            # Convert frames to time
            frame_times = librosa.frames_to_time(np.arange(len(silence_frames)), sr=sr)
            frame_duration = frame_times[1] - frame_times[0] if len(frame_times) > 1 else 0.02
            
            # Find silence segments
            silence_segments = []
            current_silence_start = None
            total_silence = 0.0
            
            for i, is_silent in enumerate(silence_frames):
                if is_silent:
                    if current_silence_start is None:
                        current_silence_start = frame_times[i]
                else:
                    if current_silence_start is not None:
                        silence_duration = frame_times[i-1] - current_silence_start + frame_duration
                        
                        # Only count if duration exceeds minimum
                        if silence_duration >= self.min_duration:
                            silence_segments.append({
                                'start': current_silence_start + segment_start,
                                'end': frame_times[i-1] + segment_start + frame_duration,
                                'duration': silence_duration
                            })
                            total_silence += silence_duration
                        
                        current_silence_start = None
            
            # Handle silence at end of segment
            if current_silence_start is not None:
                silence_duration = frame_times[-1] - current_silence_start + frame_duration
                if silence_duration >= self.min_duration:
                    silence_segments.append({
                        'start': current_silence_start + segment_start,
                        'end': segment_end,
                        'duration': silence_duration
                    })
                    total_silence += silence_duration
            
            # Calculate statistics
            silence_percentage = (total_silence / segment_duration * 100) if segment_duration > 0 else 0
            pause_count = len(silence_segments)
            average_pause = (total_silence / pause_count) if pause_count > 0 else 0
            longest_pause = max([s['duration'] for s in silence_segments]) if silence_segments else 0
            
            return {
                'total_silence_duration': round(total_silence, 2),
                'silence_percentage': round(silence_percentage, 2),
                'pause_count': pause_count,
                'average_pause_duration': round(average_pause, 2),
                'longest_pause': round(longest_pause, 2),
                'silence_segments': [
                    {
                        'start': round(s['start'], 2),
                        'end': round(s['end'], 2),
                        'duration': round(s['duration'], 2)
                    }
                    for s in silence_segments
                ]
            }
        except Exception as e:
            print(f"Error in silence detection: {str(e)}")
            return {
                'total_silence_duration': 0.0,
                'silence_percentage': 0.0,
                'pause_count': 0,
                'average_pause_duration': 0.0,
                'longest_pause': 0.0,
                'silence_segments': []
            }
    
    def detect_silence_overall(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict:
        """
        Detect silence in the entire audio
        
        Args:
            y: Audio waveform
            sr: Sample rate
            
        Returns:
            Dictionary with overall silence statistics
        """
        duration = librosa.get_duration(y=y, sr=sr)
        return self.detect_silence_in_segment(y, sr, 0.0, duration)
    
    def analyze_pauses_by_speaker(self, speaker_silences: List[Dict]) -> Dict:
        """
        Analyze pause patterns across speakers
        
        Args:
            speaker_silences: List of silence analysis for each speaker
            
        Returns:
            Aggregated pause statistics and ranking
        """
        if not speaker_silences:
            return {
                'total_silence_time': 0.0,
                'average_pause_count': 0.0,
                'speaker_pause_ranking': [],
                'quietest_speaker': None,
                'most_conversational': None,
                'insights': []
            }
        
        # Calculate aggregates
        total_silence = sum(s.get('total_silence_duration', 0) for s in speaker_silences)
        avg_pause_count = np.mean([s.get('pause_count', 0) for s in speaker_silences])
        
        # Rank speakers by pause frequency (more pauses = less silence = more engagement)
        pause_ranking = sorted(
            speaker_silences,
            key=lambda x: x.get('pause_count', 0),
            reverse=True
        )
        
        # Find quietest speaker (most total silence)
        quietest = max(speaker_silences, key=lambda x: x.get('total_silence_duration', 0))
        most_conversational = min(speaker_silences, key=lambda x: x.get('total_silence_duration', 0))
        
        # Generate insights
        insights = []
        for silence_data in speaker_silences:
            speaker_id = silence_data.get('speaker_id', 'Unknown')
            silence_pct = silence_data.get('silence_percentage', 0)
            avg_pause = silence_data.get('average_pause_duration', 0)
            
            if silence_pct > 40:
                insights.append(f"{speaker_id}: Very high silence ({silence_pct}%) - may indicate low engagement")
            elif silence_pct > 25:
                insights.append(f"{speaker_id}: High silence ({silence_pct}%) - natural pauses")
            elif avg_pause > 3.0:
                insights.append(f"{speaker_id}: Long average pauses ({avg_pause}s) - thinking/processing")
        
        return {
            'total_silence_time': round(total_silence, 2),
            'average_pause_count': round(avg_pause_count, 2),
            'speaker_pause_ranking': [
                {
                    'speaker_id': s.get('speaker_id', 'Unknown'),
                    'pause_count': s.get('pause_count', 0),
                    'avg_pause_duration': s.get('average_pause_duration', 0),
                    'total_silence': s.get('total_silence_duration', 0)
                }
                for s in pause_ranking
            ],
            'quietest_speaker': quietest.get('speaker_id', 'Unknown'),
            'most_conversational': most_conversational.get('speaker_id', 'Unknown'),
            'insights': insights
        }
