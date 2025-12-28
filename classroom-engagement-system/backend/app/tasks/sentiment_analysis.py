"""
Sentiment and Tone Analysis Module
Analyzes sentiment, tone, and engagement indicators in transcripts
"""

from typing import List, Dict
import re
from textblob import TextBlob
from transformers import pipeline
import numpy as np


class SentimentToneAnalyzer:
    """Analyzes sentiment and tone of speech"""
    
    # Define emotion-indicating words
    POSITIVE_INDICATORS = {
        'great': 2, 'excellent': 2, 'amazing': 2, 'wonderful': 2, 'fantastic': 2,
        'love': 1.5, 'good': 1, 'nice': 1, 'happy': 1.5, 'glad': 1.5,
        'brilliant': 2, 'awesome': 2, 'perfect': 1.5, 'brilliant': 2,
        'interesting': 0.5, 'cool': 1, 'fun': 1, 'enjoy': 1.5
    }
    
    NEGATIVE_INDICATORS = {
        'terrible': -2, 'awful': -2, 'horrible': -2, 'hate': -2, 'bad': -1,
        'poor': -1, 'wrong': -1, 'sad': -1.5, 'angry': -1.5, 'frustrated': -1.5,
        'difficult': -0.5, 'hard': -0.5, 'problem': -0.5, 'issue': -0.5, 'concerned': -0.5
    }
    
    # Engagement indicators
    ENGAGEMENT_INDICATORS = {
        'agree': 1, 'absolutely': 1, 'definitely': 1, 'exactly': 1, 'right': 0.5,
        'understand': 0.5, 'know': 0.5, 'think': 0.5, 'believe': 0.5, 'feel': 0.5
    }
    
    DISENGAGEMENT_INDICATORS = {
        'whatever': -1, 'dunno': -0.5, 'maybe': -0.5, 'probably': -0.5, 'guess': -0.5,
        'not sure': -0.5, 'confused': -1, 'lost': -1
    }
    
    def __init__(self):
        """Initialize sentiment analyzer with transformer models"""
        try:
            # Try to load zero-shot classification for better sentiment detection
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        except:
            self.zero_shot_classifier = None
    
    def analyze_speaker_sentiment(
        self,
        transcript: str,
        speaker_id: str
    ) -> Dict:
        """
        Analyze sentiment of a speaker's transcript
        
        Args:
            transcript: Speaker's transcribed text
            speaker_id: Speaker identifier
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not transcript or not transcript.strip():
            return {
                'speaker_id': speaker_id,
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'emotions': {}
            }
        
        try:
            # Use TextBlob for basic sentiment
            blob = TextBlob(transcript)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment_label = 'positive'
                confidence = min(polarity, 1.0)
            elif polarity < -0.1:
                sentiment_label = 'negative'
                confidence = min(abs(polarity), 1.0)
            else:
                sentiment_label = 'neutral'
                confidence = 0.5
            
            # Detect emotions
            emotions = self._detect_emotions(transcript)
            
            # Calculate engagement score from sentiment
            engagement_score = self._calculate_sentiment_engagement(transcript)
            
            return {
                'speaker_id': speaker_id,
                'polarity': round(polarity, 2),  # -1 to 1
                'subjectivity': round(subjectivity, 2),  # 0 to 1
                'sentiment_label': sentiment_label,
                'confidence': round(confidence, 2),
                'emotions': emotions,
                'engagement_from_sentiment': round(engagement_score, 2)
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return {
                'speaker_id': speaker_id,
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment_label': 'unknown',
                'confidence': 0.0,
                'emotions': {},
                'engagement_from_sentiment': 0.0
            }
    
    def _detect_emotions(self, transcript: str) -> Dict:
        """
        Detect emotional indicators in text
        
        Args:
            transcript: Text to analyze
            
        Returns:
            Dictionary with emotion scores
        """
        text_lower = transcript.lower()
        emotions = {}
        
        # Calculate positive indicators
        positive_score = sum(
            score for word, score in self.POSITIVE_INDICATORS.items()
            if word in text_lower
        )
        
        # Calculate negative indicators
        negative_score = sum(
            score for word, score in self.NEGATIVE_INDICATORS.items()
            if word in text_lower
        )
        
        # Determine dominant emotion
        if positive_score > abs(negative_score):
            emotions['dominant'] = 'positive'
            emotions['intensity'] = min(positive_score / 5, 1.0)
        elif negative_score < -1 * positive_score:
            emotions['dominant'] = 'negative'
            emotions['intensity'] = min(abs(negative_score) / 5, 1.0)
        else:
            emotions['dominant'] = 'neutral'
            emotions['intensity'] = 0.5
        
        emotions['positive_indicators'] = positive_score
        emotions['negative_indicators'] = negative_score
        
        return emotions
    
    def _calculate_sentiment_engagement(self, transcript: str) -> float:
        """
        Calculate engagement score based on sentiment markers
        
        Args:
            transcript: Text to analyze
            
        Returns:
            Engagement score 0-100
        """
        text_lower = transcript.lower()
        
        # Count engagement markers
        engagement_score = sum(
            score for word, score in self.ENGAGEMENT_INDICATORS.items()
            if word in text_lower
        )
        
        # Subtract disengagement markers
        engagement_score -= sum(
            abs(score) for word, score in self.DISENGAGEMENT_INDICATORS.items()
            if word in text_lower
        )
        
        # Normalize to 0-100
        engagement_score = max(0, min(100, engagement_score * 10))
        return engagement_score
    
    def analyze_all_speakers_sentiment(
        self,
        speaker_sentiments: List[Dict]
    ) -> Dict:
        """
        Aggregate sentiment analysis across all speakers
        
        Args:
            speaker_sentiments: List of sentiment analysis for each speaker
            
        Returns:
            Aggregated sentiment statistics
        """
        if not speaker_sentiments:
            return {
                'average_polarity': 0.0,
                'overall_sentiment': 'neutral',
                'sentiment_distribution': {},
                'emotional_tone': 'calm',
                'engagement_ranking': [],
                'insights': []
            }
        
        # Calculate averages
        polarities = [s.get('polarity', 0) for s in speaker_sentiments]
        avg_polarity = np.mean(polarities)
        
        # Overall sentiment
        if avg_polarity > 0.2:
            overall_sentiment = 'positive'
        elif avg_polarity < -0.2:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Sentiment distribution
        sentiment_counts = {}
        for s in speaker_sentiments:
            label = s.get('sentiment_label', 'unknown')
            sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
        
        # Engagement ranking
        engagement_ranking = sorted(
            speaker_sentiments,
            key=lambda x: x.get('engagement_from_sentiment', 0),
            reverse=True
        )
        
        # Emotional tone analysis
        emotions = [s.get('emotions', {}).get('dominant', 'neutral') for s in speaker_sentiments]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
        emotional_tone = self._classify_emotional_tone(dominant_emotion)
        
        # Generate insights
        insights = []
        for sentiment_data in speaker_sentiments:
            speaker_id = sentiment_data.get('speaker_id', 'Unknown')
            polarity = sentiment_data.get('polarity', 0)
            engagement = sentiment_data.get('engagement_from_sentiment', 0)
            
            if polarity > 0.5:
                insights.append(f"{speaker_id}: Highly positive and enthusiastic")
            elif polarity < -0.5:
                insights.append(f"{speaker_id}: Negative tone detected - may indicate frustration")
            
            if engagement > 70:
                insights.append(f"{speaker_id}: Very engaged and interactive")
            elif engagement < 30:
                insights.append(f"{speaker_id}: Limited engagement markers")
        
        return {
            'average_polarity': round(avg_polarity, 2),
            'overall_sentiment': overall_sentiment,
            'sentiment_distribution': sentiment_counts,
            'emotional_tone': emotional_tone,
            'engagement_ranking': [
                {
                    'speaker_id': s.get('speaker_id', 'Unknown'),
                    'engagement_score': s.get('engagement_from_sentiment', 0),
                    'sentiment': s.get('sentiment_label', 'unknown')
                }
                for s in engagement_ranking
            ],
            'insights': insights
        }
    
    def _classify_emotional_tone(self, dominant_emotion: str) -> str:
        """
        Classify overall emotional tone
        
        Args:
            dominant_emotion: The dominant emotion
            
        Returns:
            Classification of emotional tone
        """
        if dominant_emotion == 'positive':
            return 'engaged_and_positive'
        elif dominant_emotion == 'negative':
            return 'concerned_or_frustrated'
        else:
            return 'calm_and_neutral'
