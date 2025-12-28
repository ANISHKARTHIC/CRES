"""
Analysis Report Generator
Generates comprehensive, formatted analysis reports for meeting assessments
"""

from typing import Dict, List
from datetime import datetime


class AnalysisReportGenerator:
    """Generates comprehensive analysis reports"""
    
    def __init__(self):
        self.timestamp = datetime.now()
    
    def generate_overall_summary(self, analysis: Dict) -> str:
        """
        Generate an overall summary of the analysis
        
        Args:
            analysis: The MeetingAnalysis data
            
        Returns:
            Formatted summary string
        """
        meeting_id = analysis.get('meeting_id', 'Unknown')
        duration = analysis.get('duration', 0)
        engagement = analysis.get('engagement_score', 0)
        overall_sentiment = analysis.get('overall_sentiment', 'neutral')
        
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║               MEETING ENGAGEMENT ANALYSIS REPORT                ║
╚════════════════════════════════════════════════════════════════╝

Meeting ID: {meeting_id}
Duration: {self._format_time(duration)}
Analysis Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OVERALL METRICS:
  • Engagement Score: {engagement:.1f}/100 {'🟢' if engagement > 70 else '🟡' if engagement > 40 else '🔴'}
  • Overall Sentiment: {overall_sentiment.upper()} 
  • Average Polarity: {analysis.get('average_polarity', 0):.2f} (-1 to 1)
  • Emotional Tone: {analysis.get('emotional_tone', 'calm')}

"""
        return summary
    
    def generate_speaker_report(self, speaker_analysis: Dict) -> str:
        """
        Generate detailed speaker-by-speaker report
        
        Args:
            speaker_analysis: Dictionary of speaker analyses
            
        Returns:
            Formatted speaker report
        """
        report = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 SPEAKER ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for speaker_id, analysis in speaker_analysis.items():
            report += f"""
┌─ {speaker_id} ─────────────────────────────────────────────┐
│
│  📝 SPEAKING METRICS:
│    • Talk Time: {self._format_time(analysis.talk_time)}
│    • Participation: {analysis.participation_percentage:.1f}%
│    • Words Spoken: {analysis.word_count}
│    • Turn Count: {analysis.turn_count}
│
│  ❌ FILLER WORDS:
│    • Total Fillers: {analysis.filler_count}
│    • Filler Ratio: {analysis.filler_ratio:.2f}%
"""
            
            if analysis.filler_breakdown:
                report += "│    • Breakdown: "
                fillers = [f"{word}({count})" for word, count in list(analysis.filler_breakdown.items())[:3]]
                report += ", ".join(fillers) + "\n"
            
            report += f"""│
│  ⏸️  SILENCE & PAUSES:
│    • Total Silence: {self._format_time(analysis.total_silence_duration)}
│    • Silence %%: {analysis.silence_percentage:.1f}%
│    • Pause Count: {analysis.pause_count}
│    • Avg Pause: {analysis.average_pause_duration:.2f}s
│
│  😊 SENTIMENT & TONE:
│    • Sentiment: {analysis.sentiment_label.upper()}
│    • Polarity: {analysis.sentiment_polarity:.2f}
│    • Engagement Score: {analysis.engagement_from_sentiment:.1f}/100
│    • Dominant Emotion: {analysis.dominant_emotion}
│
"""
            
            if analysis.transcript:
                preview = analysis.transcript[:80] + "..." if len(analysis.transcript) > 80 else analysis.transcript
                report += f"""│  📄 TRANSCRIPT PREVIEW:
│    "{preview}"
│
"""
            
            report += "└────────────────────────────────────────────────────┘\n"
        
        return report
    
    def generate_filler_analysis(self, filler_summary: Dict) -> str:
        """
        Generate detailed filler word analysis
        
        Args:
            filler_summary: Filler analysis summary
            
        Returns:
            Formatted filler report
        """
        report = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ FILLER WORD ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        total = filler_summary.get('total_fillers', 0)
        avg_ratio = filler_summary.get('average_filler_ratio', 0)
        
        report += f"""
Total Fillers Used: {total}
Average Filler Ratio: {avg_ratio:.2f}%

"""
        
        if filler_summary.get('most_common_fillers'):
            report += "Most Common Fillers:\n"
            for filler, count in filler_summary['most_common_fillers'].items():
                bar_length = min(30, count)
                bar = "█" * bar_length
                report += f"  • {filler:15} {count:3} times  {bar}\n"
            report += "\n"
        
        if filler_summary.get('filler_ranking'):
            report += "Speaker Ranking (Most Fillers):\n"
            for rank, data in enumerate(filler_summary['filler_ranking'], 1):
                report += f"  {rank}. {data['speaker_id']:15} - {data['total_fillers']} fillers ({data['filler_ratio']:.1f}%)\n"
        
        report += "\n"
        return report
    
    def generate_silence_analysis(self, pause_summary: Dict) -> str:
        """
        Generate detailed silence/pause analysis
        
        Args:
            pause_summary: Pause analysis summary
            
        Returns:
            Formatted silence report
        """
        report = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏸️  SILENCE & PAUSE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        report += f"""
Total Silence Time: {self._format_time(pause_summary.get('total_silence_time', 0))}
Average Pause Count: {pause_summary.get('average_pause_count', 0):.1f}

"""
        
        if pause_summary.get('speaker_pause_ranking'):
            report += "Speaker Pause Statistics:\n"
            for data in pause_summary['speaker_pause_ranking']:
                report += f"""
  {data['speaker_id']}:
    • Pause Count: {data['pause_count']}
    • Avg Pause: {data['avg_pause_duration']:.2f}s
    • Total Silence: {self._format_time(data['total_silence'])}
"""
        
        if pause_summary.get('insights'):
            report += "\nKey Insights:\n"
            for insight in pause_summary['insights']:
                report += f"  • {insight}\n"
        
        report += "\n"
        return report
    
    def generate_sentiment_analysis(self, sentiment_summary: Dict) -> str:
        """
        Generate detailed sentiment analysis
        
        Args:
            sentiment_summary: Sentiment analysis summary
            
        Returns:
            Formatted sentiment report
        """
        report = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😊 SENTIMENT & TONE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        sentiment = sentiment_summary.get('overall_sentiment', 'neutral')
        polarity = sentiment_summary.get('average_polarity', 0)
        tone = sentiment_summary.get('emotional_tone', 'calm')
        
        report += f"""
Overall Sentiment: {sentiment.upper()}
Average Polarity: {polarity:.2f} (-1 neutral to +1 positive)
Emotional Tone: {tone}

"""
        
        if sentiment_summary.get('sentiment_distribution'):
            report += "Sentiment Distribution:\n"
            dist = sentiment_summary['sentiment_distribution']
            for sentiment_type, count in dist.items():
                report += f"  • {sentiment_type.upper()}: {count}\n"
            report += "\n"
        
        if sentiment_summary.get('engagement_ranking'):
            report += "Engagement Ranking (by sentiment):\n"
            for rank, data in enumerate(sentiment_summary['engagement_ranking'], 1):
                emoji = "🟢" if data['engagement_score'] > 70 else "🟡" if data['engagement_score'] > 40 else "🔴"
                report += f"  {rank}. {data['speaker_id']:15} - {data['engagement_score']:.1f}/100 {emoji}\n"
        
        if sentiment_summary.get('insights'):
            report += "\nKey Insights:\n"
            for insight in sentiment_summary['insights']:
                report += f"  • {insight}\n"
        
        report += "\n"
        return report
    
    def generate_recommendations(self, recommendations: List[str]) -> str:
        """
        Generate recommendations section
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Formatted recommendations
        """
        report = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMMENDATIONS FOR IMPROVEMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        if not recommendations:
            report += "No specific recommendations at this time.\n\n"
        else:
            for idx, rec in enumerate(recommendations, 1):
                report += f"  {idx}. {rec}\n"
            report += "\n"
        
        return report
    
    def generate_full_report(self, analysis: Dict) -> str:
        """
        Generate the complete analysis report
        
        Args:
            analysis: The MeetingAnalysis data
            
        Returns:
            Complete formatted report
        """
        full_report = self.generate_overall_summary(analysis)
        full_report += self.generate_speaker_report(analysis.get('speaker_analysis', {}))
        full_report += self.generate_filler_analysis({
            'total_fillers': analysis.get('total_filler_count', 0),
            'average_filler_ratio': analysis.get('average_filler_ratio', 0),
            'most_common_fillers': analysis.get('most_common_fillers', {}),
            'filler_ranking': []
        })
        full_report += self.generate_silence_analysis(analysis.get('pause_statistics', {}))
        full_report += self.generate_sentiment_analysis({
            'overall_sentiment': analysis.get('overall_sentiment', 'neutral'),
            'average_polarity': analysis.get('average_polarity', 0),
            'emotional_tone': analysis.get('emotional_tone', 'calm'),
            'sentiment_distribution': {},
            'engagement_ranking': []
        })
        full_report += self.generate_recommendations(analysis.get('recommendations', []))
        full_report += """
╔════════════════════════════════════════════════════════════════╗
║                    END OF REPORT                               ║
╚════════════════════════════════════════════════════════════════╝
"""
        
        return full_report
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to human-readable time"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            mins = (seconds % 3600) / 60
            return f"{int(hours)}h {int(mins)}m"
