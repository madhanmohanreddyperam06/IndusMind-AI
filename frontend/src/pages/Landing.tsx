import { Link } from 'react-router-dom'

function Landing() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <div className="flex items-center">
              <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">IndusMind AI</h1>
            </div>
            <div className="flex items-center space-x-6">
              <Link
                to="/signin"
                className="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="bg-gray-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 lg:px-8 pt-32 pb-32 relative">
        <div className="max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-semibold text-gray-900 tracking-tight leading-[1.1] mb-8">
            IndusMind AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 leading-relaxed mb-12 max-w-3xl">
            Transforming Scattered Industrial Documents into Intelligent, Connected, and Actionable Knowledge
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/signup"
              className="bg-gray-900 text-white px-8 py-4 rounded-lg text-base font-medium hover:bg-gray-800 transition-colors text-center"
            >
              Start Free Trial
            </Link>
            <Link
              to="/signin"
              className="border border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-base font-medium hover:border-gray-400 hover:bg-gray-50 transition-colors text-center"
            >
              Sign In
            </Link>
          </div>
        </div>
        <div className="hidden md:block absolute right-6 lg:right-8 top-32">
          <img src="/Logo1.png" alt="IndusMind AI Logo" className="h-64 w-auto max-w-lg" />
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-24">
        <div className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 tracking-tight mb-4">What We Do</h2>
          <p className="text-lg text-gray-600 max-w-2xl">Intelligent document processing for industrial operations</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="group bg-white rounded-xl p-8 border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mb-6 group-hover:bg-gray-200 transition-colors">
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Document Ingestion</h3>
            <p className="text-gray-600 leading-relaxed">
              Upload and process industrial documents with intelligent extraction and categorization.
            </p>
          </div>

          <div className="group bg-white rounded-xl p-8 border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mb-6 group-hover:bg-gray-200 transition-colors">
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">AI-Powered Insights</h3>
            <p className="text-gray-600 leading-relaxed">
              Extract actionable insights from your documents using advanced machine learning.
            </p>
          </div>

          <div className="group bg-white rounded-xl p-8 border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mb-6 group-hover:bg-gray-200 transition-colors">
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Knowledge Graph</h3>
            <p className="text-gray-600 leading-relaxed">
              Build connected knowledge graphs to understand relationships across your data.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gray-50 py-24">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-semibold text-gray-900 tracking-tight mb-4">Ready to Get Started?</h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Transform your industrial documents into intelligent knowledge today.
          </p>
          <Link
            to="/signup"
            className="inline-block bg-gray-900 text-white px-8 py-4 rounded-lg text-base font-medium hover:bg-gray-800 transition-colors"
          >
            Create Free Account
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-100 py-16">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-8 md:mb-0">
              <h3 className="text-xl font-semibold text-white">IndusMind AI</h3>
              <p className="text-gray-400 text-sm mt-2">Industrial Knowledge Intelligence Platform</p>
            </div>
            <div className="flex space-x-8">
              <Link to="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy</Link>
              <Link to="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms</Link>
              <Link to="#" className="text-gray-400 hover:text-white text-sm transition-colors">Contact</Link>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 IndusMind AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Landing
