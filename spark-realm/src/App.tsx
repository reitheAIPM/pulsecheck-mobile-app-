import './App.css'
// Import Builder.io registry for visual editing
import '../builder-registry'
import { Routes, Route } from 'react-router-dom'
import Index from './pages/Index'
import JournalEntry from './pages/JournalEntry'
import PulseResponse from './pages/PulseResponse'
import Insights from './pages/Insights'
import Profile from './pages/Profile'
import Privacy from './pages/Privacy'
import History from './pages/History'
import NotFound from './pages/NotFound'
import { BottomNav } from './components/BottomNav'
import { ErrorBoundary } from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-b from-violet-50 via-blue-50 to-indigo-100">
        <div className="max-w-lg mx-auto pb-20">
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/journal/:id?" element={<JournalEntry />} />
            <Route path="/pulse/:id?" element={<PulseResponse />} />
            <Route path="/history" element={<History />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/new-entry" element={<JournalEntry />} />
            {/* Test route - this will show the test content */}
            <Route path="/test" element={
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="bg-white p-8 rounded-lg shadow-lg">
                  <h1 className="text-2xl font-bold text-blue-600">PulseCheck Test Page</h1>
                  <p className="mt-4">If you can see this, React is rendering correctly.</p>
                  <p className="mt-2 text-gray-500">Builder.io API Key: 93b18bce96bf4218884de91289488848</p>
                  <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                    Test Button
                  </button>
                </div>
              </div>
            } />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <BottomNav />
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App
