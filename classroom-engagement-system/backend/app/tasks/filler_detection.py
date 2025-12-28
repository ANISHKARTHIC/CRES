"""
Filler Word Detection Module
Detects and analyzes filler words like 'um', 'uh', 'aah', 'mmm', 'ooo', 'eh', 'like', 'you know', etc.
"""

import librosa
import numpy as np
from typing import List, Dict, Tuple
import re
from scipy import signal


class FillerWordDetector:
    """Detects and analyzes filler words in audio"""
    
    # Common filler words and patterns
    FILLER_PATTERNS = {
        'um': r'\bum\b|\bumm\b|\bhmm\b',
        'uh': r'\buh\b|\buuh\b|\bahh\b|\baah\b',
        'er': r'\ber\b|\berr\b',
        'ah': r'\bah\b',
        'oh': r'\boh\b|\booh\b',
        'mmm': r'\bmmm\b|\bmm\b|\bmhm\b',
        'like': r'\blike\b',
        'you_know': r'\byou know\b',
        'i_mean': r'\bi mean\b',
        'basically': r'\bbasically\b',
        'actually': r'\bactually\b',
        'literally': r'\bliterally\b',
        'right': r'\bright\b',
        'so': r'\bso\b',
        'yeah': r'\byeah\b|\byeaah\b',
    }
    
    def __init__(self):
        self.filler_word_timestamps = []
        
    def detect_fillers_from_transcript(
        self, 
        transcript: str, 
        speaker_id: str,
        start_time: float = 0.0
    ) -> Dict:
        """
        Detect filler words from transcript text
        
        Args:
            transcript: The transcribed text
            speaker_id: Speaker identifier
            start_time: Start time of this segment in seconds
            
        Returns:
            Dictionary with filler word counts and details
        """
        text_lower = transcript.lower()
        filler_counts = {}
        
        for filler_name, pattern in self.FILLER_PATTERNS.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                filler_counts[filler_name] = len(matches)
        
        total_fillers = sum(filler_counts.values())
        word_count = len(transcript.split())
        filler_ratio = (total_fillers / word_count * 100) if word_count > 0 else 0
        
        return {
            'speaker_id': speaker_id,
            'filler_counts': filler_counts,
            'total_fillers': total_fillers,
            'word_count': word_count,
            'filler_ratio': round(filler_ratio, 2),  # Percentage of words that are fillers
            'timestamp': start_time
        }
    
    def detect_fillers_from_audio(
        self,
        y: np.ndarray,
        sr: int,
        segment_start: float,
        segment_end: float
    ) -> Dict:
        """
        Detect probable filler sounds in audio using spectral analysis
        This is a heuristic approach to detect vocal fillers like 'um', 'uh', 'mmm'
        
        Args:
            y: Audio waveform
            sr: Sample rate
            segment_start: Segment start time in seconds
            segment_end: Segment end time in seconds
            
        Returns:
            Dictionary with detected filler info
        """
        try:
            # Extract segment
            start_sample = int(segment_start * sr)
            end_sample = int(segment_end * sr)
            segment = y[start_sample:end_sample]
            
            if len(segment) == 0:
                return {
                    'probable_fillers': 0,
                    'filler_segments': [],
                    'confidence': 0.0
                }
            
            # Compute MFCC (Mel-Frequency Cepstral Coefficients) for speech characteristics
            mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
            
            # Detect speech activity
            S = librosa.feature.melspectrogram(y=segment, sr=sr)
            S_db = librosa.power_to_db(S, ref=np.max)
            
            # Energy-based activity detection
            energy = np.sqrt(np.mean(S ** 2, axis=0))
            threshold = np.mean(energy) * 0.5
            
            # Find speech segments
            speech_frames = energy > threshold
            
            # Convert frames to time
            times = librosa.frames_to_time(np.arange(len(speech_frames)), sr=sr)
            
            # Group consecutive speech frames
            filler_segments = []
            current_segment_start = None
            
            for i, is_speech in enumerate(speech_frames):
                if is_speech:
                    if current_segment_start is None:
                        current_segment_start = times[i]
                else:
                    if current_segment_start is not None:
                        segment_duration = times[i-1] - current_segment_start
                        # Fillers typically very short (<1 second) or have specific characteristics
                        if segment_duration < 1.0:  # Likely filler
                            filler_segments.append({
                                'start': current_segment_start + segment_start,
                                'end': times[i-1] + segment_start,
                                'duration': segment_duration
                            })
                        current_segment_start = None
            
            probable_filler_count = len(filler_segments)
            confidence = min(0.8, probable_filler_count * 0.1)  # Heuristic confidence
            
            return {
                'probable_fillers': probable_filler_count,
                'filler_segments': filler_segments,
                'confidence': round(confidence, 2)
            }
        except Exception as e:
            print(f"Error in audio filler detection: {str(e)}")
            return {
                'probable_fillers': 0,
                'filler_segments': [],
                'confidence': 0.0
            }
    
    def analyze_all_fillers(self, fillers_by_speaker: List[Dict]) -> Dict:
        """
        Analyze filler words across all speakers
        
        Args:
            fillers_by_speaker: List of filler analysis for each speaker
            
        Returns:
            Aggregated filler statistics
        """
        if not fillers_by_speaker:
            return {
                'total_fillers': 0,
                'average_filler_ratio': 0.0,
                'filler_ranking': [],
                'most_common_fillers': {}
            }
        
        total_fillers = sum(f.get('total_fillers', 0) for f in fillers_by_speaker)
        
        # Rank speakers by filler usage
        filler_ranking = sorted(
            fillers_by_speaker,
            key=lambda x: x.get('total_fillers', 0),
            reverse=True
        )
        
        # Get most common filler words overall
        all_fillers = {}
        for filler_data in fillers_by_speaker:
            for filler_name, count in filler_data.get('filler_counts', {}).items():
                all_fillers[filler_name] = all_fillers.get(filler_name, 0) + count
        
        sorted_fillers = sorted(
            all_fillers.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        most_common_fillers = dict(sorted_fillers[:5])  # Top 5
        
        avg_filler_ratio = (
            sum(f.get('filler_ratio', 0) for f in fillers_by_speaker) / len(fillers_by_speaker)
            if fillers_by_speaker else 0
        )
        
        return {
            'total_fillers': total_fillers,
            'average_filler_ratio': round(avg_filler_ratio, 2),
            'filler_ranking': [
                {
                    'speaker_id': f['speaker_id'],
                    'total_fillers': f['total_fillers'],
                    'filler_ratio': f['filler_ratio']
                }
                for f in filler_ranking
            ],
            'most_common_fillers': most_common_fillers
        }
