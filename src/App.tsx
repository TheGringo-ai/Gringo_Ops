// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Admin from './pages/Admin';
import Reports from './pages/Reports';
import AgentChat from './pages/AgentChat';
import FileHistory from './pages/FileHistory';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/chat" element={<AgentChat />} />
        <Route path="/history" element={<FileHistory />} />
      </Routes>
    </Router>
  );
};

export default App;