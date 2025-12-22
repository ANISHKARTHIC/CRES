import React, { useState } from 'react';

import FileUpload from '../components/FileUpload';
import MeetingDashboard from '../components/MeetingDashboard';

import logo from '../assets/col-kitelogo-removebg-preview2.jpg';
import pyExpoLogo from '../assets/PyExpoLogo.svg';
import techCommunityLogo from '../assets/ips.webp';

const Template = () => {
  const [uploadKey, setUploadKey] = useState(0);

  const handleUploadSuccess = () => {
    setUploadKey((prev) => prev + 1);
  };

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
                  <p className="text-blue-700 text-lg font-medium">Speaker diarization & engagement analytics</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="bg-white p-3 rounded-lg shadow-md border border-blue-100">
                  <img src={pyExpoLogo} alt="Logo" className="h-12 w-auto object-contain" />
                </div>
                <div className="bg-white p-3 rounded-lg shadow-md border border-blue-100">
                  <img src={techCommunityLogo} alt="Logo" className="h-12 w-auto object-contain" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="shadow-xl rounded-2xl overflow-hidden">
          <div className="bg-gradient-to-r from-sky-900 to-blue-700 px-8 py-6">
            <h1 className="text-white text-3xl font-bold tracking-tight">Engagement Dashboard</h1>
            <p className="text-blue-50 text-sm mt-1">Upload meeting audio and view participation metrics</p>
          </div>

          <div className="px-6 sm:px-8 py-8 space-y-8 bg-gradient-to-br from-blue-50 to-sky-50">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            <MeetingDashboard key={uploadKey} />
          </div>
        </div>

        <footer className="mt-12">
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center mb-4 md:mb-0">
                <span className="text-blue-600 font-mono text-xl mr-2">&lt;/&gt;</span>
                <h3 className="text-lg font-bold text-slate-800 tracking-tight">Classroom Engagement</h3>
              </div>

              <p className="text-gray-600 text-sm">© {new Date().getFullYear()} Classroom Engagement System</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Template;
