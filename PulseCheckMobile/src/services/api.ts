// Mobile API Service for PulseCheck React Native App
// Adapted from web version with React Native compatibility

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

class MobileApiService {
  private baseURL = this.getBaseURL();

  private getBaseURL(): string {
    // Production Railway URL
    return 'https://pulsecheck-mobile-app-production.up.railway.app';
  }

  constructor() {
    console.log('🚀 Mobile API Service initialized with URL:', this.baseURL);
  }

  async healthCheck(): Promise<HealthCheck> {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }

  async createJournalEntry(entry: JournalEntryCreate): Promise<JournalEntry> {
    const response = await fetch(`${this.baseURL}/api/v1/journal/entries`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entry),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async getJournalEntries(page: number = 1, per_page: number = 30): Promise<JournalEntry[]> {
    const response = await fetch(
      `${this.baseURL}/api/v1/journal/entries?page=${page}&per_page=${per_page}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.entries || data; // Handle both paginated and direct array responses
  }

  async getJournalEntry(id: string): Promise<JournalEntry> {
    const response = await fetch(`${this.baseURL}/api/v1/journal/entries/${id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async updateJournalEntry(id: string, entry: Partial<JournalEntryCreate>): Promise<JournalEntry> {
    const response = await fetch(`${this.baseURL}/api/v1/journal/entries/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entry),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async deleteJournalEntry(id: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/v1/journal/entries/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }

  async getPulseResponse(entryId: string): Promise<PulseResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/journal/entries/${entryId}/pulse`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async getJournalStats(): Promise<JournalStats> {
    const response = await fetch(`${this.baseURL}/api/v1/journal/stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  handleError(error: any, context?: Record<string, any>): string {
    console.error('API Error:', error, context);
    
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  }

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

  getBaseUrl(): string {
    return this.baseURL;
  }
}

// Export singleton instance
export const mobileApiService = new MobileApiService(); 