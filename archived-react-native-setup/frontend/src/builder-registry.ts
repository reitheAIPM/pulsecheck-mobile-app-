// Builder.io Component Registry
// This file registers custom components for use in Builder's Visual Editor

import { Builder } from "@builder.io/react";

// Import your custom components
// import { YourCustomComponent } from './components/YourCustomComponent';

// Initialize Builder with your API key
// Note: For React Native, Builder.init() is not needed in the registry
// The API key will be used in individual components

// Export your custom components for use in the Visual Editor
export const CUSTOM_COMPONENTS: React.ComponentType<any>[] = [
  // YourCustomComponent
];

// Register components with Builder
CUSTOM_COMPONENTS.forEach(component => {
  Builder.registerComponent(component, {
    name: component.displayName || component.name || 'CustomComponent',
    inputs: [
      // Define your component inputs here
      // {
      //   name: 'title',
      //   type: 'string',
      //   defaultValue: 'Default Title'
      // }
    ]
  });
}); 