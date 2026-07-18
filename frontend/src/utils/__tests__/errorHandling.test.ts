import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  ApiError,
  NetworkError,
  ValidationError,
  retry,
  formatErrorMessage,
  debounce,
  throttle,
  CircuitBreaker,
} from '../errorHandling';

describe('Error Classes', () => {
  it('creates ApiError with correct properties', () => {
    const error = new ApiError('Not found', 404);
    expect(error.message).toBe('Not found');
    expect(error.statusCode).toBe(404);
    expect(error.name).toBe('ApiError');
  });

  it('creates NetworkError with correct properties', () => {
    const error = new NetworkError('Connection failed');
    expect(error.message).toBe('Connection failed');
    expect(error.name).toBe('NetworkError');
  });

  it('creates ValidationError with field', () => {
    const error = new ValidationError('Invalid email', 'email');
    expect(error.message).toBe('Invalid email');
    expect(error.field).toBe('email');
    expect(error.name).toBe('ValidationError');
  });
});

describe('retry function', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('retries on retryable error', async () => {
    const mockFn = vi.fn()
      .mockRejectedValueOnce(new NetworkError('Network error'))
      .mockResolvedValueOnce('success');

    const result = await retry(mockFn, { maxAttempts: 2, delayMs: 100 });

    expect(result).toBe('success');
    expect(mockFn).toHaveBeenCalledTimes(2);
  });

  it('does not retry on non-retryable error', async () => {
    const mockFn = vi.fn().mockRejectedValue(new ValidationError('Invalid data'));

    await expect(retry(mockFn)).rejects.toThrow(ValidationError);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('throws error after max attempts', async () => {
    const mockFn = vi.fn().mockRejectedValue(new NetworkError('Network error'));

    await expect(retry(mockFn, { maxAttempts: 2, delayMs: 100 })).rejects.toThrow(NetworkError);
    expect(mockFn).toHaveBeenCalledTimes(2);
  });
});

describe('formatErrorMessage', () => {
  it('formats ApiError with 401 status', () => {
    const error = new ApiError('Unauthorized', 401);
    expect(formatErrorMessage(error)).toContain('Authentication failed');
  });

  it('formats ApiError with 403 status', () => {
    const error = new ApiError('Forbidden', 403);
    expect(formatErrorMessage(error)).toContain('permission');
  });

  it('formats NetworkError', () => {
    const error = new NetworkError('Connection failed');
    expect(formatErrorMessage(error)).toContain('Network error');
  });

  it('formats ValidationError', () => {
    const error = new ValidationError('Invalid email');
    expect(formatErrorMessage(error)).toBe('Invalid email');
  });

  it('formats generic error', () => {
    const error = new Error('Unknown error');
    expect(formatErrorMessage(error)).toContain('unexpected error');
  });
});

describe('debounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('delays function execution', () => {
    const mockFn = vi.fn();
    const debouncedFn = debounce(mockFn, 100);

    debouncedFn();
    expect(mockFn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('cancels previous calls', () => {
    const mockFn = vi.fn();
    const debouncedFn = debounce(mockFn, 100);

    debouncedFn();
    debouncedFn();
    debouncedFn();

    vi.advanceTimersByTime(100);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });
});

describe('throttle', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('limits function execution frequency', () => {
    const mockFn = vi.fn();
    const throttledFn = throttle(mockFn, 100);

    throttledFn();
    throttledFn();
    throttledFn();

    expect(mockFn).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(100);
    throttledFn();
    expect(mockFn).toHaveBeenCalledTimes(2);
  });
});

describe('CircuitBreaker', () => {
  it('executes function successfully', async () => {
    const circuitBreaker = new CircuitBreaker();
    const mockFn = vi.fn().mockResolvedValue('success');

    const result = await circuitBreaker.execute(mockFn);

    expect(result).toBe('success');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('opens circuit after threshold failures', async () => {
    const circuitBreaker = new CircuitBreaker(3, 1000);
    const mockFn = vi.fn().mockRejectedValue(new Error('Failed'));

    for (let i = 0; i < 3; i++) {
      await expect(circuitBreaker.execute(mockFn)).rejects.toThrow();
    }

    // Circuit should be open now
    await expect(circuitBreaker.execute(mockFn)).rejects.toThrow('Circuit breaker is open');
    expect(mockFn).toHaveBeenCalledTimes(3);
  });

  it('resets circuit after timeout', async () => {
    vi.useFakeTimers();
    const circuitBreaker = new CircuitBreaker(2, 1000);
    const mockFn = vi.fn()
      .mockRejectedValueOnce(new Error('Failed'))
      .mockRejectedValueOnce(new Error('Failed'))
      .mockResolvedValueOnce('success');

    // Fail twice to open circuit
    await expect(circuitBreaker.execute(mockFn)).rejects.toThrow();
    await expect(circuitBreaker.execute(mockFn)).rejects.toThrow();

    // Wait for timeout
    vi.advanceTimersByTime(1000);

    // Circuit should be closed now
    const result = await circuitBreaker.execute(mockFn);
    expect(result).toBe('success');

    vi.restoreAllMocks();
  });

  it('can be manually reset', async () => {
    const circuitBreaker = new CircuitBreaker(2, 1000);
    const mockFn = vi.fn().mockRejectedValue(new Error('Failed'));

    // Fail twice to open circuit
    await expect(circuitBreaker.execute(mockFn)).rejects.toThrow();
    await expect(circuitBreaker.execute(mockFn)).rejects.toThrow();

    circuitBreaker.reset();

    // Circuit should be closed now
    const result = await circuitBreaker.execute(mockFn);
    expect(result).rejects.toThrow(); // Still fails but circuit is not open
  });
});
