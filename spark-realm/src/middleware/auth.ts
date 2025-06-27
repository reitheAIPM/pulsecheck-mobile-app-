/**
 * Auth Middleware for PulseCheck
 * Based on Supabase Next.js middleware patterns from their official examples
 * Provides consistent auth state management and route protection
 */

import React from 'react';
import { supabase } from '../services/authService';
import type { User } from '../services/authService';

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export class AuthMiddleware {
  private static instance: AuthMiddleware;
  private authState: AuthState = {
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null
  };
  private listeners: Array<(state: AuthState) => void> = [];
  private initialized = false;

  static getInstance(): AuthMiddleware {
    if (!AuthMiddleware.instance) {
      AuthMiddleware.instance = new AuthMiddleware();
    }
    return AuthMiddleware.instance;
  }

  /**
   * Initialize auth middleware - should be called once at app startup
   * Based on Supabase middleware pattern from their examples
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      // Get initial session
      const { data: { session }, error } = await supabase.auth.getSession();
      
      if (error) {
        console.warn('Auth initialization warning:', error.message);
        this.updateAuthState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          error: error.message
        });
      } else {
        this.updateAuthState({
          user: session?.user ? this.mapSupabaseUser(session.user) : null,
          isLoading: false,
          isAuthenticated: !!session?.user,
          error: null
        });
      }

      // Set up auth state listener
      supabase.auth.onAuthStateChange(async (event, session) => {
        console.log('🔄 Auth state changed:', event);
        
        // Handle different auth events
        switch (event) {
          case 'SIGNED_IN':
            this.updateAuthState({
              user: session?.user ? this.mapSupabaseUser(session.user) : null,
              isLoading: false,
              isAuthenticated: true,
              error: null
            });
            break;
            
          case 'SIGNED_OUT':
            this.updateAuthState({
              user: null,
              isLoading: false,
              isAuthenticated: false,
              error: null
            });
            break;
            
          case 'TOKEN_REFRESHED':
            // User remains the same, just update tokens
            if (session?.user && this.authState.user) {
              console.log('🔄 Token refreshed successfully');
            }
            break;
            
          case 'USER_UPDATED':
            this.updateAuthState({
              user: session?.user ? this.mapSupabaseUser(session.user) : null,
              isLoading: false,
              isAuthenticated: !!session?.user,
              error: null
            });
            break;
            
          default:
            // Handle any other auth state changes
            this.updateAuthState({
              user: session?.user ? this.mapSupabaseUser(session.user) : null,
              isLoading: false,
              isAuthenticated: !!session?.user,
              error: null
            });
        }
      });

      this.initialized = true;
      console.log('✅ Auth middleware initialized');

    } catch (error) {
      console.error('❌ Auth middleware initialization failed:', error);
      this.updateAuthState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: error instanceof Error ? error.message : 'Auth initialization failed'
      });
    }
  }

  /**
   * Subscribe to auth state changes
   */
  subscribe(listener: (state: AuthState) => void): () => void {
    this.listeners.push(listener);
    
    // Immediately call with current state
    listener(this.authState);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * Get current auth state
   */
  getAuthState(): AuthState {
    return { ...this.authState };
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.authState.isAuthenticated;
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.authState.user;
  }

  /**
   * Get auth token for API requests
   * IMPORTANT: This ensures fresh tokens are used (prevents RLS issues)
   */
  async getAuthToken(): Promise<string | null> {
    try {
      const { data: { session }, error } = await supabase.auth.getSession();
      
      if (error) {
        console.warn('Failed to get auth session:', error.message);
        return null;
      }

      if (!session?.access_token) {
        console.log('No active session found');
        return null;
      }

      return session.access_token;
    } catch (error) {
      console.error('Error getting auth token:', error);
      return null;
    }
  }

  /**
   * Route protection middleware
   * Based on Supabase protected route patterns
   */
  requireAuth(): boolean {
    if (!this.isAuthenticated()) {
      console.warn('🚫 Route requires authentication');
      return false;
    }
    return true;
  }

  /**
   * Redirect to login if not authenticated
   */
  redirectToLogin(): void {
    if (typeof window !== 'undefined') {
      window.location.href = '/auth';
    }
  }

  /**
   * Sign out with proper cleanup
   */
  async signOut(): Promise<void> {
    try {
      await supabase.auth.signOut();
      
      // Clear any cached data
      localStorage.removeItem('auth_tokens');
      
      // State will be updated via onAuthStateChange
    } catch (error) {
      console.error('Sign out error:', error);
    }
  }

  /**
   * Refresh session if needed
   */
  async refreshSession(): Promise<boolean> {
    try {
      const { data: { session }, error } = await supabase.auth.refreshSession();
      
      if (error) {
        console.warn('Session refresh failed:', error.message);
        return false;
      }

      if (session) {
        console.log('✅ Session refreshed successfully');
        return true;
      }

      return false;
    } catch (error) {
      console.error('Error refreshing session:', error);
      return false;
    }
  }

  /**
   * Update auth state and notify listeners
   */
  private updateAuthState(newState: Partial<AuthState>): void {
    this.authState = { ...this.authState, ...newState };
    
    // Notify all listeners
    this.listeners.forEach(listener => {
      try {
        listener(this.authState);
      } catch (error) {
        console.error('Auth state listener error:', error);
      }
    });
  }

  /**
   * Map Supabase user to our User interface
   */
  private mapSupabaseUser(supabaseUser: any): User {
    return {
      id: supabaseUser.id,
      email: supabaseUser.email || '',
      name: supabaseUser.user_metadata?.name || 'User',
      tech_role: supabaseUser.user_metadata?.tech_role || 'user'
    };
  }
}

// Export singleton instance
export const authMiddleware = AuthMiddleware.getInstance();

// React hook for auth state (if using React)
export function useAuth(): AuthState & {
  signOut: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
  getAuthToken: () => Promise<string | null>;
} {
  const [authState, setAuthState] = React.useState<AuthState>(authMiddleware.getAuthState());

  React.useEffect(() => {
    const unsubscribe = authMiddleware.subscribe(setAuthState);
    return unsubscribe;
  }, []);

  return {
    ...authState,
    signOut: () => authMiddleware.signOut(),
    refreshSession: () => authMiddleware.refreshSession(),
    getAuthToken: () => authMiddleware.getAuthToken()
  };
}

// Helper for protected routes
export function withAuth<T extends Record<string, any>>(Component: React.ComponentType<T>) {
  return function AuthenticatedComponent(props: T) {
    const { isAuthenticated, isLoading } = useAuth();

    React.useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        authMiddleware.redirectToLogin();
      }
    }, [isAuthenticated, isLoading]);

    if (isLoading) {
      return React.createElement('div', null, 'Loading...');
    }

    if (!isAuthenticated) {
      return React.createElement('div', null, 'Redirecting to login...');
    }

    return React.createElement(Component, props);
  };
}

// API request helper with auth
export async function authenticatedFetch(
  url: string, 
  options: RequestInit = {}
): Promise<Response> {
  const token = await authMiddleware.getAuthToken();
  
  if (!token) {
    throw new Error('No authentication token available');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);

  return fetch(url, {
    ...options,
    headers
  });
} 