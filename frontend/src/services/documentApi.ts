/** Document API service for document management. */
import axios from 'axios';
import API_CONFIG from '../config/api';

const API_BASE_URL = API_CONFIG.BASE_URL;

export interface Document {
  id: string;
  document_name: string;
  original_filename: string;
  mime_type: string;
  extension: string;
  file_size: number;
  checksum: string;
  storage_path: string;
  document_category: string;
  processing_status: string;
  version: number;
  description: string | null;
  tags: string[] | null;
  uploaded_by: string | null;
  uploaded_at: string;
  updated_at: string | null;
  is_deleted: boolean;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  last_accessed: string | null;
  future_metadata: Record<string, any> | null;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DocumentUpdate {
  document_name?: string;
  description?: string;
  tags?: string[];
  document_category?: string;
}

export interface DocumentFilters {
  filename?: string;
  category?: string;
  status?: string;
  uploaded_by?: string;
  date_from?: string;
  date_to?: string;
}

class DocumentApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
    };
  }

  async uploadDocument(
    file: File,
    metadata?: {
      document_name?: string;
      description?: string;
      tags?: string;
      category?: string;
    }
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (metadata?.document_name) {
      formData.append('document_name', metadata.document_name);
    }
    if (metadata?.description) {
      formData.append('description', metadata.description);
    }
    if (metadata?.tags) {
      formData.append('tags', metadata.tags);
    }
    if (metadata?.category) {
      formData.append('category', metadata.category);
    }

    const response = await axios.post(
      `${this.baseUrl}/api/v1/documents/upload`,
      formData,
      {
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data.document;
  }

  async uploadMultipleDocuments(files: File[]): Promise<Document[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await axios.post(
      `${this.baseUrl}/api/v1/documents/upload/multiple`,
      formData,
      {
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data.map((item: any) => item.document);
  }

  async listDocuments(
    page: number = 1,
    pageSize: number = 20,
    filters?: DocumentFilters,
    sortBy: string = 'uploaded_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<DocumentListResponse> {
    const params: any = {
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_order: sortOrder,
    };

    if (filters?.filename) params.filename = filters.filename;
    if (filters?.category) params.category = filters.category;
    if (filters?.status) params.status = filters.status;
    if (filters?.uploaded_by) params.uploaded_by = filters.uploaded_by;
    if (filters?.date_from) params.date_from = filters.date_from;
    if (filters?.date_to) params.date_to = filters.date_to;

    const response = await axios.get(`${this.baseUrl}/api/v1/documents`, {
      headers: this.getAuthHeaders(),
      params,
    });

    return response.data;
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await axios.get(
      `${this.baseUrl}/api/v1/documents/${documentId}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return response.data;
  }

  async downloadDocument(documentId: string): Promise<Blob> {
    const response = await axios.get(
      `${this.baseUrl}/api/v1/documents/${documentId}/download`,
      {
        headers: this.getAuthHeaders(),
        responseType: 'blob',
      }
    );

    return response.data;
  }

  async updateDocument(documentId: string, updateData: DocumentUpdate): Promise<Document> {
    const response = await axios.patch(
      `${this.baseUrl}/api/v1/documents/${documentId}`,
      updateData,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return response.data;
  }

  async deleteDocument(documentId: string): Promise<{ message: string; document_id: string }> {
    const response = await axios.delete(
      `${this.baseUrl}/api/v1/documents/${documentId}`,
      {
        headers: this.getAuthHeaders(),
      }
    );

    return response.data;
  }

  async searchDocuments(query: string, page: number = 1, pageSize: number = 20): Promise<DocumentListResponse> {
    const response = await axios.get(`${this.baseUrl}/api/v1/documents/search/query`, {
      headers: this.getAuthHeaders(),
      params: {
        query,
        page,
        page_size: pageSize,
      },
    });

    return response.data;
  }
}

export const documentApiService = new DocumentApiService();
