module.exports = {
  // Your Builder.io API key (get this from your Builder.io dashboard)
  apiKey: process.env.BUILDER_API_KEY || '93b18bce96bf4218884de91289488848',
  
  // Build configuration
  buildCommand: 'npm run build',
  outputDirectory: 'dist',
  installCommand: 'npm install',
  
  // Framework configuration
  framework: 'vite',
  
  // Development server configuration
  devCommand: 'npm run dev',
  devPort: 8080,
  
  // Component registration
  components: {
    // Path to your component registry
    registry: './builder-registry.ts'
  },
  
  // Content types
  contentTypes: [
    {
      name: 'page',
      fields: [
        {
          name: 'title',
          type: 'string'
        },
        {
          name: 'content',
          type: 'blocks'
        }
      ]
    },
    {
      name: 'journal-entry',
      fields: [
        {
          name: 'title',
          type: 'string'
        },
        {
          name: 'content',
          type: 'text'
        },
        {
          name: 'mood',
          type: 'enum',
          enum: ['😊', '😐', '😔', '😤', '😴']
        },
        {
          name: 'energy',
          type: 'number',
          min: 1,
          max: 10
        },
        {
          name: 'stress',
          type: 'number',
          min: 1,
          max: 10
        }
      ]
    }
  ],
  
  // Custom fields
  customFields: [
    {
      name: 'mood-selector',
      type: 'component',
      component: 'MoodSelector'
    },
    {
      name: 'energy-slider',
      type: 'component',
      component: 'EnergySlider'
    }
  ]
} 