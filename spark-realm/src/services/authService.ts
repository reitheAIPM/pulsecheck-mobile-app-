import { createClient } from '@supabase/supabase-js';

// Supabase configuration with debugging
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key';

// Debug environment variables in development
if (import.meta.env.DEV) {
  console.log('🔧 Auth Service Debug Info:');
  console.log('- Supabase URL:', supabaseUrl);
  console.log('- Has Anon Key:', !!supabaseAnonKey && supabaseAnonKey !== 'your-anon-key');
  console.log('- Key length:', supabaseAnonKey?.length || 0);
}

// Validate configuration
if (!supabaseUrl || supabaseUrl === 'https://your-project.supabase.co') {
  console.error('❌ VITE_SUPABASE_URL not configured');
}

if (!supabaseAnonKey || supabaseAnonKey === 'your-anon-key') {
  console.error('❌ VITE_SUPABASE_ANON_KEY not configured');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce', // Use PKCE flow for better security
    debug: import.meta.env.DEV
  },
  global: {
    headers: {
      'X-Client-Info': 'supabase-js-web'
    }
  },
  db: {
    schema: 'public'
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
});

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
        // Store tokens if session exists (user confirmed email or confirmation disabled)
        if (result.session) {
          localStorage.setItem('auth_tokens', JSON.stringify({
            access_token: result.session.access_token,
            refresh_token: result.session.refresh_token,
            expires_at: result.session.expires_at
          }));
        }

        return {
          user: {
            id: result.user.id,
            email: result.user.email || '',
            name: result.user.user_metadata?.name || name || 'User',
            tech_role: result.user.user_metadata?.tech_role || techRole || 'user'
          },
          session: result.session,
          needsEmailConfirmation: result.needsEmailConfirmation,
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

  // Wrapper method for Profile component compatibility
  async logout() {
    return this.signOut();
  }

  async resetPassword(email: string) {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) throw error;

      return { success: true, error: null };
    } catch (error: any) {
      console.error('Password reset error:', error);
      return { success: false, error: error.message || 'Password reset failed' };
    }
  }

  async updatePassword(newPassword: string) {
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      });

      if (error) throw error;

      return { success: true, error: null };
    } catch (error: any) {
      console.error('Password update error:', error);
      return { success: false, error: error.message || 'Password update failed' };
    }
  }

  async resendConfirmation(email: string) {
    try {
      const { error } = await supabase.auth.resend({
        type: 'signup',
        email: email
      });

      if (error) throw error;

      return { success: true, error: null };
    } catch (error: any) {
      console.error('Resend confirmation error:', error);
      return { success: false, error: error.message || 'Resend confirmation failed' };
    }
  }

  async getCurrentUser(): Promise<{ user: User | null; error: string | null }> {
    try {
      // Always try Supabase authentication first
      const { data: { user: supabaseUser }, error } = await supabase.auth.getUser();
      
      if (error) {
        // Don't log 403/session errors as scary errors - they're expected for unauthenticated users
        if (error.message.includes('session') || error.message.includes('Auth session missing')) {
          console.log('ℹ️ No active authentication session (expected for unauthenticated users)');
          return { user: null, error: null }; // Return null error for expected states
        } else {
          console.error('❌ Auth error:', error.message);
          return { user: null, error: error.message };
        }
      }

      if (!supabaseUser) {
        return { user: null, error: null }; // No error - just no user
      }

      const user: User = {
        id: supabaseUser.id,
        email: supabaseUser.email || '',
        name: supabaseUser.user_metadata?.name || 'User',
        tech_role: supabaseUser.user_metadata?.tech_role || 'user'
      };

      return { user, error: null };
    } catch (error) {
      console.error('❌ getCurrentUser error:', error);
      return { user: null, error: 'Authentication failed' };
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
      // Check localStorage first for stored tokens (faster, no API call)
      const tokens = localStorage.getItem('auth_tokens');
      if (tokens) {
        const parsed = JSON.parse(tokens) as AuthTokens;
        
        // Check if token is expired
        if (parsed.expires_at && parsed.expires_at < Date.now() / 1000) {
          console.log('🔄 Auth token expired, clearing localStorage');
          localStorage.removeItem('auth_tokens');
          return null;
        }
        
        console.log('✅ Auth token retrieved from cache');
        return parsed.access_token;
      }

      console.log('⚠️ No auth token found in localStorage');
      return null;
    } catch (error) {
      console.error('Get auth token error:', error);
      return null;
    }
  }

  // New method to get token synchronously from current Supabase session
  async getAuthTokenAsync(): Promise<string | null> {
    try {
      const { data: { session }, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error('Error getting session:', error);
        return null;
      }

      if (session?.access_token) {
        // Update localStorage with fresh token
        localStorage.setItem('auth_tokens', JSON.stringify({
          access_token: session.access_token,
          refresh_token: session.refresh_token,
          expires_at: session.expires_at
        }));
        
        console.log('✅ Fresh auth token retrieved from Supabase session');
        return session.access_token;
      }

      console.log('⚠️ No active Supabase session');
      return null;
    } catch (error) {
      console.error('Get auth token async error:', error);
      return null;
    }
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

  // Remove development mode fallback - always use real authentication
  getDevelopmentUser(): User {
    throw new Error('Development mode disabled - use real authentication only');
  }

  isDevelopmentMode(): boolean {
    // Always return false - no more development mode fallbacks
    return false;
  }
}

export const authService = new AuthService(); 