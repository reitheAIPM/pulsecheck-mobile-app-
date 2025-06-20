import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  JournalEntry, 
  JournalEntryCreate, 
  JournalStats, 
  PulseResponse, 
  AIAnalysisResponse,
  PaginatedResponse 
} from '../types';

class ApiService {
  private client: AxiosInstance;
  private baseURL = this.getBaseURL();

  private getBaseURL(): string {
    // Check for explicit environment variable first
    if (process.env.EXPO_PUBLIC_API_URL) {
      return process.env.EXPO_PUBLIC_API_URL;
    }
    
    // Check if we're explicitly in development mode
    const isExplicitDevelopment = process.env.NODE_ENV === 'development' && 
                                 process.env.EXPO_PUBLIC_USE_LOCALHOST === 'true';
    
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
        'User-Agent': 'PulseCheck-Mobile/1.0',
      },
    });

    // Request interceptor for adding auth headers (when we implement auth)
    this.client.interceptors.request.use(
      (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        console.log('Request params:', config.params);
        console.log('Request headers:', config.headers);
        // TODO: Add auth token when implemented
        // const token = AsyncStorage.getItem('auth_token');
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
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Journal Endpoints
  async createJournalEntry(entry: JournalEntryCreate): Promise<JournalEntry> {
    // Ensure integer values are properly typed
    const processedEntry = {
      ...entry,
      mood_level: Math.round(entry.mood_level),
      energy_level: Math.round(entry.energy_level),
      stress_level: Math.round(entry.stress_level),
      sleep_hours: entry.sleep_hours ? Math.round(entry.sleep_hours) : entry.sleep_hours,
      work_hours: entry.work_hours ? Math.round(entry.work_hours) : entry.work_hours,
    };
    
    const response = await this.client.post('/api/v1/journal/entries', processedEntry);
    return response.data;
  }

  async getJournalEntries(page = 1, perPage = 10): Promise<PaginatedResponse<JournalEntry>> {
    // Ensure valid pagination parameters
    const validPage = Math.max(1, Math.round(page));
    const validPerPage = Math.max(1, Math.min(100, Math.round(perPage)));
    
    console.log(`📝 Fetching journal entries: page=${validPage}, perPage=${validPerPage}`);
    
    return this._retryRequest(async () => {
      const response = await this.client.get('/api/v1/journal/entries', {
        params: { page: validPage, per_page: validPerPage }
      });
      console.log(`✅ Journal entries response:`, {
        status: response.status,
        entriesCount: response.data?.entries?.length || 0,
        total: response.data?.total || 0
      });
      return response.data;
    });
  }

  async getJournalEntry(entryId: string): Promise<JournalEntry> {
    return this._retryRequest(async () => {
      const response = await this.client.get(`/api/v1/journal/entries/${entryId}`);
      return response.data;
    });
  }

  async getJournalStats(): Promise<JournalStats> {
    return this._retryRequest(async () => {
      const response = await this.client.get('/api/v1/journal/stats');
      return response.data;
    });
  }

  // AI Endpoints
  async getPulseResponse(entryId: string): Promise<PulseResponse> {
    const response = await this.client.get(`/api/v1/journal/entries/${entryId}/pulse`);
    return response.data;
  }

  async getAIAnalysis(entryId: string, includeHistory = true): Promise<AIAnalysisResponse> {
    const response = await this.client.get(`/api/v1/journal/entries/${entryId}/analysis`, {
      params: { include_history: includeHistory }
    });
    return response.data;
  }

  // Feedback Endpoints
  async submitFeedback(feedback: {
    entryId: string;
    feedbackType: 'thumbs_up' | 'thumbs_down' | 'detailed' | 'report';
    feedbackText?: string;
  }): Promise<any> {
    const response = await this.client.post(
      `/api/v1/journal/entries/${feedback.entryId}/feedback`,
      null,
      {
        params: {
          feedback_type: feedback.feedbackType,
          feedback_text: feedback.feedbackText
        }
      }
    );
    return response.data;
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

  // Error handling helper
  handleError(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error.response?.data?.message) {
      return error.response.data.message;
    } else if (error.message) {
      return error.message;
    } else {
      return 'An unexpected error occurred';
    }
  }

  // Retry logic for intermittent errors
  private async _retryRequest<T>(requestFn: () => Promise<T>, maxRetries = 3): Promise<T> {
    let lastError: any;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error: any) {
        lastError = error;
        
        console.log(`🔄 Retry attempt ${attempt}/${maxRetries} for ${error.config?.url}`);
        console.log(`❌ Error details:`, {
          status: error.response?.status,
          message: error.message,
          data: JSON.stringify(error.response?.data, null, 2)
        });
        
        // Don't retry on 4xx errors (client errors)
        if (error.response?.status >= 400 && error.response?.status < 500) {
          throw error;
        }
        
        // Don't retry on network errors after first attempt
        if (attempt === 1 && error.message?.includes('Network Error')) {
          throw error;
        }
        
        // Wait before retrying (exponential backoff)
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      }
    }
    
    throw lastError;
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export individual methods for convenience
export const submitFeedback = (feedback: {
  entryId: string;
  feedbackType: 'thumbs_up' | 'thumbs_down' | 'detailed' | 'report';
  feedbackText?: string;
}) => apiService.submitFeedback(feedback);

export default apiService; 