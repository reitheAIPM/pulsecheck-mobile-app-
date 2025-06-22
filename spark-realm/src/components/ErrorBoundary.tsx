/**
 * AI-Optimized React Error Boundary for PulseCheck
 * 
 * This component catches React errors, provides detailed context for AI debugging,
 * and offers graceful fallback UI with recovery options.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { errorHandler, ErrorSeverity, ErrorCategory } from '../utils/errorHandler';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  showDetails?: boolean;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
  retryCount: number;
}

export class ErrorBoundary extends Component<Props, State> {
  private maxRetries = 3;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Enhanced error context for AI debugging
    const aiContext = {
      componentStack: errorInfo.componentStack,
      errorBoundary: true,
      retryCount: this.state.retryCount,
      props: this.sanitizeProps(this.props),
      timestamp: new Date().toISOString(),
      reactVersion: React.version,
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Log error with AI-optimized context
    const errorId = errorHandler.handleError(
      error,
      ErrorSeverity.HIGH,
      ErrorCategory.COMPONENT,
      aiContext
    );

    // Dispatch custom event for global error tracking
    window.dispatchEvent(new CustomEvent('react-error', {
      detail: { error, errorInfo, errorId }
    }));

    // Update state with error details
    this.setState({
      errorInfo,
      errorId,
      retryCount: this.state.retryCount + 1
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log comprehensive error details to console
    console.group('🚨 React Error Boundary - AI Debug Info');
    console.error('Error:', error);
    console.error('Error Info:', errorInfo);
    console.log('Error ID:', errorId);
    console.log('AI Context:', aiContext);
    console.log('Component Props:', this.sanitizeProps(this.props));
    console.groupEnd();
  }

  private sanitizeProps(props: Props): Record<string, any> {
    // Remove sensitive data and functions for logging
    const sanitized: Record<string, any> = {};
    
    Object.entries(props).forEach(([key, value]) => {
      if (typeof value === 'function') {
        sanitized[key] = '[Function]';
      } else if (key.toLowerCase().includes('password') || 
                 key.toLowerCase().includes('token') ||
                 key.toLowerCase().includes('secret')) {
        sanitized[key] = '[REDACTED]';
      } else if (value && typeof value === 'object') {
        sanitized[key] = '[Object]';
      } else {
        sanitized[key] = value;
      }
    });

    return sanitized;
  }

  private handleRetry = () => {
    if (this.state.retryCount < this.maxRetries) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null
      });
    }
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private copyErrorDetails = () => {
    const errorDetails = {
      errorId: this.state.errorId,
      error: {
        name: this.state.error?.name,
        message: this.state.error?.message,
        stack: this.state.error?.stack
      },
      componentStack: this.state.errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      retryCount: this.state.retryCount,
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      .then(() => {
        console.log('Error details copied to clipboard');
      })
      .catch((err) => {
        console.error('Failed to copy error details:', err);
      });
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default AI-optimized error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <CardTitle className="text-2xl font-bold text-gray-900">
                Something went wrong
              </CardTitle>
              <CardDescription className="text-lg">
                We encountered an unexpected error. Our team has been notified.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Error ID for support */}
              {this.state.errorId && (
                <div className="bg-gray-100 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Error ID</p>
                      <p className="text-xs text-gray-500 font-mono">
                        {this.state.errorId}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      For Support
                    </Badge>
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                {this.state.retryCount < this.maxRetries && (
                  <Button 
                    onClick={this.handleRetry}
                    className="flex-1"
                    variant="default"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again ({this.maxRetries - this.state.retryCount} left)
                  </Button>
                )}
                
                <Button 
                  onClick={this.handleGoHome}
                  className="flex-1"
                  variant="outline"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </Button>
                
                <Button 
                  onClick={this.handleReload}
                  className="flex-1"
                  variant="outline"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reload Page
                </Button>
              </div>

              {/* Debug information (only in development or if showDetails is true) */}
              {(process.env.NODE_ENV === 'development' || this.props.showDetails) && (
                <details className="bg-gray-100 p-4 rounded-lg">
                  <summary className="cursor-pointer font-medium text-gray-700 mb-2">
                    <Bug className="w-4 h-4 inline mr-2" />
                    Debug Information
                  </summary>
                  
                  <div className="space-y-4 mt-4">
                    {this.state.error && (
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Error Details</h4>
                        <div className="bg-white p-3 rounded border text-xs font-mono">
                          <p><strong>Type:</strong> {this.state.error.name}</p>
                          <p><strong>Message:</strong> {this.state.error.message}</p>
                          {this.state.error.stack && (
                            <div className="mt-2">
                              <strong>Stack Trace:</strong>
                              <pre className="whitespace-pre-wrap text-xs mt-1 text-gray-600">
                                {this.state.error.stack}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {this.state.errorInfo?.componentStack && (
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Component Stack</h4>
                        <div className="bg-white p-3 rounded border">
                          <pre className="whitespace-pre-wrap text-xs text-gray-600">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button 
                        onClick={this.copyErrorDetails}
                        size="sm"
                        variant="outline"
                      >
                        Copy Error Details
                      </Button>
                    </div>
                  </div>
                </details>
              )}

              {/* AI-optimized user guidance */}
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-900 mb-2">What can you do?</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Try refreshing the page or going back to the home screen</li>
                  <li>• Check your internet connection</li>
                  <li>• Clear your browser cache if the problem persists</li>
                  <li>• Contact support with the Error ID if you continue to have issues</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for wrapping components with error boundary
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

// Hook for triggering error boundary from child components
export const useErrorBoundary = () => {
  const [, setState] = React.useState();
  
  return React.useCallback((error: Error) => {
    setState(() => {
      throw error;
    });
  }, []);
}; 