import { Loader2, AlertCircle, CheckCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function LoadingSpinner({ size = "md", className }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <Loader2 
      className={cn(
        "animate-spin text-primary",
        sizeClasses[size],
        className
      )} 
    />
  );
}

interface LoadingCardProps {
  className?: string;
  lines?: number;
}

export function LoadingCard({ className, lines = 3 }: LoadingCardProps) {
  return (
    <div className={cn("animate-pulse", className)}>
      <div className="bg-muted/50 rounded-lg p-4 space-y-3">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-muted rounded-full"></div>
          <div className="h-4 bg-muted rounded w-24"></div>
          <div className="h-4 bg-muted rounded w-16"></div>
        </div>
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, i) => (
            <div 
              key={i} 
              className={cn(
                "h-4 bg-muted rounded",
                i === lines - 1 ? "w-1/2" : "w-full"
              )}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

interface StatusIndicatorProps {
  status: 'loading' | 'success' | 'error' | 'idle';
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function StatusIndicator({ 
  status, 
  message, 
  onRetry, 
  className 
}: StatusIndicatorProps) {
  const getIcon = () => {
    switch (status) {
      case 'loading':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getTextColor = () => {
    switch (status) {
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <div className={cn("flex items-center justify-between p-3 bg-muted/50 rounded-lg border", className)}>
      <div className="flex items-center gap-2 text-sm">
        {getIcon()}
        <span className={getTextColor()}>
          {message}
        </span>
      </div>
      
      {status === 'error' && onRetry && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRetry}
          className="h-8 px-2 text-xs"
        >
          <RefreshCw className="w-3 h-3" />
          Retry
        </Button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({ 
  icon, 
  title, 
  description, 
  action, 
  className 
}: EmptyStateProps) {
  return (
    <div className={cn("text-center py-12 animate-fade-in", className)}>
      {icon && (
        <div className="w-16 h-16 rounded-full bg-pulse-100 flex items-center justify-center mx-auto mb-4">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-medium text-calm-800 mb-2">
        {title}
      </h3>
      <p className="text-calm-600 mb-6 max-w-sm mx-auto">
        {description}
      </p>
      {action && (
        <Button
          onClick={action.onClick}
          className="gap-2 bg-gradient-to-r from-pulse-500 to-pulse-600 hover:from-pulse-600 hover:to-pulse-700 text-white rounded-xl transition-all duration-200 hover:scale-105 active:scale-95"
        >
          {action.label}
        </Button>
      )}
    </div>
  );
}

interface ErrorBoundaryFallbackProps {
  error?: Error;
  resetError?: () => void;
}

export function ErrorBoundaryFallback({ error, resetError }: ErrorBoundaryFallbackProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-6 text-center">
      <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
        <AlertCircle className="w-8 h-8 text-red-500" />
      </div>
      <h3 className="text-lg font-medium text-calm-800 mb-2">
        Something went wrong
      </h3>
      <p className="text-calm-600 mb-6 max-w-sm">
        We encountered an unexpected error. Please try refreshing the page.
      </p>
      {error && (
        <details className="mb-4 text-left">
          <summary className="cursor-pointer text-sm text-calm-500 hover:text-calm-700">
            Error details
          </summary>
          <pre className="mt-2 text-xs text-calm-600 bg-muted p-2 rounded overflow-auto">
            {error.message}
          </pre>
        </details>
      )}
      <div className="flex gap-2">
        <Button
          onClick={() => window.location.reload()}
          variant="outline"
          className="gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Page
        </Button>
        {resetError && (
          <Button
            onClick={resetError}
            className="gap-2"
          >
            Try Again
          </Button>
        )}
      </div>
    </div>
  );
} 