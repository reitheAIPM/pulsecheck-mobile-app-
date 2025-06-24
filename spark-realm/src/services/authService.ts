import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface User {
  id: string;
  email: string;
  name?: string;
  tech_role?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_at?: number;
}

class AuthService {
  async signUp(email: string, password: string, name?: string, techRole?: string) {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name: name || 'User',
            tech_role: techRole || 'user'
          }
        }
      });

      if (error) throw error;

      return {
        user: data.user,
        session: data.session,
        needsEmailConfirmation: !data.session
      };
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  }

  // Wrapper method for Auth component compatibility
  async register({ email, password, name, techRole }: { email: string; password: string; name?: string; techRole?: string }) {
    try {
      const result = await this.signUp(email, password, name, techRole);
      
      if (result.user) {
        return {
          user: {
            id: result.user.id,
            email: result.user.email || '',
            name: result.user.user_metadata?.name || name || 'User',
            tech_role: result.user.user_metadata?.tech_role || techRole || 'user'
          },
          error: null
        };
      }
      
      return { user: null, error: 'Registration failed' };
    } catch (error: any) {
      return { user: null, error: error.message || 'Registration failed' };
    }
  }

  async signIn(email: string, password: string) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) throw error;

      // Store tokens in localStorage
      if (data.session) {
        localStorage.setItem('auth_tokens', JSON.stringify({
          access_token: data.session.access_token,
          refresh_token: data.session.refresh_token,
          expires_at: data.session.expires_at
        }));
      }

      return data;
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  }

  // Wrapper method for Auth component compatibility
  async login({ email, password }: { email: string; password: string }) {
    try {
      const result = await this.signIn(email, password);
      
      if (result.user) {
        return {
          user: {
            id: result.user.id,
            email: result.user.email || '',
            name: result.user.user_metadata?.name || 'User',
            tech_role: result.user.user_metadata?.tech_role || 'user'
          },
          error: null
        };
      }
      
      return { user: null, error: 'Login failed' };
    } catch (error: any) {
      return { user: null, error: error.message || 'Login failed' };
    }
  }

  async signOut() {
    try {
      const { error } = await supabase.auth.signOut();
      
      // Clear stored tokens
      localStorage.removeItem('auth_tokens');
      
      if (error) throw error;
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }

  async getCurrentUser(): Promise<{ user: User | null }> {
    try {
      const { data: { user }, error } = await supabase.auth.getUser();
      
      if (error) throw error;
      
      if (user) {
        return {
          user: {
            id: user.id,
            email: user.email || '',
            name: user.user_metadata?.name || 'User',
            tech_role: user.user_metadata?.tech_role || 'user'
          }
        };
      }
      
      return { user: null };
    } catch (error) {
      console.error('Get user error:', error);
      return { user: null };
    }
  }

  async getSession() {
    try {
      const { data: { session }, error } = await supabase.auth.getSession();
      
      if (error) throw error;
      
      return session;
    } catch (error) {
      console.error('Get session error:', error);
      return null;
    }
  }

  getAuthToken(): string | null {
    try {
      const tokens = localStorage.getItem('auth_tokens');
      if (tokens) {
        const parsed = JSON.parse(tokens) as AuthTokens;
        
        // Check if token is expired
        if (parsed.expires_at && parsed.expires_at < Date.now() / 1000) {
          localStorage.removeItem('auth_tokens');
          return null;
        }
        
        return parsed.access_token;
      }
    } catch (error) {
      console.error('Get auth token error:', error);
    }
    
    return null;
  }

  onAuthStateChange(callback: (user: User | null) => void) {
    return supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user) {
        callback({
          id: session.user.id,
          email: session.user.email || '',
          name: session.user.user_metadata?.name || 'User',
          tech_role: session.user.user_metadata?.tech_role || 'user'
        });
      } else {
        callback(null);
      }
    });
  }

  // Development mode fallback
  getDevelopmentUser(): User {
    return {
      id: 'user_reiale01gmailcom_1750733000000',
      email: 'rei.ale01@gmail.com',
      name: 'Rei (Development User)',
      tech_role: 'beta_tester'
    };
  }

  isDevelopmentMode(): boolean {
    return !supabaseUrl.includes('supabase.co') || !supabaseAnonKey || supabaseAnonKey === 'your-anon-key';
  }
}

export const authService = new AuthService(); 