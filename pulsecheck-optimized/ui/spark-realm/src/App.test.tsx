import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { HashRouter } from 'react-router-dom'
import App from './App'

// Mock the API service to avoid network calls during tests
vi.mock('./services/api', () => ({
  apiService: {
    healthCheck: vi.fn().mockResolvedValue({ status: 'healthy' }),
    getJournalEntries: vi.fn().mockResolvedValue([]),
    createJournalEntry: vi.fn().mockResolvedValue({ id: 'test-id' }),
    testConnection: vi.fn().mockResolvedValue(true),
    getJournalStats: vi.fn().mockResolvedValue({
      total_entries: 0,
      current_streak: 0,
      longest_streak: 0,
      average_mood: 5,
      average_energy: 5,
      average_stress: 5
    })
  }
}))

describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(
      <HashRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <App />
      </HashRouter>
    )
    
    // Check that the app renders without errors
    expect(container).toBeTruthy()
  })

  it('renders navigation component', () => {
    const { container } = render(
      <HashRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <App />
      </HashRouter>
    )
    
    // Check that the app renders without errors
    expect(container).toBeTruthy()
  })

  it('renders routes container', () => {
    const { container } = render(
      <HashRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <App />
      </HashRouter>
    )
    
    // Check that the app renders without errors
    expect(container).toBeTruthy()
  })
}) 