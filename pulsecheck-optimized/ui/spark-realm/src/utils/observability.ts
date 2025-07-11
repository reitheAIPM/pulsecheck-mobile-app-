/**
 * Frontend Observability System for PulseCheck
 * AI-optimized error tracking and performance monitoring
 * 
 * Features:
 * - Request correlation with backend
 * - Error boundary integration
 * - Performance monitoring
 * - User journey tracking
 * - AI-friendly error context
 */

import * as Sentry from '@sentry/react';

interface RequestContext {
  requestId: string;
  timestamp: number;
  operation: string;
  endpoint?: string;
  method?: string;
}

interface ErrorContext {
  requestId: string;
  userAgent: string;
  url: string;
  timestamp: number;
  userJourney: string[];
  performanceMetrics: {
    loadTime: number;
    networkLatency: number;
    renderTime: number;
  };
}

class FrontendObservability {
  private requestId: string | null = null;
  private userJourney: string[] = [];
  private performanceBaselines: Record<string, number[]> = {};

  constructor() {
    this.initializeSentry();
    this.setupPerformanceMonitoring();
    this.setupErrorBoundary();
  }

  private initializeSentry() {
    Sentry.init({
      dsn: process.env.REACT_APP_SENTRY_DSN,
      environment: process.env.NODE_ENV,
      integrations: [
        new Sentry.BrowserTracing({
          tracePropagationTargets: [/^https:\/\/pulsecheck-mobile-app-production\.up\.railway\.app\/api/],
        }),
      ],
      tracesSampleRate: process.env.NODE_ENV === 'development' ? 1.0 : 0.1,
    });

    // Add custom tags for AI debugging
    Sentry.setTag('component', 'pulsecheck-frontend');
    Sentry.setTag('ai_debugging', 'enabled');
  }

  private setupPerformanceMonitoring() {
    // Monitor navigation timing
    if ('performance' in window) {
      window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        this.trackPerformance('page_load', perfData.loadEventEnd - perfData.fetchStart);
      });
    }
  }

  private setupErrorBoundary() {
    // Global error handler for unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.captureError(new Error(event.reason), {
        type: 'unhandled_promise_rejection',
        promise: event.promise,
      });
    });

    // Global error handler for JavaScript errors
    window.addEventListener('error', (event) => {
      this.captureError(event.error, {
        type: 'javascript_error',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });
  }

  public generateRequestId(): string {
    this.requestId = crypto.randomUUID();
    return this.requestId;
  }

  public getCurrentRequestId(): string | null {
    return this.requestId;
  }

  public trackUserAction(action: string, metadata?: Record<string, any>) {
    this.userJourney.push(`${Date.now()}: ${action}`);
    
    // Keep only last 50 actions
    if (this.userJourney.length > 50) {
      this.userJourney = this.userJourney.slice(-50);
    }

    // Add to Sentry breadcrumbs
    Sentry.addBreadcrumb({
      message: action,
      category: 'user_action',
      level: 'info',
      data: metadata,
    });
  }

  public trackPerformance(operation: string, duration: number) {
    if (!this.performanceBaselines[operation]) {
      this.performanceBaselines[operation] = [];
    }
    
    this.performanceBaselines[operation].push(duration);
    
    // Keep only last 100 measurements
    if (this.performanceBaselines[operation].length > 100) {
      this.performanceBaselines[operation] = this.performanceBaselines[operation].slice(-100);
    }

    // Log performance for AI analysis
    console.log(`Performance: ${operation} took ${duration}ms`, {
      operation,
      duration,
      baseline: this.getPerformanceBaseline(operation),
      ai_hint: duration > this.getPerformanceBaseline(operation) * 2 ? 'Performance regression detected' : 'Normal performance',
    });
  }

  private getPerformanceBaseline(operation: string): number {
    const measurements = this.performanceBaselines[operation];
    if (!measurements || measurements.length === 0) return 0;
    
    return measurements.reduce((sum, val) => sum + val, 0) / measurements.length;
  }

  public captureError(error: Error, context?: Record<string, any>) {
    const errorContext: ErrorContext = {
      requestId: this.requestId || 'no-request-id',
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: Date.now(),
      userJourney: [...this.userJourney],
      performanceMetrics: {
        loadTime: performance.now(),
        networkLatency: this.estimateNetworkLatency(),
        renderTime: this.estimateRenderTime(),
      },
    };

    // Send to backend error tracking
    this.sendErrorToBackend(error, errorContext, context);

    // Send to Sentry with enhanced context
    Sentry.withScope((scope) => {
      scope.setContext('ai_debug_context', errorContext);
      scope.setContext('additional_context', context);
      scope.setTag('request_id', errorContext.requestId);
      
      Sentry.captureException(error);
    });

    return errorContext;
  }

  private async sendErrorToBackend(error: Error, errorContext: ErrorContext, additionalContext?: Record<string, any>) {
    try {
      await fetch('/api/v1/monitoring/frontend-error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': errorContext.requestId,
        },
        body: JSON.stringify({
          error_id: errorContext.requestId,
          error_type: error.name,
          error_message: error.message,
          severity: this.classifyErrorSeverity(error),
          category: this.categorizeError(error),
          stack_trace: error.stack,
          context: {
            ...errorContext,
            ...additionalContext,
          },
          suggested_actions: this.getSuggestedActions(error),
          ai_debugging_hints: this.getAIDebuggingHints(error, errorContext),
        }),
      });
    } catch (backendError) {
      console.error('Failed to send error to backend:', backendError);
    }
  }

  private classifyErrorSeverity(error: Error): string {
    const criticalErrors = ['ChunkLoadError', 'TypeError', 'ReferenceError'];
    const highErrors = ['NetworkError', 'TimeoutError'];
    const mediumErrors = ['ValidationError', 'UserInputError'];

    if (criticalErrors.some(type => error.name.includes(type))) return 'critical';
    if (highErrors.some(type => error.name.includes(type))) return 'high';
    if (mediumErrors.some(type => error.name.includes(type))) return 'medium';
    
    return 'low';
  }

  private categorizeError(error: Error): string {
    if (error.name.includes('Network')) return 'network';
    if (error.name.includes('Chunk')) return 'bundle_loading';
    if (error.name.includes('Validation')) return 'user_input';
    if (error.message.includes('fetch')) return 'api_call';
    
    return 'unknown';
  }

  private getSuggestedActions(error: Error): string[] {
    const actions: string[] = [];
    
    if (error.name.includes('Network')) {
      actions.push('Check internet connection');
      actions.push('Retry the request');
    }
    
    if (error.name.includes('Chunk')) {
      actions.push('Refresh the page');
      actions.push('Clear browser cache');
    }
    
    if (error.message.includes('fetch')) {
      actions.push('Verify API endpoint availability');
      actions.push('Check request parameters');
    }
    
    return actions.length > 0 ? actions : ['Report this issue to support'];
  }

  private getAIDebuggingHints(error: Error, context: ErrorContext): string[] {
    const hints: string[] = [];
    
    hints.push(`Error occurred at ${new Date(context.timestamp).toISOString()}`);
    hints.push(`User journey leading to error: ${context.userJourney.slice(-3).join(' -> ')}`);
    
    if (context.performanceMetrics.loadTime > 3000) {
      hints.push('High load time may be related to error');
    }
    
    if (error.stack?.includes('async')) {
      hints.push('Async operation error - check promise handling');
    }
    
    return hints;
  }

  private estimateNetworkLatency(): number {
    // Simple estimation based on recent network performance
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      return connection.rtt || 0;
    }
    return 0;
  }

  private estimateRenderTime(): number {
    // Estimate based on performance timeline
    if ('performance' in window) {
      const paintEntries = performance.getEntriesByType('paint');
      const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
      return firstPaint ? firstPaint.startTime : 0;
    }
    return 0;
  }

  public getAIDebuggingSummary() {
    return {
      timestamp: new Date().toISOString(),
      current_request_id: this.requestId,
      user_journey_length: this.userJourney.length,
      recent_actions: this.userJourney.slice(-5),
      performance_summary: Object.entries(this.performanceBaselines).map(([operation, measurements]) => ({
        operation,
        avg_duration: measurements.reduce((sum, val) => sum + val, 0) / measurements.length,
        measurement_count: measurements.length,
      })),
      browser_context: {
        user_agent: navigator.userAgent,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        url: window.location.href,
      },
      ai_debugging_hints: [
        'Check recent_actions for user behavior patterns',
        'Review performance_summary for frontend bottlenecks',
        'Use current_request_id for backend correlation',
        'Analyze browser_context for environment-specific issues',
      ],
    };
  }
}

// Global instance
export const observability = new FrontendObservability();

// React hooks for easy integration
export const useObservability = () => {
  return {
    trackAction: observability.trackUserAction.bind(observability),
    captureError: observability.captureError.bind(observability),
    trackPerformance: observability.trackPerformance.bind(observability),
    getRequestId: observability.getCurrentRequestId.bind(observability),
    generateRequestId: observability.generateRequestId.bind(observability),
  };
};

// API client wrapper with observability
export const createObservableAPIClient = (baseURL: string) => {
  return {
    async request(endpoint: string, options: RequestInit = {}) {
      const requestId = observability.generateRequestId();
      const startTime = performance.now();
      
      // Add observability headers
      const headers = {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
        ...options.headers,
      };

      try {
        observability.trackUserAction(`API Request: ${options.method || 'GET'} ${endpoint}`);
        
        const response = await fetch(`${baseURL}${endpoint}`, {
          ...options,
          headers,
        });

        const duration = performance.now() - startTime;
        observability.trackPerformance(`api_${endpoint.replace(/\//g, '_')}`, duration);

        if (!response.ok) {
          throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
      } catch (error) {
        observability.captureError(error as Error, {
          api_endpoint: endpoint,
          api_method: options.method || 'GET',
          request_id: requestId,
        });
        throw error;
      }
    },
  };
}; 