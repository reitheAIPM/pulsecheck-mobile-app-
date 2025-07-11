/**
 * AI-Optimized Error Handling System for PulseCheck Frontend
 * 
 * This module provides comprehensive error handling, logging, and recovery mechanisms
 * designed specifically for AI-assisted debugging and problem resolution.
 */

import { apiService } from '../services/api';

// Error severity levels for AI classification
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// Error categories for AI pattern recognition
export enum ErrorCategory {
  NETWORK = 'network',
  API = 'api',
  COMPONENT = 'component',
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  BUSINESS_LOGIC = 'business_logic',
  PERFORMANCE = 'performance',
  UNKNOWN = 'unknown'
}

// AI-optimized error context interface
export interface AIErrorContext {
  errorId: string;
  timestamp: string;
  userAgent: string;
  url: string;
  userId?: string;
  sessionId?: string;
  componentStack?: string;
  userActions: string[];
  systemState: Record<string, any>;
  networkStatus: string;
  memoryUsage?: number;
  performanceMetrics?: Record<string, number>;
}

// Error details for AI analysis
export interface ErrorDetails {
  message: string;
  stack?: string;
  name: string;
  severity: ErrorSeverity;
  category: ErrorCategory;
  context: AIErrorContext;
  recoveryAttempts: number;
  isRecoverable: boolean;
  suggestedActions: string[];
  aiDebuggingHints: string[];
}

// Global error tracking for AI analysis
class AIOptimizedErrorHandler {
  private errors: ErrorDetails[] = [];
  private userActions: string[] = [];
  private maxErrors = 100;
  private maxUserActions = 50;
  private sessionId: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.setupGlobalErrorHandlers();
    this.trackUserActions();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private setupGlobalErrorHandlers(): void {
    // Global JavaScript error handler
    window.addEventListener('error', (event) => {
      this.handleError(
        new Error(event.message),
        ErrorSeverity.HIGH,
        ErrorCategory.UNKNOWN,
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          source: 'global_error_handler'
        }
      );
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(
        new Error(`Unhandled Promise Rejection: ${event.reason}`),
        ErrorSeverity.HIGH,
        ErrorCategory.UNKNOWN,
        {
          reason: event.reason,
          source: 'unhandled_promise_rejection'
        }
      );
    });

    // React error boundary integration
    window.addEventListener('react-error', (event: any) => {
      this.handleError(
        event.detail.error,
        ErrorSeverity.HIGH,
        ErrorCategory.COMPONENT,
        {
          componentStack: event.detail.errorInfo?.componentStack,
          source: 'react_error_boundary'
        }
      );
    });
  }

  private trackUserActions(): void {
    // Track clicks
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      const action = `click:${target.tagName}:${target.className}:${target.textContent?.slice(0, 50)}`;
      this.addUserAction(action);
    });

    // Track navigation
    window.addEventListener('popstate', () => {
      this.addUserAction(`navigation:${window.location.pathname}`);
    });

    // Track form submissions
    document.addEventListener('submit', (event) => {
      const form = event.target as HTMLFormElement;
      this.addUserAction(`form_submit:${form.id || form.className}`);
    });
  }

  private addUserAction(action: string): void {
    this.userActions.push(`${new Date().toISOString()}: ${action}`);
    if (this.userActions.length > this.maxUserActions) {
      this.userActions.shift();
    }
  }

  private getSystemState(): Record<string, any> {
    return {
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      connection: (navigator as any).connection ? {
        effectiveType: (navigator as any).connection.effectiveType,
        downlink: (navigator as any).connection.downlink,
        rtt: (navigator as any).connection.rtt
      } : 'unknown',
      memory: (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
        jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
      } : 'unknown',
      localStorage: {
        available: this.isLocalStorageAvailable(),
        usage: this.getLocalStorageUsage()
      },
      cookies: {
        enabled: navigator.cookieEnabled
      }
    };
  }

  private isLocalStorageAvailable(): boolean {
    try {
      const test = 'test';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }

  private getLocalStorageUsage(): number {
    if (!this.isLocalStorageAvailable()) return 0;
    
    let total = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        total += localStorage[key].length + key.length;
      }
    }
    return total;
  }

  private categorizeError(error: Error, context?: Record<string, any>): ErrorCategory {
    const message = error.message.toLowerCase();
    const stack = error.stack?.toLowerCase() || '';

    if (message.includes('network') || message.includes('fetch') || message.includes('cors')) {
      return ErrorCategory.NETWORK;
    }
    if (message.includes('api') || message.includes('http') || context?.source === 'api_call') {
      return ErrorCategory.API;
    }
    if (message.includes('component') || message.includes('render') || stack.includes('react')) {
      return ErrorCategory.COMPONENT;
    }
    if (message.includes('validation') || message.includes('invalid') || message.includes('required')) {
      return ErrorCategory.VALIDATION;
    }
    if (message.includes('auth') || message.includes('token') || message.includes('permission')) {
      return ErrorCategory.AUTHENTICATION;
    }
    if (message.includes('performance') || message.includes('memory') || message.includes('timeout')) {
      return ErrorCategory.PERFORMANCE;
    }
    
    return ErrorCategory.UNKNOWN;
  }

  private getSuggestedActions(error: Error, category: ErrorCategory): string[] {
    const actions: string[] = [];

    switch (category) {
      case ErrorCategory.NETWORK:
        actions.push(
          'Check internet connection',
          'Verify API endpoint URL',
          'Check for CORS issues',
          'Retry the request',
          'Use fallback data if available'
        );
        break;
      
      case ErrorCategory.API:
        actions.push(
          'Check API server status',
          'Verify request parameters',
          'Check authentication tokens',
          'Review API response format',
          'Implement retry logic'
        );
        break;
      
      case ErrorCategory.COMPONENT:
        actions.push(
          'Check component props',
          'Verify data types',
          'Add null checks',
          'Review component lifecycle',
          'Check for memory leaks'
        );
        break;
      
      case ErrorCategory.VALIDATION:
        actions.push(
          'Verify input data format',
          'Check validation rules',
          'Add proper error messages',
          'Review form constraints',
          'Implement client-side validation'
        );
        break;
      
      default:
        actions.push(
          'Check browser console for details',
          'Review recent code changes',
          'Check for browser compatibility',
          'Clear browser cache',
          'Try in incognito mode'
        );
    }

    return actions;
  }

  private getAIDebuggingHints(error: Error, category: ErrorCategory): string[] {
    const hints: string[] = [];

    // General AI debugging hints
    hints.push(
      'Check error frequency and patterns',
      'Review user actions leading to error',
      'Analyze system state at time of error',
      'Compare with similar errors in logs'
    );

    // Category-specific hints
    switch (category) {
      case ErrorCategory.NETWORK:
        hints.push(
          'Check network conditions and connectivity',
          'Verify API endpoint accessibility',
          'Review CORS configuration',
          'Check for rate limiting'
        );
        break;
      
      case ErrorCategory.API:
        hints.push(
          'Verify API key and authentication',
          'Check request/response format',
          'Review API version compatibility',
          'Analyze response status codes'
        );
        break;
      
      case ErrorCategory.COMPONENT:
        hints.push(
          'Review React component lifecycle',
          'Check for state management issues',
          'Verify prop types and validation',
          'Look for rendering optimization opportunities'
        );
        break;
    }

    return hints;
  }

  public handleError(
    error: Error,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category?: ErrorCategory,
    additionalContext?: Record<string, any>
  ): string {
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const detectedCategory = category || this.categorizeError(error, additionalContext);

    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      name: error.name,
      severity,
      category: detectedCategory,
      context: {
        errorId,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: this.sessionId,
        userActions: [...this.userActions],
        systemState: this.getSystemState(),
        networkStatus: navigator.onLine ? 'online' : 'offline',
        ...additionalContext
      },
      recoveryAttempts: 0,
      isRecoverable: this.isRecoverableError(error, detectedCategory),
      suggestedActions: this.getSuggestedActions(error, detectedCategory),
      aiDebuggingHints: this.getAIDebuggingHints(error, detectedCategory)
    };

    // Add to error list
    this.errors.push(errorDetails);
    if (this.errors.length > this.maxErrors) {
      this.errors.shift();
    }

    // Log to console with AI-optimized format
    console.group(`🚨 AI-Optimized Error [${errorId}]`);
    console.error('Error Details:', errorDetails);
    console.log('Suggested Actions:', errorDetails.suggestedActions);
    console.log('AI Debugging Hints:', errorDetails.aiDebuggingHints);
    console.log('System State:', errorDetails.context.systemState);
    console.log('User Actions:', errorDetails.context.userActions.slice(-10));
    console.groupEnd();

    // Send to backend monitoring (if available)
    this.sendToBackendMonitoring(errorDetails).catch(console.error);

    // Show user-friendly error message
    this.showUserErrorMessage(errorDetails);

    return errorId;
  }

  private isRecoverableError(error: Error, category: ErrorCategory): boolean {
    // Network errors are usually recoverable
    if (category === ErrorCategory.NETWORK) return true;
    
    // API errors might be recoverable
    if (category === ErrorCategory.API) return true;
    
    // Validation errors are recoverable
    if (category === ErrorCategory.VALIDATION) return true;
    
    // Component errors are usually not recoverable
    if (category === ErrorCategory.COMPONENT) return false;
    
    // Authentication errors require user action
    if (category === ErrorCategory.AUTHENTICATION) return false;
    
    return false;
  }

  private async sendToBackendMonitoring(errorDetails: ErrorDetails): Promise<void> {
    try {
      await fetch('/api/v1/monitoring/frontend-error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          error_id: errorDetails.context.errorId,
          error_type: errorDetails.name,
          error_message: errorDetails.message,
          severity: errorDetails.severity,
          category: errorDetails.category,
          stack_trace: errorDetails.stack,
          context: errorDetails.context,
          suggested_actions: errorDetails.suggestedActions,
          ai_debugging_hints: errorDetails.aiDebuggingHints
        })
      });
    } catch (monitoringError) {
      console.warn('Failed to send error to backend monitoring:', monitoringError);
    }
  }

  private showUserErrorMessage(errorDetails: ErrorDetails): void {
    // Only show user messages for certain error types
    if (errorDetails.severity === ErrorSeverity.CRITICAL || 
        errorDetails.category === ErrorCategory.NETWORK ||
        errorDetails.category === ErrorCategory.API) {
      
      // Create user-friendly message
      let userMessage = 'Something went wrong. ';
      
      if (errorDetails.category === ErrorCategory.NETWORK) {
        userMessage += 'Please check your internet connection and try again.';
      } else if (errorDetails.category === ErrorCategory.API) {
        userMessage += 'We\'re having trouble connecting to our servers. Please try again in a moment.';
      } else {
        userMessage += 'Please refresh the page or try again.';
      }

      // Show toast notification (you can integrate with your toast system)
      console.warn('User Message:', userMessage);
      
      // You can integrate with a toast notification system here
      // toast.error(userMessage);
    }
  }

  public getErrorSummary(): Record<string, any> {
    const summary = {
      total_errors: this.errors.length,
      errors_by_severity: {} as Record<string, number>,
      errors_by_category: {} as Record<string, number>,
      recent_errors: this.errors.slice(-10),
      session_id: this.sessionId,
      ai_analysis: {
        most_common_category: '',
        recurring_errors: [] as string[],
        suggested_improvements: [] as string[]
      }
    };

    // Count by severity
    this.errors.forEach(error => {
      summary.errors_by_severity[error.severity] = 
        (summary.errors_by_severity[error.severity] || 0) + 1;
    });

    // Count by category
    this.errors.forEach(error => {
      summary.errors_by_category[error.category] = 
        (summary.errors_by_category[error.category] || 0) + 1;
    });

    // Find most common category
    const categories = Object.entries(summary.errors_by_category);
    if (categories.length > 0) {
      summary.ai_analysis.most_common_category = categories
        .sort(([,a], [,b]) => b - a)[0][0];
    }

    // Find recurring errors
    const errorMessages = this.errors.map(e => e.message);
    const messageCounts: Record<string, number> = {};
    errorMessages.forEach(msg => {
      messageCounts[msg] = (messageCounts[msg] || 0) + 1;
    });
    
    summary.ai_analysis.recurring_errors = Object.entries(messageCounts)
      .filter(([, count]) => count > 1)
      .map(([message]) => message);

    return summary;
  }

  public exportErrorData(): string {
    return JSON.stringify({
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      errors: this.errors,
      user_actions: this.userActions,
      summary: this.getErrorSummary()
    }, null, 2);
  }
}

// Global error handler instance
export const errorHandler = new AIOptimizedErrorHandler();

// Convenience functions for different error types
export const handleNetworkError = (error: Error, context?: Record<string, any>) => 
  errorHandler.handleError(error, ErrorSeverity.HIGH, ErrorCategory.NETWORK, context);

export const handleAPIError = (error: Error, context?: Record<string, any>) => 
  errorHandler.handleError(error, ErrorSeverity.HIGH, ErrorCategory.API, context);

export const handleComponentError = (error: Error, context?: Record<string, any>) => 
  errorHandler.handleError(error, ErrorSeverity.MEDIUM, ErrorCategory.COMPONENT, context);

export const handleValidationError = (error: Error, context?: Record<string, any>) => 
  errorHandler.handleError(error, ErrorSeverity.LOW, ErrorCategory.VALIDATION, context);

// React hook for error handling
export const useErrorHandler = () => {
  const handleError = (error: Error, severity?: ErrorSeverity, category?: ErrorCategory) => {
    return errorHandler.handleError(error, severity, category, {
      source: 'react_hook'
    });
  };

  const getErrorSummary = () => errorHandler.getErrorSummary();
  const exportErrors = () => errorHandler.exportErrorData();

  return { handleError, getErrorSummary, exportErrors };
}; 