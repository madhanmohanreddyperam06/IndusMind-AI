import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Sidebar, TopNavigation, MainWorkspace, Footer } from './components/layout'
import PageLoader from './components/common/PageLoader'
import ErrorPage from './components/common/ErrorPage'
import NotFoundPage from './components/common/NotFoundPage'

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
                    <Suspense fallback={<PageLoader message="Loading page..." />}>
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
                <Footer />
              </>
            }
          />
          <Route path="/error" element={<ErrorPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
