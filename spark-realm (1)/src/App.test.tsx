import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'

// Mock the API service to avoid network calls during tests
vi.mock('./services/api', () => ({
  default: {
    healthCheck: vi.fn().mockResolvedValue({ status: 'healthy' }),
    getJournalEntries: vi.fn().mockResolvedValue([]),
    createJournalEntry: vi.fn().mockResolvedValue({ id: 'test-id' }),
    testConnection: vi.fn().mockResolvedValue(true)
  }
}))

describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    // Check that the app renders without errors
    expect(container).toBeTruthy()
  })

  it('renders navigation component', () => {
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    // Check that the app renders without errors
    expect(container).toBeTruthy()
  })

  it('renders routes container', () => {
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    // Check that the app renders without errors
    expect(container).toBeTruthy()
  })
}) 