// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  tech_role: TechRole;
  experience_years?: number;
  company_size?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  total_journal_entries: number;
  current_streak: number;
  longest_streak: number;
  last_journal_date?: string;
}

export enum UserRole {
  USER = "user",
  ADMIN = "admin"
}

export enum TechRole {
  DEVELOPER = "developer",
  DESIGNER = "designer",
  PRODUCT_MANAGER = "product_manager",
  ENGINEERING_MANAGER = "engineering_manager",
  DATA_SCIENTIST = "data_scientist",
  DEVOPS = "devops",
  QA = "qa",
  OTHER = "other"
}

// Journal Types
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
  ai_insights?: any;
  ai_generated_at?: string;
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

export interface JournalStats {
  total_entries: number;
  current_streak: number;
  longest_streak: number;
  average_mood: number;
  average_energy: number;
  average_stress: number;
  last_entry_date?: string;
  mood_trend?: string;
  energy_trend?: string;
  stress_trend?: string;
}

// AI Types
export interface PulseResponse {
  message: string;
  insight?: AIInsight;
  suggested_actions: string[];
  follow_up_question?: string;
  response_time_ms?: number;
  confidence_score: number;
}

export interface AIInsight {
  id: string;
  title: string;
  content: string;
  insight_type: InsightType;
  priority: InsightPriority;
  tone: string;
  confidence_score: number;
  suggested_action?: string;
  follow_up_question?: string;
  tags: string[];
  references: string[];
  user_id: string;
  journal_entry_id: string;
  created_at: string;
  is_helpful?: boolean;
  user_feedback?: string;
  feedback_at?: string;
}

export enum InsightType {
  PATTERN_RECOGNITION = "pattern_recognition",
  WELLNESS_TIP = "wellness_tip",
  BURNOUT_WARNING = "burnout_warning",
  POSITIVE_REINFORCEMENT = "positive_reinforcement",
  ACTIONABLE_SUGGESTION = "actionable_suggestion",
  REFLECTION_PROMPT = "reflection_prompt"
}

export enum InsightPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent"
}

export interface AIAnalysisResponse {
  insights: AIInsight[];
  overall_wellness_score: number;
  burnout_risk_level: string;
  mood_pattern?: string;
  stress_pattern?: string;
  energy_pattern?: string;
  immediate_actions: string[];
  long_term_suggestions: string[];
  pulse_message: string;
  pulse_question?: string;
}

// Navigation Types
export type RootStackParamList = {
  Main: undefined;
  JournalEntry: undefined;
  JournalDetail: { entryId: string };
  PulseResponse: { entryId: string };
  Statistics: undefined;
  Settings: undefined;
};

export type TabParamList = {
  Home: undefined;
  Journal: undefined;
  Insights: undefined;
  Profile: undefined;
};

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  entries: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
} 