import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Admin from './pages/Admin';
import Reports from './pages/Reports';
import AgentChat from './pages/AgentChat';
import FileHistory from './pages/FileHistory';
import FirebaseViewer from './firebase';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/admin">Admin</Link></li>
            <li><Link to="/reports">Reports</Link></li>
            <li><Link to="/agentchat">Agent Chat</Link></li>
            <li><Link to="/filehistory">File History</Link></li>
            <li><Link to="/firebase">Firebase Data</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/agentchat" element={<AgentChat />} />
          <Route path="/filehistory" element={<FileHistory />} />
          <Route path="/firebase" element={<FirebaseViewer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
