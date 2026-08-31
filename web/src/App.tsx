import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Services from './pages/Services'
import Logs from './pages/Logs'
import Alerts from './pages/Alerts'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Services />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/alerts" element={<Alerts />} />
      </Routes>
    </Layout>
  )
}
