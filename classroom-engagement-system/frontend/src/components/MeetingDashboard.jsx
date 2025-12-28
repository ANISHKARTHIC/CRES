import React, { useState, useEffect, useRef, useCallback } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import '../styles/Dashboard.css';

const MeetingDashboard = () => {
  const [meetingData, setMeetingData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const waveformRef = useRef(null);
  const wavesurferRef = useRef(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  const fetchAnalyses = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/all-analyses`);
      if (response.data.data && response.data.data.length > 0) {
        setMeetingData(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching analyses:', error);
    } finally {
      setLoading(false);
    }
  }, [API_URL]);

  // Fetch all analyses on mount
  useEffect(() => {
    fetchAnalyses();
  }, [fetchAnalyses]);

  const loadMeetingAnalysis = (meeting) => {
    setSelectedMeeting(meeting);
    // Initialize WaveSurfer if audio file is available
    if (meeting.audio_file_name) {
      initWaveSurfer(meeting);
    }
  };

  const initWaveSurfer = (meeting) => {
    if (waveformRef.current) {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
      }

      wavesurferRef.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#4f46e5',
        progressColor: '#818cf8',
        height: 100,
        responsive: true,
      });

      // Draw speaker regions on waveform
      if (meeting.segments && meeting.segments.length > 0) {
        drawSpeakerRegions(meeting.segments);
      }
    }
  };

  const drawSpeakerRegions = (segments) => {
    const colors = {
      'Speaker_1': '#3B82F6', // Blue - Teacher
      'Speaker_2': '#10B981', // Green - Student
      'Speaker_3': '#F59E0B', // Orange
      'Speaker_4': '#EF4444', // Red
      'Speaker_5': '#8B5CF6', // Purple
    };

    segments.forEach((segment, index) => {
      const color = colors[segment.speaker_id] || '#6B7280';
      
      // Create a region marker for visualization
      const regionContainer = document.createElement('div');
      regionContainer.style.position = 'absolute';
      regionContainer.style.top = '0';
      regionContainer.style.height = '100%';
      regionContainer.style.backgroundColor = color;
      regionContainer.style.opacity = '0.3';
      regionContainer.style.cursor = 'pointer';
      regionContainer.title = `${segment.speaker_id}: ${segment.start.toFixed(2)}s - ${segment.end.toFixed(2)}s`;
      
      if (waveformRef.current) {
        const duration = wavesurferRef.current?.getDuration() || 1;
        const startPercent = (segment.start / duration) * 100;
        const widthPercent = ((segment.end - segment.start) / duration) * 100;
        
        regionContainer.style.left = `${startPercent}%`;
        regionContainer.style.width = `${widthPercent}%`;
        
        waveformRef.current.appendChild(regionContainer);
      }
    });
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  const renderParticipationChart = () => {
    if (!selectedMeeting || !selectedMeeting.speaker_participation) {
      return null;
    }

    const data = Object.entries(selectedMeeting.speaker_participation).map(([speaker, percentage]) => ({
      name: speaker,
      value: parseFloat(percentage),
    }));

    return (
      <div className="chart-container">
        <h3>Participation Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderEngagementMetrics = () => {
    if (!selectedMeeting) return null;

    return (
      <div className="metrics-container">
        <div className="metric-card">
          <div className="metric-label">Engagement Score</div>
          <div className="metric-value" style={{ color: selectedMeeting.engagement_score >= 70 ? '#10B981' : '#F59E0B' }}>
            {selectedMeeting.engagement_score?.toFixed(1) || 'N/A'}
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Turn-Taking Frequency</div>
          <div className="metric-value">{selectedMeeting.turn_taking_frequency?.toFixed(2) || 'N/A'}/min</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Duration</div>
          <div className="metric-value">{(selectedMeeting.duration / 60)?.toFixed(1) || 'N/A'} min</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Source</div>
          <div className="metric-value">{selectedMeeting.source_type?.toUpperCase() || 'N/A'}</div>
        </div>
      </div>
    );
  };

  const renderTalkTimeStats = () => {
    if (!selectedMeeting || !selectedMeeting.speaker_talk_time) return null;

    return (
      <div className="stats-container">
        <h3>Talk Time per Speaker</h3>
        <table className="stats-table">
          <thead>
            <tr>
              <th>Speaker</th>
              <th>Talk Time (s)</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(selectedMeeting.speaker_talk_time).map(([speaker, talkTime]) => (
              <tr key={speaker}>
                <td>{speaker}</td>
                <td>{parseFloat(talkTime).toFixed(2)}</td>
                <td>{selectedMeeting.speaker_participation[speaker]}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading analyses...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Classroom Engagement Dashboard</h1>
        <p>Analyze speaker participation and engagement metrics</p>
      </header>

      <div className="dashboard-content">
        <div className="sidebar">
          <h2>Meetings</h2>
          <button onClick={fetchAnalyses} className="refresh-btn">Refresh</button>
          
          {meetingData && meetingData.length > 0 ? (
            <div className="meeting-list">
              {meetingData.map((meeting, idx) => (
                <div
                  key={idx}
                  className={`meeting-item ${selectedMeeting === meeting ? 'active' : ''}`}
                  onClick={() => loadMeetingAnalysis(meeting)}
                >
                  <div className="meeting-id">{meeting.meeting_id?.substring(0, 8)}...</div>
                  <div className="meeting-date">
                    {new Date(meeting.created_at).toLocaleDateString()}
                  </div>
                  <div className="meeting-type">{meeting.source_type}</div>
                </div>
              ))}
            </div>
          ) : (
            <p>No analyses available</p>
          )}
        </div>

        <div className="main-content">
          {selectedMeeting ? (
            <>
              <div className="waveform-section">
                <h2>Audio Waveform</h2>
                <div ref={waveformRef} className="waveform-container" />
              </div>

              {renderEngagementMetrics()}

              <div className="charts-section">
                {renderParticipationChart()}
                {renderTalkTimeStats()}
              </div>
            </>
          ) : (
            <div className="no-selection">
              <p>Select a meeting to view analysis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MeetingDashboard;
