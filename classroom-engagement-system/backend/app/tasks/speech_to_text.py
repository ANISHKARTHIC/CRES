"""
Speech-to-Text with Speaker Identification Module
Transcribes audio and associates speech with identified speakers
"""

import whisper
import numpy as np
from typing import List, Dict
import librosa


class SpeechToTextService:
    """Converts speech to text with speaker attribution using Whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_size: Size of Whisper model ('tiny', 'base', 'small', 'medium', 'large')
        """
        try:
            self.model = whisper.load_model(model_size)
        except Exception as e:
            print(f"Error loading Whisper model: {str(e)}")
            self.model = None
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription and word-level timestamps
        """
        if not self.model:
            return {
                'full_transcript': '',
                'segments': [],
                'language': 'unknown'
            }
        
        try:
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                audio_path,
                verbose=False,
                language=None  # Auto-detect language
            )
            
            return {
                'full_transcript': result.get('text', ''),
                'segments': result.get('segments', []),
                'language': result.get('language', 'en')
            }
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return {
                'full_transcript': '',
                'segments': [],
                'language': 'unknown'
            }
    
    def match_transcript_to_speakers(
        self,
        transcript_segments: List[Dict],
        speaker_segments: List[Dict]
    ) -> List[Dict]:
        """
        Enhanced multi-speaker transcript matching algorithm
        Handles multiple speakers by finding best temporal overlap
        
        Args:
            transcript_segments: List of transcript segments with timestamps
            speaker_segments: List of speaker segments with timestamps
            
        Returns:
            List of speaker segments with matched transcription
        """
        matched_segments = []
        transcript_segments_copy = transcript_segments.copy()
        
        for speaker_seg in speaker_segments:
            speaker_start = speaker_seg.get('start', 0)
            speaker_end = speaker_seg.get('end', 0)
            speaker_id = speaker_seg.get('speaker_id', 'Unknown')
            speaker_duration = speaker_end - speaker_start
            
            # Find transcription segments with best temporal overlap
            matching_texts = []
            matched_trans_indices = []
            
            for trans_idx, trans_seg in enumerate(transcript_segments):
                trans_start = trans_seg.get('start', 0)
                trans_end = trans_seg.get('end', 0)
                trans_text = trans_seg.get('text', '').strip()
                
                # Calculate overlap percentage
                overlap_start = max(speaker_start, trans_start)
                overlap_end = min(speaker_end, trans_end)
                
                if overlap_end > overlap_start:  # There is overlap
                    overlap_duration = overlap_end - overlap_start
                    overlap_percentage = (overlap_duration / speaker_duration * 100) if speaker_duration > 0 else 0
                    
                    # Accept if at least 50% overlap
                    if overlap_percentage > 50 and trans_text:
                        matching_texts.append(trans_text)
                        matched_trans_indices.append(trans_idx)
            
            # Combine matching text - prioritize contiguous segments
            if matching_texts:
                full_text = ' '.join(matching_texts)
            else:
                # Fallback: find closest transcript segment
                closest_dist = float('inf')
                closest_text = ''
                
                for trans_seg in transcript_segments:
                    trans_start = trans_seg.get('start', 0)
                    trans_end = trans_seg.get('end', 0)
                    
                    # Distance to segment
                    distance = abs(speaker_start - trans_start)
                    
                    if distance < closest_dist:
                        closest_dist = distance
                        closest_text = trans_seg.get('text', '').strip()
                
                full_text = closest_text
            
            matched_segments.append({
                'speaker_id': speaker_id,
                'start': speaker_start,
                'end': speaker_end,
                'duration': speaker_duration,
                'transcript': full_text,
                'word_count': len(full_text.split()) if full_text else 0
            })
        
        return matched_segments
    
    def get_speaker_transcripts(
        self,
        speaker_transcript_segments: List[Dict]
    ) -> Dict:
        """
        Aggregate transcripts by speaker
        
        Args:
            speaker_transcript_segments: Speaker segments with transcripts
            
        Returns:
            Dictionary with speaker-wise transcripts and statistics
        """
        speaker_data = {}
        
        for segment in speaker_transcript_segments:
            speaker_id = segment.get('speaker_id', 'Unknown')
            transcript = segment.get('transcript', '')
            word_count = segment.get('word_count', 0)
            
            if speaker_id not in speaker_data:
                speaker_data[speaker_id] = {
                    'full_transcript': [],
                    'total_words': 0,
                    'segments': []
                }
            
            if transcript:
                speaker_data[speaker_id]['full_transcript'].append(transcript)
                speaker_data[speaker_id]['total_words'] += word_count
                speaker_data[speaker_id]['segments'].append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': transcript
                })
        
        # Combine full transcripts
        for speaker_id in speaker_data:
            speaker_data[speaker_id]['full_transcript'] = ' '.join(
                speaker_data[speaker_id]['full_transcript']
            )
        
        return speaker_data
    
    def extract_keywords_and_phrases(self, transcript: str) -> Dict:
        """
        Extract important keywords and phrases from transcript
        
        Args:
            transcript: The transcript text
            
        Returns:
            Dictionary with extracted information
        """
        if not transcript:
            return {
                'words': [],
                'topics': [],
                'questions_asked': 0,
                'statements_made': 0,
                'average_sentence_length': 0
            }
        
        # Simple statistics
        words = transcript.split()
        sentences = transcript.split('.')
        
        # Count questions and statements
        questions = transcript.count('?')
        statements = len(sentences) - questions - 1
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Extract potential keywords (simplified - words longer than 5 chars and not common words)
        common_words = {'the', 'and', 'that', 'this', 'with', 'from', 'have', 'what', 'when', 'where', 'which'}
        keywords = list(set(
            w.lower() for w in words 
            if len(w) > 5 and w.lower() not in common_words
        ))[:10]
        
        return {
            'total_words': len(words),
            'unique_words': len(set(w.lower() for w in words)),
            'keywords': keywords,
            'questions_asked': questions,
            'statements_made': statements,
            'average_sentence_length': round(avg_sentence_length, 2),
            'text_length': len(transcript)
        }
