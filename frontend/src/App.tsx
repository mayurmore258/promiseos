import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Dashboard } from './pages/Dashboard';
import { Analyze } from './pages/Analyze';
import { Commitments } from './pages/Commitments';
import { CommitmentDetails } from './pages/CommitmentDetails';
import { Evidence } from './pages/Evidence';
import { VerificationResultPage } from './pages/VerificationResult';
import { FollowUp } from './pages/FollowUp';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-surface text-on-surface flex flex-col font-body selection:bg-secondary/20 selection:text-secondary">
        {/* Global Navigation Header */}
        <Header />

        {/* Main Content Area */}
        <main className="flex-1 pb-16">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/commitments" element={<Commitments />} />
            <Route path="/commitments/:id" element={<CommitmentDetails />} />
            <Route path="/commitments/:id/verification" element={<VerificationResultPage />} />
            <Route path="/commitments/:id/follow-up" element={<FollowUp />} />
            <Route path="/evidence" element={<Evidence />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
