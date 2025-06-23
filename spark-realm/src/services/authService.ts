import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://qwpwlubxhtuzvmvajjjr.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3cHdsdWJ4aHR1enZtdmFqampyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU2Nzk1NzksImV4cCI6MjA1MTI1NTU3OX0.bEXYwXp5CjOJ_JBYoF9-jdZPE4-RSwDFzSR0_5YRyTQ'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export interface UserProfile {
  id: string
  email: string
  name: string
  tech_role?: string
  company?: string
  created_at: string
}

export interface RegistrationData {
  email: string
  password: string
  name: string
  tech_role?: string
  company?: string
}

export interface LoginData {
  email: string
  password: string
}

class AuthService {
  
  async register(data: RegistrationData): Promise<{ user: UserProfile; error: string | null }> {
    try {
      // Register with Supabase Auth
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
        options: {
          data: {
            name: data.name,
            tech_role: data.tech_role,
            company: data.company
          }
        }
      })

      if (authError) {
        return { user: null as any, error: authError.message }
      }

      if (!authData.user) {
        return { user: null as any, error: 'Registration failed' }
      }

      // The profile will be created automatically by the database trigger
      const profile: UserProfile = {
        id: authData.user.id,
        email: authData.user.email!,
        name: data.name,
        tech_role: data.tech_role,
        company: data.company,
        created_at: authData.user.created_at
      }

      return { user: profile, error: null }
    } catch (error) {
      console.error('Registration error:', error)
      return { user: null as any, error: 'Registration failed' }
    }
  }

  async login(data: LoginData): Promise<{ user: UserProfile; error: string | null }> {
    try {
      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password
      })

      if (authError) {
        return { user: null as any, error: authError.message }
      }

      if (!authData.user) {
        return { user: null as any, error: 'Login failed' }
      }

      // Get user profile from database
      const { data: profileData, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', authData.user.id)
        .single()

      if (profileError || !profileData) {
        // If profile doesn't exist, create it (fallback)
        const profile: UserProfile = {
          id: authData.user.id,
          email: authData.user.email!,
          name: authData.user.user_metadata?.name || 'User',
          tech_role: authData.user.user_metadata?.tech_role,
          company: authData.user.user_metadata?.company,
          created_at: authData.user.created_at
        }
        return { user: profile, error: null }
      }

      return { user: profileData as UserProfile, error: null }
    } catch (error) {
      console.error('Login error:', error)
      return { user: null as any, error: 'Login failed' }
    }
  }

  async logout(): Promise<{ error: string | null }> {
    try {
      const { error } = await supabase.auth.signOut()
      return { error: error?.message || null }
    } catch (error) {
      console.error('Logout error:', error)
      return { error: 'Logout failed' }
    }
  }

  async getCurrentUser(): Promise<{ user: UserProfile | null; error: string | null }> {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      
      if (sessionError || !session?.user) {
        return { user: null, error: sessionError?.message || 'No active session' }
      }

      // Get user profile from database
      const { data: profileData, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', session.user.id)
        .single()

      if (profileError || !profileData) {
        // Fallback to auth user data
        const profile: UserProfile = {
          id: session.user.id,
          email: session.user.email!,
          name: session.user.user_metadata?.name || 'User',
          tech_role: session.user.user_metadata?.tech_role,
          company: session.user.user_metadata?.company,
          created_at: session.user.created_at
        }
        return { user: profile, error: null }
      }

      return { user: profileData as UserProfile, error: null }
    } catch (error) {
      console.error('Get current user error:', error)
      return { user: null, error: 'Failed to get current user' }
    }
  }

  async updateProfile(updates: Partial<UserProfile>): Promise<{ user: UserProfile | null; error: string | null }> {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.user) {
        return { user: null, error: 'No active session' }
      }

      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', session.user.id)
        .select()
        .single()

      if (error) {
        return { user: null, error: error.message }
      }

      return { user: data as UserProfile, error: null }
    } catch (error) {
      console.error('Update profile error:', error)
      return { user: null, error: 'Failed to update profile' }
    }
  }

  onAuthStateChange(callback: (user: UserProfile | null) => void) {
    return supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        const { user } = await this.getCurrentUser()
        callback(user)
      } else {
        callback(null)
      }
    })
  }

  // OAuth methods for future expansion
  async signInWithGoogle(): Promise<{ error: string | null }> {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin
      }
    })
    return { error: error?.message || null }
  }

  async signInWithGitHub(): Promise<{ error: string | null }> {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: {
        redirectTo: window.location.origin
      }
    })
    return { error: error?.message || null }
  }
}

export const authService = new AuthService() 