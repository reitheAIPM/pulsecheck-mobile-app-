# PulseCheck Project Context for AI Assistant

## Quick Overview
- **Product**: AI-powered wellness journaling app with 4 AI personas acting as "caring friends"
- **Status**: Failed beta launch with 3-6 users, critical bug blocking core functionality
- **Main Issue**: End-to-end AI interaction flow broken - users submit journal entries but don't receive AI responses

## Technical Stack
- **Frontend**: React + Vite deployed on Vercel (spark-realm directory)
- **Backend**: FastAPI deployed on Railway (backend directory)  
- **Database**: Supabase (PostgreSQL with RLS)
- **AI**: OpenAI API (GPT-4 for analysis, GPT-3.5-turbo for responses)
- **Mobile**: React Native (Expo) in development

## Core Features
1. **Journal Entries**: Users write daily reflections
2. **AI Personas**: 4 distinct personalities provide responses
   - **Pulse**: Warm empath with emotional intelligence
   - **Sage**: Wise mentor offering philosophical insights
   - **Spark**: Energetic motivator encouraging action
   - **Anchor**: Grounding presence for stability
3. **Social Features**: Like/save AI responses, view interaction history

## Architecture Flow
```
User Journal Entry → Frontend (React) → Backend API (FastAPI)
                                              ↓
                                    AdaptiveAIService
                                              ↓
                                    Pattern Analysis & Persona Selection
                                              ↓
                                    PulseAI Service → OpenAI API
                                              ↓
                                    Response Generation & Safety Checks
                                              ↓
                                    Store in Database ← Supabase
                                              ↓
                                    Return to Frontend
```

## Current Implementation Details

### Backend Services
- **AdaptiveAIService**: Analyzes journal patterns, selects appropriate persona
- **PulseAI**: Handles OpenAI API calls with retry logic and fallbacks
- **AIDebugContext**: Comprehensive error tracking and debugging
- **Fallback Layers**: 
  1. Intelligent fallback (GPT-based)
  2. Smart fallback (template-based)
  3. Emergency fallback (basic response)

### Error Handling
- Performance baseline tracking
- Error pattern counters (topic_classification, persona_selection, etc.)
- Debug context storage for analysis
- Multiple retry mechanisms with exponential backoff

### Database Schema
- Users, journal_entries, ai_responses tables
- Comprehensive RLS policies
- Admin analytics functions for monitoring

## Known Issues & Bugs

### Primary Bug: End-to-End AI Flow
**Symptoms**: 
- Journal entries submitted successfully
- Backend processes request
- AI response generated but not displayed to user

**Potential Causes**:
1. Frontend state management not updating
2. Response parsing mismatch between services
3. Timeout issues with long AI processing
4. Beta service rate limiting
5. Content safety filters blocking responses
6. WebSocket/real-time connection issues

### Other Issues
- Complex over-engineered architecture for current user base
- Multiple layers of abstraction causing debugging difficulty
- Deployment configuration mismatches between environments

## Research Insights
Analyzed similar projects:
- **Journal-Tree**: Faced similar deployment and API integration issues
- **JBUD**: Solved context management with vector databases
- **Momentum**: Simpler architecture with Supabase functions
- **Key Learning**: Multi-LLM debugging workflows help identify issues faster

## Immediate Priorities
1. **Fix Core Bug**: Get basic journal → AI response flow working
2. **Simplify Architecture**: Remove unnecessary complexity
3. **Add Debugging**: Better logging and error visibility

## Enhancement Goals (Post-Fix)
1. **Long-term Memory**: Personas remember past conversations
2. **Growth Reframing**: Transform struggles into opportunities
3. **Task Breakdown**: Help users with overwhelming situations
4. **Continuity**: Follow up on previous journal topics

## File Structure
- `/backend/`: FastAPI application with all services
- `/spark-realm/`: React frontend application
- `/PulseCheckMobile/`: React Native mobile app (in development)
- `/ai/`: Documentation and context files
- `/tests/`: Testing scripts and debugging tools
- `/supabase/`: Database migrations and configurations

## Testing & Debugging
- PowerShell test scripts in `/tests/` directory
- AI debugging system tracks all interactions
- Comprehensive error logging throughout stack

## Key Questions for Debugging
1. Are API responses reaching the frontend?
2. Is the frontend correctly parsing AI responses?
3. Are there CORS or authentication issues?
4. Is the WebSocket connection for real-time updates working?
5. Are rate limits being hit on OpenAI or Railway?

## Success Metrics
- Users receive AI responses within 10 seconds
- 95%+ success rate for AI interactions
- Meaningful, personalized responses from personas
- Users return daily to journal

## Context for AI Assistant
When helping debug or enhance this project:
- Focus on fixing the core bug first before adding features
- The system is over-engineered - simplification is welcome
- User experience is paramount - the app should "just work"
- AI responses should feel like caring friends, not therapists
- Keep solutions practical for a small beta user base 