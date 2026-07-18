// Main types export
export * from './rag';
export * from './graph';
export * from './documents';
export * from './extraction';

// Common types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SearchFilters {
  query?: string;
  document_type?: string;
  equipment?: string;
  entity_type?: string;
  date_from?: string;
  date_to?: string;
  confidence_min?: number;
}

export interface KPICard {
  title: string;
  value: number | string;
  change?: number;
  change_type?: 'increase' | 'decrease';
  icon?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color?: string;
  }[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    handler: () => void;
  };
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  llm_provider: string;
  max_response_length: number;
  streaming_enabled: boolean;
  citation_display: 'inline' | 'panel' | 'both';
  confidence_threshold: number;
  notifications_enabled: boolean;
}
