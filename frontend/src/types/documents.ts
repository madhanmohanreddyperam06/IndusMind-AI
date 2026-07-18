// Document Types

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  processed_date?: string;
  status: DocumentStatus;
  processing_status?: ProcessingStatus;
  ocr_status?: ProcessingStatus;
  extraction_status?: ProcessingStatus;
  graph_sync_status?: ProcessingStatus;
  vector_index_status?: ProcessingStatus;
  metadata?: DocumentMetadata;
}

export type DocumentStatus = 'uploaded' | 'processing' | 'processed' | 'failed';

export type ProcessingStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface DocumentMetadata {
  title?: string;
  author?: string;
  creation_date?: string;
  modification_date?: string;
  page_count?: number;
  language?: string;
  document_type?: string;
  equipment?: string[];
  tags?: string[];
}

export interface ProcessingTimeline {
  document_id: number;
  events: ProcessingEvent[];
}

export interface ProcessingEvent {
  event_type: string;
  status: ProcessingStatus;
  timestamp: string;
  duration_ms?: number;
  error_message?: string;
  metadata?: Record<string, any>;
}

export interface DocumentUploadResponse {
  document_id: number;
  filename: string;
  status: DocumentStatus;
  upload_date: string;
}

export interface ProcessedDocument {
  document_id: number;
  normalized_text: string;
  pages: DocumentPage[];
  tables: DocumentTable[];
  images: DocumentImage[];
  metadata: DocumentMetadata;
  processing_statistics: ProcessingStatistics;
}

export interface DocumentPage {
  page_number: number;
  text: string;
  layout_regions: LayoutRegion[];
}

export interface LayoutRegion {
  type: 'text' | 'table' | 'image' | 'header' | 'footer';
  bbox: [number, number, number, number];
  text?: string;
  confidence?: number;
}

export interface DocumentTable {
  table_id: string;
  page_number: number;
  rows: number;
  columns: number;
  data: string[][];
  bbox?: [number, number, number, number];
}

export interface DocumentImage {
  image_id: string;
  page_number: number;
  bbox: [number, number, number, number];
  ocr_text?: string;
  confidence?: number;
}

export interface ProcessingStatistics {
  total_pages: number;
  ocr_pages: number;
  extracted_tables: number;
  extracted_images: number;
  processing_time_ms: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
