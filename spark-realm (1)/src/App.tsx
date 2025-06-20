import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Index from './pages/Index'
import JournalEntry from './pages/JournalEntry'
import PulseResponse from './pages/PulseResponse'
import Insights from './pages/Insights'
import Profile from './pages/Profile'
import NotFound from './pages/NotFound'
import { BottomNav } from './components/BottomNav'
import { Toaster } from './components/ui/toaster'

// Import Builder.io registry for visual editing
import '../builder-registry'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/journal" element={<JournalEntry />} />
          <Route path="/pulse" element={<PulseResponse />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <BottomNav />
        <Toaster />
      </div>
    </Router>
  )
}

export default App
