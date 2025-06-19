# PulseCheck - Consolidated Frontend Development Guide

*Comprehensive React Native development guide with Builder.io integration and testing strategies*

---

## 🏗️ **Frontend Architecture Overview**

### **Tech Stack**
- **Framework**: React Native (Expo) with TypeScript
- **Navigation**: React Navigation v6 (Stack + Tab navigators)
- **UI Components**: Builder.io for visual editing and component management
- **State Management**: React Context + AsyncStorage for persistence
- **Styling**: StyleSheet API with design tokens
- **Testing**: Jest + React Native Testing Library

### **Project Structure**
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Shared components (Button, Input, etc.)
│   │   ├── screens/        # Screen-specific components
│   │   └── builder/        # Builder.io registered components
│   ├── screens/            # Screen components
│   │   ├── auth/           # Authentication screens
│   │   ├── checkin/        # Mood tracking screens
│   │   ├── insights/       # AI insights screens
│   │   └── profile/        # User profile screens
│   ├── navigation/         # Navigation configuration
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── TabNavigator.tsx
│   ├── services/           # API and external services
│   │   ├── api.ts          # API client
│   │   ├── auth.ts         # Authentication service
│   │   └── builder.ts      # Builder.io integration
│   ├── hooks/              # Custom React hooks
│   ├── context/            # React Context providers
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Helper functions
│   └── constants/          # App constants and config
├── assets/                 # Images, fonts, etc.
├── builder-registry.ts     # Builder.io component registry
└── app.json               # Expo configuration
```

---

## 🧭 **Navigation Architecture**

### **Navigation Structure**
```
AppNavigator (Root)
├── AuthNavigator (Stack)
│   ├── LoginScreen
│   ├── RegisterScreen
│   └── ForgotPasswordScreen
└── MainNavigator (Tab)
    ├── HomeTab
    │   ├── HomeScreen
    │   └── CheckinScreen
    ├── InsightsTab
    │   ├── InsightsScreen
    │   └── ChatScreen
    ├── ProfileTab
    │   ├── ProfileScreen
    │   └── SettingsScreen
    └── BuilderTab (Dev only)
        └── FigmaImportsScreen
```

### **Navigation Best Practices**
- **Single NavigationContainer**: Only one at the root level
- **Type Safety**: Use TypeScript for navigation types
- **Deep Linking**: Configure for app-to-app navigation
- **Screen Transitions**: Consistent animations and timing
- **Error Boundaries**: Handle navigation errors gracefully

### **Implementation Example**
```typescript
// navigation/AppNavigator.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useAuth } from '../context/AuthContext';

const Stack = createStackNavigator();

export function AppNavigator() {
  const { isAuthenticated } = useAuth();

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

---

## 🎨 **Builder.io Integration**

### **Setup and Configuration**

#### 1. Install Dependencies
```bash
npm install --save-dev @builder.io/react @builder.io/dev-tools concurrently
```

#### 2. Environment Configuration
```typescript
// src/constants/config.ts
export const BUILDER_CONFIG = {
  apiKey: process.env.EXPO_PUBLIC_BUILDER_API_KEY || '',
  model: 'figma-imports',
  previewUrl: 'http://localhost:19006', // Expo dev server
};
```

#### 3. Component Registry
```typescript
// builder-registry.ts
import { Builder } from '@builder.io/react';
import { CheckinForm } from './src/components/checkin/CheckinForm';
import { MoodCard } from './src/components/common/MoodCard';
import { InsightCard } from './src/components/insights/InsightCard';

// Register custom components
Builder.registerComponent(CheckinForm, {
  name: 'CheckinForm',
  inputs: [
    { name: 'title', type: 'string', defaultValue: 'How are you feeling?' },
    { name: 'showJournal', type: 'boolean', defaultValue: true }
  ]
});

Builder.registerComponent(MoodCard, {
  name: 'MoodCard',
  inputs: [
    { name: 'moodScore', type: 'number', defaultValue: 7 },
    { name: 'date', type: 'date' }
  ]
});

Builder.registerComponent(InsightCard, {
  name: 'InsightCard',
  inputs: [
    { name: 'title', type: 'string' },
    { name: 'content', type: 'richText' },
    { name: 'actionText', type: 'string' }
  ]
});

// Initialize Builder
Builder.init(BUILDER_CONFIG.apiKey);
```

#### 4. Figma Imports Component
```typescript
// src/components/builder/FigmaImportsScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text } from 'react-native';
import { BuilderComponent, builder, useIsPreviewing } from '@builder.io/react';
import { BUILDER_CONFIG } from '../../constants/config';

export function FigmaImportsScreen() {
  const [content, setContent] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const isPreviewing = useIsPreviewing();

  useEffect(() => {
    async function fetchContent() {
      try {
        const builderContent = await builder
          .get(BUILDER_CONFIG.model, {
            url: window.location.pathname,
            userAttributes: {
              platform: 'mobile',
              app: 'pulsecheck'
            }
          })
          .promise();

        setContent(builderContent);
        setNotFound(!builderContent);
      } catch (error) {
        console.error('Builder content fetch error:', error);
        setNotFound(true);
      }
    }

    fetchContent();
  }, []);

  if (notFound && !isPreviewing) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <Text>Content not found</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <BuilderComponent
        model={BUILDER_CONFIG.model}
        content={content}
        apiKey={BUILDER_CONFIG.apiKey}
      />
    </View>
  );
}
```

### **Development Workflow**

#### 1. Development Script
```json
// package.json
{
  "scripts": {
    "dev": "concurrently \"expo start\" \"builder-dev-tools\"",
    "dev:builder": "builder-dev-tools",
    "build": "expo build",
    "test": "jest"
  }
}
```

#### 2. Component Development Process
1. **Design in Figma**: Create components and layouts
2. **Import to Builder**: Use Builder Figma plugin
3. **Map Components**: Connect Figma components to React Native code
4. **Preview & Iterate**: Use Builder Visual Editor
5. **Generate Code**: Export optimized React Native code
6. **Integrate**: Add to component registry and screens

---

## 🧩 **Component Architecture**

### **Component Categories**

#### 1. Common Components
```typescript
// src/components/common/Button.tsx
import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { COLORS, TYPOGRAPHY } from '../../constants/design';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
}

export function Button({ 
  title, 
  onPress, 
  variant = 'primary', 
  size = 'medium',
  disabled = false 
}: ButtonProps) {
  return (
    <TouchableOpacity
      style={[styles.button, styles[variant], styles[size], disabled && styles.disabled]}
      onPress={onPress}
      disabled={disabled}
    >
      <Text style={[styles.text, styles[`${variant}Text`]]}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}
```

#### 2. Screen Components
```typescript
// src/screens/checkin/CheckinScreen.tsx
import React, { useState } from 'react';
import { View, ScrollView, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { CheckinForm } from '../../components/checkin/CheckinForm';
import { useCheckin } from '../../hooks/useCheckin';
import { styles } from './CheckinScreen.styles';

export function CheckinScreen() {
  const navigation = useNavigation();
  const { submitCheckin, loading } = useCheckin();
  const [formData, setFormData] = useState({
    moodScore: 5,
    energyLevel: 5,
    stressLevel: 5,
    journalEntry: ''
  });

  const handleSubmit = async () => {
    try {
      await submitCheckin(formData);
      navigation.navigate('Insights');
    } catch (error) {
      Alert.alert('Error', 'Failed to submit check-in');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <CheckinForm
        data={formData}
        onChange={setFormData}
        onSubmit={handleSubmit}
        loading={loading}
      />
    </ScrollView>
  );
}
```

#### 3. Builder Components
```typescript
// src/components/builder/MoodTracker.tsx
import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Builder } from '@builder.io/react';

interface MoodTrackerProps {
  currentMood?: number;
  onMoodChange?: (mood: number) => void;
  title?: string;
}

export function MoodTracker({ 
  currentMood = 5, 
  onMoodChange, 
  title = 'How are you feeling?' 
}: MoodTrackerProps) {
  const moods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 20 }}>
        {title}
      </Text>
      <View style={{ flexDirection: 'row', justifyContent: 'space-around' }}>
        {moods.map((mood) => (
          <TouchableOpacity
            key={mood}
            style={{
              width: 40,
              height: 40,
              borderRadius: 20,
              backgroundColor: currentMood === mood ? '#007AFF' : '#E5E5EA',
              justifyContent: 'center',
              alignItems: 'center'
            }}
            onPress={() => onMoodChange?.(mood)}
          >
            <Text style={{ color: currentMood === mood ? 'white' : 'black' }}>
              {mood}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

// Register with Builder
Builder.registerComponent(MoodTracker, {
  name: 'MoodTracker',
  inputs: [
    { name: 'title', type: 'string', defaultValue: 'How are you feeling?' },
    { name: 'currentMood', type: 'number', defaultValue: 5 }
  ]
});
```

---

## 🎯 **Design System & Tokens**

### **Design Tokens**
```typescript
// src/constants/design.ts
export const COLORS = {
  primary: '#007AFF',
  secondary: '#5856D6',
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  background: '#FFFFFF',
  surface: '#F2F2F7',
  text: {
    primary: '#000000',
    secondary: '#8E8E93',
    disabled: '#C7C7CC'
  }
};

export const TYPOGRAPHY = {
  h1: { fontSize: 32, fontWeight: 'bold' },
  h2: { fontSize: 24, fontWeight: 'bold' },
  h3: { fontSize: 20, fontWeight: '600' },
  body: { fontSize: 16, fontWeight: 'normal' },
  caption: { fontSize: 14, fontWeight: 'normal' }
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48
};

export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: 50
};
```

### **Style Guidelines**
- **Consistent Spacing**: Use design tokens for all spacing
- **Color Usage**: Follow semantic color naming
- **Typography**: Use predefined text styles
- **Responsive Design**: Support different screen sizes
- **Accessibility**: Include proper contrast ratios and touch targets

---

## 🧪 **Testing Strategy**

### **Testing Framework Setup**

#### 1. Install Dependencies
```bash
npm install --save-dev @testing-library/react-native @testing-library/jest-native jest jest-expo @types/jest
```

#### 2. Jest Configuration (jest.config.js)
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

#### 3. Package.json Scripts
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### **Testing Patterns**

#### 1. Component Testing
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

#### 2. API Service Testing
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

#### 3. Utility Function Testing
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

### **Testing Best Practices**

#### 1. Test Organization
- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user flows (future implementation)

#### 2. Naming Conventions
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

#### 3. Mocking Strategies
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

#### 4. Async Testing
```typescript
it('loads data asynchronously', async () => {
  render(<YourComponent />);
  
  // Wait for async operations
  const element = await screen.findByText('Loaded Data');
  expect(element).toBeTruthy();
});
```

### **Coverage Goals**

#### Minimum Coverage Thresholds
- **Lines**: 70%
- **Functions**: 70%
- **Branches**: 70%
- **Statements**: 70%

#### Coverage Exclusions
- Type definition files (*.d.ts)
- Index files (index.ts)
- Story files (*.stories.tsx)
- Test files (*.test.tsx, *.spec.tsx)

---

## 🔧 **Development Workflow**

### **1. Component Development**
```bash
# Start development environment
npm run dev

# This runs both Expo and Builder Dev Tools concurrently
```

### **2. Testing Strategy**
```typescript
// src/components/common/__tests__/Button.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { Button } from '../Button';

describe('Button', () => {
  it('renders correctly', () => {
    const { getByText } = render(
      <Button title="Test Button" onPress={() => {}} />
    );
    expect(getByText('Test Button')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <Button title="Test Button" onPress={onPress} />
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(onPress).toHaveBeenCalled();
  });
});
```

### **3. Code Quality**
- **TypeScript**: Strict mode enabled
- **ESLint**: Configured for React Native
- **Prettier**: Consistent code formatting
- **Husky**: Pre-commit hooks for quality checks

### **4. Performance Optimization**
- **Memoization**: Use React.memo for expensive components
- **Lazy Loading**: Implement for heavy screens
- **Image Optimization**: Use appropriate formats and sizes
- **Bundle Analysis**: Monitor bundle size regularly

---

## 🚀 **Deployment & CI/CD**

### **Build Process**
```bash
# Development build
expo build --platform ios --profile development

# Production build
expo build --platform all --profile production
```

### **Environment Management**
```typescript
// src/config/environment.ts
export const ENV = {
  development: {
    apiUrl: 'http://localhost:8000/api/v1',
    builderApiKey: 'dev-key',
    enableLogging: true
  },
  staging: {
    apiUrl: 'https://staging-api.pulsecheck.app/v1',
    builderApiKey: 'staging-key',
    enableLogging: true
  },
  production: {
    apiUrl: 'https://api.pulsecheck.app/v1',
    builderApiKey: 'prod-key',
    enableLogging: false
  }
};
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### 1. Builder.io Connection Errors
```bash
# Check API key
echo $EXPO_PUBLIC_BUILDER_API_KEY

# Verify Builder configuration
npm run type-check
```

#### 2. Navigation Errors
```typescript
// Ensure single NavigationContainer
// Check navigation types
// Verify screen names match
```

#### 3. Expo Issues
```bash
# Clear cache
expo start --clear

# Reset Metro bundler
npx expo start --clear

# Check Expo CLI version
expo --version
```

#### 4. Testing Issues
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

---

## 📚 **Best Practices Summary**

### **Navigation**
- ✅ Single NavigationContainer at root
- ✅ Type-safe navigation with TypeScript
- ✅ Consistent screen transitions
- ✅ Proper error handling

### **Builder.io Integration**
- ✅ Component registry for reusability
- ✅ Figma-to-code workflow
- ✅ Visual editing capabilities
- ✅ Development tools integration

### **Component Architecture**
- ✅ Separation of concerns
- ✅ Reusable component library
- ✅ Consistent design tokens
- ✅ Accessibility compliance

### **Development Workflow**
- ✅ Concurrent development tools
- ✅ Comprehensive testing strategy
- ✅ Code quality enforcement
- ✅ Performance optimization

---

*This guide should be updated as the project evolves and new patterns emerge.* 