import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './layouts/Layout'
import Landing from './pages/Landing'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import DocumentDetails from './pages/DocumentDetails'
import Profile from './pages/Profile'
import KnowledgeGraph from './pages/KnowledgeGraph'
import AICopilot from './pages/AICopilot'
import Maintenance from './pages/Maintenance'
import Compliance from './pages/Compliance'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/" element={<Layout />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="documents" element={<Documents />} />
          <Route path="documents/:documentId" element={<DocumentDetails />} />
          <Route path="profile" element={<Profile />} />
          <Route path="knowledge-graph" element={<KnowledgeGraph />} />
          <Route path="ai-copilot" element={<AICopilot />} />
          <Route path="maintenance" element={<Maintenance />} />
          <Route path="compliance" element={<Compliance />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
