/**
 * Secure Logging Utility
 * Prevents sensitive information from being logged in production
 */

interface LogConfig {
  enableDebug: boolean;
  enableInfo: boolean;
  enableWarn: boolean;
  enableError: boolean;
}

class SecureLogger {
  private config: LogConfig;

  constructor() {
    this.config = {
      enableDebug: import.meta.env.DEV,
      enableInfo: true,
      enableWarn: true,
      enableError: true
    };
  }

  /**
   * Log debug information (only in development)
   */
  debug(message: string, data?: any): void {
    if (this.config.enableDebug) {
      console.log(`🔧 ${message}`, this.sanitizeData(data));
    }
  }

  /**
   * Log info messages
   */
  info(message: string, data?: any): void {
    if (this.config.enableInfo) {
      console.log(`ℹ️ ${message}`, this.sanitizeData(data));
    }
  }

  /**
   * Log warning messages
   */
  warn(message: string, data?: any): void {
    if (this.config.enableWarn) {
      console.warn(`⚠️ ${message}`, this.sanitizeData(data));
    }
  }

  /**
   * Log error messages
   */
  error(message: string, error?: any): void {
    if (this.config.enableError) {
      console.error(`❌ ${message}`, this.sanitizeError(error));
    }
  }

  /**
   * Sanitize data to prevent sensitive information leakage
   */
  private sanitizeData(data: any): any {
    if (!data) return data;

    // If it's a string, check for sensitive patterns
    if (typeof data === 'string') {
      return this.sanitizeString(data);
    }

    // If it's an object, recursively sanitize
    if (typeof data === 'object') {
      const sanitized: any = {};
      for (const [key, value] of Object.entries(data)) {
        if (this.isSensitiveKey(key)) {
          sanitized[key] = '[REDACTED]';
        } else {
          sanitized[key] = this.sanitizeData(value);
        }
      }
      return sanitized;
    }

    return data;
  }

  /**
   * Sanitize error objects
   */
  private sanitizeError(error: any): any {
    if (!error) return error;

    // Don't log full error objects in production
    if (!import.meta.env.DEV) {
      return {
        message: error.message || 'Unknown error',
        type: error.constructor.name
      };
    }

    return error;
  }

  /**
   * Sanitize strings to remove sensitive information
   */
  private sanitizeString(str: string): string {
    if (!str) return str;

    // Remove API keys, tokens, and other sensitive patterns
    return str
      .replace(/sk-[a-zA-Z0-9]{20,}/g, '[API_KEY]')
      .replace(/eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}/g, '[JWT_TOKEN]')
      .replace(/[a-zA-Z0-9]{20,}/g, (match) => {
        // Only redact if it looks like a key/token
        if (match.length > 30) return '[TOKEN]';
        return match;
      });
  }

  /**
   * Check if a key name indicates sensitive data
   */
  private isSensitiveKey(key: string): boolean {
    const sensitivePatterns = [
      /api[_-]?key/i,
      /token/i,
      /secret/i,
      /password/i,
      /auth/i,
      /credential/i,
      /private/i
    ];

    return sensitivePatterns.some(pattern => pattern.test(key));
  }

  /**
   * Log configuration status safely
   */
  logConfigStatus(config: Record<string, any>): void {
    const sanitizedConfig: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(config)) {
      if (this.isSensitiveKey(key)) {
        sanitizedConfig[key] = value ? '[CONFIGURED]' : '[NOT_SET]';
      } else {
        sanitizedConfig[key] = value;
      }
    }

    this.info('Configuration Status', sanitizedConfig);
  }
}

// Export singleton instance
export const secureLogger = new SecureLogger(); 