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
  user_id: string;
  content: string;
  mood_level: number;
  energy_level: number;
  stress_level: number;
  sleep_hours?: number;
  work_hours?: number;
  tags: string[];
  work_challenges: string[];
  gratitude_items: string[];
  created_at: string;
  updated_at: string;
}

export interface JournalEntryCreate {
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
export interface UserPatternSummary {
  writing_style: string;
  common_topics: string[];
  mood_trends: {
    mood: number;
    energy: number;
    stress: number;
  };
  interaction_preferences: {
    prefers_questions: boolean;
    prefers_validation: boolean;
    prefers_advice: boolean;
  };
  response_preferences: {
    length: string;
    style: string;
  };
  pattern_confidence: number;
  entries_analyzed: number;
  last_updated: string;
}

export interface PersonaRecommendation {
  persona_id: string;
  persona_name: string;
  description: string;
  recommended: boolean;
  recommendation_reason?: string;
  available: boolean;
  requires_premium: boolean;
  times_used: number;
  last_used?: string;
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
  patterns: UserPatternSummary;
  adaptive_context: AdaptiveContext;
  persona_recommendations: PersonaRecommendation[];
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
  persona_used: PersonaRecommendation;
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
  private baseURL = this.getBaseURL();

  private getBaseURL(): string {
    // Check for explicit environment variable first
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }
    
    // Check if we're explicitly in development mode
    const isExplicitDevelopment = import.meta.env.DEV && 
                                 import.meta.env.VITE_USE_LOCALHOST === 'true';
    
    // Default to production URL unless explicitly set to development
    return isExplicitDevelopment 
      ? 'http://localhost:8000'
      : 'https://pulsecheck-mobile-app-production.up.railway.app';
  }

  constructor() {
    console.log('API Service initialized with base URL:', this.baseURL);
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'PulseCheck-Web/1.0',
      },
      withCredentials: false, // Disable credentials for CORS
    });

    // Request interceptor for adding auth headers (when we implement auth)
    this.client.interceptors.request.use(
      (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        console.log('Request params:', config.params);
        console.log('Request headers:', config.headers);
        // TODO: Add auth token when implemented
        // const token = localStorage.getItem('auth_token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log('API Response:', response.status, response.config.url);
        return response;
      },
      (error) => {
        console.error('API Response Error:', {
          url: error.config?.url,
          status: error.response?.status,
          data: error.response?.data,
          message: error.message
        });
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck(): Promise<HealthCheck> {
    const response: AxiosResponse<HealthCheck> = await this.client.get('/health');
    return response.data;
  }

  // Journal endpoints
  async createJournalEntry(entry: JournalEntryCreate): Promise<JournalEntry> {
    console.log('Creating journal entry:', entry);
    console.log('Full URL will be:', `${this.baseURL}/api/v1/journal/entries`);
    const response: AxiosResponse<JournalEntry> = await this.client.post('/api/v1/journal/entries', entry);
    console.log('Journal entry created successfully:', response.data);
    return response.data;
  }

  async getJournalEntries(page: number = 1, per_page: number = 30): Promise<JournalEntry[]> {
    console.log('Fetching journal entries, page:', page, 'per_page:', per_page);
    console.log('Full URL will be:', `${this.baseURL}/api/v1/journal/entries`);
    const response: AxiosResponse<{
      entries: JournalEntry[];
      total: number;
      page: number;
      per_page: number;
      has_next: boolean;
      has_prev: boolean;
    }> = await this.client.get('/api/v1/journal/entries', {
      params: { page, per_page }
    });
    console.log('Journal entries fetched:', response.data.entries.length, 'entries out of', response.data.total, 'total');
    return response.data.entries; // Return just the entries array
  }

  async getJournalEntry(id: string): Promise<JournalEntry> {
    const response: AxiosResponse<JournalEntry> = await this.client.get(`/api/v1/journal/entries/${id}`);
    return response.data;
  }

  async updateJournalEntry(id: string, entry: Partial<JournalEntryCreate>): Promise<JournalEntry> {
    const response: AxiosResponse<JournalEntry> = await this.client.put(`/api/v1/journal/entries/${id}`, entry);
    return response.data;
  }

  async deleteJournalEntry(id: string): Promise<void> {
    await this.client.delete(`/api/v1/journal/entries/${id}`);
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

  async generateAdaptiveResponse(request: AdaptiveResponseRequest): Promise<AdaptiveResponseResponse> {
    console.log('Generating adaptive response:', request);
    const response: AxiosResponse<AdaptiveResponseResponse> = await this.client.post('/api/v1/adaptive-ai/generate-response', request);
    console.log('Adaptive response generated:', response.data);
    return response.data;
  }

  async getAvailablePersonas(userId: string): Promise<PersonaRecommendation[]> {
    console.log('Fetching available personas for user:', userId);
    const response: AxiosResponse<PersonaRecommendation[]> = await this.client.get('/api/v1/adaptive-ai/personas', {
      params: { user_id: userId }
    });
    console.log('Available personas fetched:', response.data.length, 'personas');
    return response.data;
  }

  async getUserPatterns(userId: string): Promise<UserPatternSummary> {
    console.log('Fetching user patterns for:', userId);
    const response: AxiosResponse<UserPatternSummary> = await this.client.get(`/api/v1/adaptive-ai/patterns/${userId}`);
    console.log('User patterns fetched:', response.data);
    return response.data;
  }

  async refreshUserPatterns(userId: string): Promise<{ message: string; user_id: string }> {
    console.log('Refreshing user patterns for:', userId);
    const response: AxiosResponse<{ message: string; user_id: string }> = await this.client.post(`/api/v1/adaptive-ai/refresh-patterns/${userId}`);
    console.log('User patterns refreshed:', response.data);
    return response.data;
  }

  // Enhanced Pulse AI with adaptive features
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
  async testConnection(): Promise<boolean> {
    try {
      console.log('Testing connection to:', this.baseURL);
      const result = await this.healthCheck();
      console.log('Connection test successful:', result);
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  // Get current base URL (for debugging)
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

  async getSubscriptionStatus(userId: string): Promise<SubscriptionStatus> {
    console.log('Getting subscription status for user:', userId);
    const response: AxiosResponse<SubscriptionStatus> = await this.client.get(`/api/v1/auth/subscription-status/${userId}`);
    console.log('Subscription status retrieved:', response.data);
    return response.data;
  }

  async getAvailablePersonasEnhanced(): Promise<{
    personas: Array<{
      id: string;
      name: string;
      description: string;
      topic_affinities: Record<string, number>;
      tone_variations: string[];
      recommended_for_user?: boolean;
    }>;
    user_patterns: {
      writing_style: string;
      common_topics: string[];
      response_preference: string;
    };
  }> {
    try {
      const response = await this.client.get('/journal/personas');
      return response.data;
    } catch (error) {
      throw new Error(this.handleError(error, { operation: 'get_personas' }));
    }
  }

  async classifyTopics(content: string): Promise<string[]> {
    try {
      // This would typically call a dedicated topic classification endpoint
      // For now, we'll use the adaptive response endpoint to get topic flags
      const mockEntry = {
        id: 'temp',
        content: content,
        mood_level: 5,
        energy_level: 5,
        stress_level: 5,
        created_at: new Date().toISOString()
      };
      
      // Use a lightweight endpoint for topic classification
      const response = await this.client.post('/journal/topic-classification', {
        content: content
      });
      
      return response.data.topics || [];
    } catch (error) {
      console.warn('Topic classification failed, returning empty array:', error);
      return [];
    }
  }
}

// Export singleton instance
export const apiService = new ApiService(); 