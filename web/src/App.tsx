import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Services from './pages/Services'
import Logs from './pages/Logs'
import Alerts from './pages/Alerts'
import Status from './pages/Status'
import Login from './pages/Login'

export default function App() {
  return (
    <Routes>
      {/* Public: deliberately outside the admin chrome and outside the auth
          gate, so the URL can be shared with people who have no account. */}
      <Route path="/status" element={<Status />} />
      <Route path="/login" element={<Login />} />

      <Route
        path="*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Services />} />
                <Route path="/logs" element={<Logs />} />
                <Route path="/alerts" element={<Alerts />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
