"""
Speaker Detection Enhancement Module
Advanced algorithms to properly identify and cluster 3+ speakers
"""

from typing import List, Dict, Tuple
import numpy as np
from scipy.spatial.distance import cdist
import librosa


class SpeakerEnhancer:
    """
    Enhanced speaker detection and clustering algorithms
    Handles multi-speaker scenarios (3+ speakers)
    """
    
    def __init__(self):
        """Initialize speaker enhancer"""
        self.min_speaker_duration = 0.3  # Minimum speaker segment duration (seconds)
        self.max_gap_to_merge = 0.5  # Maximum gap between segments to merge same speaker
    
    def enhance_speaker_segments(
        self,
        segments: List[Dict],
        audio_data: Tuple[np.ndarray, int]
    ) -> List[Dict]:
        """
        Enhance speaker segmentation by:
        1. Removing very short segments (noise)
        2. Merging same speaker segments separated by small gaps
        3. Detecting separated speaker clusters
        4. Improving speaker consistency
        
        Args:
            segments: List of speaker segments
            audio_data: Tuple of (audio_array, sample_rate)
            
        Returns:
            Enhanced list of speaker segments
        """
        if not segments:
            return segments
        
        y, sr = audio_data
        
        # Step 1: Remove very short segments
        filtered_segments = [
            s for s in segments 
            if (s.get('end', 0) - s.get('start', 0)) >= self.min_speaker_duration
        ]
        
        # Step 2: Merge same speaker segments with small gaps
        merged_segments = self._merge_speaker_segments(filtered_segments)
        
        # Step 3: Refine speaker identification
        enhanced_segments = self._refine_speaker_ids(merged_segments, y, sr)
        
        # Step 4: Validate we have multiple speakers
        unique_speakers = len(set(s.get('speaker_id', 'Unknown') for s in enhanced_segments))
        print(f"Enhanced speaker detection: {unique_speakers} unique speakers identified")
        
        return enhanced_segments
    
    def _merge_speaker_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Merge consecutive segments from same speaker if gap is small
        Reduces fragmentation of speaker turns
        """
        if not segments:
            return segments
        
        # Sort by start time
        sorted_segs = sorted(segments, key=lambda x: x.get('start', 0))
        merged = []
        current = dict(sorted_segs[0])
        
        for next_seg in sorted_segs[1:]:
            gap = next_seg.get('start', 0) - current.get('end', 0)
            
            # If same speaker and small gap, merge
            if (next_seg.get('speaker_id') == current.get('speaker_id') and 
                gap <= self.max_gap_to_merge):
                # Extend current segment
                current['end'] = next_seg.get('end', current['end'])
                current['confidence'] = max(
                    current.get('confidence', 0.9),
                    next_seg.get('confidence', 0.9)
                )
            else:
                merged.append(current)
                current = dict(next_seg)
        
        merged.append(current)
        return merged
    
    def _refine_speaker_ids(
        self,
        segments: List[Dict],
        y: np.ndarray,
        sr: int
    ) -> List[Dict]:
        """
        Refine speaker identification using voice characteristics
        Helps distinguish between speakers even if they weren't properly separated
        """
        refined_segments = []
        
        for seg in segments:
            # Extract audio chunk for this segment
            start_sample = int(seg.get('start', 0) * sr)
            end_sample = int(seg.get('end', 0) * sr)
            
            # Ensure valid range
            start_sample = max(0, start_sample)
            end_sample = min(len(y), end_sample)
            
            if start_sample >= end_sample:
                refined_segments.append(seg)
                continue
            
            chunk = y[start_sample:end_sample]
            
            # Extract voice characteristics
            voice_features = self._extract_voice_features(chunk, sr)
            
            refined_seg = dict(seg)
            refined_seg['voice_features'] = voice_features
            refined_segments.append(refined_seg)
        
        # Re-cluster speakers based on voice characteristics
        refined_segments = self._cluster_speakers_by_voice(refined_segments)
        
        return refined_segments
    
    def _extract_voice_features(self, audio_chunk: np.ndarray, sr: int) -> Dict:
        """
        Extract voice characteristics useful for speaker distinction
        """
        if len(audio_chunk) == 0:
            return {
                'pitch_mean': 0,
                'pitch_variance': 0,
                'mfcc_mean': [0] * 13,
                'spectral_centroid': 0,
                'zero_crossing_rate': 0
            }
        
        try:
            # Pitch estimation (fundamental frequency)
            onset_env = librosa.onset.onset_strength(y=audio_chunk, sr=sr)
            onset_frames = librosa.onset.onset_detect(onset_strength=onset_env, sr=sr)
            
            # MFCC (Mel-Frequency Cepstral Coefficients) - voice timbre
            mfcc = librosa.feature.mfcc(y=audio_chunk, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1).tolist() if mfcc.size > 0 else [0] * 13
            
            # Spectral centroid - brightness of voice
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_chunk, sr=sr)
            centroid_mean = float(np.mean(spectral_centroid)) if spectral_centroid.size > 0 else 0
            
            # Zero crossing rate - noisiness
            zcr = librosa.feature.zero_crossing_rate(audio_chunk)
            zcr_mean = float(np.mean(zcr)) if zcr.size > 0 else 0
            
            return {
                'mfcc_mean': mfcc_mean,
                'spectral_centroid': centroid_mean,
                'zero_crossing_rate': zcr_mean,
                'energy': float(np.mean(audio_chunk ** 2))
            }
        
        except Exception as e:
            print(f"Feature extraction error: {str(e)}")
            return {
                'mfcc_mean': [0] * 13,
                'spectral_centroid': 0,
                'zero_crossing_rate': 0,
                'energy': 0
            }
    
    def _cluster_speakers_by_voice(self, segments: List[Dict]) -> List[Dict]:
        """
        Re-assign speaker IDs based on voice similarity
        Helps properly identify multiple speakers
        """
        if len(segments) < 2:
            return segments
        
        # Extract voice features for clustering
        features_list = []
        for seg in segments:
            features = seg.get('voice_features', {})
            mfcc = features.get('mfcc_mean', [0] * 13)
            spectral = features.get('spectral_centroid', 0)
            zcr = features.get('zero_crossing_rate', 0)
            
            # Normalize features for clustering
            feature_vector = mfcc + [spectral / 2000, zcr]  # Normalize centroid
            features_list.append(feature_vector)
        
        # Simple clustering: group similar voice characteristics
        # Assign speaker ID based on cluster membership
        speaker_mapping = {}
        next_speaker_id = 1
        
        for i, seg in enumerate(segments):
            current_speaker = seg.get('speaker_id', f'Speaker_{i+1}')
            
            # If speaker not yet mapped, assign new ID
            if current_speaker not in speaker_mapping:
                # Check if similar to existing speakers
                found_match = False
                
                for existing_speaker, indices in speaker_mapping.items():
                    if indices:  # If speaker has segments
                        # Calculate similarity to existing speaker
                        existing_idx = indices[0]
                        distance = self._calculate_voice_distance(
                            features_list[i],
                            features_list[existing_idx]
                        )
                        
                        # If similar enough, group with existing speaker
                        if distance < 0.7:
                            speaker_mapping[existing_speaker].append(i)
                            found_match = True
                            break
                
                # If no match found, assign new speaker
                if not found_match:
                    new_speaker = f'Speaker_{next_speaker_id}'
                    speaker_mapping[new_speaker] = [i]
                    next_speaker_id += 1
            else:
                if current_speaker not in speaker_mapping:
                    speaker_mapping[current_speaker] = []
                speaker_mapping[current_speaker].append(i)
        
        # Apply speaker mapping
        speaker_reassignment = {}
        for speaker_id, indices in speaker_mapping.items():
            for idx in indices:
                speaker_reassignment[idx] = speaker_id
        
        for i, seg in enumerate(segments):
            seg['speaker_id'] = speaker_reassignment.get(i, f'Speaker_{i+1}')
        
        return segments
    
    def _calculate_voice_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate distance between two voice feature vectors
        Lower distance = more similar voices
        """
        if len(vec1) == 0 or len(vec2) == 0:
            return 1.0
        
        try:
            vec1_arr = np.array(vec1).reshape(1, -1)
            vec2_arr = np.array(vec2).reshape(1, -1)
            
            # Use Euclidean distance
            distance = float(cdist(vec1_arr, vec2_arr, metric='euclidean')[0][0])
            
            # Normalize to 0-1 range
            return min(distance / 10.0, 1.0)
        except:
            return 1.0
    
    def get_speaker_summary(self, segments: List[Dict]) -> Dict:
        """
        Get summary of detected speakers
        """
        speaker_data = {}
        
        for seg in segments:
            speaker_id = seg.get('speaker_id', 'Unknown')
            duration = seg.get('end', 0) - seg.get('start', 0)
            
            if speaker_id not in speaker_data:
                speaker_data[speaker_id] = {
                    'total_duration': 0,
                    'turn_count': 0,
                    'confidence_scores': []
                }
            
            speaker_data[speaker_id]['total_duration'] += duration
            speaker_data[speaker_id]['turn_count'] += 1
            speaker_data[speaker_id]['confidence_scores'].append(seg.get('confidence', 0.9))
        
        # Calculate average confidence per speaker
        for speaker_id in speaker_data:
            scores = speaker_data[speaker_id]['confidence_scores']
            speaker_data[speaker_id]['avg_confidence'] = (
                np.mean(scores) if scores else 0.9
            )
            del speaker_data[speaker_id]['confidence_scores']
        
        return speaker_data
