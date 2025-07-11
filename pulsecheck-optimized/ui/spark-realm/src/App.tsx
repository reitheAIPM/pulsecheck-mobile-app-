import './App.css'
// Import Builder.io registry for visual editing
import '../builder-registry'
import React, { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { authService } from '@/services/authService'

// Import page components
import Index from './pages/Index'
import JournalEntry from './pages/JournalEntry'
import PulseResponse from './pages/PulseResponse'
import History from './pages/History'
import Insights from './pages/Insights'
import Profile from './pages/Profile'
import Privacy from './pages/Privacy'
import Auth from './pages/Auth'
import ResetPassword from './pages/ResetPassword'
import NotFound from './pages/NotFound'

// Import UI components
import { BottomNav } from './components/BottomNav'
import { ErrorBoundary } from './components/ErrorBoundary'
import { StatusIndicator } from '@/components/ui/loading-states'

interface User {
  id: string
  email: string
  name?: string
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if user is already authenticated
        const { user: currentUser, error } = await authService.getCurrentUser()
        
        if (currentUser && !error) {
          setUser(currentUser)
        }
      } catch (error) {
        console.log('No authenticated user found')
        // User is not authenticated, will show auth screen
      } finally {
        setIsLoading(false)
        setIsInitialized(true)
      }
    }

    initializeAuth()

    // Listen for auth state changes
    const { data: { subscription } } = authService.onAuthStateChange((user) => {
      console.log('Auth state changed:', user ? `User ${user.email} signed in` : 'User signed out')
      setUser(user)
    })

    // Cleanup subscription on unmount
    return () => {
      if (subscription) {
        subscription.unsubscribe()
      }
    }
  }, [])

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-violet-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">PulseCheck</h2>
            <p className="text-sm text-gray-600">Loading your wellness companion...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen">
        {user ? (
          // User is authenticated - show main app with all features
          <div className="bg-gradient-to-b from-violet-50 via-blue-50 to-indigo-100">
            <div className="max-w-none pb-20">
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/journal/:id?" element={<JournalEntry />} />
                <Route path="/pulse/:id?" element={<PulseResponse />} />
                <Route path="/history" element={<History />} />
                <Route path="/insights" element={<Insights />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/privacy" element={<Privacy />} />
                <Route path="/new-entry" element={<JournalEntry />} />
                <Route path="/reset-password" element={<ResetPassword />} />
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
                {/* Redirect auth routes to main app when authenticated */}
                <Route path="/auth" element={<Navigate to="/" replace />} />
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="/register" element={<Navigate to="/" replace />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
              <BottomNav />
            </div>
          </div>
        ) : (
          // User is not authenticated - show ONLY auth screen
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route path="/login" element={<Auth />} />
            <Route path="/register" element={<Auth />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            {/* For all other routes when not authenticated, show Auth page directly to avoid redirect loops */}
            <Route path="*" element={<Auth />} />
          </Routes>
        )}
        <Toaster />
      </div>
    </ErrorBoundary>
  )
}

export default App
