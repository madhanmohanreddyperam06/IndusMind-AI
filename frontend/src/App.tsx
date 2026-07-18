import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Sidebar, TopNavigation, MainWorkspace } from './components/layout'

// Lazy load pages for code splitting
const Landing = lazy(() => import('./pages/Landing'))
const SignIn = lazy(() => import('./pages/SignIn'))
const SignUp = lazy(() => import('./pages/SignUp'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Documents = lazy(() => import('./pages/Documents'))
const DocumentDetails = lazy(() => import('./pages/DocumentDetails'))
const KnowledgeGraph = lazy(() => import('./pages/KnowledgeGraph'))
const AICopilot = lazy(() => import('./pages/AICopilot'))
const Maintenance = lazy(() => import('./pages/Maintenance'))
const Compliance = lazy(() => import('./pages/Compliance'))
const Analytics = lazy(() => import('./pages/Analytics.tsx'))
const Settings = lazy(() => import('./pages/Settings'))
const Profile = lazy(() => import('./pages/Profile'))

import { useAuthStore } from './stores'

// Loading component for lazy-loaded routes
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/dashboard/*"
            element={
              <>
                <Sidebar />
                <TopNavigation />
                <MainWorkspace>
                  <ProtectedRoute>
                    <Suspense fallback={<PageLoader />}>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/copilot" element={<AICopilot />} />
                        <Route path="/documents" element={<Documents />} />
                        <Route path="/documents/:documentId" element={<DocumentDetails />} />
                        <Route path="/graph" element={<KnowledgeGraph />} />
                        <Route path="/maintenance" element={<Maintenance />} />
                        <Route path="/compliance" element={<Compliance />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/settings" element={<Settings />} />
                        <Route path="/profile" element={<Profile />} />
                      </Routes>
                    </Suspense>
                  </ProtectedRoute>
                </MainWorkspace>
              </>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
