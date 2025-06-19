# Builder.io Integration Guide - PulseCheck

## Overview

This guide covers the integration of Builder.io with the PulseCheck React Native app for visual page building and component management.

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in the frontend directory:

```bash
# Frontend/.env
REACT_APP_PUBLIC_BUILDER_KEY=your_builder_api_key_here
```

### 2. Start Development Server

```bash
# Navigate to frontend directory
cd frontend

# Start both Expo and Builder Dev Tools
npm run dev
```

This will start:
- Expo development server (typically on port 19006)
- Builder Dev Tools (typically on port 1234)

### 3. Access Builder Dev Tools

Open your browser and navigate to `http://localhost:1234` to access the Builder Dev Tools interface.

## 📦 Installed Packages

- `@builder.io/dev-tools`: Development tools for Builder.io integration
- `@builder.io/react`: React components for Builder.io
- `concurrently`: Run multiple commands simultaneously

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── builder-registry.ts          # Component registration
│   └── components/
│       └── figma-imports.tsx        # Figma imports component
├── package.json                     # Updated with dev script
└── .env                            # Builder API key
```

## 🔧 Configuration Files

### package.json Scripts

```json
{
  "scripts": {
    "dev": "concurrently \"expo start\" \"builder-dev-tools\""
  }
}
```

### Builder Registry (src/builder-registry.ts)

This file registers custom components for use in Builder's Visual Editor:

```typescript
import { Builder } from "@builder.io/react";

// Initialize Builder with your API key
Builder.init(process.env.REACT_APP_PUBLIC_BUILDER_KEY);

// Register custom components
export const CUSTOM_COMPONENTS: React.ComponentType<any>[] = [
  // Add your custom components here
];

CUSTOM_COMPONENTS.forEach(component => {
  Builder.registerComponent(component, {
    name: component.displayName || component.name || 'CustomComponent',
    inputs: [
      // Define component inputs
    ]
  });
});
```

### Figma Imports Component (src/components/figma-imports.tsx)

This component handles Figma design imports and Builder content rendering:

```typescript
import { BuilderComponent, builder, useIsPreviewing } from "@builder.io/react";

export default function BuilderPage() {
  // Component logic for rendering Builder content
}
```

## 🎨 Using Builder.io

### 1. Visual Editor

- Access Builder Dev Tools at `http://localhost:1234`
- Create new pages and sections
- Import designs from Figma
- Use drag-and-drop interface

### 2. Component Registration

To register custom PulseCheck components:

1. Create your component in `src/components/`
2. Import it in `builder-registry.ts`
3. Add it to the `CUSTOM_COMPONENTS` array
4. Define inputs for the component

Example:

```typescript
// src/components/MoodTracker.tsx
import React from 'react';
import { View, Text } from 'react-native';

export const MoodTracker: React.FC<{ title: string }> = ({ title }) => {
  return (
    <View>
      <Text>{title}</Text>
      {/* Mood tracking UI */}
    </View>
  );
};

// src/builder-registry.ts
import { MoodTracker } from './components/MoodTracker';

export const CUSTOM_COMPONENTS: React.ComponentType<any>[] = [
  MoodTracker
];

Builder.registerComponent(MoodTracker, {
  name: 'MoodTracker',
  inputs: [
    {
      name: 'title',
      type: 'string',
      defaultValue: 'How are you feeling?'
    }
  ]
});
```

### 3. Figma Integration

1. Install the Builder.io Figma plugin
2. Select designs in Figma
3. Import to Builder.io
4. Edit and customize in the Visual Editor

## 🔍 Troubleshooting

### Common Issues

1. **API Key Mismatch**
   - Ensure `REACT_APP_PUBLIC_BUILDER_KEY` is set correctly
   - Check that the key matches your Builder Space

2. **Component Not Found**
   - Verify component is registered in `builder-registry.ts`
   - Check component imports and exports

3. **Development Server Issues**
   - Ensure both Expo and Builder Dev Tools are running
   - Check ports 19006 and 1234 are available

4. **React Version Conflicts**
   - Use `--legacy-peer-deps` when installing packages
   - Ensure React version compatibility

### Debug Commands

```bash
# Check if Builder Dev Tools is running
curl http://localhost:1234

# Check Expo server
curl http://localhost:19006

# View Builder Dev Tools logs
# Check terminal output for error messages
```

## 📱 Mobile Considerations

### React Native Specifics

- Builder.io components work with React Native
- Use React Native components (View, Text, etc.) instead of HTML
- Test on actual devices, not just web preview

### Performance Optimization

- Lazy load Builder components when possible
- Optimize images and assets
- Monitor bundle size

## 🚀 Next Steps

1. **Get Builder API Key**: Sign up at builder.io and get your API key
2. **Configure Environment**: Add API key to `.env` file
3. **Start Development**: Run `npm run dev`
4. **Create First Page**: Use Builder Dev Tools to create your first page
5. **Import Figma Designs**: Use the Figma plugin to import designs
6. **Register Components**: Add custom PulseCheck components

## 📚 Resources

- [Builder.io Documentation](https://www.builder.io/c/docs)
- [React Integration Guide](https://www.builder.io/c/docs/devtools-manual-react)
- [Figma Plugin](https://www.builder.io/c/docs/figma-plugin)
- [Component Registration](https://www.builder.io/c/docs/custom-components)

## 🎯 PulseCheck Integration Goals

1. **Visual Page Building**: Enable non-developers to create pages
2. **Design System**: Maintain consistent UI/UX across the app
3. **Rapid Prototyping**: Quickly iterate on designs and features
4. **Component Library**: Build reusable components for the wellness app
5. **Figma Workflow**: Seamlessly import designs from Figma

---

**Note**: This integration follows the CONTRIBUTING.md guidelines for rapid MVP development and production-quality code standards. 