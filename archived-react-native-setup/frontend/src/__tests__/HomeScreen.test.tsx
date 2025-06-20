import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import HomeScreen from '../screens/HomeScreen';

// Mock the API service
jest.mock('../services/api', () => ({
  __esModule: true,
  default: {
    getJournalStats: jest.fn().mockResolvedValue({
      current_streak: 5,
      average_mood: 7.5,
      average_energy: 6.8,
      average_stress: 4.2
    }),
    getJournalEntries: jest.fn().mockResolvedValue({
      entries: [{
        id: 1,
        content: 'Test entry',
        mood_level: 8,
        energy_level: 7,
        stress_level: 3,
        created_at: '2024-01-01T00:00:00Z'
      }]
    })
  }
}));

describe('HomeScreen', () => {
  const mockNavigation = {
    navigate: jest.fn(),
  };

  const renderWithNavigation = (component: React.ReactElement) => {
    return render(
      <NavigationContainer>
        {component}
      </NavigationContainer>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders greeting message', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    // Wait for the component to load and check for greeting
    const greetingElement = await screen.findByText(/Hey there!/i);
    expect(greetingElement).toBeTruthy();
  });

  it('renders subtitle', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    const subtitleElement = await screen.findByText(/How are you feeling today?/i);
    expect(subtitleElement).toBeTruthy();
  });

  it('renders new check-in button', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    const checkInButton = await screen.findByText(/New Check-in/i);
    expect(checkInButton).toBeTruthy();
  });

  it('renders view all button', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    const viewAllButton = await screen.findByText(/View All/i);
    expect(viewAllButton).toBeTruthy();
  });

  it('renders insights button', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    // Use getAllByText and check that at least one Insights button exists
    const insightsButtons = await screen.findAllByText(/Insights/i);
    expect(insightsButtons.length).toBeGreaterThan(0);
  });

  it('displays streak information', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    // Look for the specific streak number in the stats section
    const streakElements = await screen.findAllByText(/5/i);
    expect(streakElements.length).toBeGreaterThan(0);
  });

  it('displays mood emoji', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    // Look for mood emoji in the stats section
    const moodElements = await screen.findAllByText(/😊/i);
    expect(moodElements.length).toBeGreaterThan(0);
  });

  it('displays latest check-in section', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    const latestCheckInTitle = await screen.findByText(/Latest Check-in/i);
    expect(latestCheckInTitle).toBeTruthy();
  });

  it('displays pulse teaser message', async () => {
    renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
    
    const pulseTeaser = await screen.findByText(/Pulse is here to support your wellness journey/i);
    expect(pulseTeaser).toBeTruthy();
  });
}); 