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

  async getJournalEntries(limit: number = 30, offset: number = 0): Promise<JournalEntry[]> {
    console.log('Fetching journal entries, limit:', limit, 'offset:', offset);
    console.log('Full URL will be:', `${this.baseURL}/api/v1/journal/entries`);
    const response: AxiosResponse<JournalEntry[]> = await this.client.get('/api/v1/journal/entries', {
      params: { limit, offset }
    });
    console.log('Journal entries fetched:', response.data.length, 'entries');
    return response.data;
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

  // Error handling utility
  handleError(error: any): string {
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
}

// Export singleton instance
export const apiService = new ApiService(); 