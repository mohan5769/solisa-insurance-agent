import { useState } from 'react'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import FollowUpBrain from './pages/FollowUpBrain'
import LifelineRetention from './pages/LifelineRetention'

function App() {
  const [currentView, setCurrentView] = useState('landing')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Navigation Bar */}
      <nav className="bg-white/80 backdrop-blur-md shadow-lg sticky top-0 z-50 border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-500 rounded-xl flex items-center justify-center shadow-md">
                <span className="text-white font-bold text-lg">S</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Solisa</h1>
                <span className="text-xs text-gray-500">Insurance That Actually Cares</span>
              </div>
            </div>

            {/* Navigation Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={() => setCurrentView('landing')}
                className={`px-5 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'landing'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-blue-50 border border-gray-200'
                }`}
              >
                Get Quote
              </button>
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-5 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'dashboard'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-blue-50 border border-gray-200'
                }`}
              >
                Leads
              </button>
              <button
                onClick={() => setCurrentView('followup')}
                className={`px-5 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'followup'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-blue-50 border border-gray-200'
                }`}
              >
                AI Assistant
              </button>
              <button
                onClick={() => setCurrentView('retention')}
                className={`px-5 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'retention'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-blue-50 border border-gray-200'
                }`}
              >
                Retention
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {currentView === 'landing' && <LandingPage />}
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'followup' && <FollowUpBrain />}
        {currentView === 'retention' && <LifelineRetention />}
      </main>
    </div>
  )
}

export default App
