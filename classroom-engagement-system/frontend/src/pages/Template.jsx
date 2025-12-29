import React, { useState } from 'react';

import FileUpload from '../components/FileUpload';
import EnhancedDashboard from '../components/EnhancedDashboard';

import logo from '../assets/col-kitelogo-removebg-preview2.jpg';
import techCommunityLogo from '../assets/ips.webp';

const Template = () => {
  const [uploadKey, setUploadKey] = useState(0);
  const [meetingData, setMeetingData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUploadSuccess = async () => {
    setUploadKey((prev) => prev + 1);
    // Refresh meeting data after upload
    await fetchMeetingData();
  };

  const fetchMeetingData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/all-analyses');
      const data = await response.json();
      if (data.data) {
        setMeetingData(data.data);
      }
    } catch (error) {
      console.error('Error fetching meeting data:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchMeetingData();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 to-slate-200 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-100 rounded-2xl shadow-lg mb-8 overflow-hidden">
          <div className="relative">
            <div className="h-2 bg-gradient-to-r from-blue-500 via-indigo-800 to-blue-900"></div>

            <div className="p-6 flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center space-x-4 mb-4 md:mb-0">
                <div className="bg-white p-3 rounded-lg shadow-md border border-blue-100">
                  <img src={logo} alt="Logo" className="h-14 w-auto object-contain" />
                </div>
                <div className="pl-2">
                  <h2 className="text-2xl font-bold text-blue-900 tracking-tight">Classroom Engagement System</h2>
                  <p className="text-blue-700 text-lg font-medium">Advanced Meeting Analysis & Engagement Analytics</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="bg-white p-3 rounded-lg shadow-md border border-blue-100">
                  <img src={techCommunityLogo} alt="Logo" className="h-16 w-auto object-contain" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="shadow-xl rounded-2xl overflow-hidden">
          <div className="bg-gradient-to-r from-sky-900 to-blue-700 px-8 py-6">
            <h1 className="text-white text-3xl font-bold tracking-tight">Enhanced Meeting Analysis</h1>
            <p className="text-blue-50 text-sm mt-1">Upload Teams meeting videos/audio and get comprehensive engagement analysis with AI-powered insights</p>
          </div>

          <div className="px-6 sm:px-8 py-8 space-y-8 bg-gradient-to-br from-blue-50 to-sky-50">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            <EnhancedDashboard meetingData={meetingData} loading={loading} />
          </div>
        </div>

        <footer className="mt-12">
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex items-center">
                <span className="text-blue-600 font-mono text-xl mr-2">&lt;/&gt;</span>
                <h3 className="text-lg font-bold text-slate-800 tracking-tight">Classroom Engagement System v2.0</h3>
              </div>
              <div className="flex items-center gap-3">
                <p className="text-gray-600 text-sm">© {new Date().getFullYear()} Powered by IPS Tech Community</p>
                <img src={techCommunityLogo} alt="IPS Tech Community Logo" className="h-9 w-auto object-contain" />
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Template;

