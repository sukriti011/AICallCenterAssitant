import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ManagerDashboard from './pages/ManagerDashboard.jsx';
import CallDetails from './pages/CallDetails.jsx';
import { getAllCalls } from './data/callStore.js';

function CallsRedirect() {
  const calls = getAllCalls();
  const first = calls[0];
  return <Navigate to={first ? `/calls/${first.call_id}` : '/dashboard'} replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<ManagerDashboard />} />
        <Route path="/calls" element={<CallsRedirect />} />
        <Route path="/calls/:callId" element={<CallDetails />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
