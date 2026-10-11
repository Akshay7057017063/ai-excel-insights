import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import LandingPage from './pages/LandingPage'
import UploadPage from './pages/UploadPage'
import ReportPage from './pages/ReportPage'
import ReportsListPage from './pages/ReportsListPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import PricingPage from './pages/PricingPage'
import DashboardLayout from './layouts/DashboardLayout'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/app" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/upload" replace />} />
          <Route path="reports" element={<ReportsListPage />} />
          <Route path="reports/:reportId" element={<ReportPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
