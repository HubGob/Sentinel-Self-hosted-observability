import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Services from './pages/Services'
import Logs from './pages/Logs'
import Alerts from './pages/Alerts'
import Status from './pages/Status'

export default function App() {
  return (
    <Routes>
      {/* Public status page: deliberately renders outside the admin chrome so the
          URL can be shared with anyone. */}
      <Route path="/status" element={<Status />} />
      <Route
        path="*"
        element={
          <Layout>
            <Routes>
              <Route path="/" element={<Services />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/alerts" element={<Alerts />} />
            </Routes>
          </Layout>
        }
      />
    </Routes>
  )
}
