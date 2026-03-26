import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'
import UploadPage from './pages/UploadPage'
import DocumentsPage from './pages/DocumentsPage'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import { isAuthenticated } from './services/api'

function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-dark-950">
      <Navbar />
      <main>{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public route */}
        <Route path="/login" element={
          isAuthenticated() ? <Navigate to="/chat" replace /> : <LoginPage />
        } />

        {/* Protected routes */}
        <Route path="/chat" element={
          <ProtectedRoute>
            <AppLayout><ChatPage /></AppLayout>
          </ProtectedRoute>
        } />
        <Route path="/upload" element={
          <ProtectedRoute>
            <AppLayout><UploadPage /></AppLayout>
          </ProtectedRoute>
        } />
        <Route path="/documents" element={
          <ProtectedRoute>
            <AppLayout><DocumentsPage /></AppLayout>
          </ProtectedRoute>
        } />

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </Router>
  )
}
