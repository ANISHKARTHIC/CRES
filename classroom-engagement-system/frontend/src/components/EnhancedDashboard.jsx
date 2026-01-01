import React, { useState, useEffect, useRef } from 'react';
import {
  PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line
} from 'recharts';
import axios from 'axios';
import '../styles/EnhancedDashboard.css';

const EnhancedDashboard = ({ meetingData, loading }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [expandedSpeaker, setExpandedSpeaker] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#6366F1', '#8B5CF6'];

  const getEngagementColor = (score) => {
    if (score >= 80) return '#10B981'; // Green
    if (score >= 60) return '#F59E0B'; // Orange
    if (score >= 40) return '#EF4444'; // Red
    return '#DC2626'; // Dark Red
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10B981';
      case 'negative': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0s';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  if (!selectedMeeting) {
    return (
      <div className="dashboard-container">
        <div className="meetings-list">
          <h2>Recorded Meetings</h2>
          {loading ? (
            <div className="loading">Loading meetings...</div>
          ) : meetingData && meetingData.length > 0 ? (
            meetingData.map((meeting) => (
              <div
                key={meeting._id}
                className="meeting-card"
                onClick={() => setSelectedMeeting(meeting)}
              >
                <div className="meeting-header">
                  <h3>{meeting.meeting_id}</h3>
                  <span className="engagement-badge" style={{ background: getEngagementColor(meeting.engagement_score) }}>
                    {meeting.engagement_score?.toFixed(1)}/100
                  </span>
                </div>
                <div className="meeting-meta">
                  <span className="meta-item">
                    <strong>Duration:</strong> {formatTime(meeting.duration)}
                  </span>
                  <span className="meta-item">
                    <strong>Speakers:</strong> {Object.keys(meeting.speaker_participation || {}).length}
                  </span>
                  <span className="meta-item" style={{ color: getSentimentColor(meeting.overall_sentiment) }}>
                    <strong>Sentiment:</strong> {meeting.overall_sentiment?.toUpperCase()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="no-data">No meetings found. Upload one to get started!</div>
          )}
        </div>
      </div>
    );
  }

  const speakerAnalysis = selectedMeeting.speaker_analysis || {};
  const participationData = Object.entries(selectedMeeting.speaker_participation || {}).map(
    ([speaker, percentage]) => ({ name: speaker, value: percentage })
  );

  const fillerData = Object.entries(selectedMeeting.most_common_fillers || {})
    .map(([word, count]) => ({ name: word, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return (
    <div className="enhanced-dashboard">
      <button className="back-button" onClick={() => setSelectedMeeting(null)}>← Back</button>

      <div className="tabs">
        {['overview', 'speakers', 'fillers', 'silence', 'sentiment'].map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div className="tab-content overview">
          <div className="overview-grid">
            {/* Main Metrics */}
            <div className="metric-card primary">
              <div className="metric-content">
                <div className="metric-label">Engagement Score</div>
                <div className="metric-value" style={{ color: 'white' }}>
                  {selectedMeeting.engagement_score?.toFixed(1)}/100
                </div>
                <div className="metric-description">Overall classroom engagement level</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Meeting Duration</div>
                <div className="metric-value">{formatTime(selectedMeeting.duration)}</div>
                <div className="metric-description">Total session time</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Turn-Taking Frequency</div>
                <div className="metric-value">{selectedMeeting.turn_taking_frequency?.toFixed(2)}</div>
                <div className="metric-description">Turns per minute</div>
              </div>
            </div>

            <div className="metric-card" style={{ borderLeftColor: getSentimentColor(selectedMeeting.overall_sentiment) }}>
              <div className="metric-content">
                <div className="metric-label">Overall Sentiment</div>
                <div className="metric-value" style={{ color: getSentimentColor(selectedMeeting.overall_sentiment) }}>
                  {selectedMeeting.overall_sentiment?.toUpperCase()}
                </div>
                <div className="metric-description">Class emotional tone</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Total Fillers</div>
                <div className="metric-value">{selectedMeeting.total_filler_count || 0}</div>
                <div className="metric-description">Filler words detected</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Silence Time</div>
                <div className="metric-value">{formatTime(selectedMeeting.total_silence_time)}</div>
                <div className="metric-description">Total quiet periods</div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="charts-grid">
            <div className="chart-container">
              <h3>Participation Distribution</h3>
              {participationData.length > 0 && (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={participationData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}%`} outerRadius={80} fill="#8884d8" dataKey="value">
                      {participationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="chart-container">
              <h3>Top Filler Words</h3>
              {fillerData.length > 0 && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={fillerData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#EF4444" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Insights */}
          {selectedMeeting.analysis_insights && selectedMeeting.analysis_insights.length > 0 && (
            <div className="insights-section">
              <h3>Key Insights</h3>
              <ul className="insights-list">
                {selectedMeeting.analysis_insights.slice(0, 5).map((insight, idx) => (
                  <li key={idx}>
                    <span className="insight-number">{idx + 1}</span>
                    <span className="insight-text">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {selectedMeeting.recommendations && selectedMeeting.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h3>Recommendations</h3>
              <ul className="recommendations-list">
                {selectedMeeting.recommendations.slice(0, 5).map((rec, idx) => (
                  <li key={idx}>
                    <span className="rec-number">{idx + 1}</span>
                    <span className="rec-text">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* SPEAKERS TAB */}
      {activeTab === 'speakers' && (
        <div className="tab-content speakers">
          {Object.entries(speakerAnalysis).map(([speakerId, analysis]) => (
            <div key={speakerId} className="speaker-card">
              <div className="speaker-header" onClick={() => setExpandedSpeaker(expandedSpeaker === speakerId ? null : speakerId)}>
                <h3>{speakerId}</h3>
                <div className="speaker-quick-stats">
                  <span className="stat-badge"><strong>Time:</strong> {formatTime(analysis.talk_time)}</span>
                  <span className="stat-badge"><strong>Share:</strong> {analysis.participation_percentage?.toFixed(1)}%</span>
                  <span className="stat-badge" style={{ background: getSentimentColor(analysis.sentiment_label) }}>
                    <strong>Engagement:</strong> {analysis.engagement_from_sentiment?.toFixed(0)}/100
                  </span>
                </div>
              </div>

              {expandedSpeaker === speakerId && (
                <div className="speaker-details">
                  <div className="detail-grid">
                    <div className="detail-item">
                      <label>Words Spoken</label>
                      <value>{analysis.word_count}</value>
                    </div>
                    <div className="detail-item">
                      <label>Turn Count</label>
                      <value>{analysis.turn_count}</value>
                    </div>
                    <div className="detail-item">
                      <label>Filler Count</label>
                      <value>{analysis.filler_count}</value>
                    </div>
                    <div className="detail-item">
                      <label>Filler Ratio</label>
                      <value>{analysis.filler_ratio?.toFixed(2)}%</value>
                    </div>
                    <div className="detail-item">
                      <label>Silence Duration</label>
                      <value>{formatTime(analysis.total_silence_duration)}</value>
                    </div>
                    <div className="detail-item">
                      <label>Avg Pause</label>
                      <value>{analysis.average_pause_duration?.toFixed(2)}s</value>
                    </div>
                    <div className="detail-item">
                      <label>Sentiment</label>
                      <value>{analysis.sentiment_label?.toUpperCase()}</value>
                    </div>
                    <div className="detail-item">
                      <label>Polarity</label>
                      <value>{analysis.sentiment_polarity?.toFixed(2)}</value>
                    </div>
                  </div>

                  {analysis.filler_breakdown && Object.keys(analysis.filler_breakdown).length > 0 && (
                    <div className="filler-breakdown">
                      <h4>Filler Breakdown:</h4>
                      {Object.entries(analysis.filler_breakdown).map(([word, count]) => (
                        <span key={word} className="filler-tag">
                          {word}: {count}
                        </span>
                      ))}
                    </div>
                  )}

                  {analysis.transcript && (
                    <div className="transcript-section">
                      <h4>Transcript Preview:</h4>
                      <p className="transcript-text">{analysis.transcript.substring(0, 500)}...</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* FILLERS TAB */}
      {activeTab === 'fillers' && (
        <div className="tab-content fillers">
          <div className="metric-card primary">
            <div className="metric-content">
              <div className="metric-label">Average Filler Ratio</div>
              <div className="metric-value">{selectedMeeting.average_filler_ratio?.toFixed(2)}%</div>
            </div>
          </div>

          {fillerData.length > 0 && (
            <div className="chart-container full-width">
              <h3>Filler Word Distribution</h3>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={fillerData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#EF4444" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* SILENCE TAB */}
      {activeTab === 'silence' && (
        <div className="tab-content silence">
          <div className="metrics-row">
            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Total Silence Duration</div>
                <div className="metric-value">{formatTime(selectedMeeting.total_silence_time)}</div>
                <div className="metric-description">Cumulative pause time</div>
              </div>
            </div>
          </div>

          {selectedMeeting.pause_statistics && (
            <div className="pause-stats">
              <h3>Pause Statistics by Speaker</h3>
              {selectedMeeting.pause_statistics.speaker_pause_ranking?.map((speaker) => (
                <div key={speaker.speaker_id} className="speaker-pause-stat">
                  <h4>{speaker.speaker_id}</h4>
                  <div className="stat-row">
                    <span>Pause Count: {speaker.pause_count}</span>
                    <span>Avg Pause: {speaker.avg_pause_duration?.toFixed(2)}s</span>
                    <span>Total Silence: {formatTime(speaker.total_silence)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* SENTIMENT TAB */}
      {activeTab === 'sentiment' && (
        <div className="tab-content sentiment">
          <div className="sentiment-overview">
            <div className="metric-card" style={{ borderLeftColor: getSentimentColor(selectedMeeting.overall_sentiment) }}>
              <div className="metric-content">
                <div className="metric-label">Overall Sentiment</div>
                <div className="metric-value" style={{ color: getSentimentColor(selectedMeeting.overall_sentiment) }}>
                  {selectedMeeting.overall_sentiment?.toUpperCase()}
                </div>
                <div className="metric-description">Aggregate emotional state</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Average Polarity</div>
                <div className="metric-value">{selectedMeeting.average_polarity?.toFixed(2)}</div>
                <div className="metric-description">Scale: -1 (negative) to +1 (positive)</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-content">
                <div className="metric-label">Emotional Tone</div>
                <div className="metric-value emotional-tone-text">{selectedMeeting.emotional_tone}</div>
                <div className="metric-description">Detected mood patterns</div>
              </div>
            </div>
          </div>

          {Object.entries(speakerAnalysis).length > 0 && (
            <div className="speaker-sentiment">
              <h3>Sentiment by Speaker</h3>
              {Object.entries(speakerAnalysis).map(([speakerId, analysis]) => (
                <div key={speakerId} className="speaker-sentiment-card" style={{ borderLeftColor: getSentimentColor(analysis.sentiment_label) }}>
                  <h4>{speakerId}</h4>
                  <div className="sentiment-details">
                    <span><strong>Sentiment:</strong> <span style={{ color: getSentimentColor(analysis.sentiment_label) }}>{analysis.sentiment_label?.toUpperCase()}</span></span>
                    <span><strong>Polarity:</strong> {analysis.sentiment_polarity?.toFixed(2)}</span>
                    <span><strong>Emotion:</strong> {analysis.dominant_emotion}</span>
                    <span><strong>Engagement:</strong> {analysis.engagement_from_sentiment?.toFixed(0)}/100</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedDashboard;
