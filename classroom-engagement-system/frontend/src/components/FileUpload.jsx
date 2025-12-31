import React, { useState, useRef } from 'react';
import axios from 'axios';
import '../styles/FileUpload.css';

const FileUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [meetingId, setMeetingId] = useState('');
  const [sourceType, setSourceType] = useState('teams');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  const validateFile = (f) => {
    const maxSize = 500 * 1024 * 1024; // 500MB
    const validTypes = [
      'audio/wav',
      'audio/mpeg',
      'audio/mp3',
      'audio/x-wav',
      'audio/wave',
      // video containers we support (will extract audio server-side)
      'video/mp4',
      'video/webm',
      'video/ogg',
      'video/x-matroska',
    ];
    
    if (!f.type || !validTypes.includes(f.type)) {
      return { valid: false, error: `Invalid format. Supported: WAV, MP3, MP4 (video) . Got: ${f.type || 'unknown'}` };
    }
    if (f.size > maxSize) {
      return { valid: false, error: `File too large. Max 500MB, got ${(f.size / 1024 / 1024).toFixed(2)}MB` };
    }
    return { valid: true };
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    
    const validation = validateFile(selectedFile);
    if (validation.valid) {
      setFile(selectedFile);
      setMessage('');
    } else {
      setMessage(validation.error);
      setMessageType('error');
      setFile(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (!droppedFile) return;
    
    const validation = validateFile(droppedFile);
    if (validation.valid) {
      setFile(droppedFile);
      setMessage('');
    } else {
      setMessage(validation.error);
      setMessageType('error');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select an audio file');
      setMessageType('error');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if (meetingId.trim()) {
      formData.append('meeting_id', meetingId.trim());
    }
    formData.append('source_type', sourceType);

    try {
      setUploading(true);
      setMessage('Uploading...');
      setMessageType('info');
      
      const response = await axios.post(`${API_URL}/analyze-meeting`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        },
      });

      setMessage(`✓ Upload accepted. Task ID: ${response.data.task_id}. Waiting for analysis...`);
      setMessageType('info');

      // Clear file input while we poll
      setFile(null);
      setMeetingId('');
      if (fileInputRef.current) fileInputRef.current.value = '';

      // Poll task status until it's finished
      const taskId = response.data.task_id;
      const pollInterval = 3000;

      const pollTaskStatus = async () => {
        try {
          const statusResp = await axios.get(`${API_URL}/task-status/${taskId}`);
          const status = statusResp.data.status;

          if (status === 'SUCCESS') {
            setMessage(`✓ Analysis complete (meeting: ${statusResp.data.result?.meeting_id || ''})`);
            setMessageType('success');
            if (onUploadSuccess) onUploadSuccess(statusResp.data);
            return;
          }

          if (status === 'FAILURE' || status === 'REVOKED') {
            setMessage(`✗ Analysis failed: ${status}`);
            setMessageType('error');
            return;
          }

          // still processing; schedule next poll
          setTimeout(pollTaskStatus, pollInterval);
        } catch (err) {
          // network or server error while polling
          console.error('Task polling error:', err);
          setMessage(`✗ Error while checking task status: ${err.message || 'network error'}`);
          setMessageType('error');
        }
      };

      // start polling
      setTimeout(pollTaskStatus, pollInterval);
    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Upload failed';
      setMessage(`✗ ${errorMsg}`);
      setMessageType('error');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <div className="upload-header">
          <h2>Upload Meeting Recording</h2>
          <p className="subtitle">Analyze speaker engagement and turn-taking patterns</p>
        </div>
        
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label htmlFor="meetingId">Meeting ID <span className="optional">(optional)</span></label>
            <input
              id="meetingId"
              type="text"
              value={meetingId}
              onChange={(e) => setMeetingId(e.target.value)}
              placeholder="e.g., class-2024-01-15"
              className="input-field"
            />
          </div>

          <div className="form-row">
            <div className="form-group form-half">
              <label htmlFor="sourceType">Source Type</label>
              <select 
                id="sourceType"
                value={sourceType} 
                onChange={(e) => setSourceType(e.target.value)}
                className="select-field"
              >
                <option value="teams">Teams Meeting</option>
                <option value="live">Live Class</option>
              </select>
            </div>

            {file && (
              <div className="form-group form-half file-info">
                <label>File Info</label>
                <div className="file-details">
                  <p><strong>{file.name}</strong></p>
                  <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="fileInput">Audio File</label>
            <div 
              className={`file-input-wrapper ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                id="fileInput"
                type="file"
                accept="audio/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              <div className="file-input-content">
                <div className="file-icon"></div>
                <p className="file-label">
                  {file?.name || 'Drag audio file here or click to browse'}
                </p>
                <p className="file-hint">Supported: WAV, MP3, MP4/WEBM (video) — server will extract audio (max 500MB)</p>
              </div>
            </div>
          </div>

          {uploading && (
            <div className="progress-container">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
              </div>
              <p className="progress-text">{uploadProgress}% Complete</p>
            </div>
          )}

          <button
            type="submit"
            disabled={!file || uploading}
            className="upload-btn"
          >
            {uploading ? `Uploading (${uploadProgress}%)...` : 'Upload & Analyze'}
          </button>
        </form>

        {message && (
          <div className={`message message-${messageType}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
