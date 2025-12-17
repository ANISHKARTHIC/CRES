import React, { useState } from 'react';
import MeetingDashboard from './components/MeetingDashboard';
import FileUpload from './components/FileUpload';
import './styles/App.css';

function App() {
  const [uploadKey, setUploadKey] = useState(0);

  const handleUploadSuccess = () => {
    // Refresh the dashboard after upload
    setUploadKey(prev => prev + 1);
  };

  return (
    <div className="App">
      <FileUpload onUploadSuccess={handleUploadSuccess} />
      <MeetingDashboard key={uploadKey} />
    </div>
  );
}

export default App;
