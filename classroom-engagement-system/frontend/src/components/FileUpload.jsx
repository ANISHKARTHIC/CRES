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
  const fileInputRef = useRef(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type.startsWith('audio/')) {
      setFile(selectedFile);
      setMessage('');
    } else {
      setMessage('Please select a valid audio file');
      setFile(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if (meetingId) {
      formData.append('meeting_id', meetingId);
    }
    formData.append('source_type', sourceType);

    try {
      setUploading(true);
      setMessage('');
      
      const response = await axios.post(`${API_URL}/analyze-meeting`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        },
      });

      setMessage(`✓ Upload successful! Task ID: ${response.data.task_id}`);
      setFile(null);
      setMeetingId('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      setMessage(`✗ Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h2>Upload Meeting Recording</h2>
        
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label>Meeting ID (optional)</label>
            <input
              type="text"
              value={meetingId}
              onChange={(e) => setMeetingId(e.target.value)}
              placeholder="e.g., class-2024-01-15"
            />
          </div>

          <div className="form-group">
            <label>Source Type</label>
            <select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              <option value="teams">Teams Meeting</option>
              <option value="live">Live Class</option>
            </select>
          </div>

          <div className="form-group">
            <label>Audio File</label>
            <div className="file-input-wrapper">
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileSelect}
              />
              <span>{file?.name || 'Choose an audio file'}</span>
            </div>
          </div>

          {uploading && (
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${uploadProgress}%` }}>
                {uploadProgress}%
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={!file || uploading}
            className="upload-btn"
          >
            {uploading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
        </form>

        {message && (
          <div className={`message ${message.startsWith('✓') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
