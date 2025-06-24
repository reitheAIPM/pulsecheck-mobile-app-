// Mock authentication service for MVP
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  tech_role?: string;
  company?: string;
  created_at: string;
}

export interface RegistrationData {
  email: string;
  password: string;
  name: string;
  tech_role?: string;
  company?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

class AuthService {
  private currentUser: UserProfile | null = null;
  private authToken: string | null = null;

  // Generate a user ID for mock auth
  private generateUserId(): string {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async register(data: RegistrationData): Promise<{ user: UserProfile | null; error: string | null }> {
    try {
      // For MVP, we'll create a mock user since we're using backend mock auth
      const userId = this.generateUserId();
      
      const user: UserProfile = {
        id: userId,
        email: data.email,
        name: data.name,
        tech_role: data.tech_role,
        company: data.company,
        created_at: new Date().toISOString()
      };

      // Store auth token for API calls
      this.authToken = userId;
      this.currentUser = user;

      // Store in localStorage for persistence
      localStorage.setItem('authToken', userId);
      localStorage.setItem('currentUser', JSON.stringify(user));

      return { user, error: null };
    } catch (error) {
      console.error('Registration error:', error);
      return { user: null, error: 'Registration failed' };
    }
  }

  async login(data: LoginData): Promise<{ user: UserProfile | null; error: string | null }> {
    try {
      // For MVP, we'll simulate login with mock user
      // In production, this would call the backend /api/v1/auth/login endpoint
      
      const userId = this.generateUserId();
      const user: UserProfile = {
        id: userId,
        email: data.email,
        name: data.email.split('@')[0], // Extract name from email for demo
        created_at: new Date().toISOString()
      };

      // Store auth token for API calls
      this.authToken = userId;
      this.currentUser = user;

      // Store in localStorage for persistence
      localStorage.setItem('authToken', userId);
      localStorage.setItem('currentUser', JSON.stringify(user));

      return { user, error: null };
    } catch (error) {
      console.error('Login error:', error);
      return { user: null, error: 'Login failed' };
    }
  }

  async logout(): Promise<{ error: string | null }> {
    try {
      // Clear stored auth data
      this.authToken = null;
      this.currentUser = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('currentUser');

      return { error: null };
    } catch (error) {
      console.error('Logout error:', error);
      return { error: 'Logout failed' };
    }
  }

  async getCurrentUser(): Promise<{ user: UserProfile | null; error: string | null }> {
    try {
      // Check if user is already loaded
      if (this.currentUser) {
        return { user: this.currentUser, error: null };
      }

      // Try to restore from localStorage
      const storedUser = localStorage.getItem('currentUser');
      const storedToken = localStorage.getItem('authToken');

      if (storedUser && storedToken) {
        this.currentUser = JSON.parse(storedUser);
        this.authToken = storedToken;
        return { user: this.currentUser, error: null };
      }

      return { user: null, error: 'No active session' };
    } catch (error) {
      console.error('Get current user error:', error);
      return { user: null, error: 'Failed to get current user' };
    }
  }

  async updateProfile(updates: Partial<UserProfile>): Promise<{ user: UserProfile | null; error: string | null }> {
    try {
      if (!this.currentUser) {
        return { user: null, error: 'No active session' };
      }

      // Update current user object
      this.currentUser = { ...this.currentUser, ...updates };
      
      // Store updated user in localStorage
      localStorage.setItem('currentUser', JSON.stringify(this.currentUser));

      return { user: this.currentUser, error: null };
    } catch (error) {
      console.error('Update profile error:', error);
      return { user: null, error: 'Failed to update profile' };
    }
  }

  // Get the auth token for API requests
  getAuthToken(): string | null {
    return this.authToken || localStorage.getItem('authToken');
  }

  // Auth state change handler (simplified for mock auth)
  onAuthStateChange(callback: (user: UserProfile | null) => void) {
    // Initial call with current user
    callback(this.currentUser);

    // Return an unsubscribe function
    return {
      data: {
        subscription: {
          unsubscribe: () => {
            // Mock unsubscribe
          }
        }
      }
    };
  }

  // OAuth methods (disabled for MVP)
  async signInWithGoogle(): Promise<{ error: string | null }> {
    return { error: 'OAuth not implemented in MVP' };
  }

  async signInWithGitHub(): Promise<{ error: string | null }> {
    return { error: 'OAuth not implemented in MVP' };
  }
}

export const authService = new AuthService(); 