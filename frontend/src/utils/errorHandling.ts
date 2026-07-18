// Custom error classes
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  constructor(message: string, public field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// Retry configuration
export interface RetryConfig {
  maxAttempts?: number;
  delayMs?: number;
  backoffMultiplier?: number;
  retryableErrors?: (error: Error) => boolean;
}

// Default retry configuration
const defaultRetryConfig: Required<RetryConfig> = {
  maxAttempts: 3,
  delayMs: 1000,
  backoffMultiplier: 2,
  retryableErrors: (error) => {
    // Retry on network errors and 5xx server errors
    return (
      error instanceof NetworkError ||
      (error instanceof ApiError && (error.statusCode || 0) >= 500)
    );
  },
};

// Retry function with exponential backoff
export async function retry<T>(
  fn: () => Promise<T>,
  config: RetryConfig = {}
): Promise<T> {
  const finalConfig = { ...defaultRetryConfig, ...config };
  let lastError: Error;

  for (let attempt = 1; attempt <= finalConfig.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // Check if error is retryable
      if (!finalConfig.retryableErrors(lastError)) {
        throw lastError;
      }

      // Don't wait after the last attempt
      if (attempt < finalConfig.maxAttempts) {
        const delay = finalConfig.delayMs * Math.pow(finalConfig.backoffMultiplier, attempt - 1);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError!;
}

// Safe async handler wrapper
export function safeAsync<T>(
  fn: () => Promise<T>,
  onError?: (error: Error) => void
): Promise<T | null> {
  return fn().catch((error) => {
    console.error('Async error:', error);
    onError?.(error);
    return null;
  });
}

// Error message formatter
export function formatErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.statusCode === 401) {
      return 'Authentication failed. Please sign in again.';
    }
    if (error.statusCode === 403) {
      return 'You do not have permission to perform this action.';
    }
    if (error.statusCode === 404) {
      return 'The requested resource was not found.';
    }
    if (error.statusCode === 429) {
      return 'Too many requests. Please try again later.';
    }
    if (error.statusCode && error.statusCode >= 500) {
      return 'Server error. Please try again later.';
    }
  }

  if (error instanceof NetworkError) {
    return 'Network error. Please check your connection and try again.';
  }

  if (error instanceof ValidationError) {
    return error.message;
  }

  return 'An unexpected error occurred. Please try again.';
}

// Error logger
export function logError(error: Error, context?: Record<string, any>) {
  const errorData = {
    message: error.message,
    name: error.name,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
  };

  console.error('Error logged:', errorData);

  // In production, send to error tracking service
  // Example: Sentry, LogRocket, etc.
  if (typeof window !== 'undefined' && (window as any).Sentry) {
    (window as any).Sentry.captureException(error, { extra: context });
  }
}

// Debounce utility for preventing rapid API calls
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

// Throttle utility for limiting API call frequency
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// Request timeout wrapper
export function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  timeoutMessage: string = 'Request timed out'
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error(timeoutMessage)), timeoutMs)
    ),
  ]);
}

// Circuit breaker pattern for preventing cascading failures
export class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime = 0;
  private isOpen = false;

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000 // 1 minute
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.isOpen) {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.isOpen = false;
        this.failureCount = 0;
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await fn();
      this.failureCount = 0;
      return result;
    } catch (error) {
      this.failureCount++;
      this.lastFailureTime = Date.now();

      if (this.failureCount >= this.threshold) {
        this.isOpen = true;
      }

      throw error;
    }
  }

  reset() {
    this.failureCount = 0;
    this.lastFailureTime = 0;
    this.isOpen = false;
  }

  getState() {
    return {
      isOpen: this.isOpen,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime,
    };
  }
}
