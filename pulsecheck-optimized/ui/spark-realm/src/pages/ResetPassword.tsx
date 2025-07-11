import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { authService } from '../services/authService';

interface ResetPasswordState {
  password: string;
  confirmPassword: string;
  isLoading: boolean;
  error: string | null;
  success: string | null;
  showPassword: boolean;
  showConfirmPassword: boolean;
}

interface ValidationErrors {
  password?: string;
  confirmPassword?: string;
}

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<ResetPasswordState>({
    password: '',
    confirmPassword: '',
    isLoading: false,
    error: null,
    success: null,
    showPassword: false,
    showConfirmPassword: false
  });
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  useEffect(() => {
    // Check if we have the required tokens in the URL
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    
    if (!accessToken || !refreshToken) {
      setState(prev => ({ 
        ...prev, 
        error: 'Invalid reset link. Please request a new password reset.' 
      }));
    }
  }, [searchParams]);

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};

    // Password validation
    if (!state.password) {
      errors.password = 'Password is required';
    } else if (state.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    // Confirm password validation
    if (!state.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (state.password !== state.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null, success: null }));

    try {
      const { success, error } = await authService.updatePassword(state.password);

      if (error) {
        throw new Error(error);
      }

      if (success) {
        setState(prev => ({ 
          ...prev, 
          success: 'Password updated successfully! Redirecting to sign in...',
          error: null 
        }));
        
        // Redirect to auth page after success
        setTimeout(() => {
          navigate('/auth', { replace: true });
        }, 2000);
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to update password';
      setState(prev => ({ 
        ...prev, 
        error: errorMessage,
        success: null 
      }));
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            Reset Your Password
          </CardTitle>
          <CardDescription>
            Enter your new password below
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

          {/* Reset Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* New Password field */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-gray-700">
                New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="password"
                  type={state.showPassword ? 'text' : 'password'}
                  placeholder="Enter your new password"
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

            {/* Confirm Password field */}
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                Confirm New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="confirmPassword"
                  type={state.showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirm your new password"
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

            {/* Submit button */}
            <Button
              type="submit"
              className="w-full"
              disabled={state.isLoading}
            >
              {state.isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating Password...
                </>
              ) : (
                'Update Password'
              )}
            </Button>
          </form>

          {/* Back to sign in */}
          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/auth')}
              className="text-sm text-blue-600 hover:text-blue-500 focus:outline-none focus:underline"
              disabled={state.isLoading}
            >
              Back to Sign In
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 