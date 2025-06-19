# Frontend Testing Guide - PulseCheck

## Overview

This guide covers the testing setup and best practices for the PulseCheck React Native frontend, including Jest configuration, React Native Testing Library, and component testing strategies.

## 🚀 Quick Start

### 1. Run Tests

```bash
# Navigate to frontend directory
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### 2. Test Structure

```
frontend/
├── src/
│   ├── __tests__/                    # Test files
│   │   ├── HomeScreen.test.tsx       # Component tests
│   │   ├── services/                 # Service tests
│   │   └── utils/                    # Utility tests
│   ├── screens/                      # Screen components
│   ├── components/                   # Reusable components
│   ├── services/                     # API services
│   └── utils/                        # Utility functions
├── jest.config.js                    # Jest configuration
└── package.json                      # Test scripts
```

## 📦 Installed Testing Packages

- `@testing-library/react-native`: React Native testing utilities
- `@testing-library/jest-native`: Additional Jest matchers for React Native
- `jest`: JavaScript testing framework
- `jest-expo`: Expo-specific Jest preset
- `@types/jest`: TypeScript definitions for Jest

## 🔧 Configuration

### Jest Configuration (jest.config.js)

```javascript
module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEnv: ['@testing-library/jest-native/extend-expect'],
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)'
  ],
  testMatch: [
    '**/__tests__/**/*.(ts|tsx|js)',
    '**/*.(test|spec).(ts|tsx|js)'
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
    '!src/**/*.stories.{ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  }
};
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

## 🧪 Testing Patterns

### 1. Component Testing

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import YourComponent from '../YourComponent';

describe('YourComponent', () => {
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

  it('renders correctly', () => {
    renderWithNavigation(<YourComponent navigation={mockNavigation} />);
    expect(screen.getByText('Expected Text')).toBeTruthy();
  });

  it('handles user interactions', () => {
    renderWithNavigation(<YourComponent navigation={mockNavigation} />);
    
    const button = screen.getByText('Button Text');
    fireEvent.press(button);
    
    expect(mockNavigation.navigate).toHaveBeenCalledWith('TargetScreen');
  });
});
```

### 2. API Service Testing

```typescript
import apiService from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  __esModule: true,
  default: {
    getJournalStats: jest.fn(),
    getJournalEntries: jest.fn(),
    createJournalEntry: jest.fn(),
  }
}));

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches journal stats successfully', async () => {
    const mockStats = {
      current_streak: 5,
      average_mood: 7.5,
      average_energy: 6.8,
      average_stress: 4.2
    };

    apiService.getJournalStats.mockResolvedValue(mockStats);
    
    const result = await apiService.getJournalStats();
    expect(result).toEqual(mockStats);
  });
});
```

### 3. Utility Function Testing

```typescript
import { formatDate, calculateStreak } from '../utils/helpers';

describe('Utility Functions', () => {
  describe('formatDate', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-01-01T00:00:00Z');
      const formatted = formatDate(date);
      expect(formatted).toBe('January 1, 2024');
    });
  });

  describe('calculateStreak', () => {
    it('calculates streak correctly', () => {
      const entries = [
        { created_at: '2024-01-01T00:00:00Z' },
        { created_at: '2024-01-02T00:00:00Z' },
        { created_at: '2024-01-03T00:00:00Z' },
      ];
      
      const streak = calculateStreak(entries);
      expect(streak).toBe(3);
    });
  });
});
```

## 🎯 Testing Best Practices

### 1. Test Organization

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user flows (future implementation)

### 2. Naming Conventions

```typescript
// File naming
ComponentName.test.tsx
ComponentName.spec.tsx

// Test naming
describe('ComponentName', () => {
  it('should render correctly', () => {});
  it('should handle user interaction', () => {});
  it('should display error state', () => {});
});
```

### 3. Mocking Strategies

```typescript
// Mock external dependencies
jest.mock('@expo/vector-icons', () => ({
  Ionicons: 'Ionicons',
}));

// Mock API calls
jest.mock('../services/api', () => ({
  __esModule: true,
  default: {
    getJournalStats: jest.fn(),
  }
}));

// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  setOptions: jest.fn(),
};
```

### 4. Async Testing

```typescript
it('loads data asynchronously', async () => {
  render(<YourComponent />);
  
  // Wait for async operations
  const element = await screen.findByText('Loaded Data');
  expect(element).toBeTruthy();
});
```

## 📊 Coverage Goals

### Minimum Coverage Thresholds

- **Lines**: 70%
- **Functions**: 70%
- **Branches**: 70%
- **Statements**: 70%

### Coverage Exclusions

- Type definition files (*.d.ts)
- Index files (index.ts)
- Story files (*.stories.tsx)
- Test files (*.test.tsx, *.spec.tsx)

## 🔍 Common Testing Scenarios

### 1. Navigation Testing

```typescript
it('navigates to journal entry screen', () => {
  renderWithNavigation(<HomeScreen navigation={mockNavigation} />);
  
  const button = screen.getByText('New Check-in');
  fireEvent.press(button);
  
  expect(mockNavigation.navigate).toHaveBeenCalledWith('JournalEntry');
});
```

### 2. Form Testing

```typescript
it('submits form with correct data', () => {
  render(<JournalEntryScreen />);
  
  const input = screen.getByPlaceholderText('How are you feeling?');
  const submitButton = screen.getByText('Submit');
  
  fireEvent.changeText(input, 'I feel great today!');
  fireEvent.press(submitButton);
  
  expect(mockApiService.createJournalEntry).toHaveBeenCalledWith({
    content: 'I feel great today!',
    // other form data
  });
});
```

### 3. Error Handling Testing

```typescript
it('displays error message on API failure', async () => {
  apiService.getJournalStats.mockRejectedValue(new Error('API Error'));
  
  render(<HomeScreen />);
  
  const errorMessage = await screen.findByText('Failed to load dashboard data');
  expect(errorMessage).toBeTruthy();
});
```

## 🚀 Continuous Integration

### GitHub Actions Example

```yaml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      - run: npm run test:coverage
```

## 🔧 Troubleshooting

### Common Issues

1. **Transform Errors**
   - Check `transformIgnorePatterns` in jest.config.js
   - Ensure all React Native packages are properly configured

2. **Navigation Mocking**
   - Use `NavigationContainer` wrapper for navigation tests
   - Mock navigation props correctly

3. **Async Testing**
   - Use `findBy` instead of `getBy` for async operations
   - Add proper `await` statements

4. **Coverage Issues**
   - Check coverage exclusions
   - Ensure test files are not included in coverage

### Debug Commands

```bash
# Run tests with verbose output
npm test -- --verbose

# Run specific test file
npm test -- HomeScreen.test.tsx

# Run tests with coverage report
npm run test:coverage

# Debug Jest configuration
npm test -- --showConfig
```

## 📚 Resources

- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Expo Testing Guide](https://docs.expo.dev/guides/testing/)
- [React Navigation Testing](https://reactnavigation.org/docs/testing/)

## 🎯 PulseCheck Testing Goals

1. **Component Reliability**: Ensure all UI components render correctly
2. **User Flow Validation**: Test complete user journeys
3. **API Integration**: Verify data fetching and error handling
4. **Performance Testing**: Monitor component rendering performance
5. **Accessibility Testing**: Ensure app is accessible to all users

---

**Note**: This testing setup follows the CONTRIBUTING.md guidelines for production-quality code and comprehensive testing coverage. 