# Builder.io GitHub Integration Guide

This guide will help you connect your Builder.io project to your GitHub repository for visual editing and content management.

## 🚀 Quick Setup Steps

### 1. Get Your Builder.io API Key

1. **Sign in to Builder.io**: Go to [builder.io](https://builder.io) and sign in
2. **Navigate to Account Settings**: Click on your profile → Account Settings
3. **Find API Keys**: Look for "API Keys" or "Developer Settings"
4. **Copy Your API Key**: Copy the public API key for your project

### 2. Update Your Project Configuration

Replace `YOUR_BUILDER_API_KEY` in these files with your actual API key:

```bash
# In builder-registry.ts (line 150)
Builder.init('YOUR_ACTUAL_API_KEY_HERE')

# In builder.config.js (line 3)
apiKey: process.env.BUILDER_API_KEY || 'YOUR_ACTUAL_API_KEY_HERE'
```

### 3. Connect GitHub Repository

#### In Builder.io Dashboard:

1. **Go to Project Settings**: In your Builder.io project dashboard
2. **Find GitHub Integration**: Look for "GitHub" or "Source Control"
3. **Connect Repository**: Click "Connect GitHub" or "Add Repository"
4. **Authorize Access**: Grant Builder.io access to your repository
5. **Select Repository**: Choose `reitheAIPM/pulsecheck-mobile-app-`

#### Repository Settings:

1. **Go to GitHub**: Visit your repository on GitHub
2. **Settings → Integrations**: Navigate to repository settings
3. **Add Builder.io**: Look for Builder.io in available integrations
4. **Configure Permissions**: Allow read/write access

### 4. Configure Build Settings

In Builder.io dashboard, set these build configurations:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "devCommand": "npm run dev",
  "devPort": 8080
}
```

### 5. Set Up Environment Variables

Create a `.env` file in your project root:

```bash
# .env
BUILDER_API_KEY=your_actual_api_key_here
VITE_BUILDER_API_KEY=your_actual_api_key_here
```

## 🔧 Advanced Configuration

### Component Registration

Your components are already registered in `builder-registry.ts`. You can add more components by:

```typescript
Builder.registerComponent(YourComponent, {
  name: 'YourComponent',
  inputs: [
    {
      name: 'propName',
      type: 'string',
      defaultValue: 'Default value'
    }
  ]
})
```

### Content Types

Define content types in Builder.io dashboard:

1. **Go to Content Types**: In your Builder.io project
2. **Create New Type**: Click "New Content Type"
3. **Add Fields**: Define fields like title, content, mood, etc.
4. **Save**: Save your content type

### Custom Fields

You can create custom fields for better content management:

```typescript
// In builder-registry.ts
Builder.registerComponent(MoodSelector, {
  name: 'MoodSelector',
  inputs: [
    {
      name: 'mood',
      type: 'enum',
      enum: ['😊', '😐', '😔', '😤', '😴']
    }
  ]
})
```

## 🎨 Visual Editing Workflow

### 1. Access Visual Editor

1. **Go to Builder.io**: Sign in to your Builder.io dashboard
2. **Open Your Project**: Select your "spark-realm" project
3. **Visual Editor**: Click "Visual Editor" or "Edit"

### 2. Edit Components

1. **Select Component**: Click on any component in the visual editor
2. **Modify Properties**: Use the right panel to change text, colors, etc.
3. **Preview Changes**: See changes in real-time
4. **Save**: Click "Save" to commit changes

### 3. Content Management

1. **Content Tab**: Go to the "Content" tab in Builder.io
2. **Create Content**: Add new journal entries, pages, etc.
3. **Edit Content**: Modify existing content without touching code
4. **Publish**: Publish changes to your live site

## 🔄 Deployment Workflow

### Automatic Deployment

1. **Connect GitHub**: Builder.io will automatically deploy when you push to main
2. **Build Process**: Builder.io runs `npm run build` on your code
3. **Deploy**: Built files are deployed to your hosting platform

### Manual Deployment

1. **Build Locally**: Run `npm run build` in your project
2. **Upload to Builder.io**: Use Builder.io's upload feature
3. **Deploy**: Deploy through Builder.io dashboard

## 🛠️ Troubleshooting

### Common Issues

#### 1. API Key Not Working
- **Check API Key**: Ensure you're using the correct public API key
- **Environment Variables**: Make sure `.env` file is properly configured
- **Restart Dev Server**: Restart your development server after adding API key

#### 2. Components Not Showing
- **Check Registry**: Ensure `builder-registry.ts` is imported in `App.tsx`
- **Component Registration**: Verify components are properly registered
- **Build Errors**: Check for TypeScript or build errors

#### 3. GitHub Connection Issues
- **Permissions**: Ensure Builder.io has proper GitHub permissions
- **Repository Access**: Check that the correct repository is connected
- **Webhooks**: Verify GitHub webhooks are properly configured

#### 4. Build Failures
- **Dependencies**: Run `npm install` to ensure all dependencies are installed
- **Build Command**: Verify `npm run build` works locally
- **Output Directory**: Check that `dist` directory is created

### Debug Commands

```bash
# Check if Builder.io is working
npm run dev

# Test build process
npm run build

# Check for TypeScript errors
npx tsc --noEmit

# Verify API key
echo $BUILDER_API_KEY
```

## 📚 Additional Resources

- [Builder.io Documentation](https://www.builder.io/c/docs)
- [React Integration Guide](https://www.builder.io/c/docs/developers/integrate)
- [GitHub Integration](https://www.builder.io/c/docs/developers/github)
- [Visual Editor Guide](https://www.builder.io/c/docs/developers/visual-editor)

## 🎯 Next Steps

After connecting Builder.io to GitHub:

1. **Test Visual Editing**: Try editing components in the visual editor
2. **Create Content**: Add some sample journal entries
3. **Customize Components**: Modify the component registry for your needs
4. **Set Up Deployment**: Configure automatic deployment
5. **Team Collaboration**: Invite team members to Builder.io

---

**Need Help?** Check the [Builder.io Community](https://community.builder.io/) for support and best practices. 