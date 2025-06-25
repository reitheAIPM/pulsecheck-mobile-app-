import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, AlertCircle, CheckCircle, Loader2, Github, Chrome, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { authService } from '../services/authService';
import { errorHandler, ErrorSeverity, ErrorCategory } from '../utils/errorHandler';

interface AuthState {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
  isLoading: boolean;
  error: string | null;
  success: string | null;
  showPassword: boolean;
  showConfirmPassword: boolean;
}

interface ValidationErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  name?: string;
}

type AuthMode = 'login' | 'register' | 'forgot-password' | 'reset-password';

export default function Auth() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<AuthMode>('login');
  const [state, setState] = useState<AuthState>({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    isLoading: false,
    error: null,
    success: null,
    showPassword: false,
    showConfirmPassword: false
  });
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [debugInfo, setDebugInfo] = useState<any>(null);

  // Check if this is a password reset redirect
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    
    if (resetToken && refreshToken) {
      setMode('reset-password');
    }
  }, []);

  // Check if user is already authenticated
  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('🔍 Checking authentication status...');
        const { user: currentUser, error } = await authService.getCurrentUser();
        if (currentUser) {
          console.log('✅ User already authenticated:', currentUser.id);
          // Don't manually navigate - App.tsx auth state will handle this
          return;
        }
        console.log('ℹ️ No authenticated user found');
      } catch (error) {
        console.log('ℹ️ Auth check completed - no authenticated user (expected)');
        // Don't show this as an error - this is expected for unauthenticated users
      }
    };

    checkAuth();
  }, []);

  // Simplified connectivity check using our own backend
  useEffect(() => {
    const checkConnectivity = async () => {
      try {
        console.log('🌐 Testing network connectivity...');
        // Use GET instead of HEAD - the health endpoint doesn't support HEAD requests
        const response = await fetch('https://pulsecheck-mobile-app-production.up.railway.app/health', { 
          method: 'GET',
          cache: 'no-cache'
        });
        if (response.ok) {
          console.log('✅ Network connectivity OK');
        } else {
          throw new Error('Backend health check failed');
        }
      } catch (error) {
        console.error('❌ Network connectivity issue:', error);
        setState(prev => ({ 
          ...prev, 
          error: 'Unable to connect to PulseCheck servers. Please check your internet connection.' 
        }));
      }
    };

    checkConnectivity();
  }, []);

  // AI Debug: Log authentication attempts and errors
  const logAuthEvent = (event: string, data: any, isError: boolean = false) => {
    const debugContext = {
      event,
      timestamp: new Date().toISOString(),
      isLogin: mode === 'login',
      userAgent: navigator.userAgent,
      url: window.location.href,
      formData: {
        email: state.email,
        hasPassword: !!state.password,
        hasName: !!state.name
      },
      ...data
    };

    if (isError) {
      errorHandler.handleError(
        new Error(`Auth ${event}: ${JSON.stringify(data)}`),
        ErrorSeverity.MEDIUM,
        ErrorCategory.AUTHENTICATION,
        debugContext
      );
    } else {
      console.log(`Auth Event: ${event}`, debugContext);
    }

    setDebugInfo(debugContext);
  };

  // Form validation
  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};

    // Email validation
    if (!state.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!state.password) {
      errors.password = 'Password is required';
    } else if (state.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    // Registration-specific validation
    if (mode === 'register') {
      if (!state.name) {
        errors.name = 'Name is required';
      }

      if (!state.confirmPassword) {
        errors.confirmPassword = 'Please confirm your password';
      } else if (state.password !== state.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    }

    // Password validation not needed for forgot password
    if (mode === 'forgot-password') {
      delete errors.password;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      logAuthEvent('validation_failed', validationErrors, true);
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null, success: null }));

    try {
      if (mode === 'login') {
        // Login flow
        logAuthEvent('login_attempt', { email: state.email });
        
        const { user, error } = await authService.login({ email: state.email, password: state.password });

        if (error) {
          throw new Error(error);
        }

        if (user) {
          logAuthEvent('login_success', { userId: user.id });
          setState(prev => ({ 
            ...prev, 
            success: 'Login successful! Redirecting...',
            error: null 
          }));
          
          // Auth state change will handle navigation automatically
          // No manual navigation needed
        }
               } else if (mode === 'register') {
        // Registration flow
        logAuthEvent('registration_attempt', { email: state.email, name: state.name });
        
        const { user, session, needsEmailConfirmation, error } = await authService.register({
          email: state.email,
          password: state.password,
          name: state.name
        });

        if (error) {
          throw new Error(error);
        }

        if (user) {
          logAuthEvent('registration_success', { userId: user.id, hasSession: !!session });
          
          if (needsEmailConfirmation) {
            setState(prev => ({ 
              ...prev, 
              success: 'Account created! Please check your email to confirm your account before signing in.',
              error: null 
            }));
          } else if (session) {
            setState(prev => ({ 
              ...prev, 
              success: 'Account created successfully! Welcome to PulseCheck.',
              error: null 
            }));
            
            // Auth state change will handle navigation automatically
            // No manual navigation needed
          } else {
            setState(prev => ({ 
              ...prev, 
              success: 'Account created! You can now sign in with your credentials.',
              error: null 
            }));
          }
        }
      } else if (mode === 'forgot-password') {
        // Forgot password flow
        logAuthEvent('forgot_password_attempt', { email: state.email });
        
                 const { success, error } = await authService.resetPassword(state.email);

         if (error) {
           throw new Error(error);
         }

         if (success) {
           logAuthEvent('forgot_password_success', { email: state.email });
           setState(prev => ({ 
             ...prev, 
             success: 'Password reset email sent! Please check your email for instructions.',
             error: null 
           }));
         }
       } else if (mode === 'reset-password') {
         // Reset password flow
         logAuthEvent('reset_password_attempt', { password: '***' });
         
         const { success, error } = await authService.updatePassword(state.password);

        if (error) {
          throw new Error(error);
        }

        if (success) {
          logAuthEvent('reset_password_success', { email: state.email });
          setState(prev => ({ 
            ...prev, 
            success: 'Password reset successful! You can now sign in with your new password.',
            error: null 
          }));
        }
      }
    } catch (error: any) {
      const errorMessage = error.message || 'An unexpected error occurred';
      logAuthEvent('auth_error', { error: errorMessage }, true);
      setState(prev => ({ 
        ...prev, 
        error: errorMessage,
        success: null 
      }));
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  // Toggle between login and registration
  const toggleMode = () => {
    setMode(prevMode => {
      const newMode = prevMode === 'login' ? 'register' : 'login';
      setState(prev => ({
        ...prev,
        error: null,
        success: null,
        password: '',
        confirmPassword: '',
        name: ''
      }));
      setValidationErrors({});
      logAuthEvent('mode_toggle', { newMode });
      return newMode;
    });
  };

  // Handle OAuth (placeholder for future implementation)
  const handleOAuth = (provider: string) => {
    logAuthEvent('oauth_attempt', { provider });
    setState(prev => ({ 
      ...prev, 
      error: `${provider} login coming soon! Currently in development.` 
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            {mode === 'login' ? 'Welcome Back' : mode === 'register' ? 'Create Account' : mode === 'forgot-password' ? 'Forgot Password' : 'Reset Password'}
          </CardTitle>
          <CardDescription>
            {mode === 'login' ? 'Sign in to your PulseCheck account' : mode === 'register' ? 'Join PulseCheck to start your wellness journey' : mode === 'forgot-password' ? 'Forgot Password' : 'Reset Password'}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Success/Error Messages */}
          {state.error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{state.error}</AlertDescription>
            </Alert>
          )}

          {state.success && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{state.success}</AlertDescription>
            </Alert>
          )}

          {/* Authentication Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name field (registration only) */}
            {mode === 'register' && (
              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={state.name}
                    onChange={(e) => setState(prev => ({ ...prev, name: e.target.value }))}
                    className={`pl-10 ${validationErrors.name ? 'border-red-500' : ''}`}
                    disabled={state.isLoading}
                  />
                </div>
                {validationErrors.name && (
                  <p className="text-sm text-red-600">{validationErrors.name}</p>
                )}
              </div>
            )}

            {/* Email field */}
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={state.email}
                  onChange={(e) => setState(prev => ({ ...prev, email: e.target.value }))}
                  className={`pl-10 ${validationErrors.email ? 'border-red-500' : ''}`}
                  disabled={state.isLoading}
                />
              </div>
              {validationErrors.email && (
                <p className="text-sm text-red-600">{validationErrors.email}</p>
              )}
            </div>

            {/* Password field (not shown for forgot password) */}
            {mode !== 'forgot-password' && (
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  {mode === 'reset-password' ? 'New Password' : 'Password'}
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type={state.showPassword ? 'text' : 'password'}
                    placeholder={mode === 'reset-password' ? 'Enter your new password' : 'Enter your password'}
                    value={state.password}
                    onChange={(e) => setState(prev => ({ ...prev, password: e.target.value }))}
                    className={`pl-10 pr-10 ${validationErrors.password ? 'border-red-500' : ''}`}
                    disabled={state.isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setState(prev => ({ ...prev, showPassword: !prev.showPassword }))}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                    disabled={state.isLoading}
                  >
                    {state.showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {validationErrors.password && (
                  <p className="text-sm text-red-600">{validationErrors.password}</p>
                )}
              </div>
            )}

            {/* Confirm Password field (registration only) */}
            {mode === 'register' && (
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type={state.showConfirmPassword ? 'text' : 'password'}
                    placeholder="Confirm your password"
                    value={state.confirmPassword}
                    onChange={(e) => setState(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className={`pl-10 pr-10 ${validationErrors.confirmPassword ? 'border-red-500' : ''}`}
                    disabled={state.isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setState(prev => ({ ...prev, showConfirmPassword: !prev.showConfirmPassword }))}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                    disabled={state.isLoading}
                  >
                    {state.showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {validationErrors.confirmPassword && (
                  <p className="text-sm text-red-600">{validationErrors.confirmPassword}</p>
                )}
              </div>
            )}

            {/* Submit button */}
            <Button
              type="submit"
              className="w-full"
              disabled={state.isLoading}
            >
              {state.isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {mode === 'login' ? 'Signing In...' : mode === 'register' ? 'Creating Account...' : mode === 'forgot-password' ? 'Sending Reset Email...' : 'Resetting Password...'}
                </>
              ) : (
                mode === 'login' ? 'Sign In' : mode === 'register' ? 'Create Account' : mode === 'forgot-password' ? 'Send Reset Email' : 'Reset Password'
              )}
            </Button>
          </form>

          {/* OAuth Section (Future Implementation) */}
          <div className="space-y-4">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-muted-foreground">Or continue with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                onClick={() => handleOAuth('Google')}
                disabled={state.isLoading}
                className="relative"
              >
                <Chrome className="mr-2 h-4 w-4" />
                Google
                <Badge variant="secondary" className="absolute -top-2 -right-2 text-xs">
                  Soon
                </Badge>
              </Button>
              <Button
                variant="outline"
                onClick={() => handleOAuth('GitHub')}
                disabled={state.isLoading}
                className="relative"
              >
                <Github className="mr-2 h-4 w-4" />
                GitHub
                <Badge variant="secondary" className="absolute -top-2 -right-2 text-xs">
                  Soon
                </Badge>
              </Button>
            </div>
          </div>

          {/* Forgot password link (only on login) */}
          {mode === 'login' && (
            <div className="text-center">
              <button
                type="button"
                onClick={() => setMode('forgot-password')}
                className="text-sm text-blue-600 hover:text-blue-500 focus:outline-none focus:underline"
                disabled={state.isLoading}
              >
                Forgot your password?
              </button>
            </div>
          )}

          {/* Toggle between modes */}
          <div className="text-center">
            {mode === 'forgot-password' || mode === 'reset-password' ? (
              <button
                type="button"
                onClick={() => setMode('login')}
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-500 focus:outline-none focus:underline"
                disabled={state.isLoading}
              >
                <ArrowLeft className="mr-1 h-4 w-4" />
                Back to Sign In
              </button>
            ) : (
              <button
                type="button"
                onClick={toggleMode}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                disabled={state.isLoading}
              >
                {mode === 'login' ? (
                  "Don't have an account? Sign up"
                ) : (
                  'Already have an account? Sign in'
                )}
              </button>
            )}
          </div>

          {/* Debug Information (Development Mode) */}
          {process.env.NODE_ENV === 'development' && debugInfo && (
            <details className="bg-gray-100 p-3 rounded-lg text-xs">
              <summary className="cursor-pointer font-medium text-gray-700">
                🐛 AI Debug Info
              </summary>
              <pre className="mt-2 text-gray-600 overflow-auto">
                {JSON.stringify(debugInfo, null, 2)}
              </pre>
            </details>
          )}

          {/* Future Expansion Note */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-900 text-sm mb-2">🚀 Future Enhancements</h4>
            <ul className="text-xs text-blue-800 space-y-1">
              <li>• OAuth integration (Google, GitHub, Microsoft)</li>
              <li>• Two-factor authentication</li>
              <li>• Password reset functionality</li>
              <li>• Profile completion flow</li>
              <li>• Enterprise SSO support</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
