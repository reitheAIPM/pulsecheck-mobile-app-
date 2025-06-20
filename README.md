# PulseCheck - Wellness App for Tech Workers

A modern wellness application designed specifically for tech workers, featuring AI-powered insights and social media-style journaling.

## 🚀 Current Status: MVP Complete with Modern UI

**Frontend**: Modern React 18 + TypeScript + Vite application built with Builder.io  
**Backend**: FastAPI with Supabase database, deployed on Railway  
**AI Integration**: OpenAI-powered wellness insights and analysis  

## ✨ Features

### Core Functionality
- **Social Media-Style Journaling**: Twitter/Instagram-inspired wellness feed
- **AI-Powered Insights**: Personalized wellness analysis and recommendations
- **Mood Tracking**: Visual mood, energy, and stress level tracking
- **Analytics Dashboard**: Comprehensive wellness statistics and trends
- **Modern UI**: Beautiful, responsive design with TailwindCSS

### Technical Features
- **Real-time API Integration**: Full backend connectivity with error handling
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Type Safety**: Full TypeScript implementation
- **Modern Stack**: React 18, Vite, TailwindCSS, Radix UI

## 🛠️ Tech Stack

### Frontend (Builder.io Application)
- **React 18** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **Radix UI** for accessible components
- **React Router** for navigation
- **Builder.io** for visual editing

### Backend
- **FastAPI** (Python)
- **Supabase** (PostgreSQL database)
- **Railway** (deployment)
- **OpenAI API** (AI insights)

## 🚀 Quick Start

### Frontend Development
```bash
cd "spark-realm (1)"
npm install
npm run dev
```
Visit http://localhost:8080/

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 📁 Project Structure

```
PulseCheck/
├── spark-realm (1)/          # Main frontend (Builder.io app)
│   ├── src/
│   │   ├── pages/            # Application screens
│   │   ├── components/       # Reusable UI components
│   │   └── lib/              # Utilities and helpers
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── models/           # Data models
│   │   └── services/         # Business logic
│   └── main.py
├── archived-react-native-setup/  # Previous React Native implementation
└── README.md
```

## 🎨 Design System

The application uses a modern design system with:
- **Color Palette**: Primary blue (#4A90E2), success green (#4CAF50), warning amber (#FFC107)
- **Typography**: Clean, readable fonts with proper hierarchy
- **Components**: Consistent card-based layout with subtle shadows
- **Icons**: Lucide React icons throughout the interface

## 🔧 Development

### Adding New Features
1. **Frontend**: Use Builder.io for visual editing or modify components in `src/components/`
2. **Backend**: Add new endpoints in `backend/app/routers/`
3. **Database**: Update models in `backend/app/models/`

### API Integration
The frontend connects to the backend API at `https://pulsecheck-mobile-app-production.up.railway.app`

### Builder.io Integration
- Visual component editing
- Content management
- A/B testing capabilities
- Real-time preview

## 📊 Current Features

### ✅ Implemented
- [x] Modern React frontend with Builder.io
- [x] Social media-style journal feed
- [x] AI-powered wellness insights
- [x] Mood and energy tracking
- [x] Analytics dashboard
- [x] Responsive design
- [x] Full backend API integration
- [x] Error handling and fallbacks
- [x] TypeScript type safety

### 🚧 In Progress
- [ ] User authentication
- [ ] Advanced analytics
- [ ] Mobile app deployment
- [ ] Push notifications

## 🚀 Deployment

### Frontend
- Development: `npm run dev`
- Build: `npm run build`
- Deploy: Connect to Builder.io for visual deployment

### Backend
- Production: Deployed on Railway
- Environment: Supabase database
- API: https://pulsecheck-mobile-app-production.up.railway.app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Builder.io for the amazing visual development platform
- Radix UI for accessible component primitives
- TailwindCSS for the utility-first CSS framework
- OpenAI for AI-powered insights

---

**Last Updated**: June 20, 2025  
**Version**: 2.0.0 (Builder.io Frontend) 