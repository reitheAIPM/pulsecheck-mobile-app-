import axios, { AxiosInstance, AxiosResponse } from 'axios';

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
  insight: string;
  action: string;
  question: string;
  mood_analysis: string;
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
  id: string;
  name: string;
  description: string;
  recommended: boolean;
  traits: string[];
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

class ApiService {
  private client: AxiosInstance;
  private currentUserId: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: 'https://pulsecheck-mobile-app-production.up.railway.app',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Add request interceptor to include authentication
    this.client.interceptors.request.use(async (config) => {
      try {
        // Get auth token from localStorage (mock auth system)
        const authToken = localStorage.getItem('authToken');
        
        if (authToken) {
          config.headers['X-User-Id'] = authToken;
          this.currentUserId = authToken;
        } else {
          // Generate a fallback user ID for unauthenticated requests
          if (!this.currentUserId) {
            this.currentUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          }
          config.headers['X-User-Id'] = this.currentUserId;
        }
        
        // Simplified logging - removed verbose debugging
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        if (config.params) console.log('Request params:', config.params);
        
        return config;
      } catch (error) {
        console.error('Request interceptor error:', error);
        return config;
      }
    });

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log('API Response:', response.status, response.config.url);
        return response;
      },
      (error) => {
        console.log('API Response Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Health check
  async testConnection(): Promise<boolean> {
    try {
      console.log('Testing connection to:', this.client.defaults.baseURL);
      await this.healthCheck();
      console.log('Connection test successful:', { connected: true });
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Journal entries
  async getJournalEntries(page: number = 1, perPage: number = 30): Promise<JournalEntry[]> {
    console.log(`Fetching journal entries, page: ${page} per_page: ${perPage}`);
    console.log('Full URL will be:', `${this.client.defaults.baseURL}/api/v1/journal/entries`);
    
    const response = await this.client.get('/api/v1/journal/entries', {
      params: { page, per_page: perPage }
    });
    
    console.log(`Journal entries fetched: ${response.data.entries?.length || 0} entries out of ${response.data.total || 0} total`);
    return response.data.entries || [];
  }

  async getJournalEntry(id: string): Promise<JournalEntry> {
    const response = await this.client.get(`/api/v1/journal/entries/${id}`);
    return response.data;
  }

  async createJournalEntry(entry: CreateJournalEntry): Promise<JournalEntry> {
    console.log('Creating journal entry:', entry);
    console.log('Full URL will be:', `${this.client.defaults.baseURL}/api/v1/journal/entries`);
    
    const response = await this.client.post('/api/v1/journal/entries', entry);
    console.log('Journal entry created successfully:', response.data);
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
    const authToken = localStorage.getItem('authToken');
    const userId = authToken || this.currentUserId;
    
    const response = await this.client.delete(`/api/v1/journal/reset/${userId}`, {
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
    console.log('Generating adaptive response:', request);
    
    // Get the user ID from the request or fallback to current user
    const authToken = localStorage.getItem('authToken');
    const userId = request.user_id || authToken || this.currentUserId;
    
    const response = await this.client.post('/api/v1/adaptive-ai/generate-response', {
      user_id: userId,
      journal_content: request.journal_content,
      persona: request.persona || 'auto',
      force_persona: request.force_persona || false,
      include_pattern_analysis: request.include_pattern_analysis !== false,
      response_preferences: request.response_preferences || {}
    });
    
    console.log('Adaptive response generated:', response.data);
    return response.data;
  }

  async getUserPatterns(): Promise<UserPatterns> {
    const authToken = localStorage.getItem('authToken');
    const userId = authToken || this.currentUserId;
    
    console.log('Fetching user patterns for:', userId);
    
    const response = await this.client.get(`/api/v1/adaptive-ai/patterns/${userId}`);
    console.log('User patterns fetched:', response.data);
    return response.data;
  }

  async getAvailablePersonas(): Promise<PersonaInfo[]> {
    const authToken = localStorage.getItem('authToken');
    const userId = authToken || this.currentUserId;
    
    console.log('Fetching available personas for user:', userId);
    
    const response = await this.client.get('/api/v1/adaptive-ai/personas', {
      params: { user_id: userId }
    });
    
    console.log(`Available personas fetched: ${response.data.personas?.length || 0} personas`);
    return response.data.personas || [];
  }

  async getSubscriptionStatus(): Promise<any> {
    const authToken = localStorage.getItem('authToken');
    const userId = authToken || this.currentUserId;
    
    console.log('Getting subscription status for user:', userId);
    
    const response = await this.client.get(`/api/v1/auth/subscription-status/${userId}`);
    console.log('Subscription status retrieved:', response.data);
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
      console.warn('Topic classification failed, returning empty array:', error);
      return [];
    }
  }

  // User management (for mock auth integration)
  async getCurrentUser(): Promise<any> {
    const authToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    
    if (authToken && storedUser) {
      return JSON.parse(storedUser);
    }
    
    return null;
  }

  async updateUserProfile(updates: any): Promise<any> {
    const authToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    
    if (!authToken || !storedUser) {
      throw new Error('No authenticated user');
    }

    // Update user in localStorage for mock auth
    const currentUser = JSON.parse(storedUser);
    const updatedUser = { ...currentUser, ...updates };
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));

    return updatedUser;
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

  async getAdaptivePulseResponse(entryId: string, persona?: string): Promise<AIInsightResponse> {
    console.log('Getting adaptive Pulse response for entry:', entryId, 'with persona:', persona);
    const params = persona ? { persona } : {};
    const response: AxiosResponse<AIInsightResponse> = await this.client.get(`/api/v1/journal/entries/${entryId}/adaptive-pulse`, {
      params
    });
    console.log('Adaptive Pulse response received:', response.data);
    return response.data;
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
    return this.client.defaults.baseURL;
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
}

// Export singleton instance
export const apiService = new ApiService(); 