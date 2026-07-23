/**
 * Centralized API Configuration
 * Single source of truth for frontend API settings
 */

export const API_CONFIG = {
  // Base API URL - can be overridden by environment variable
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  
  // API version
  VERSION: 'v1',
  
  // Full API base URL with version
  get BASE_URL_WITH_VERSION(): string {
    return `${this.BASE_URL}/api/${this.VERSION}`;
  },
  
  // Request timeout in milliseconds
  TIMEOUT: 30000,
  
  // Default headers
  HEADERS: {
    'Content-Type': 'application/json',
  },
  
  // Authentication header key
  AUTH_HEADER: 'Authorization',
  
  // Authentication token prefix
  AUTH_PREFIX: 'Bearer',
};

export default API_CONFIG;
