import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import KYCSubmissionPage from './pages/KYCSubmissionPage'
import StatusPage from './pages/StatusPage'
import AdminDashboard from './pages/AdminDashboard'
import ReviewPage from './pages/ReviewPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/submit" element={<KYCSubmissionPage />} />
          <Route path="/status/:applicationId" element={<StatusPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/review/:applicationId" element={<ReviewPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

