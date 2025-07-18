import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { authService } from './authService';
import { secureLogger } from '../utils/secureLogger';

// Types for API responses
export interface HealthCheck {
  status: string;
  service: string;
  version: string;
  environment: string;
  config_loaded: boolean;
  warnings?: string[];
}

export interface JournalEntry {
  id: string;
  content: string;
  mood_level: number;
  energy_level: number;
  stress_level: number;
  sleep_hours?: number;
  work_hours?: number;
  tags?: string[];
  work_challenges?: string[];
  gratitude_items?: string[];
  created_at: string;
  updated_at?: string;
  ai_insights?: any;
  ai_generated_at?: string;
}

export interface CreateJournalEntry {
  content: string;
  mood_level: number;
  energy_level: number;
  stress_level: number;
  sleep_hours?: number;
  work_hours?: number;
  tags?: string[];
  work_challenges?: string[];
  gratitude_items?: string[];
}

export interface PulseResponse {
  message: string;
  insight?: AIInsightResponse;
  suggested_actions: string[];
  follow_up_question?: string;
  response_time_ms?: number;
  confidence_score: number;
}

export interface JournalStats {
  total_entries: number;
  current_streak: number;
  longest_streak: number;
  average_mood: number;
  average_energy: number;
  average_stress: number;
  last_entry_date?: string;
  mood_trend: string;
  energy_trend: string;
  stress_trend: string;
}

// Adaptive AI interfaces
export interface UserPatterns {
  writing_style: string;
  common_topics: string[];
  mood_trends: Record<string, number>;
  interaction_preferences: Record<string, boolean>;
  response_preferences: Record<string, string>;
  pattern_confidence: number;
  entries_analyzed: number;
}

export interface PersonaInfo {
  id?: string; // For compatibility - maps to persona_id
  persona_id: string;
  name?: string; // For compatibility - maps to persona_name
  persona_name: string;
  description: string;
  recommended: boolean;
  traits?: string[]; // Optional field
  requires_premium: boolean;
  times_used: number;
  recommendation_score: number;
  recommendation_reasons: string[];
  available: boolean;
  last_used?: string;
  recommendation_reason?: string;
}

export interface AIResponse {
  message: string;
  confidence_score: number;
  response_time_ms: number;
  follow_up_question?: string;
  suggested_actions?: string[];
  insight?: string;
}

export interface AdaptiveContext {
  user_id: string;
  current_mood?: number;
  current_energy?: number;
  current_stress?: number;
  time_of_day?: number;
  day_of_week?: number;
  entry_length?: number;
  current_topics: string[];
  emotional_state?: string;
  suggested_tone?: string;
  suggested_length?: string;
  focus_areas: string[];
  avoid_areas: string[];
  interaction_style?: string;
}

export interface AIInsightResponse {
  insight: string;
  suggested_action: string;
  follow_up_question?: string;
  confidence_score: number;
  pattern_insights?: {
    writing_style: string;
    common_topics: string[];
    mood_trends: any;
    interaction_preferences: any;
    response_preferences: any;
  };
  persona_used?: string;
  adaptation_level?: string;
  topic_flags?: string[];
  response_length?: string;
  tone_used?: string;
  focus_areas?: string[];
  avoid_areas?: string[];
  generated_at: string;
  metadata?: {
    structured_response?: boolean;
    multi_persona_response?: boolean;
    emotional_tone?: string;
    response_type?: string;
    persona_strengths?: string[];
    estimated_helpfulness?: number;
    encourages_reflection?: boolean;
    validates_feelings?: boolean;
    response_length_category?: string;
    contains_question?: boolean;
    total_personas?: number;
    processing_time_ms?: number;
    concurrent_processing?: boolean;
    delivery_strategy?: string;
    overall_sentiment?: string;
    priority_level?: string;
    additional_personas?: number;
    all_persona_responses?: any[];
    [key: string]: any;
  };
}

export interface UserAIPreferences {
  user_id: string;
  response_frequency: string;
  premium_enabled: boolean;
  multi_persona_enabled: boolean;
  preferred_personas: string[];
  blocked_personas: string[];
  max_response_length: string;
  tone_preference: string;
  proactive_checkins: boolean;
  pattern_analysis_enabled: boolean;
  celebration_mode: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatternAnalysisRequest {
  user_id: string;
  include_history: boolean;
  force_refresh: boolean;
  analysis_depth: string;
}

export interface PatternAnalysisResponse {
  user_id: string;
  patterns: UserPatterns;
  adaptive_context: AdaptiveContext;
  persona_recommendations: PersonaInfo[];
  analysis_completed_at: string;
  analysis_duration_ms?: number;
  cache_used: boolean;
}

export interface AdaptiveResponseRequest {
  user_id: string;
  journal_content: string;
  persona?: string;
  force_persona: boolean;
  include_pattern_analysis: boolean;
  response_preferences?: any;
}

export interface AdaptiveResponseResponse {
  ai_insight: AIInsightResponse;
  pattern_analysis?: PatternAnalysisResponse;
  persona_used: PersonaInfo;
  adaptation_applied: boolean;
  adaptation_confidence: number;
  response_generated_at: string;
}

export interface SubscriptionStatus {
  tier: string;
  is_premium_active: boolean;
  premium_expires_at?: string;
  is_beta_tester: boolean;
  beta_premium_enabled: boolean;
  available_personas: string[];
  ai_requests_today: number;
  daily_limit: number;
  beta_mode: boolean;
  premium_features: {
    advanced_personas: boolean;
    pattern_insights: boolean;
    unlimited_history: boolean;
    priority_support: boolean;
  };
}

export interface BetaToggleRequest {
  user_id: string;
  enabled: boolean;
}

export interface BetaToggleResponse {
  success: boolean;
  beta_premium_enabled: boolean;
  subscription_status: SubscriptionStatus;
  message: string;
  error?: string;
}

export interface UserReply {
  id: string;
  journal_entry_id: string;
  user_id: string;
  reply_text: string;
  created_at: string;
  is_ai_response?: boolean;
  ai_persona?: string;
}

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    // Use environment variable for API URL, fallback to relative URLs (goes through Vercel proxy)
    this.baseURL = import.meta.env.VITE_API_URL || '';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      async (config) => {
        // Get auth token from authService
        let token = authService.getAuthToken();
        
        // If no token found, try to get fresh token from Supabase session
        if (!token) {
          secureLogger.debug('No cached token found, trying to get fresh token from Supabase');
          token = await authService.getAuthTokenAsync();
        }
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          secureLogger.debug('Auth token added to request');
        } else {
          secureLogger.warn('No authentication token available for API request');
          // Don't fail the request - let backend handle 401 response properly
        }

        secureLogger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        if (config.data) {
          secureLogger.debug('Request data:', config.data);
        }

        return config;
      },
      (error) => {
        secureLogger.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for better error handling
    this.client.interceptors.response.use(
      (response) => {
        secureLogger.debug(`API Response: ${response.status} ${response.config.url}`);
        if (response.data) {
          secureLogger.debug('Response data:', response.data);
        }
        return response;
      },
      (error: AxiosError) => {
        secureLogger.error(`API Error: ${error.response?.status} ${error.config?.url}`);
        
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          secureLogger.info('Unauthorized - clearing auth and redirecting to login');
          authService.signOut();
          window.location.href = '/auth';
        }
        
        if (error.response?.data) {
          secureLogger.error('Error response:', error.response.data);
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async testConnection(): Promise<boolean> {
    try {
      secureLogger.debug('Testing connection to:', this.baseURL);
      await this.healthCheck();
      secureLogger.debug('Connection test successful:', { connected: true });
      return true;
    } catch (error) {
      secureLogger.error('Connection test failed:', error);
      return false;
    }
  }

  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Journal entries
  async getJournalEntries(page: number = 1, perPage: number = 30): Promise<JournalEntry[]> {
    const response = await this.client.get('/api/v1/journal/entries', {
      params: { page, per_page: perPage }
    });
    
    return response.data.entries || [];
  }

  async getJournalEntry(id: string): Promise<JournalEntry> {
    const response = await this.client.get(`/api/v1/journal/entries/${id}`);
    return response.data;
  }

  async createJournalEntry(entry: CreateJournalEntry): Promise<JournalEntry> {
    const response = await this.client.post('/api/v1/journal/entries', entry);
    return response.data;
  }

  async updateJournalEntry(id: string, entry: Partial<CreateJournalEntry>): Promise<JournalEntry> {
    const response = await this.client.put(`/api/v1/journal/entries/${id}`, entry);
    return response.data;
  }

  async deleteJournalEntry(id: string): Promise<void> {
    await this.client.delete(`/api/v1/journal/entries/${id}`);
  }

  async resetJournal(): Promise<any> {
    const result = await authService.getCurrentUser();
    if (!result.user?.id) {
      throw new Error('Authentication required for journal reset');
    }
    
    const response = await this.client.delete(`/api/v1/journal/reset/${result.user.id}`, {
      params: { confirm: true }
    });
    return response.data;
  }

  // AI responses
  async generateAdaptiveResponse(request: {
    journal_content: string;
    persona?: string;
    include_pattern_analysis?: boolean;
    user_id?: string;
    force_persona?: boolean;
    response_preferences?: any;
  }): Promise<AIResponse> {
    secureLogger.debug('Generating adaptive response:', request);
    
    // Get the user ID from the request or require authentication
    const result = await authService.getCurrentUser();
    const userId = request.user_id || result.user?.id;
    
    if (!userId) {
      throw new Error('Authentication required for AI response generation');
    }
    
    const response = await this.client.post('/api/v1/adaptive-ai/generate-response', {
      user_id: userId,
      journal_content: request.journal_content,
      persona: request.persona || 'auto',
      force_persona: request.force_persona || false,
      include_pattern_analysis: request.include_pattern_analysis !== false,
      response_preferences: request.response_preferences || {}
    });
    
    secureLogger.debug('Adaptive response generated:', response.data);
    return response.data;
  }

  async getUserPatterns(): Promise<UserPatterns> {
    const result = await authService.getCurrentUser();
    if (!result.user) {
      throw new Error('Authentication required for user patterns');
    }
    
    const response = await this.client.get(`/api/v1/adaptive-ai/patterns/${result.user.id}`);
    return response.data;
  }

  async getAvailablePersonas(): Promise<PersonaInfo[]> {
    const result = await authService.getCurrentUser();
    if (!result.user) {
      throw new Error('Authentication required for personas');
    }
    
    const response = await this.client.get('/api/v1/adaptive-ai/personas', {
      params: { user_id: result.user.id }
    });
    // API returns personas array directly, not wrapped in an object
    return Array.isArray(response.data) ? response.data : response.data.personas || [];
  }

  async getSubscriptionStatus(): Promise<any> {
    const result = await authService.getCurrentUser();
    if (!result.user) {
      throw new Error('Authentication required for subscription status');
    }
    
    const response = await this.client.get(`/api/v1/auth/subscription-status/${result.user.id}`);
    return response.data;
  }

  async classifyTopics(content: string): Promise<string[]> {
    try {
      // Use the correct endpoint path for topic classification
      const response = await this.client.post('/api/v1/journal/ai/topic-classification', {
        content: content
      });
      
      return response.data.topics || [];
    } catch (error) {
      secureLogger.warn('Topic classification failed, returning empty array:', error);
      return [];
    }
  }

  // User management (using Supabase authentication)
  async getCurrentUser(): Promise<any> {
    // Delegate to authService for consistent authentication
    const { user } = await authService.getCurrentUser();
    return user;
  }

  async updateUserProfile(updates: any): Promise<any> {
    // Ensure user is authenticated
    const { user } = await authService.getCurrentUser();
    if (!user) {
      throw new Error('Authentication required to update profile');
    }

    // Send updates to backend
    const response = await this.client.patch(`/api/v1/user/profile/${user.id}`, updates);
    return response.data;
  }

  // Analytics
  async trackUserAction(action: string, data?: any): Promise<void> {
    try {
      // For now, just log analytics locally
      console.log('User action:', action, data);
      
      // Future: Send to analytics service
      // await this.client.post('/api/v1/analytics/track', {
      //   action,
      //   data,
      //   timestamp: new Date().toISOString()
      // });
    } catch (error) {
      console.warn('Analytics tracking failed:', error);
    }
  }

  // Pulse AI endpoints
  async getPulseResponse(entryId: string): Promise<PulseResponse> {
    const response: AxiosResponse<PulseResponse> = await this.client.get(`/api/v1/journal/entries/${entryId}/pulse`);
    return response.data;
  }

  async submitPulseFeedback(entryId: string, feedbackType: string, feedbackText?: string): Promise<any> {
    const response = await this.client.post(`/api/v1/journal/entries/${entryId}/feedback`, {
      feedback_type: feedbackType,
      feedback_text: feedbackText
    });
    return response.data;
  }

  // Stats endpoints
  async getJournalStats(): Promise<JournalStats> {
    const response: AxiosResponse<JournalStats> = await this.client.get('/api/v1/journal/stats');
    return response.data;
  }

  // Adaptive AI endpoints
  async analyzeUserPatterns(request: PatternAnalysisRequest): Promise<PatternAnalysisResponse> {
    console.log('Analyzing user patterns:', request);
    const response: AxiosResponse<PatternAnalysisResponse> = await this.client.post('/api/v1/adaptive-ai/analyze-patterns', request);
    console.log('Pattern analysis completed:', response.data);
    return response.data;
  }

  async getAdaptivePulseResponse(entryId: string, persona?: string, options?: {
    structured?: boolean;
    streaming?: boolean;
    multi_persona?: boolean;
  }): Promise<AIInsightResponse> {
    console.log('Getting adaptive Pulse response for entry:', entryId, 'with persona:', persona, 'options:', options);
    const params: any = {};
    
    if (persona) params.persona = persona;
    if (options?.structured) params.structured = true;
    if (options?.streaming) params.streaming = true;
    if (options?.multi_persona) params.multi_persona = true;
    
    const response: AxiosResponse<AIInsightResponse> = await this.client.post(`/api/v1/journal/entries/${entryId}/adaptive-response`, {}, {
      params
    });
    console.log('Adaptive Pulse response received:', response.data);
    return response.data;
  }

  // New methods for enhanced AI capabilities
  async getStructuredAIResponse(entryId: string, persona?: string): Promise<AIInsightResponse> {
    console.log('Getting structured AI response for entry:', entryId);
    return this.getAdaptivePulseResponse(entryId, persona, { structured: true });
  }

  async getMultiPersonaResponse(entryId: string): Promise<AIInsightResponse> {
    console.log('Getting multi-persona response for entry:', entryId);
    return this.getAdaptivePulseResponse(entryId, "auto", { multi_persona: true });
  }

  // WebSocket streaming connection
  connectToAIStream(entryId: string, persona: string = "auto", token: string): WebSocket {
    const wsUrl = `${this.baseURL.replace('http', 'ws')}/api/v1/journal/entries/${entryId}/stream?persona=${persona}&token=${token}`;
    console.log('Connecting to AI stream:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('AI streaming WebSocket connected');
    };
    
    ws.onerror = (error) => {
      console.error('AI streaming WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('AI streaming WebSocket disconnected');
    };
    
    return ws;
  }

  // Enhanced error handling utility with AI debugging
  handleError(error: any, context?: Record<string, any>): string {
    // Import error handler dynamically to avoid circular dependencies
    import('../utils/errorHandler').then(({ handleAPIError }) => {
      const apiError = new Error(this.getErrorMessage(error));
      handleAPIError(apiError, {
        ...context,
        source: 'api_service',
        response_status: error.response?.status,
        response_data: error.response?.data,
        request_config: error.config
      });
    }).catch(console.error);

    return this.getErrorMessage(error);
  }

  private getErrorMessage(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  }

  // Utility methods
  getBaseUrl(): string {
    return this.baseURL;
  }

  // Beta testing endpoints
  async toggleBetaPremium(request: BetaToggleRequest): Promise<BetaToggleResponse> {
    console.log('Toggling beta premium:', request);
    const response: AxiosResponse<BetaToggleResponse> = await this.client.post('/api/v1/auth/beta/toggle-premium', request);
    console.log('Beta premium toggled:', response.data);
    return response.data;
  }

  async makeBetaTester(userId: string): Promise<BetaToggleResponse> {
    console.log('Making user beta tester:', userId);
    const response: AxiosResponse<BetaToggleResponse> = await this.client.post('/api/v1/auth/beta/make-tester', { user_id: userId });
    console.log('User made beta tester:', response.data);
    return response.data;
  }

  // User AI Preferences
  async getUserAIPreferences(userId?: string): Promise<UserAIPreferences> {
    const result = await authService.getCurrentUser();
    const targetUserId = userId || result.user?.id;
    
    if (!targetUserId) {
      throw new Error('Authentication required for AI preferences');
    }
    
    const response = await this.client.get(`/api/v1/adaptive-ai/preferences/${targetUserId}`);
    
    return response.data;
  }

  async updateUserAIPreferences(preferences: Partial<UserAIPreferences>, userId?: string): Promise<UserAIPreferences> {
    const result = await authService.getCurrentUser();
    const targetUserId = userId || result.user?.id;
    
    if (!targetUserId) {
      throw new Error('Authentication required to update AI preferences');
    }
    
    const response = await this.client.put(`/api/v1/adaptive-ai/preferences/${targetUserId}`, preferences);
    
    return response.data;
  }

  async saveUserAIPreferences(preferences: UserAIPreferences): Promise<boolean> {
    const response = await this.client.post('/api/v1/adaptive-ai/preferences', preferences);
    
    return response.data.success || false;
  }

  async updateUserPreference(userId: string, preferenceKey: string, value: any): Promise<boolean> {
    const response = await this.client.patch(
      `/api/v1/adaptive-ai/preferences/${userId}/${preferenceKey}`,
      { value }
    );
    
    return response.data.success || false;
  }

  async getFrequencySettings(): Promise<Record<string, any>> {
    const response = await this.client.get('/api/v1/adaptive-ai/frequency-settings');
    
    return response.data;
  }

  async submitAIFeedback(entryId: string, feedbackType: 'helpful' | 'not_helpful', value: boolean): Promise<any> {
    try {
      // Map frontend feedback types to backend expected types
      const backendFeedbackType = value ? 'thumbs_up' : 'thumbs_down';
      
      const response = await this.client.post(`/api/v1/journal/entries/${entryId}/feedback`, {
        feedback_type: backendFeedbackType,
        feedback_text: feedbackType === 'helpful' ? 'User found response helpful' : 'User found response not helpful'
      });
      return response.data;
    } catch (error) {
      console.error('Failed to submit AI feedback:', error);
      throw error;
    }
  }

  async submitAIReply(entryId: string, replyText: string): Promise<any> {
    try {
      const response = await this.client.post(`/api/v1/journal/entries/${entryId}/reply`, {
        reply_text: replyText
      });
      return response.data;
    } catch (error) {
      console.error('Failed to submit AI reply:', error);
      throw error;
    }
  }

  async getUserReplies(entryId: string): Promise<UserReply[]> {
    try {
      const response = await this.client.get(`/api/v1/journal/entries/${entryId}/replies`);
      return response.data.replies || [];
    } catch (error) {
      console.error('Failed to get user replies:', error);
      return [];
    }
  }

  async getAllAIInsightsForEntry(entryId: string): Promise<any> {
    try {
      const response = await this.client.get(`/api/v1/journal/entries/${entryId}/all-ai-insights`);
      return response.data;
    } catch (error) {
      console.error('Failed to get all AI insights:', error);
      throw error;
    }
  }

  async getAllEntriesWithAIInsights(page: number = 1, perPage: number = 30): Promise<any> {
    try {
      const response = await this.client.get('/api/v1/journal/all-entries-with-ai-insights', {
        params: { page, per_page: perPage }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get entries with AI insights:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService(); 